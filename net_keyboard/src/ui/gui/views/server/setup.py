from typing import Callable, List

from PySide6.QtCore import QStringListModel, Signal
from PySide6.QtWidgets import QLabel, QListView, QPushButton, QVBoxLayout, QWidget

from src.ui.gui.constants import ALIGN


class ServerSetupView(QWidget):
    submitted = Signal(str, str)
    go_to_home = Signal()

    def __init__(self, keyboards: List[str], mice: List[str]) -> None:
        super().__init__()
        layout = QVBoxLayout()
        self.first_lock = False
        self.second_lock = False

        # Models
        self.keyboard_model = QStringListModel(keyboards)
        self.mouse_model = QStringListModel(mice)

        # Labels
        label_keyboard = QLabel("Select keyboard")
        label_mouse = QLabel("Select mouse")

        # Views
        self.list_keyboard = QListView()
        self.list_keyboard.setModel(self.keyboard_model)

        self.list_mouse = QListView()
        self.list_mouse.setModel(self.mouse_model)

        # Button
        self.button_next = QPushButton("Next")
        self.button_next.setDisabled(True)
        self.button_next.setFixedHeight(60)

        self.button_next.clicked.connect(self._on_submit)
        self.list_keyboard.pressed.connect(self._disable_first_lock)
        self.list_mouse.pressed.connect(self._disable_second_lock)

        # Layout
        layout.addWidget(label_keyboard, alignment=ALIGN.AlignCenter)
        layout.addWidget(self.list_keyboard)

        layout.addWidget(label_mouse, alignment=ALIGN.AlignCenter)
        layout.addWidget(self.list_mouse)

        layout.addStretch()
        layout.addWidget(self.button_next)

        self.setLayout(layout)

    def _on_submit(self) -> None:
        keyboard = self._get_selected(self.list_keyboard)
        mouse = self._get_selected(self.list_mouse)

        self.submitted.emit(keyboard, mouse)
        self.go_to_home.emit()

    def on_submit(self, handler: Callable[[str, str], None]) -> None:
        self.submitted.connect(handler)

    def _get_selected(self, list_view: QListView) -> str:
        index = list_view.currentIndex()
        return index.data() if index.isValid() else ""

    def _disable_first_lock(self) -> None:
        self.first_lock = True
        if self.second_lock:
            self.button_next.setEnabled(True)

    def _disable_second_lock(self) -> None:
        self.second_lock = True
        if self.first_lock:
            self.button_next.setEnabled(True)
