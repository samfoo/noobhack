"""
Proxies act as the middle-men between the game that's running in a pty and the
interface that's running in the actual terminal.
"""

import sys

class Input:
    """
    Proxies raw input from the terminal to the game, calling a set of callbacks
    each input item it receives. If any of the callbacks return `False` then
    the input is not forwarded to the game.
    """

    def __init__(self, game):
        self.game = game
        self.callbacks = set()

    def register(self, callback):
        """
        Register a function that will be called *before* any input read off of
        stdin is forwarded to the game. The callback should return `False` if 
        it's not to forward the input to the game.
        """
        self.callbacks.add(callback)

    def unregister(self, callback):
        """
        Unregister a callback.
        """
        self.callbacks.remove(callback)

    def proxy(self):
        """
        Read a single input character from stdin and, if none of the callbacks
        return `False`, forward the keystroke to the game. It's the
        responsibility of the caller to make sure that reading from stdin won't
        block (e.g. by select or setting it to non-blocking).
        """
        key = sys.stdin.read(1)

        for callback in self.callbacks:
            if callback(key) is False:
                return

        self.game.write(key)

class Output:
    """
    Proxies raw output from the game and calls a set of callbacks each time 
    with the stream that was output. Typically you'd want to attach a terminal
    emulator, or something that can parse the output as meaningful to this.
    """

    def __init__(self, game):
        self.game = game
        self.callbacks = set() 

    def register(self, callback):
        """
        Register a function that will be called whenever any input is read. The
        function should accept one argument, which will be the data read from 
        the game.
        """
        self.callbacks.add(callback)

    def unregister(self, callback):
        """
        Unregister a callback.
        """
        self.callbacks.remove(callback)

    def proxy(self):
        """
        Read any available information from the game and call all of the
        registered callbacks. It is the responsibility of the caller to make
        sure that the call to `self.game.read()` will not block (e.g. by using
        select or setting the fd to non-blocking mode)
        """
        output = self.game.read()

        for callback in self.callbacks:
            callback(output)
