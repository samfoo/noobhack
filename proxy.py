import re
import sys
import tty
import socket
import termios
import threading

class Input:
    """Proxy input from stdin to the game. Safety handlers may be registered 
    that, if they return false will not forward the input key to the game. This
    is useful when, for example, the client knows that the player is about to 
    attack a cockatrice barehanded or melee a floating eye."""

    def __init__(self, conn):
        self.conn = conn
        self.safeties = {} 
        tty.setraw(sys.stdin.fileno())

    def register(self, key, callback):
        # Register a callback. The callback takes the key that was pressed as 
        # its only argument.
        self.safeties[key] = callback

    def unregister(self, key):
        # Is this even necessary? It's kind of lame that you have to deregister
        # everything, but would you even have access to the callback object
        # later when you could say "only unregister _this_ callback"?
        if self.safeties.has_key(key):
            del self.safeties[key]

    def proxy(self):
        input = sys.stdin.read(1)

        for key, callback in self.safeties.iteritems():
            match = re.search(key, input)
            if match is not None:
                if callback(input) == False:
                    # If any safety fails, don't write the character to the game.
                    return

        # No safety net triggered, just write the input to the game.
        self.conn.write(input)

class Output:
    """Pam's Gossip Train. Take output from the child and proxy it to our 
    current stdout. Before the output it displayed it's checked for any 
    matching patterns of text in the pattern callbacks. If any patterns 
    match... those methods are called."""

    def __init__(self, conn):
        self.conn = conn
        self.callbacks = {}
        tty.setraw(sys.stdout.fileno())

    def register(self, pattern, callback):
        self.callbacks[pattern] = callback

    def unregister(self, pattern):
        if self.callbacks.has_key(pattern):
            del self.callbacks[pattern]

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

