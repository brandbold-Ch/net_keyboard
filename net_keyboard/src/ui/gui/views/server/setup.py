from typing import Callable, List

from PySide6.QtCore import QStringListModel, Signal
from PySide6.QtWidgets import QLabel, QListView, QPushButton, QVBoxLayout, QWidget

from src.ui.gui.constants import ALIGN


class ServerSetupView(QWidget):
    """
    A view for setting up the server configuration.

    This class provides a GUI for selecting input devices (keyboard and mouse)
    and submitting the configuration. It ensures that both devices are selected
    before enabling the submission.

    Signals:
        submitted (Signal): Emitted when the user submits the selected devices.
            Arguments:
                - str: The selected keyboard.
                - str: The selected mouse.
        go_to_home (Signal): Emitted when the user navigates back to the home view.
    """

    submitted = Signal(str, str)
    go_to_home = Signal()

    def __init__(self, keyboards: List[str], mice: List[str]) -> None:
        """
        Initialize the ServerSetupView.

        Args:
            keyboards (List[str]): A list of available keyboard device names.
            mice (List[str]): A list of available mouse device names.
        """
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
        """
        Register a handler for the submission signal.

        Args:
            handler (Callable[[str, str], None]): A function to handle the
                submitted keyboard and mouse device names.
        """
        self.submitted.connect(handler)

    def _get_selected(self, list_view: QListView) -> str:
        """
        Retrieve the selected item from a QListView.

        Args:
            list_view (QListView): The list view to retrieve the selection from.

        Returns:
            str: The name of the selected item, or an empty string if no item is selected.
        """
        index = list_view.currentIndex()
        return index.data() if index.isValid() else ""

    def _disable_first_lock(self) -> None:
        """
        Unlock the first selection requirement.

        This method is called when the user selects an item in the keyboard list.
        If both the first and second locks are unlocked, the "Next" button is enabled.
        """
        self.first_lock = True
        if self.second_lock:
            self.button_next.setEnabled(True)

    def _disable_second_lock(self) -> None:
        """
        Unlock the second selection requirement.

        This method is called when the user selects an item in the mouse list.
        If both the first and second locks are unlocked, the "Next" button is enabled.
        """
        self.second_lock = True
        if self.first_lock:
            self.button_next.setEnabled(True)
