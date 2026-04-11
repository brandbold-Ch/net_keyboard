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
    """
    A view for setting up the client connection.

    This class provides a user interface for entering the host and port
    information, as well as options for saving the connection and enabling
    auto-reconnect.

    Signals:
        submitted (Signal): Emitted when the user submits the form with the
            following parameters:
            - str: Host address.
            - int: Port number.
            - bool: Save connection flag.
            - bool: Auto-reconnect flag.
        go_to_home (Signal): Emitted when the user navigates back to the home view.
    """

    submitted = Signal(str, int, bool, bool)
    go_to_home = Signal()

    def __init__(self) -> None:
        """
        Initialize the ClientSetupView.

        Sets up the layout and widgets for the client setup form, including
        input fields for host and port, checkboxes for additional options,
        and a submit button.
        """
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
        """
        Handle the form submission.

        Emits the `submitted` signal with the form data and the `go_to_home`
        signal to navigate back to the home view.
        """
        self.submitted.emit(
            self.input_host.text(),
            self.input_port.value(),
            self.checkbox_save.isChecked(),
            self.checkbox_reconnect.isChecked(),
        )
        self.go_to_home.emit()

    def on_submit(self, handler: Callable[[str, int, bool, bool], None]) -> None:
        """
        Register a handler for the `submitted` signal.

        Args:
            handler (Callable[[str, int, bool, bool], None]): A function to handle
                the submitted form data.
        """
        self.submitted.connect(handler)
