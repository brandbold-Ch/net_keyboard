from typing import Callable

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QCheckBox,
    QLabel,
    QLineEdit,
    QPushButton,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

from src.ui.gui.constants import ALIGN


class ClientSetupView(QWidget):
    submitted = Signal(str, int, bool, bool)
    go_to_home = Signal()

    def __init__(self) -> None:
        super().__init__()
        layout = QVBoxLayout()

        label_host = QLabel("Host")
        self.input_host = QLineEdit(placeholderText="192.168.1.100")
        self.input_host.setFixedWidth(260)
        self.input_host.setFixedHeight(30)

        label_port = QLabel("Port")
        self.input_port = QSpinBox(minimum=1, maximum=65535)
        self.input_port.setValue(3500)
        self.input_port.setFixedWidth(260)
        self.input_port.setFixedHeight(30)

        self.checkbox_save = QCheckBox("Save connection")
        self.checkbox_reconnect = QCheckBox("Auto reconnect")

        self.button_next = QPushButton("Next")
        self.button_next.setFixedHeight(60)
        self.button_next.clicked.connect(self._on_submit)

        layout.addWidget(label_host, alignment=ALIGN.AlignCenter)
        layout.addWidget(self.input_host, alignment=ALIGN.AlignCenter)

        layout.addWidget(label_port, alignment=ALIGN.AlignCenter)
        layout.addWidget(self.input_port, alignment=ALIGN.AlignCenter)

        layout.addWidget(self.checkbox_save, alignment=ALIGN.AlignCenter)
        layout.addWidget(self.checkbox_reconnect, alignment=ALIGN.AlignCenter)

        layout.addStretch()
        layout.addWidget(self.button_next)

        self.setLayout(layout)

    def _on_submit(self) -> None:
        self.submitted.emit(
            self.input_host.text(),
            self.input_port.value(),
            self.checkbox_save.isChecked(),
            self.checkbox_reconnect.isChecked(),
        )
        self.go_to_home.emit()

    def on_submit(self, handler: Callable[[str, int, bool, bool], None]) -> None:
        self.submitted.connect(handler)
