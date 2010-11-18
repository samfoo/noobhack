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

from game import player, dungeon, brain, status

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

class Helper:
    """
    Maintain the state of the helper UI and draw it to a curses screen when
    `redraw` is called.
    """

    height = 6 
    status_width = 12
    level_width = 25 

    def __init__(self, output_proxy):
        self.brain = brain.Brain(output_proxy)
        self.player = player.Player()
        self.dungeon = dungeon.Dungeon()

    def _get_statuses(self):
        """
        Return the statuses to display in the status frame, sorted.
        """

        def sort_statuses(left, right):
            """Sort statuses first by their effect (bad, good, neutral), and
            second by their name."""
            diff = cmp(status.type_of(left), status.type_of(right))
            if diff == 0:
                diff = cmp(left, right)
            return diff

        return sorted(self.player.status, sort_statuses)

    def _top(self):
        """
        Return the y coordinate of the top of where the ui overlay should be
        drawn.
        """

        for i in xrange(len(self.brain.term.display)-1, -1, -1):
            row = i
            line = self.brain.term.display[i].strip()
            if len(line) > 0:
                break
        return row - self.height - 1

    def _redraw_level(self):
        """
        Create the pane with information about this dungeon level.
        """

        level = self.dungeon.current_level()
        default = "(none)"

        dungeon_frame = curses.newwin(self.height, self.level_width, self._top(), 0)
        dungeon_frame.clear()
        dungeon_frame.border("|", "|", "-", " ", "+", "+", "|", "|")
        dungeon_frame.addstr(0, 2, " this level ", get_color(curses.COLOR_CYAN))

        features = sorted(level.features)
        for row, feature in enumerate(features, 1):
            if row > self.height + 1:
                break

            dungeon_frame.addnstr(row, 1, feature, self.level_width-2)

        if len(features) == 0:
            dungeon_frame.addstr(1, (self.level_width/2) - (len(default)/2), default)

        return dungeon_frame

    def _redraw_status(self):
        """
        Create the pane with information about the player.
        """

        default = "(none)"

        status_frame = curses.newwin(self.height, self.status_width, self._top(), self.level_width-1)
        status_frame.clear()
        status_frame.border("|", "|", "-", " ", "+", "+", "|", "|")
        status_frame.addstr(0, 2, " status ", get_color(curses.COLOR_CYAN))
        statuses = self._get_statuses()
        for row, stat in enumerate(statuses, 1):
            if row > self.height + 1:
                # Hopefully we don't often encounter having too many statuses 
                # to properly display
                break

            attrs = []
            if status.type_of(stat) == "bad":
                attrs += [get_color(curses.COLOR_RED)]

            attrs = reduce(lambda a, b: a | b, attrs, 0)
            status_frame.addnstr(row, 1, stat, self.status_width-2, attrs)

        if len(statuses) == 0:
            status_frame.addstr(1, (self.status_width/2) - (len(default)/2), default)

        return status_frame

    def redraw(self, window):
        """
        Repaint the screen with the helper UI.
        """

        status_frame = self._redraw_status()
        dungeon_frame = self._redraw_level()
        status_frame.overwrite(window)
        dungeon_frame.overwrite(window)
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

