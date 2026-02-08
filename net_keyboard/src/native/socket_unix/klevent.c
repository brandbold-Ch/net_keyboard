#include <linux/input-event-codes.h>
#include <stddef.h>
#include <stdio.h>
#include <stdint.h>
#include <fcntl.h>
#include <string.h>
#include <unistd.h>

#include <linux/input.h>
#include <sys/socket.h>
#include <sys/un.h>
#include <limits.h>
#include <libgen.h>

#define MAX_PATH 256

#pragma pack(push, 1)
struct KeyEvent {
    u_int16_t code;
    u_int8_t state;
    u_int64_t time;
};
#pragma pack(pop)

int get_exe_dir(char *out, size_t size) {
    ssize_t len = readlink("/proc/self/exe", out, size - 1);
    if (len < 0) return -1;
    out[len] = 0;

    char *dir = dirname(out);
    memmove(out, dir, strlen(dir) + 1);
    return 0;
}

int read_path_file(const char *filename, char *out, size_t out_size) {
    FILE *f = fopen(filename, "r");
    if (!f) return -1;

    if (!fgets(out, out_size, f)) {
        fclose(f);
        return -1;
    }

    out[strcspn(out, "\r\n")] = 0;

    fclose(f);
    return 0;
}

int client_socket(const char *shared_path) {
    int _socket = socket(AF_UNIX, SOCK_STREAM, 0);
    struct sockaddr_un addr = {0};

    addr.sun_family = AF_UNIX;
    strncpy(addr.sun_path, shared_path, sizeof(addr.sun_path));

    if (connect(_socket, (struct sockaddr*)&addr, sizeof(addr)) < 0) {
        close(_socket);
        return -1;
    }

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
    char shared_path[MAX_PATH];
    char device_path[MAX_PATH];

    char exe_dir[PATH_MAX];
    if (get_exe_dir(exe_dir, sizeof(exe_dir)) != 0) {
        perror("get_exe_dir");
        return 1;
    }

    char shared_cfg[PATH_MAX];
    char device_cfg[PATH_MAX];

    snprintf(shared_cfg, sizeof(shared_cfg), "%s/../shared.txt", exe_dir);
    snprintf(device_cfg, sizeof(device_cfg), "%s/../device.txt", exe_dir);

    if (read_path_file(shared_cfg, shared_path, sizeof(shared_path))) {
        perror("read shared.txt");
        return 1;
    }

    if (read_path_file(device_cfg, device_path, sizeof(device_path))) {
        perror("read device.txt");
        return 1;
    }

    int fd = open(device_path, O_RDONLY);
    if (fd < 0) {
        perror("open");
        return 1;
    }

    int client = client_socket(shared_path);
    if (client < 0) {
        perror("connect socket");
        close(fd);
        return 1;
    }

    struct input_event ev;

    while (1) {
        ssize_t n = read(fd, &ev, sizeof(ev));

        if (n == sizeof(ev) && ev.type == EV_KEY) {
            struct KeyEvent kev = kev_packet(ev);
            write(client, &kev, sizeof(kev));
        }
    }

    close(fd);
    return 0;
}
