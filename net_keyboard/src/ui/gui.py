import os
import sys
from pathlib import Path

from PySide6.QtCore import QPoint, QSize
from PySide6.QtGui import QIcon, QPixmap
from PySide6.QtWidgets import QApplication, QLabel, QMainWindow, QPushButton, QWidget

from src.core.keyboard import MKVClient, MKVServer

BASE_DIR = Path(__file__).resolve().parent


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

        posix_mode = QPushButton(container)
        posix_mode.setFixedSize(QSize(150, 50))
        posix_mode.setText("Client")
        posix_mode.move(QPoint(130, 230))
        posix_mode.clicked.connect(lambda: self.client_screen())

        nt_mode = QPushButton(container)
        nt_mode.setFixedSize(QSize(150, 50))
        nt_mode.setText("Server")
        nt_mode.move(QPoint(130, 295))
        posix_mode.clicked.connect(lambda: self.server_screen())

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

        screen = QWidget(self)
        screen.setFixedSize(QSize(400, 400))
        screen.show()

    def client_screen(self):
        self.main.hide()

        screen = QWidget(self)
        screen.setFixedSize(QSize(400, 400))
        screen.show()


app = QApplication(sys.argv)
mkv = MKV()
mkv.show()
sys.exit(app.exec())
