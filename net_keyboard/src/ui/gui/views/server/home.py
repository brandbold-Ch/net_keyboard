from PySide6.QtCore import QObject, Signal
from PySide6.QtWidgets import QLabel, QLineEdit, QTabWidget, QVBoxLayout, QWidget

from src.backends.base import TUPLE_CODES
from src.ui.gui.constants import ALIGN

KEY_MAP: dict[int, str] = {
    # letras
    30: "a",
    48: "b",
    46: "c",
    32: "d",
    18: "e",
    33: "f",
    34: "g",
    35: "h",
    23: "i",
    36: "j",
    37: "k",
    38: "l",
    50: "m",
    49: "n",
    24: "o",
    25: "p",
    16: "q",
    19: "r",
    31: "s",
    20: "t",
    22: "u",
    47: "v",
    17: "w",
    45: "x",
    21: "y",
    44: "z",
    # números (fila superior)
    2: "1",
    3: "2",
    4: "3",
    5: "4",
    6: "5",
    7: "6",
    8: "7",
    9: "8",
    10: "9",
    11: "0",
    # espacio y básicos
    57: " ",
    28: "\n",  # Enter
    14: "\b",  # Backspace
    15: "\t",  # Tab
    # símbolos comunes (layout US base)
    12: "-",
    13: "=",
    26: "[",
    27: "]",
    39: ";",
    40: "'",
    41: "`",
    51: ",",
    52: ".",
    53: "/",
}


class EventBridge(QObject):
    key_event = Signal(tuple)


bridge = EventBridge()


def on_press(event: TUPLE_CODES) -> None:
    bridge.key_event.emit(event)


def on_release(event: TUPLE_CODES) -> None:
    bridge.key_event.emit(event)


class EventTabView(QWidget):
    def __init__(self) -> None:
        super().__init__()
        layout = QVBoxLayout()

        self.key_label = QLabel("Key")
        self.key_display = QLineEdit()

        self.state_label = QLabel("Action")
        self.state_display = QLineEdit()

        self.time_label = QLabel("Timestamp")
        self.time_display = QLineEdit()

        self.ascii_label = QLabel("ASCII")
        self.ascii_display = QLineEdit()

        bridge.key_event.connect(self.update_texts)

        layout.addWidget(self.key_label, alignment=ALIGN.AlignCenter)
        layout.addWidget(self.key_display, alignment=ALIGN.AlignCenter)

        layout.addWidget(self.state_label, alignment=ALIGN.AlignCenter)
        layout.addWidget(self.state_display, alignment=ALIGN.AlignCenter)

        layout.addWidget(self.time_label, alignment=ALIGN.AlignCenter)
        layout.addWidget(self.time_display, alignment=ALIGN.AlignCenter)

        layout.addWidget(self.ascii_label, alignment=ALIGN.AlignCenter)
        layout.addWidget(self.ascii_display, alignment=ALIGN.AlignCenter)

        layout.addStretch()
        self.setLayout(layout)

    def update_texts(self, event: TUPLE_CODES) -> None:
        key, state, time = event

        self.key_display.setText(str(key))
        self.state_display.setText(str(state))
        self.time_display.setText(str(time))
        self.ascii_display.setText(KEY_MAP[key])


class ListenerTabView(QWidget):
    def __init__(self) -> None:
        super().__init__()


class ServerTabView(QWidget):
    def __init__(self) -> None:
        super().__init__()


class ServerHomeView(QWidget):
    def __init__(self) -> None:
        super().__init__()
        layout = QVBoxLayout()

        tab_widgets = QTabWidget()
        tab_widgets.addTab(EventTabView(), "Events")
        tab_widgets.addTab(ServerTabView(), "Server")
        tab_widgets.addTab(ListenerTabView(), "Listener")

        layout.addWidget(tab_widgets)
        self.setLayout(layout)
