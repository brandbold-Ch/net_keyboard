"""Pynput adapter module for keyboard and mouse event handling over network."""
from typing import Optional
from src.tcp import BaseServer, BaseClient
import threading
from src.backends.base import KeyboardTypeEvent, MouseTypeEvent
from src.backends.pynput import PynputKeyboardEvent, PynputMouseEvent, PynputKey
from pynput.keyboard import Key, KeyCode


class PynputServer(BaseServer):
    """
    TCP server adapter for keyboard events using Pynput.
    
    This class captures keyboard and mouse events locally and sends them
    over TCP to connected clients using the Pynput library.
    """
    
    def __init__(self, host: str, port: int) -> None:
        """
        Initialize the Pynput server.
        
        Args:
            host (str): The hostname or IP address to bind the server to.
            port (int): The port number to listen on.
        """
        super().__init__(host, port)
        self.keyboard_event = PynputKeyboardEvent()
        self.mouse_event = PynputMouseEvent()

        self.keyboard_event.add_callback(self.keyboard_press, KeyboardTypeEvent.PRESS)

    def keyboard_press(self, key: PynputKey) -> None:
        """
        Handle keyboard press events and send them to the client.
        
        Args:
            key (PynputKey): The key that was pressed.
        """
        if isinstance(key, Key): 
            self.send(key.name)
        
        elif isinstance(key, KeyCode):
            self.send(key.char)

    def run(self) -> None:
        """
        Start the server and listen for keyboard events in a separate thread.
        """
        threading.Thread(target=self.keyboard_event.listen).start()


class PynputClient(BaseClient):
    """
    TCP client adapter for simulating keyboard and mouse events using Pynput.
    
    This class connects to a TCP server, receives keyboard and mouse events,
    and simulates them locally using the Pynput library.
    """

    def __init__(self, host: str, port: int) -> None:
        """
        Initialize the Pynput client.
        
        Args:
            host (str): The hostname or IP address of the server to connect to.
            port (int): The port number of the server.
        """
        super().__init__(host, port)
        self.keyboard_event = PynputKeyboardEvent()
        self.mouse_event = PynputMouseEvent()

    def run(self) -> None:
        """
        Start the client and receive keyboard events from the server.
        
        Continuously receives keyboard event data from the server and
        simulates the keystrokes locally.
        """
        while True:
            data: bytes = self.receive()
            self.keyboard_event.insert("data")
