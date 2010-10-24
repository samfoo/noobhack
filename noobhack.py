import sys
import tty
import pdb
import getopt
import select
import termios

import telnet
import process
import proxy
import server
import dungeon
import dungeon.player
import dungeon.shops
import dungeon.callbacks

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

def main():
    options = parse_options()
    exit_message = None 
    rpc = None

    try:
        # Store off our terminal settings so we can restore them later.
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)

        game = connect_to_game(options) 
        output, input = proxy.Output(game), proxy.Input(game) 
        rpc = server.Server(output, input)

        while True:
            # Let's wait until we have something to do...
            fds = [rpc.fileno(), game.fileno(), sys.stdin.fileno()]
            if rpc.client is not None:
                fds.append(rpc.client)
            available = select.select(fds, [], [])[0]

            if game.fileno() in available:
                # Do our display logic.
                output.proxy()

            if sys.stdin.fileno() in available:
                # Do our input logic.
                input.proxy()

            if rpc.socket.fileno() in available:
                # Process a new connection to the RPC server.
                rpc.accept()

            if rpc.client in available:
                # Process input from the client.
                rpc.process()

    except IOError, e:
        # Nethack terminated or there was some problem communicating with it.
        exit_message = e
        if rpc is not None:
            rpc.close()

    finally:
        # Make sure we restore the terminal settings to where they were.
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)

    if exit_message is not None:
        print exit_message

if __name__ == "__main__":
    main()
