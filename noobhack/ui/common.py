import sys
import fcntl
import curses 
import struct
import termios

# Map vt102 colors to curses colors. Notably nethack likes to use `brown`
# which is the only difference between curses and linux console colors. Turns
# out that it just renders as yellow (at least in OSX Terminal.app) anyway.
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

# Map vt102 text styles to curses attributes.
styles = {
    "bold": curses.A_BOLD,
    "dim": curses.A_DIM,
    "underline": curses.A_UNDERLINE,
    "blink": curses.A_BLINK,
    "reverse": curses.A_REVERSE,
}

def get_color(foreground, background=-1, registered={}):
    """
    Given a foreground and background color pair, return the curses
    attribute. If there isn't a color of that type registered yet, then
    create it.

    :param registered: Don't ever pass something in for this. The default
    mutable param as static is overriden as a feature of sorts so that
    a static variable doesn't have to be declared somewhere else.
    """
    if not registered.has_key((foreground, background)):
        curses.init_pair(len(registered)+1, foreground, background)
        registered[(foreground, background)] = len(registered) + 1
    return curses.color_pair(registered[(foreground, background)])

def size():
    """
    Get the current terminal size.

    :return: (rows, cols)
    """

    raw = fcntl.ioctl(sys.stdin, termios.TIOCGWINSZ, 'SSSS')
    return struct.unpack('hh', raw) 
