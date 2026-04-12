#include <windows.h>
#include <stdio.h>
#include <stdint.h>
#include <string.h>
#include <stdlib.h>

#define MAX_PATH_LEN 260

#pragma pack(push, 1)
struct KeyEvent {
    uint16_t code;
    uint8_t  state;
    uint64_t time;
};
#pragma pack(pop)

HANDLE pipe = NULL;
HANDLE target_device = NULL;

uint64_t now_us() {
    FILETIME ft;
    GetSystemTimeAsFileTime(&ft);
    uint64_t t = ((uint64_t)ft.dwHighDateTime << 32) | ft.dwLowDateTime;
    return (t - 116444736000000000ULL) / 10;
}

int get_exe_dir(char *out, size_t size) {
    DWORD len = GetModuleFileNameA(NULL, out, (DWORD)size);
    if (len == 0 || len == size) return -1;

    for (int i = len - 1; i >= 0; i--) {
        if (out[i] == '\\') {
            out[i] = '\0';
            break;
        }
    }
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

// 🔥 SERVER PIPE (FIX REAL)
HANDLE pipe_server(const char *path) {
    HANDLE h = CreateNamedPipeA(
        path,
        PIPE_ACCESS_OUTBOUND,
        PIPE_TYPE_BYTE | PIPE_WAIT,
        1,
        0,
        0,
        0,
        NULL
    );

    if (h == INVALID_HANDLE_VALUE) {
        printf("CreateNamedPipe failed: %lu\n", GetLastError());
        return NULL;
    }

    printf("Waiting for Python client...\n");

    if (!ConnectNamedPipe(h, NULL)) {
        if (GetLastError() != ERROR_PIPE_CONNECTED) {
            printf("ConnectNamedPipe failed: %lu\n", GetLastError());
            CloseHandle(h);
            return NULL;
        }
    }

    printf("Client connected!\n");
    return h;
}

// 🔥 DEVICE MATCH FLEXIBLE
int find_device(const char *wanted) {
    UINT count = 0;
    if (GetRawInputDeviceList(NULL, &count, sizeof(RAWINPUTDEVICELIST)) != 0)
        return -1;

    RAWINPUTDEVICELIST *list = malloc(sizeof(*list) * count);
    if (!list) return -1;

    if (GetRawInputDeviceList(list, &count, sizeof(RAWINPUTDEVICELIST)) == (UINT)-1) {
        free(list);
        return -1;
    }

    for (UINT i = 0; i < count; i++) {
        if (list[i].dwType != RIM_TYPEKEYBOARD) continue;

        char name[512];
        UINT size = sizeof(name);

        if (GetRawInputDeviceInfoA(list[i].hDevice, RIDI_DEVICENAME, name, &size) > 0) {

            printf("DEVICE: %s\n", name);

            if (strstr(name, wanted)) {
                printf("MATCHED DEVICE\n");
                target_device = list[i].hDevice;
                free(list);
                return 0;
            }
        }
    }

    free(list);
    return -1;
}

UINT raw_input_data(LPARAM lParam, LPVOID buffer, PUINT size) {
    return GetRawInputData((HRAWINPUT)lParam, RID_INPUT, buffer, size, sizeof(RAWINPUTHEADER));
}

void send_event(struct KeyEvent *ev) {
    DWORD written;
    if (!WriteFile(pipe, ev, sizeof(*ev), &written, NULL) || written != sizeof(*ev)) {
        printf("write error: %lu\n", GetLastError());
    }
}

LRESULT CALLBACK WndProc(HWND hwnd, UINT msg, WPARAM wParam, LPARAM lParam) {

    if (msg == WM_INPUT) {

        UINT size = 0;
        raw_input_data(lParam, NULL, &size);

        BYTE buffer[512];
        if (size > sizeof(buffer)) return 0;

        raw_input_data(lParam, buffer, &size);

        RAWINPUT *raw = (RAWINPUT*)buffer;

        if (raw->header.dwType == RIM_TYPEKEYBOARD) {

            if (target_device && raw->header.hDevice != target_device)
                return 0;

            RAWKEYBOARD *kb = &raw->data.keyboard;

            struct KeyEvent ev;
            ev.code  = kb->MakeCode;
            ev.state = !(kb->Flags & RI_KEY_BREAK);
            ev.time  = now_us();

            send_event(&ev);
        }
        return 0;
    }

    return DefWindowProc(hwnd, msg, wParam, lParam);
}

int main() {
    char exe_dir[MAX_PATH_LEN];
    char shared_cfg[MAX_PATH_LEN];
    char device_cfg[MAX_PATH_LEN];

    char shared_path[MAX_PATH_LEN];
    char device_name[512];

    if (get_exe_dir(exe_dir, sizeof(exe_dir)) != 0) {
        printf("get_exe_dir failed\n");
        return 1;
    }

    snprintf(shared_cfg, sizeof(shared_cfg), "%s\\..\\..\\shared.txt", exe_dir);
    snprintf(device_cfg, sizeof(device_cfg), "%s\\..\\..\\device.txt", exe_dir);

    printf("shared file: %s\n", shared_cfg);
    printf("device file: %s\n", device_cfg);

    if (read_path_file(shared_cfg, shared_path, sizeof(shared_path))) {
        printf("read shared.txt failed\n");
        return 1;
    }

    if (read_path_file(device_cfg, device_name, sizeof(device_name))) {
        printf("read device.txt failed\n");
        return 1;
    }

    if (find_device(device_name) != 0) {
        printf("device not found\n");
        return 1;
    }

    // 🔥 SERVER (FIX)
    pipe = pipe_server(shared_path);
    if (!pipe) {
        printf("pipe server failed\n");
        return 1;
    }

    // 🔥 ventana (como la que sí funciona)
    WNDCLASS wc = {0};
    wc.lpfnWndProc = WndProc;
    wc.lpszClassName = "RawInputWindow";
    RegisterClass(&wc);

    HWND hwnd = CreateWindowEx(
        0,
        wc.lpszClassName,
        "RawInput",
        WS_OVERLAPPEDWINDOW,
        0, 0, 100, 100,
        NULL, NULL, NULL, NULL
    );

    ShowWindow(hwnd, SW_HIDE);

    RAWINPUTDEVICE rid;
    rid.usUsagePage = 0x01;
    rid.usUsage     = 0x06;
    rid.dwFlags     = RIDEV_EXINPUTSINK | RIDEV_NOLEGACY;
    rid.hwndTarget  = hwnd;

    if (!RegisterRawInputDevices(&rid, 1, sizeof(rid))) {
        printf("RegisterRawInputDevices failed: %lu\n", GetLastError());
        return 1;
    }

    MSG msg;
    while (GetMessage(&msg, NULL, 0, 0) > 0) {
        DispatchMessage(&msg);
    }

    CloseHandle(pipe);
    return 0;
}
