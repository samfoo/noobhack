"""
noobhack helps you ascend at nethack.
"""

import sys
import fcntl
import getopt
import select
import struct
import curses
import termios

import vt102

import telnet
import process
import proxy

#from game.player import Player
#from game import events 

class Noobhack:
    toggle = "\t"

    def __init__(self):
        self.options = self.parse_options()
        self.mode = "game"

        self.game = self.connect_to_game() 
        self.output_proxy = proxy.Output(self.game)
        self.input_proxy = proxy.Input(self.game) 

        # Create an in-memory terminal screen and register it's stream
        # processor with the output proxy.
        self.stream = vt102.stream()

        # For some reason that I can't assertain: curses freaks out and crashes
        # when you use exactly the number of rows that are available on the
        # terminal. It seems easiest just to subtract one from the rows and 
        # deal with it rather than hunt forever trying to figure out what I'm
        # doing wrong with curses.
        rows, cols = self.size()
        self.term = vt102.screen((rows-1, cols))
        self.term.attach(self.stream)
        self.output_proxy.register(self.stream.process)

        # Register the `toggle` key to open up the interactive nooback 
        # assistant.
        self.input_proxy.register(self._toggle_handler)

        # Create a player object to track player state.
        #self.player = Player()
        #self.output_proxy.register(events.dispatcher.process)

    def usage(self):
        sys.stderr.write("""Usage: noobhack.py [options]
    Help: noobhack helps you ascend in nethack.
        By default, it runs a copy of nethack locally, however it's possible to
        connect to a remote telnet server and proxy a game.
    Options:
        -l      Play a local game (default)
        -h      Host to play a remote game on
        -p      Port to connect to the remote host (default: 23)""")
        sys.stderr.flush()
        sys.exit(1)

    def parse_options(self):
        opts_dict = {"local": True}

        options, remaining = \
            getopt.getopt(sys.argv[1:], "lh:p:", [])

        if len(remaining) > 0:
            sys.stderr.write("noobhack: unrecognized argument(s) `%s'\n" % \
                             ",".join(remaining))
            self.usage()

        opts = [pair[0] for pair in options]
        if ("-h" in opts and "-l" in opts) or ("-p" in opts and "-l" in opts):
            sys.stderr.write("noobhack: invalid option `-p' or `-h' with `-l'")
            self.usage()

        if "-p" in opts and "-h" not in opts:
            sys.stderr.write("noobhack: invalid option `-p' requires a host\n")
            self.usage()

        for opt, val in options:
            if opt == "-h":
                options["host"] = val
                options["local"] = False
            elif opt == "-p":
                options["port"] = val

        return opts_dict 

    def connect_to_game(self):
        """
        Fork the game, or connect to a foreign host to play.

        :return: A file like object of the game. Reading/writing is the same as
        accessing stdout/stdin in the game respectively.
        """

        try:
            if self.options.get("local", False):
                conn = process.Local()
            else:
                conn = telnet.Telnet(
                    self.options["host"], 
                    self.options.get("port", 23)
                )
            conn.open()
        except IOError, error:
            sys.stderr.write("Unable to open nethack: `%s'\n" % error)
            raise 

        return conn

    def size(self):
        """
        Get the current terminal size.

        :return: (rows, cols)
        """

        raw = fcntl.ioctl(sys.stdin, termios.TIOCGWINSZ, 'SSSS')
        return struct.unpack('hh', raw) 

    def _toggle_handler(self, key):
        if key == self.toggle:
            self._toggle_mode()
            return False

    def _toggle_mode(self):
        if self.mode == "game":
            self.mode = "help"
        else:
            self.mode = "game"

    colors = {
        "black": curses.COLOR_BLACK,
        "blue": curses.COLOR_BLUE,
        "cyan": curses.COLOR_CYAN,
        "green": curses.COLOR_GREEN,
        "magenta": curses.COLOR_MAGENTA,
        "red": curses.COLOR_RED,
        "white": curses.COLOR_WHITE,
        "yellow": curses.COLOR_YELLOW,
        "brown": curses.COLOR_YELLOW,
        "default": -1,
    }

    styles = {
        "bold": curses.A_BOLD,
        "dim": curses.A_DIM,
        "underline": curses.A_UNDERLINE,
        "blink": curses.A_BLINK,
    }

    def _get_color(self, fg, bg, registered={}):
        if not registered.has_key((fg, bg)):
            curses.init_pair(len(registered)+1, fg, bg)
            registered[(fg,bg)] = len(registered) + 1
        return curses.color_pair(registered[(fg,bg)])

    def _redraw_game_row(self, window, row):
        row_a = self.term.attributes[row]
        row_c = self.term.display[row]
        for col, (char, (styles, fg, bg)) in enumerate(zip(row_c, row_a)): 
            styles = set(styles)
            fg = self.colors.get(fg, -1)
            bg = self.colors.get(bg, -1)
            styles = [self.styles.get(s, curses.A_NORMAL) for s in styles]
            attrs = styles + [self._get_color(fg, bg)]
            window.addch(row, col, char, reduce(lambda a, b: a | b, attrs))

    def _redraw_game(self, window):
        # Repaint the screen with the new contents of our terminal 
        # emulator...
        window.clear()
        for row_index in xrange(len(self.term.display)):
            self._redraw_game_row(window, row_index)

        # Don't forget to move the cursor to where it is in game...
        cur_x, cur_y = self.term.cursor()
        window.move(cur_y, cur_x)

        # Finally, redraw the whole thing.
        window.refresh()

    def _game(self, window):
        self._redraw_game(window) 

        # Let's wait until we have something to do...
        available = select.select(
            [self.game.fileno(), sys.stdin.fileno()], [], []
        )[0]

        if self.game.fileno() in available:
            # Do our display logic.
            self.output_proxy.proxy()

        if sys.stdin.fileno() in available:
            # Do our input logic.
            self.input_proxy.proxy()

    def _redraw_help(self, window):
        window.clear()
        window.addstr(0, 0, "help")
        window.refresh()

    def _help(self, window):
        self._redraw_help(window)
        select.select([sys.stdin.fileno()], [], [])
        self._toggle_handler(sys.stdin.read(1))

    def run(self, window):
        # We prefer to let the console pick the colors for the bg/fg instead of
        # using what curses thinks looks good.
        curses.use_default_colors()

        while True:
            if self.mode == "game":
                self._game(window)
            else:
                self._help(window)

    def main(self):
        try:
            curses.wrapper(self.run)
        except IOError, exit_message:
            print exit_message

if __name__ == "__main__":
    hack = Noobhack()
    hack.main()
