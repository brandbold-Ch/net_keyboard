from PySide6.QtWidgets import QStackedWidget, QWidget


class NavigationController:
    def __init__(self, stack: QStackedWidget) -> None:
        self.stack = stack
        self.views = {}

    def register(self, name: str, widget: QWidget) -> None:
        self.views[name] = widget
        self.stack.addWidget(widget)

    def go(self, name: str) -> None:
        widget = self.views.get(name)
        if widget:
            self.stack.setCurrentWidget(widget)
