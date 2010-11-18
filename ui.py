"""
The UI components of noobhack. `Game` draws and manages the actual nethack 
game, while `Helper` draws the help/cheat screen.
"""

import sys
import fcntl
import curses 
import struct
import termios

import vt102 

from game import player, brain, status

# Map vt102 colors to curses colors. Notably nethack likes to use `brown`
# which is the only difference between curses and linux console colors. Turns
# out that it just renders as yellow anyway.
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
}

def get_color(foreground, background, registered={}):
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

class Helper:
    """
    Maintain the state of the helper UI and draw it to a curses screen when
    `redraw` is called.
    """

    def __init__(self, output_proxy):
        self.brain = brain.Brain(output_proxy)
        self.player = player.Player()

    def _get_statuses(self):
        """
        Return the statuses to display in the status frame, sorted.
        """

        def sort_statuses(left, right):
            """Sort statuses first by their effect (bad, good, neutral), and
            second by their name."""
            diff = cmp(status.type(left), status.type(right))
            if diff == 0:
                diff = cmp(left, right)
            return diff

        return sorted(self.player.status, sort_statuses)

    def _redraw_status(self, window):
        """
        Redraw the status frame.
        """

        height, width = 10, 15
        # TODO: I'm unclear whether creating a derived window every time 
        # there's a repaint is a memory leak or not. For now I'm going to leave
        # it, but `status_frame` might have to be a property instead.
        status_frame = window.derwin(height, width, 0, 0)
        status_frame.border("|", "|", "-", "-", "+", "+", "+", "+")
        status_frame.addstr(0, 2, " status ")
        statuses = self._get_statuses()
        for row, stat in enumerate(statuses, 1):
            attrs = []
            if status.type(stat) == "bad":
                attrs += [curses.A_BOLD, get_color(curses.COLOR_RED, -1)]
            elif status.type(stat) == "good":
                attrs += [get_color(curses.COLOR_GREEN, -1)]

            attrs = reduce(lambda a, b: a | b, attrs, 0)
            status_frame.addnstr(row, 1, stat, width-2, attrs)
        status_frame.refresh()

    def redraw(self, window):
        """
        Repaint the screen with the helper UI.
        """
        window.clear()
        self._redraw_status(window)
        window.refresh()

class Game:
    """
    Given an output proxy, a game maintains a terminal in-memory and writes it
    out to a curses screen when `redraw` is called.
    """

    def __init__(self, output_proxy):
        # Create an in-memory terminal screen and register it's stream
        # processor with the output proxy.
        self.stream = vt102.stream()

        # For some reason that I can't assertain: curses freaks out and crashes
        # when you use exactly the number of rows that are available on the
        # terminal. It seems easiest just to subtract one from the rows and 
        # deal with it rather than hunt forever trying to figure out what I'm
        # doing wrong with curses.
        rows, cols = size()
        self.term = vt102.screen((rows-1, cols))
        self.term.attach(self.stream)
        output_proxy.register(self.stream.process)

    def _redraw_row(self, window, row):
        """
        Draw a single game-row in the curses display window. This means writing
        the text from the in-memory terminal out and setting the color/style
        attributes appropriately.
        """
        row_a = self.term.attributes[row]
        row_c = self.term.display[row]
        for col, (char, (char_style, foreground, background)) in enumerate(zip(row_c, row_a)): 
            char_style = set(char_style)
            foreground = colors.get(foreground, -1)
            background = colors.get(background, -1)
            char_style = [styles.get(s, curses.A_NORMAL) for s in char_style]
            attrs = char_style + [get_color(foreground, background)]
            window.addch(row, col, char, reduce(lambda a, b: a | b, attrs))

    def redraw(self, window):
        """
        Repaint the screen with the new contents of our terminal emulator...
        """

        window.clear()
        for row_index in xrange(len(self.term.display)):
            self._redraw_row(window, row_index)

        # Don't forget to move the cursor to where it is in game...
        cur_x, cur_y = self.term.cursor()
        window.move(cur_y, cur_x)

        # Finally, redraw the whole thing.
        window.refresh()

