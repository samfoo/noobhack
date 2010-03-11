import sys
import tty
import socket
import termios
import threading

class Input:
    def __init__(self, conn):
        self.filter_callbacks = []
        self.conn = conn
        tty.setraw(sys.stdin.fileno())

    def set_filter_callback(self, name, callback):
        self.filter_callbacks.append(callback)

    def proxy(self):
        ch = sys.stdin.read(1)

        send_command = True

        for callback in self.filter_callbacks:
            if callback(ch) != True:
                send_command = False

        if send_command:
            self.conn.write(ch)

class Output:
    """Otherwise known as: Pam's Gossip Train"""

    def __init__(self, conn):
        self.conn = conn
        self.filter_callbacks = {}
        tty.setraw(sys.stdout.fileno())

    def set_filter_callback(self, pattern, callback):
        self.filter_callbacks[pattern] = callback

    def proxy(self):
        output = self.conn.read()

        for pattern, callback in self.filter_callbacks.values():
            if re.search(pattern, output) is not None:
                callback(output)

        sys.stdout.write(output)
        sys.stdout.flush()

