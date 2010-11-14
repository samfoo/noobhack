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

def usage():
    sys.stderr.write("""Usage: noobhack.py [options]
Help: noobhack helps you ascend in nethack.
    By default, it runs a copy of nethack locally, however it's possible to
    connect to a remote telnet server and proxy a game.
Options:
    -l      Play a local game (default)
    -h      Host to play a remote game on
    -p      Port to connect to the remote host (default: 23)""")
    sys.exit(1)

def parse_options():
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

def connect_to_game(options):
    """
    Fork the game, or connect to a foreign host to play.

    :return: A file like object of the game. Reading/writing is the same as
    accessing stdout/stdin in the game respectively.
    """

    try:
        if options.get("local", False):
            conn = process.Local()
        else:
            conn = telnet.Telnet(options["host"], options.get("port", 23))
        conn.open()
    except IOError, error:
        sys.stderr.write("Unable to open nethack: `%s'\n" % error)
        raise 

    return conn

def get_size():
    """
    Get the current terminal size.

    :return: (rows, cols)
    """

    raw = fcntl.ioctl(sys.stdin, termios.TIOCGWINSZ, 'SSSS')
    return struct.unpack('hh', raw) 

def run(window):
    options = parse_options()

    # We prefer to let the console pick the colors for the bg/fg instead of
    # using what curses thinks looks good.
    curses.use_default_colors()

    game = connect_to_game(options) 
    output_proxy, input_proxy = proxy.Output(game), proxy.Input(game) 

    # Create an in-memory terminal screen and register it's stream
    # processor with the output proxy.
    term_stream = vt102.stream()

    # For some reason that I can't assertain: curses freaks out and crashes
    # when you use exactly the number of rows that are available on the
    # terminal. It seems easiest just to subtract one from the rows and 
    # deal with it rather than hunt forever trying to figure out what I'm
    # doing wrong with curses.
    rows, cols = get_size()
    term_screen = vt102.screen((rows-1, cols))
    term_screen.attach(term_stream)
    output_proxy.register(term_stream.process)

    while True:
        # Let's wait until we have something to do...
        available = select.select([game.fileno(), sys.stdin.fileno()], [], [])[0]

        if game.fileno() in available:
            # Do our display logic.
            output_proxy.proxy()

        if sys.stdin.fileno() in available:
            # Do our input logic.
            input_proxy.proxy()

        # Repaint the screen with the new contents of our terminal 
        # emulator...
        window.clear()
        for row_index, game_row in enumerate(term_screen.display):
            window.addstr(row_index, 0, game_row)

        # Don't forget to move the cursor to where it is in game...
        cur_x, cur_y = term_screen.cursor()
        window.move(cur_y, cur_x)

        # Finally, redraw the whole thing.
        window.refresh()

def main():
    try:
        curses.wrapper(run)
    except IOError, exit_message:
        print exit_message

if __name__ == "__main__":
    main()
