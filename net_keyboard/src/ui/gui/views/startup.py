import platform

from PySide6.QtCore import QSize, Signal
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QLabel, QPushButton, QVBoxLayout, QWidget

from src.ui.gui.constants import ALIGN, BASE_DIR


class StartupView(QWidget):
    go_to_client_setup = Signal()
    go_to_server_setup = Signal()

    def __init__(self, system_info: str) -> None:
        super().__init__()
        layout = QVBoxLayout()

        self.button_client = QPushButton("Client")
        self.button_client.setFixedHeight(60)

        self.button_server = QPushButton("Server")
        self.button_server.setFixedHeight(60)

        self.button_client.clicked.connect(self._on_client_clicked)
        self.button_server.clicked.connect(self._on_server_clicked)

        self.label_platform = QLabel()
        self.label_platform.setFixedSize(QSize(150, 150))
        self.label_platform.setScaledContents(True)

        label_title = QLabel("NetKeyboard Selector")
        label_info = QLabel(system_info)

        match platform.system():
            case "Linux":
                self.label_platform.setPixmap(
                    QPixmap(BASE_DIR / "assets/images/linux.png")
                )
            case "Windows":
                self.label_platform.setPixmap(
                    QPixmap(BASE_DIR / "assets/images/windows.png")
                )

        layout.addWidget(label_title, alignment=ALIGN.AlignCenter)
        layout.addWidget(self.label_platform, alignment=ALIGN.AlignCenter)
        layout.addWidget(label_info, alignment=ALIGN.AlignCenter)

        layout.addStretch()
        layout.addWidget(self.button_client)
        layout.addWidget(self.button_server)

        self.setLayout(layout)

    def _on_client_clicked(self) -> None:
        self.go_to_client_setup.emit()

    def _on_server_clicked(self) -> None:
        self.go_to_server_setup.emit()
