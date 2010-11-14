import re
import sys
import tty
import socket
import termios
import threading

class Input:
    """
    Proxies raw input from the terminal to the game, calling a set of callbacks
    each input item it receives. If any of the callbacks return `False` then
    the input is not forwarded to the game.
    """

    def __init__(self, conn):
        self.conn = conn
        self.callbacks = set()

    def register(self, callback):
        self.callbacks.add(callback)

    def unregister(self, callback):
        self.callbacks.remove(callback)

    def proxy(self):
        input = sys.stdin.read(1)

        for callback in self.callbacks:
            if callback(input) is False:
                return

        self.conn.write(input)

class Output:
    """
    Proxies raw output from the game and calls a set of callbacks each time 
    with the stream that was output. Typically you'd want to attach a terminal
    emulator, or something that can parse the output as meaningful to this.
    """

    def __init__(self, conn):
        self.conn = conn
        self.callbacks = set() 

    def register(self, callback):
        self.callbacks.add(callback)

    def unregister(self, callback):
        self.callbacks.remove(callback)

    def proxy(self):
        output = self.conn.read()

        for callback in self.callbacks:
            callback(output)
