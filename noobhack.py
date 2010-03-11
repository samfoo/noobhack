import sys
import tty
import pdb
import termios
import select

import telnet
import process
import proxy

def main():
    try:
        # Store off our terminal settings so we can restore them later.
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)

        conn = process.Local()
        conn.open();

        output, input = proxy.Output(conn), proxy.Input(conn)

        while True:
            reads = select.select([conn.fileno(), sys.stdin.fileno()], [], [])[0]

            if conn.fileno() in reads:
                # Do our display logic.
                output.proxy()

            if sys.stdin.fileno() in reads:
                # Do our input logic.
                input.proxy()
    except IOError:
        # Nethack terminated or there was some problem communicating with it.
        pass
    finally:
        # Make sure we restore the terminal settings to where they were.
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)

if __name__ == "__main__":
    # TODO: optparse
    main()
