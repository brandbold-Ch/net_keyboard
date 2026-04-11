import sys

from PySide6.QtWidgets import QApplication

from src.ui.gui.main_window import MainWindow


class NetKeyboardApp:
    @classmethod
    def run(cls) -> None:
        app = QApplication(sys.argv)
        mkv = MainWindow()
        mkv.show()
        sys.exit(app.exec())
