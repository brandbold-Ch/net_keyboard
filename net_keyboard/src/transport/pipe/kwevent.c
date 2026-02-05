#include <windows.h>
#include <stdio.h>
#include <winsock2.h>
#include <stdint.h>

#pragma pack(push, 1)
struct KeyEvent {
    uint16_t code;
    uint8_t state;
    uint64_t time;
};
#pragma pack(pop)

struct KeyEvent ev = {0};
HANDLE pipe;

uint64_t now_us() {
    FILETIME ft;
    GetSystemTimeAsFileTime(&ft);
    uint64_t t = ((uint64_t) ft.dwHighDateTime << 32) | ft.dwLowDateTime;
    return (t - 116444736000000000ULL) / 10;
}

HANDLE pipe_server() {
    HANDLE _pipe = CreateNamedPipeA(
        "\\\\.\\pipe\\keyboard_ipc",
        PIPE_ACCESS_OUTBOUND,
        PIPE_TYPE_BYTE | PIPE_WAIT,
        1, 0, 0, 0, 
        NULL
    );

    if (_pipe == INVALID_HANDLE_VALUE) {
        return NULL;
    }

    ConnectNamedPipe(_pipe, NULL);
    
    return _pipe;
}

UINT __stdcall raw_input_data(LPARAM lParam, LPVOID lPvoid, PUINT size) {
    return GetRawInputData((HRAWINPUT) lParam, RID_INPUT, lPvoid, size, sizeof(RAWINPUTHEADER));
}

LRESULT CALLBACK WndProc(HWND hwnd, UINT msg, WPARAM wParam, LPARAM lParam) {
    if (msg == WM_INPUT) {
        UINT size = 0;

        raw_input_data(lParam, NULL, &size);

        BYTE buffer[512];
        if (size > sizeof(buffer)) return 0;

        raw_input_data(lParam, buffer, &size);

        RAWINPUT *raw = (RAWINPUT *) buffer;

        if (raw -> header.dwType == RIM_TYPEKEYBOARD) {
            RAWKEYBOARD *kb = &raw -> data.keyboard;
            int down = !(kb -> Flags & RI_KEY_BREAK);
            
            ev.code = kb->MakeCode;
            ev.state = down ? 1 : 0;
            ev.time = now_us();
            
            DWORD written;
            WriteFile(pipe, &ev, sizeof(ev), &written, NULL);
        }
        return 0;
    }
    return DefWindowProc(hwnd, msg, wParam, lParam);
}

int main() {
    pipe = pipe_server();

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
    rid.usUsage = 0x06;
    rid.dwFlags = RIDEV_EXINPUTSINK | RIDEV_NOLEGACY;
    rid.hwndTarget = hwnd;

    if (!RegisterRawInputDevices(&rid, 1, sizeof(rid))) {
        printf("RegisterRawInputDevices failed: %lu\n", GetLastError());
        return 1;
    }
    
    MSG msg;
    while (GetMessage(&msg, NULL, 0, 0) > 0) {
        DispatchMessage(&msg);
    }

    return 0;
}
