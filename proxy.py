import re
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

    Filter callbacks take two arguments, the first of which is the dungeon
    and the second is the string of the character that was read off of stdin."""

    def __init__(self, conn):
        self.filter_callbacks = []
        self.conn = conn
        tty.setraw(sys.stdin.fileno())

    def proxy(self):
        ch = sys.stdin.read(1)

        send_command = True

        for callback in self.filter_callbacks:
            pass

        if send_command:
            self.conn.write(ch)

class Output:
    """Otherwise known as: Pam's Gossip Train
    
    Take output from the child and proxy it to our current stdout. Before the
    output it displayed it's checked for any matching patterns of text in the
    pattern callbacks. If any patterns match those methods are called."""

    def __init__(self, conn):
        self.conn = conn
        self.callbacks = {}
        tty.setraw(sys.stdout.fileno())

    def register(self, pattern, callback):
        self.callbacks[pattern] = callback

    def proxy(self):
        output = self.conn.read()

        for pattern, callback in self.callbacks.iteritems():
            # Force the search to be insensitive and multiline. The clients can
            # always be more specific on their own if they want since the
            # entirety of the data is sent to them.
            match = re.search(pattern, output, re.I | re.M)
            if match is not None:
                callback(pattern, output)

        sys.stdout.write(output)
        sys.stdout.flush()

