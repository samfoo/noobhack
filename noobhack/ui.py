"""
The UI components of noobhack. `Game` draws and manages the actual nethack 
game, while `Helper` draws the help/cheat overlay.
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

class Map:
    """
    Map is the graphical representation of the level graph. It draws the map on
    the entire screen and allows vertical scrolling with the 'j' and 'k' keys.
    """

    def __init__(self, output_proxy):
        self.brain = brain.Brain(output_proxy)
        self.player = player.Player()
        self.dungeon = dungeon.Dungeon()
        self.columns = {}

    def _draw_level(self, window, y, x, level, current=False):
        """
        Draw the box for an individual level at (x, y). 
        """

        if len(level.features) > 0:
            features = ",".join(level.short_codes())
        else:
            features = "?"

        title = " %s:%d " % (level.branch, level.dlvl)

        height = 3
        width = max(len(features), len(title) + 2) + 2 

        draw_x = x - (width / 2)
        draw_y = y - 1

        node = window.derwin(height, width, draw_y, draw_x)
        node.border("|", "|", "-", "-", "+", "+", "+", "+")

        if current:
            node.addstr(0, 2, title, 
                        curses.A_BOLD | get_color(curses.COLOR_YELLOW))
        else:
            node.addstr(0, 2, title)

        node.addstr(1, (width / 2) - (len(features) / 2), features)

        return draw_x, draw_y

    def _get_level_x(self, level):
        """
        Given a level, return the x-coord where its box should be drawn.
        """
        return self.columns[level.branch] 

    def _get_level_y(self, level):
        """
        Given a level, return the y-coord where its box should be drawn.
        """
        return level.dlvl * 4 + (size()[0] / 2) 

    def _r_draw_branch(self, window, level):
        """
        Starting at `level` draw all of the children and all of their children.
        """

        x, y = self._get_level_x(level), self._get_level_y(level)

        graph = self.dungeon.graph

        # The first thing we can do is draw the current level... 
        is_current = level == graph.current
        drawn_x, drawn_y = self._draw_level(window, y, x, level, is_current)

        if graph.is_orphan(level):
            window.addstr(drawn_y - 1, x, "*", 
                          curses.A_BOLD | get_color(curses.COLOR_RED))

        # Now draw any links that this current level has with others...
        children = graph.children(level)

        for child in children:
            self._r_draw_branch(window, child)

            # Now draw the link.
            child_x = self._get_level_x(child)
            if child_x == x:
                # Same column, just add a down pipe.
                window.addstr(y + 2, x, "|", get_color(curses.COLOR_CYAN))
            elif child_x < x:
                # Column to the left...
                slash_x = (child_x + 7)
                window.addstr(y + 2, slash_x, "/", get_color(curses.COLOR_CYAN))
                connector_x = slash_x + 1
                connector = "." + "-" * (drawn_x - slash_x - 2)
                window.addstr(y + 1, slash_x + 1, connector, 
                              get_color(curses.COLOR_CYAN))
            else:
                # Column to the right...
                slash_x = (child_x - 7)
                window.addstr(y + 2, slash_x, "\\", get_color(curses.COLOR_CYAN))
                connector_x = x + (x - drawn_x)
                connector = ("-" * (slash_x - connector_x - 1)) + "."
                window.addstr(y + 1, connector_x, connector, get_color(curses.COLOR_CYAN))

    def _draw_legend(self):
        """
        Create the legend box in the upper left.
        """

        items = {
            "o": "Oracle",
            "r": "Rogue",
            "a[cnl]": "Altar",
            "w": "Angry watch",
            "z": "Zoo",
            "b": "Barracks",
            "s": "Shop",
            "v": "Vault",
            "h": "Beehive",
        }

        legend = curses.newwin(11, 20, 1, 3)
        legend.border("|", "|", "-", "-", "+", "+", "+", "+")
        legend.addstr(0, 3, " Legend: ")

        codes = sorted(items.keys())
        for i, code in enumerate(codes, 1):
            legend.addstr(i, 2, "%s" % code, curses.A_BOLD)
            legend.addstr(i, 20 - len(items[code]) - 2, items[code])

        return legend

    def display(self, window, close="`"):
        """
        Draw the map ui.
        """

        approx_height = max(self.dungeon.graph.levels.keys()) * 4 + size()[0] 
        approx_width = size()[1]
        plane = curses.newpad(approx_height, approx_width)

        # Ghetto fabulous hard coded numbers. But I want the map to display the
        # same every game, and I know something about what branches there's 
        # going to be.
        self.columns["main"] = approx_width / 2
        self.columns["mines"] = (approx_width / 2) - 20 
        self.columns["sokoban"] = (approx_width / 2) + 20 

        self._r_draw_branch(plane, self.dungeon.graph.first())

        # Don't forget to draw the orphaned levels too...
        for dlvl in [lvl for lvl in self.dungeon.graph.levels.keys() if lvl != 1]:
            for orphan in self.dungeon.graph.orphans(dlvl):
                self._r_draw_branch(plane, orphan)

        scroll_y = self._get_level_y(self.dungeon.graph.current) 
        scroll_y -= size()[0] / 2
        while True:
            # To get the legend flicker-free we need to draw everything first,
            # call noutrefresh() to refresh curses' screen buffer, but not to
            # copy it to the screen yet. After we've done all that we can
            # refresh the screen.
            legend = self._draw_legend()
            plane.noutrefresh(scroll_y, 0, 0, 0, size()[0] - 1, size()[1] - 1)
            legend.noutrefresh()

            # For some reason, curses *really* wants the cursor to below to the
            # main window, no matter who used it last. Regardless, just move it
            # to the lower left so it's out of the way.
            window.move(window.getmaxyx()[0] - 1, 0)
            window.noutrefresh()

            curses.doupdate()

            # Wait around until we get some input.
            # TODO: I suspect in longer games pgup, pgdown are going to be 
            # important. Implement them here.
            key = sys.stdin.read(1)
            if key == "k":
                scroll_y = max(scroll_y - 1, 4) 
            elif key == "j":
                scroll_y = min(scroll_y + 1, approx_height - size()[0])
            elif key == close:
                break

class Helper:
    """
    Maintain the state of the helper UI and draw it to a curses screen when
    `redraw` is called.
    """

    resistance_width = 12
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

    def _height(self):
        """
        Return the height of the helper ui. This means finding the max number
        of lines that is to be displayed in all of the boxes. 
        """

        return 1 + max(1, max(
            len(self.dungeon.current_level().features),
            len(self._get_statuses()),
            len(self.player.resistances),
        ))

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
        return row - self._height() - 1

    def _level_box(self):
        """
        Create the pane with information about this dungeon level.
        """

        level = self.dungeon.current_level()
        default = "(none)"

        dungeon_frame = curses.newwin(
            self._height(), 
            self.level_width, 
            self._top(), 
            0
        )

        dungeon_frame.clear()
        dungeon_frame.border("|", "|", "-", " ", "+", "+", "|", "|")
        dungeon_frame.addstr(0, 2, " this level ", get_color(curses.COLOR_CYAN))

        features = sorted(level.features)
        for row, feature in enumerate(features, 1):
            dungeon_frame.addnstr(row, 1, feature, self.level_width-2)

        if len(features) == 0:
            center = (self.level_width / 2) - (len(default) / 2)
            dungeon_frame.addstr(1, center, default)

        return dungeon_frame

    def _resistance_box(self):
        """
        Create the pane with information with the player's current resistances.
        """

        default = "(none)"

        def res_color(res):
            """Return the color of a resistance."""
            if res == "fire": return curses.COLOR_RED
            elif res == "cold": return curses.COLOR_BLUE 
            elif res == "poison": return curses.COLOR_GREEN
            elif res == "disintegration": return curses.COLOR_YELLOW
            else: return -1

        res_frame = curses.newwin(
            self._height(), 
            self.resistance_width, 
            self._top(), 
            self.level_width + self.status_width - 2
        )

        res_frame.clear()
        res_frame.border("|", "|", "-", " ", "+", "+", "|", "|")
        res_frame.addstr(0, 2, " resist ", get_color(curses.COLOR_CYAN))
        resistances = sorted(self.player.resistances)
        for row, res in enumerate(resistances, 1):
            color = get_color(res_color(res))
            res_frame.addnstr(row, 1, res, self.resistance_width-2, color)

        if len(resistances) == 0:
            center = (self.resistance_width / 2) - (len(default) / 2)
            res_frame.addstr(1, center, default)

        return res_frame

    def _status_box(self):
        """
        Create the pane with information about the player's current state.
        """

        default = "(none)"

        status_frame = curses.newwin(
            self._height(), 
            self.status_width, 
            self._top(), 
            self.level_width - 1
        )

        status_frame.clear()
        status_frame.border("|", "|", "-", " ", "+", "+", "|", "|")
        status_frame.addstr(0, 2, " status ", get_color(curses.COLOR_CYAN))
        statuses = self._get_statuses()
        for row, stat in enumerate(statuses, 1):
            attrs = []
            if status.type_of(stat) == "bad":
                attrs += [get_color(curses.COLOR_RED)]

            attrs = reduce(lambda a, b: a | b, attrs, 0)
            status_frame.addnstr(row, 1, stat, self.status_width-2, attrs)

        if len(statuses) == 0:
            center = (self.status_width / 2) - (len(default) / 2)
            status_frame.addstr(1, center, default)

        return status_frame

    def redraw(self, window):
        """
        Repaint the screen with the helper UI.
        """

        status_frame = self._status_box()
        dungeon_frame = self._level_box()
        resist_frame = self._resistance_box()

        status_frame.overwrite(window)
        dungeon_frame.overwrite(window)
        resist_frame.overwrite(window)

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

