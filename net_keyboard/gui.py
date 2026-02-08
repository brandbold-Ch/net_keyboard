import os
import sys
from pathlib import Path

from PySide6.QtCore import QPoint, QSize
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QApplication, QLabel, QMainWindow, QPushButton, QWidget

from src.backends.keyboard import EventListener
from src.core.mkv_client import MKVClient
from src.core.mkv_server import MKVServer
from src.transport.ipc.tools import IPCProcessLauncher, KeyListener, scan_keyboard
from src.utils.config import e

BASE_DIR = Path(__file__).resolve().parent

listener: EventListener
OS = os.name


def launcher_factory() -> IPCProcessLauncher:
    kbds = (
        scan_keyboard()
    )  # usb-1bcf_08a0-event-kbd usb-BY_Tech_Gaming_Keyboard-event-kbd

    return (
        IPCProcessLauncher(
            client="bin/socket_unix/klevent"
            if OS == "posix"
            else "bin/pipe/kwevent.exe",
            server=KeyListener(
                on_press=listener.on_press,
                on_release=listener.on_release,
                device=str(kbds["usb-BY_Tech_Gaming_Keyboard-event-kbd"]),
            ),
            shared="/tmp/keyboard_ipc.sock"
            if OS == "posix"
            else r"\\.\pipe\keyboard_ipc",
        )
        if OS == "posix"
        else IPCProcessLauncher(
            server="bin/socket_unix/klevent"
            if OS == "posix"
            else "bin/pipe/kwevent.exe",
            client=KeyListener(
                on_press=listener.on_press, on_release=listener.on_release
            ),
            shared="/tmp/keyboard_ipc.sock"
            if OS == "posix"
            else r"\\.\pipe\keyboard_ipc",
        )
    )


listener = EventListener(launcher_factory)
listener.listen()


def build_server() -> None:
    server = MKVServer(e.CLIENT_HOST, e.CLIENT_PORT, listener)
    server.start()


def build_client() -> None:
    client = MKVClient(e.CLIENT_HOST, e.CLIENT_PORT, listener)
    client.start()


class MKV(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("NetKeyboard")
        self.setFixedSize(QSize(400, 400))

        self.os_name = os.name

        self.main = self.main_screen()

    def main_screen(self) -> QWidget:
        container = QWidget(self)
        container.setFixedSize(QSize(400, 400))

        os_img = QLabel(container)
        os_img.setFixedSize(QSize(120, 120))
        os_img.setScaledContents(True)
        os_img.move(QPoint(147, 50))

        mkv_mode = QLabel(container)
        mkv_mode.setText("MKV Mode")
        mkv_mode.move(QPoint(167, 185))

        client_mode = QPushButton(container)
        client_mode.setFixedSize(QSize(150, 50))
        client_mode.setText("Client")
        client_mode.move(QPoint(130, 230))
        client_mode.clicked.connect(lambda: self.client_screen())

        server_mode = QPushButton(container)
        server_mode.setFixedSize(QSize(150, 50))
        server_mode.setText("Server")
        server_mode.move(QPoint(130, 295))
        server_mode.clicked.connect(lambda: self.server_screen())

        os_name = QLabel(container)

        if self.os_name == "posix":
            os_img.setPixmap(QPixmap(BASE_DIR / "linux.png"))
            os_name.setText("OS: Linux")
            os_name.move(QPoint(175, 10))

        elif self.os_name == "nt":
            os_img.setPixmap(QPixmap(BASE_DIR / "windows.png"))
            os_name.setText("OS: Windows")
            os_name.move(QPoint(170, 10))

        container.show()
        return container

    def server_screen(self):
        self.main.hide()
        print("Listening Server")
        build_server()

        screen = QWidget(self)
        screen.setFixedSize(QSize(400, 400))
        screen.show()

    def client_screen(self):
        self.main.hide()
        print("Client ready")
        build_client()

        screen = QWidget(self)
        screen.setFixedSize(QSize(400, 400))
        screen.show()


app = QApplication(sys.argv)
mkv = MKV()
mkv.show()
sys.exit(app.exec())
