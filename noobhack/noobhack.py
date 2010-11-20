"""
noobhack helps you ascend at nethack. You can press tab at anytime during the
game to display the helper screen. Press tab again to dismiss it.
"""

import sys
import getopt
import select
import curses

import ui 
import telnet
import process
import proxy

def usage():
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

def parse_options():
    """
    Parse commandline options and return a dict with any settings.
    """

    opts_dict = {"local": True}

    options, remaining = \
        getopt.getopt(sys.argv[1:], "lh:p:", [])

    if len(remaining) > 0:
        sys.stderr.write("noobhack: unrecognized argument(s) `%s'\n" % \
                         ",".join(remaining))
        usage()

    opts = [pair[0] for pair in options]
    if ("-h" in opts and "-l" in opts) or ("-p" in opts and "-l" in opts):
        sys.stderr.write("noobhack: invalid option `-p' or `-h' with `-l'")
        usage()

    if "-p" in opts and "-h" not in opts:
        sys.stderr.write("noobhack: invalid option `-p' requires a host\n")
        usage()

    for opt, val in options:
        if opt == "-h":
            options["host"] = val
            options["local"] = False
        elif opt == "-p":
            options["port"] = val

    return opts_dict 

class Noobhack:
    """
    Manager of the global game state. This runs the main event loop and makes 
    sure the screen gets updated as necessary.
    """

    def __init__(self, toggle_help="\t", toggle_map="`"):
        self.options = parse_options()
        self.toggle_help = toggle_help
        self.toggle_map = toggle_map
        self.mode = "game"

        self.nethack = self.connect_to_game() 
        self.output_proxy = proxy.Output(self.nethack)
        self.input_proxy = proxy.Input(self.nethack) 

        self.game = ui.Game(self.output_proxy)
        self.helper = ui.Helper(self.output_proxy)
        self.dungeon = ui.Map(self.output_proxy)

        # Register the `toggle` key to open up the interactive nooback 
        # assistant.
        self.input_proxy.register(self._toggle)

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

    def _toggle(self, key):
        """
        Toggle between game mode and help mode.
        """

        if key == self.toggle_help:
            if self.mode == "game":
                self.mode = "help"
            else:
                self.mode = "game"
            return False
        elif key == self.toggle_map:
            self.mode = "map"
            return False

    def _game(self, window):
        """
        Run the game loop.
        """

        if self.mode == "map":
            self.dungeon.display(window, self.toggle_map)
            # Map mode handles it's own input. Make sure that we don't get
            # forever stuck in map mode by toggling back out of it when it's
            # done.
            self.mode = "game"

        self.game.redraw(window)
        if self.mode == "help":
            self.helper.redraw(window)

        # Let's wait until we have something to do...
        available = select.select(
            [self.nethack.fileno(), sys.stdin.fileno()], [], []
        )[0]

        if self.nethack.fileno() in available:
            # Do our display logic.
            self.output_proxy.proxy()

        if sys.stdin.fileno() in available:
            # Do our input logic.
            self.input_proxy.proxy()

    def run(self, window):
        """
        Game loop.
        """

        # We prefer to let the console pick the colors for the bg/fg instead of
        # using what curses thinks looks good.
        curses.use_default_colors()

        while True:
            self._game(window)

if __name__ == "__main__":
    hack = Noobhack()
    try:
        curses.wrapper(hack.run)
    except IOError, exit_message:
        print exit_message
