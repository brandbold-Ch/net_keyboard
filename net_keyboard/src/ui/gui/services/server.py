import platform

from src.backends.base import KeyboardTypeEvent
from src.backends.keyboard import EventListener
from src.core.ntk_client import NetKeyboardClient
from src.core.ntk_server import NetKeyboardServer
from src.transport.ipc.tools import IPCProcessLauncher, KeyListener
from src.ui.gui.models.client import Client
from src.ui.gui.views.server.home import on_press, on_release
from src.utils.context import context

listener: EventListener
OS: str = platform.system()


def launcher_factory() -> IPCProcessLauncher:

    return (
        IPCProcessLauncher(
            client="bin/socket_unix/keyboard/input"
            if OS == "Linux"
            else "bin/pipe/keyboard/input.exe",
            server=KeyListener(
                on_press=listener.on_press,
                on_release=listener.on_release,
                device=str(context.kbds[context.server.keyboard]),
            ),
            shared="/tmp/keyboard_ipc.sock"
            if OS == "Linux"
            else r"\\.\pipe\keyboard_ipc",
        )
        if OS == "Linux"
        else IPCProcessLauncher(
            server="bin/socket_unix/keyboard/input"
            if OS == "Linux"
            else "bin/pipe/keyboard/input.exe",
            client=KeyListener(
                on_press=listener.on_press, on_release=listener.on_release
            ),
            shared="/tmp/keyboard_ipc.sock"
            if OS == "Linux"
            else r"\\.\pipe\keyboard_ipc",
        )
    )


listener = EventListener(launcher_factory)
listener.add_subscriber(on_press, kind=KeyboardTypeEvent.PRESS)
listener.add_subscriber(on_release, kind=KeyboardTypeEvent.RELEASE)


class ServerService:
    def set_host(self, host: str) -> None:
        context.server.host = host

    def set_port(self, port: int) -> None:
        context.server.port = port

    def add_client(self, client: Client) -> None:
        context.server.clients.append(client)

    def set_pool(self, pool: int) -> None:
        context.server.pool = pool

    def set_keyboard(self, keyboard: str) -> None:
        context.server.keyboard = keyboard

    def set_mouse(self, mouse: str) -> None:
        context.server.mouse = mouse

    def set_save_connection(self, status: bool) -> None:
        context.server.save_connection = status

    def set_auto_reconnect(self, status: bool) -> None:
        context.server.auto_reconnect = status

    def start_server(self) -> None:
        listener.listen()
