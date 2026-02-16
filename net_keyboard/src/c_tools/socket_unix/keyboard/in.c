#include <linux/uinput.h>
#include <linux/input-event-codes.h>

#include <sys/socket.h>
#include <sys/un.h>
#include <sys/ioctl.h>
#include <unistd.h>
#include <fcntl.h>
#include <stddef.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>
#include <errno.h>

// ----- Protocolo -----
#pragma pack(push, 1)
struct KeyEvent {
    uint16_t code;
    uint8_t  state; // 1 = down, 0 = up
    uint64_t time;  // timestamp (no usado aquí)
};
#pragma pack(pop)

// ----- Utils -----
static ssize_t read_full(int fd, void *buf, size_t size) {
    size_t off = 0;
    while (off < size) {
        ssize_t n = read(fd, (char*)buf + off, size - off);
        if (n < 0) {
            if (errno == EINTR) continue;
            return -1;
        }
        if (n == 0) return 0; // EOF
        off += n;
    }
    return off;
}

static int connect_unix(const char *path) {
    int s = socket(AF_UNIX, SOCK_STREAM, 0);
    if (s < 0) return -1;

    struct sockaddr_un addr;
    memset(&addr, 0, sizeof(addr));
    addr.sun_family = AF_UNIX;

    if (strlen(path) >= sizeof(addr.sun_path)) {
        close(s);
        errno = ENAMETOOLONG;
        return -1;
    }
    strcpy(addr.sun_path, path);

    socklen_t len = offsetof(struct sockaddr_un, sun_path) + strlen(addr.sun_path) + 1;
    if (connect(s, (struct sockaddr*)&addr, len) < 0) {
        close(s);
        return -1;
    }
    return s;
}

// ----- uinput -----
static int setup_uinput(void) {
    int fd = open("/dev/uinput", O_WRONLY | O_NONBLOCK);
    if (fd < 0) return -1;

    if (ioctl(fd, UI_SET_EVBIT, EV_KEY) < 0) return -1;

    // Habilita todas las teclas
    for (int k = KEY_ESC; k <= KEY_MAX; ++k) {
        ioctl(fd, UI_SET_KEYBIT, k);
    }

    struct uinput_setup us;
    memset(&us, 0, sizeof(us));
    snprintf(us.name, UINPUT_MAX_NAME_SIZE, "virtual-ipc-keyboard");
    us.id.bustype = BUS_USB;
    us.id.vendor  = 0x1234;
    us.id.product = 0x5678;
    us.id.version = 1;

    if (ioctl(fd, UI_DEV_SETUP, &us) < 0) return -1;
    if (ioctl(fd, UI_DEV_CREATE) < 0) return -1;

    usleep(100000); // espera a que el kernel registre el device
    return fd;
}

static int emit_event(int ufd, uint16_t type, uint16_t code, int32_t value) {
    struct input_event ev;
    memset(&ev, 0, sizeof(ev));
    ev.type = type;
    ev.code = code;
    ev.value = value;
    if (write(ufd, &ev, sizeof(ev)) != sizeof(ev)) return -1;
    return 0;
}

static int inject_key(int ufd, uint16_t code, uint8_t state) {
    if (emit_event(ufd, EV_KEY, code, state ? 1 : 0) < 0) return -1;
    if (emit_event(ufd, EV_SYN, SYN_REPORT, 0) < 0) return -1;
    return 0;
}

// ----- main -----
int main(int argc, char **argv) {
    if (argc != 2) {
        fprintf(stderr, "Uso: %s /ruta/al/socket_unix\n", argv[0]);
        return 1;
    }

    const char *sock_path = argv[1];

    int sock = connect_unix(sock_path);
    if (sock < 0) {
        perror("connect_unix");
        return 1;
    }

    int ufd = setup_uinput();
    if (ufd < 0) {
        perror("setup_uinput");
        close(sock);
        return 1;
    }

    printf("Conectado. Esperando eventos...\n");

    struct KeyEvent kev;
    for (;;) {
        ssize_t n = read_full(sock, &kev, sizeof(kev));
        if (n <= 0) {
            perror("read socket");
            break;
        }

        // Inyecta la tecla (ignora kev.time por ahora)
        if (inject_key(ufd, kev.code, kev.state) < 0) {
            perror("inject_key");
            break;
        }
    }

    ioctl(ufd, UI_DEV_DESTROY);
    close(ufd);
    close(sock);
    return 0;
}