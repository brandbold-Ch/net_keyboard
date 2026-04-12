import platform

from PySide6.QtCore import QSize
from PySide6.QtGui import QCloseEvent
from PySide6.QtWidgets import QMainWindow, QStackedWidget

from src.core.devices.base import IODevice
from src.core.devices.resolver import DeviceResolver
from src.ui.gui.controllers.client import ClientController
from src.ui.gui.controllers.navigation import NavigationController
from src.ui.gui.controllers.server import ServerController
from src.ui.gui.views import (
    ClientHomeView,
    ClientSetupView,
    ServerHomeView,
    ServerSetupView,
    StartupView,
)
from src.utils.context import context

context.kbds = DeviceResolver.scan_devices(device=IODevice.KEYBOARD)
context.mice = DeviceResolver.scan_devices(device=IODevice.MOUSE)
system_info = "Platform: {} \
    \nRelease: {} \
    \nArchitecture: {}".format(
    platform.system(), platform.release(), platform.machine()
)


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()

        self.setWindowTitle("NetKeyboard 1.0")
        self.setFixedSize(QSize(400, 400))

        # Main Stack
        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)

        # Views
        self.startup_view = StartupView(system_info)
        self.client_setup_view = ClientSetupView()
        self.server_setup_view = ServerSetupView(
            list(context.kbds.keys()), list(context.mice.keys())
        )
        self.client_home_view = ClientHomeView()
        self.server_home_view = ServerHomeView()

        # Router
        self.router = NavigationController(self.stack)
        self.router.register("startup_view", self.startup_view)
        self.router.register("client_setup_view", self.client_setup_view)
        self.router.register("server_setup_view", self.server_setup_view)
        self.router.register("client_home_view", self.client_home_view)
        self.router.register("server_home_view", self.server_home_view)

        # Controllers
        self.client_controller = ClientController(self.client_setup_view)
        self.server_controller = ServerController(self.server_setup_view)

        # Called Views
        self.router.go("startup_view")

        # Navigation Conections
        self.startup_view.go_to_client_setup.connect(
            lambda: self.router.go("client_setup_view")
        )
        self.startup_view.go_to_server_setup.connect(
            lambda: self.router.go("server_setup_view")
        )
        self.client_setup_view.go_to_home.connect(
            lambda: self.router.go("client_home_view")
        )
        self.server_setup_view.go_to_home.connect(
            lambda: self.router.go("server_home_view")
        )

    def closeEvent(self, event: QCloseEvent, /) -> None:
        context.dump_config()
        return super().closeEvent(event)
