#include <stdio.h>
#include <stdint.h>
#include <fcntl.h>
#include <unistd.h>

#include <linux/input.h>
#include <sys/socket.h>
#include <sys/un.h>

#pragma pack(push, 1)
struct KeyEvent {
    u_int16_t code;
    u_int8_t state;
    u_int64_t time;
};
#pragma pack(pop)

int client_socket() {
    int _socket = socket(AF_UNIX, SOCK_STREAM, 0);
    struct sockaddr_un addr = {0};

    addr.sun_family = AF_UNIX;
    strncpy(addr.sun_path, "/tmp/keyboard_ipc.sock", sizeof(addr.sun_path));
    connect(_socket, (struct sockaddr*)&addr, sizeof(addr));

    return _socket;
}

struct KeyEvent kev_packet(struct input_event ev) {
    struct KeyEvent kev;

    kev.code = ev.code;
    kev.state = ev.value;
    kev.time = ev.time.tv_sec * 1000000 + ev.time.tv_usec;

    return kev;
}

int main() {
    struct input_event ev;
    int fd = open("/dev/input/event4", O_RDONLY);
    int client = client_socket();

    if (fd < 0) {
        perror("open");
        return 1;
    }

    while (1) {
        ssize_t n = read(fd, &ev, sizeof(ev));

        if (n == sizeof(ev)) {
            if (ev.type == EV_KEY) {
                struct KeyEvent kev = kev_packet(ev);
                write(client, &kev, sizeof(kev));
            }
        }
    }

    close(fd);
    return 0;
}
