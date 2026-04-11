from PySide6.QtCore import QSize
from PySide6.QtWidgets import QProgressBar, QVBoxLayout, QWidget

from src.ui.gui.constants import ALIGN


class ClientHomeView(QWidget):
    """
    A view representing the home screen for the client.

    This class provides a simple layout with a progress bar to display
    the client's current status or progress.

    Attributes:
        progress_bar (QProgressBar): A progress bar widget to show progress.
    """

    def __init__(self) -> None:
        """
        Initialize the ClientHomeView.

        Sets up the layout and adds a progress bar widget to the view.
        """
        super().__init__()
        layout = QVBoxLayout()
        progress_bar = QProgressBar(minimum=0, maximum=100, value=40)
        progress_bar.setFixedSize(QSize(200, 30))

        layout.addWidget(progress_bar, alignment=ALIGN.AlignCenter)
        self.setLayout(layout)
