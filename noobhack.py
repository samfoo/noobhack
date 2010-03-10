import sys
import tty
import termios

import telnet
import proxy

def main():
    try:
        # Store off our terminal settings.
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)

        t = telnet.Telnet()
        t.open();

        # Start our input/output threads.
        output = proxy.Output(t.conn)
        input = proxy.Input(t.conn)

        output.start()
        input.start()

        # Wait for the output thread to die
        output.join()
    finally:
        # Make sure we restore the terminal settings to where they were.
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)

    sys.exit(1)

if __name__ == "__main__":
    # TODO: optparse
    main()
