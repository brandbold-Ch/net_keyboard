import sys
from pathlib import Path

from PySide6.QtCore import Qt

BASE_DIR = (
    Path(getattr(sys, "_MEIPASS"))
    if getattr(sys, "frozen", False)
    else Path(__file__).resolve().parent
)
ALIGN = Qt.AlignmentFlag
