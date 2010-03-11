import sys
import tty
import socket
import termios
import threading

class Input:
    """Take input from the current tty and proxy it to the nethack game. Before
    the input is proxied, a series of filter callbacks are called if any of 
    them return something other than True the input will not be proxied to the
    game and will instead be ignored.

    Filter callbacks take one argument which is the string of the character
    that was read off of stdin."""

    def __init__(self, conn):
        self.filter_callbacks = []
        self.conn = conn
        tty.setraw(sys.stdin.fileno())

    def add_filter_callback(self, callback):
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
    """Otherwise known as: Pam's Gossip Train
    
    Take output from the child and proxy it to our current stdout. Before the
    output it displayed it's checked for any matching patterns of text in the
    pattern callbacks. If any of the patterns match those methods are called 
    with the input as their only argument."""

    def __init__(self, conn):
        self.conn = conn
        self.pattern_callbacks = {}
        tty.setraw(sys.stdout.fileno())

    def add_pattern_callback(self, pattern, callback):
        self.pattern_callbacks[pattern] = callback

    def proxy(self):
        output = self.conn.read()

        for pattern, callback in self.pattern_callbacks.values():
            if re.search(pattern, output) is not None:
                callback(output)

        sys.stdout.write(output)
        sys.stdout.flush()

