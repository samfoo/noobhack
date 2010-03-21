import sys
import tty
import pdb
import getopt
import select
import termios

import telnet
import process
import proxy
import dungeon

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
        sys.stderr.write("noobhack: unrecognized argument(s) `%s'\n" % ",".join(remaining))
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
            host = val
            local = False
        elif opt == "-p":
            port = val

    return opts_dict 

def connect_to_game(options):
    try:
        if options.get("local", False):
            conn = process.Local()
        else:
            conn = telnet.Telnet(options["host"], options.get("port", 23))
        conn.open()
    except IOError, e:
        sys.stderr.write("Could not establish a connection to nethack: `%s'\n" % e)
        raise e

    return conn

def load_or_create_dungeon():
   return dungeon.load() or dungeon.Dungeon() 

def begin_proxying(conn, dun):
    return (proxy.Output(conn, dun), proxy.Input(conn, dun))

def main():
    options = parse_options()

    try:
        # Store off our terminal settings so we can restore them later.
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)

        dun = load_or_create_dungeon()

        conn = connect_to_game(options) 
        output, input = begin_proxying(conn, dun) 

        while True:
            available = select.select([conn.fileno(), sys.stdin.fileno()], [], [])[0]

            if conn.fileno() in available:
                # Do our display logic.
                output.proxy()

            if sys.stdin.fileno() in available:
                # Do our input logic.
                input.proxy()
    except IOError, e:
        # Nethack terminated or there was some problem communicating with it.
        pass
    finally:
        # Make sure we restore the terminal settings to where they were.
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)

if __name__ == "__main__":
    main()
