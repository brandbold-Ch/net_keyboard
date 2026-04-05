from PySide6.QtCore import QSize
from PySide6.QtWidgets import QProgressBar, QVBoxLayout, QWidget

from src.ui.gui.constants import ALIGN


class ClientHomeView(QWidget):
    def __init__(self) -> None:
        super().__init__()
        layout = QVBoxLayout()
        progress_bar = QProgressBar(minimum=0, maximum=100, value=40)
        progress_bar.setFixedSize(QSize(200, 30))

        layout.addWidget(progress_bar, alignment=ALIGN.AlignCenter)
        self.setLayout(layout)
