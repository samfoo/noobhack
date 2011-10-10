"""
The UI components of noobhack. `Game` draws and manages the actual nethack 
game, while `Helper` draws the help/cheat overlay, and `Map` draws the map 
screen.
"""

import re
import sys
import fcntl
import curses 
import struct
import locale
import termios

from noobhack.game import status, shops

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

class Debug:
    def __init__(self, player, dungeon):
        self.player = player
        self.dungeon = dungeon

    def _draw_dungeon(self, window):
        window.border("|", "|", "-", "-", "+", "+", "+", "+")
        window.addstr(1, 1, "current: " + str(self.dungeon.graph.current))
        window.addstr(2, 1, "links: " + str(self.dungeon.graph.links))

        ordered_and_flattened = []
        levels_we_know_about = sorted(self.dungeon.graph.levels.keys())
        for tier in levels_we_know_about:
            ordered_and_flattened += self.dungeon.graph.levels[tier]

        for i, lvl in enumerate(ordered_and_flattened):
            window.addstr(4+i, 1, str(lvl))

    def display(self, window):
        window.clear()

        self._draw_dungeon(window)

        while True:
            window.refresh()

            # Wait around until we get some input.
            key = sys.stdin.read(1)
            if key == "!" or key == "\x1b":
                break

class Map:
    """
    Map is the graphical representation of the level graph. It draws the map on
    the entire screen and allows vertical scrolling with the 'j' and 'k' keys.
    """

    def __init__(self, brain, player, dungeon):
        self.brain = brain
        self.columns = {}

        self.player = player
        self.dungeon = dungeon

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
            node.addstr(0, 2, title)
            node.chgat(0, 2, len(title), curses.A_BOLD | get_color(curses.COLOR_YELLOW))
        else:
            node.addstr(0, 2, title)

        node.addstr(1, (width / 2) - (len(features) / 2), features)

        return draw_x, draw_y

    def _get_level_x(self, level):
        """
        Given a level, return the x-coord where its box should be drawn.
        """
        graph = self.dungeon.graph
        siblings_whose_branch_is_ambiguous = \
                [s for s in graph.levels[level.dlvl] if s.branch == level.branch and s != level]

        if len(siblings_whose_branch_is_ambiguous) > 0:
            order = [l for l in graph.levels[level.dlvl] if l.branch == level.branch]
            far_left = self.columns[level.branch] - \
                    (len(siblings_whose_branch_is_ambiguous) / 2) * 10
            return far_left + 10 * order.index(level)
        else:
            return self.columns[level.branch] 

    def _get_level_y(self, level):
        """
        Given a level, return the y-coord where its box should be drawn.
        """
        if level.dlvl > 0:
            return level.dlvl * 4 + (size()[0] / 2) 
        elif -1 >= level.dlvl >= -4:
            return (size()[0] / 2)
        else:
            return (size()[0] / 2) - 4 

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
            window.addstr(drawn_y - 1, x, "*")
            window.chgat(drawn_y - 1, x, 1, curses.A_BOLD | get_color(curses.COLOR_RED))

        # Now draw any links that this current level has with others...
        children = graph.children(level)

        for child in children:
            self._r_draw_branch(window, child)

            # Now draw the link.
            child_x = self._get_level_x(child)
            if child_x == x:
                # Same column, just add a down pipe.
                window.addstr(y + 2, x, "|")
                window.chgat(y + 2, x, get_color(curses.COLOR_CYAN))
            elif child_x < x:
                # Column to the left...
                slash_x = (child_x + 7)
                window.addstr(y + 2, slash_x, "/")
                window.chgat(y + 2, slash_x, 1, get_color(curses.COLOR_CYAN)) 
                connector_x = slash_x + 1
                connector = "." + "-" * (drawn_x - slash_x - 2)
                window.addstr(y + 1, slash_x + 1, connector)
                window.chgat(y + 1, slash_x + 1, len(connector), get_color(curses.COLOR_CYAN))
            else:
                # Column to the right...
                slash_x = (child_x - 7)
                window.addstr(y + 2, slash_x, "\\")
                window.chgat(y + 2, slash_x, 1, get_color(curses.COLOR_CYAN))
                connector_x = x + (x - drawn_x)
                connector = ("-" * (slash_x - connector_x - 1)) + "."
                window.addstr(y + 1, connector_x, connector)
                window.chgat(y + 1, connector_x, len(connector), get_color(curses.COLOR_CYAN))

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
            "c": "Chest",
        }

        legend = curses.newwin(15, 20, 1, 3)
        legend.border("|", "|", "-", "-", "+", "+", "+", "+")
        legend.addstr(0, 3, " Legend: ")
        legend.addstr(1, 2, "Press ` to exit", curses.A_BOLD)
        legend.addstr(2, 2, "j, k to scroll", curses.A_BOLD)

        codes = sorted(items.keys())
        for i, code in enumerate(codes, 4):
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
        self.columns["earth"] = (approx_width / 2 ) - (approx_width / 4)
        self.columns["air"] = (approx_width / 2) - 8 
        self.columns["fire"] = (approx_width / 2) + 8 
        self.columns["water"] = (approx_width / 2) + (approx_width / 4)
        self.columns["astral"] = approx_width / 2
        self.columns["quest"] = (approx_width / 2) + 20
        self.columns["ludios"] = (approx_width / 2) - 20
        self.columns["unknown"] = (approx_width / 2) + 30

        self._r_draw_branch(plane, self.dungeon.graph.first())

        # Draw the elemental planes
        for dlvl in [lvl for lvl in self.dungeon.graph.levels.keys() if lvl < 1]:
            element = self.dungeon.graph.levels[dlvl][0]
            self._r_draw_branch(plane, element)

        # Don't forget to draw the orphaned levels too...
        for dlvl in [lvl for lvl in self.dungeon.graph.levels.keys() if lvl > 1]:
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
            # In longer games pgup, pgdown are going to be 
            # important. 
            key = sys.stdin.read(1)
            if key == "k":
                scroll_y = max(scroll_y - 1, 0) 
            elif key == "j":
                scroll_y = min(scroll_y + 1, approx_height - size()[0])
            elif key == "K":
                scroll_y = max(scroll_y - 10, 0) 
            elif key == "J":
                scroll_y = min(scroll_y + 10, approx_height - size()[0])
            elif key == close or key == "\x1b":
                break

class Helper:
    """
    Maintain the state of the helper UI and draw it to a curses screen when
    `redraw` is called.
    """

    intrinsic_width = 25
    status_width = 12
    level_width = 25 

    def __init__(self, brain, player, dungeon):
        self.brain = brain

        self.player = player
        self.dungeon = dungeon

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

        level = self.dungeon.current_level()
        return 1 + max(1, max(
            len(level.features) + len(level.shops),
            len(self._get_statuses()),
            len(self.player.intrinsics),
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

        dungeon_frame.erase()
        dungeon_frame.border("|", "|", "-", " ", "+", "+", "|", "|")
        dungeon_frame.addstr(0, 2, " this level ")
        dungeon_frame.chgat(0, 2, len(" this level "), get_color(curses.COLOR_CYAN))

        features = sorted(level.features)
        row = 1
        i = 0
        while i < len(features):
            feature = features[i]
            dungeon_frame.addnstr(row, 1, feature, self.level_width-2)
            row += 1
            i += 1

            if feature == "shop":
                for shop in sorted(level.shops):
                    dungeon_frame.addnstr(row, 3, "* " + shop, self.level_width-5)
                    row += 1

        if len(features) == 0:
            center = (self.level_width / 2) - (len(default) / 2)
            dungeon_frame.addstr(1, center, default)

        return dungeon_frame

    def _intrinsic_box(self):
        """
        Create the pane with information with the player's current intrinsics.
        """

        default = "(none)"

        def res_color(res):
            """Return the color of a intrinsic."""
            if res == "fire": 
                return curses.COLOR_RED
            elif res == "cold": 
                return curses.COLOR_BLUE 
            elif res == "poison": 
                return curses.COLOR_GREEN
            elif res == "disintegration": 
                return curses.COLOR_YELLOW
            else: 
                return -1

        res_frame = curses.newwin(
            self._height(), 
            self.intrinsic_width, 
            self._top(), 
            self.level_width + self.status_width - 2
        )

        res_frame.erase()
        res_frame.border("|", "|", "-", " ", "+", "+", "|", "|")
        res_frame.addstr(0, 2, " intrinsic ")
        res_frame.chgat(0, 2, len(" intrinsic "), get_color(curses.COLOR_CYAN))
        intrinsics = sorted(self.player.intrinsics)
        for row, res in enumerate(intrinsics, 1):
            color = get_color(res_color(res))
            res_frame.addnstr(row, 1, res, self.intrinsic_width-2)
            res_frame.chgat(row, 1, min(len(res), self.intrinsic_width-2), color)

        if len(intrinsics) == 0:
            center = (self.intrinsic_width / 2) - (len(default) / 2)
            res_frame.addstr(1, center, default)

        return res_frame

    def _identify_box(self, items):
        """
        Create the pain with information about price identifying something.
        """

        items = sorted(items, lambda a, b: cmp(b[2], a[2]))
        total_chance = sum(float(i[2]) for i in items)
        items = [(i[0], i[1], (i[2] / total_chance) * 100.) for i in items]
        items = [("%s" % i[0], "%0.2f%%" % float(i[2])) for i in items]
        if len(items) == 0:
            items = set([("(huh... can't identify)", "100%")])

        width = 2 + max([len(i[0]) + len(i[1]) + 4 for i in items])

        identify_frame = curses.newwin(len(items) + 1, width, 1, 0)
        identify_frame.border("|", "|", " ", "-", "|", "|", "+", "+")
        identify_frame.addstr(len(items), 2, " identify ")
        identify_frame.chgat(len(items), 2, len(" identify "), get_color(curses.COLOR_CYAN))

        for row, item in enumerate(items):
            identify_frame.addstr(row, 2, item[0])
            identify_frame.addstr(row, width - len(item[1]) - 2, item[1])

        return identify_frame

    def _things_to_sell_identify(self):
        line = self.brain.term.display[0]
        match = re.search(shops.offer, line, re.I)
        if match is not None:
            price = int(match.groups()[0])
            item = match.groups()[1]

            return (item, price)

        return None

    def _things_to_buy_identify(self):
        # TODO: Make sure that unpaid prices can only ever appear on the first
        # line. I might have to check the second line too.
        line = self.brain.term.display[0]
        match = re.search(shops.price, line, re.I)
        if match is not None:
            count = match.groups()[0]
            item = match.groups()[1]
            price = int(match.groups()[2])

            if count == "a":
                count = 1
            else:
                count = int(count)

            price = price / count

            return (item, price)

        return None

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

        status_frame.erase()
        status_frame.border("|", "|", "-", " ", "+", "+", "|", "|")
        status_frame.addstr(0, 2, " status ")
        status_frame.chgat(0, 2, len(" status "), get_color(curses.COLOR_CYAN))
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

    def _breadcrumbs(self, window):
        breadcrumbs = self.dungeon.current_level().breadcrumbs

        for crumb in breadcrumbs:
            x, y = crumb
            if self.brain.char_at(x, y) not in [".", "#", " "]: 
                # Ignore anything that's not something we can step on.
                continue

            if self.brain.char_at(x, y) == " ":
                window.addch(y, x, ".")

            window.chgat(y, x, 1, curses.A_BOLD | get_color(curses.COLOR_MAGENTA))

        cur_x, cur_y = self.brain.term.cursor()
        window.move(cur_y, cur_x)

    def redraw(self, window, breadcrumbs=False):
        """
        Repaint the screen with the helper UI.
        """

        if self.brain.cursor_is_on_player() and breadcrumbs:
            self._breadcrumbs(window)

        if self._things_to_buy_identify() is not None:
            item, price = self._things_to_buy_identify()
            items = shops.buy_identify(self.brain.charisma(), item, price, self.brain.sucker())

            identify_frame = self._identify_box(items)
            identify_frame.overwrite(window)
        elif self._things_to_sell_identify() is not None:
            item, price = self._things_to_sell_identify()
            items = shops.sell_identify(item, price, self.brain.sucker())

            identify_frame = self._identify_box(items)
            identify_frame.overwrite(window)

        status_frame = self._status_box()
        dungeon_frame = self._level_box()
        intrinsic_frame = self._intrinsic_box()

        status_frame.overwrite(window)
        dungeon_frame.overwrite(window)
        intrinsic_frame.overwrite(window)

        window.noutrefresh()

class Game:
    """
    Draw the game in the terminal.
    """

    def __init__(self, term):
        self.term = term
        self.code = locale.getpreferredencoding()

    def _redraw_row(self, window, row):
        """
        Draw a single game-row in the curses display window. This means writing
        the text from the in-memory terminal out and setting the color/style
        attributes appropriately.
        """
        row_c = self.term.display[row].encode(self.code)
        window.addstr(row, 0, row_c)

        row_a = self.term.attributes[row]
        for col, (char_style, foreground, background) in enumerate(row_a): 
            char_style = set(char_style)
            foreground = colors.get(foreground, -1)
            background = colors.get(background, -1)
            char_style = [styles.get(s, curses.A_NORMAL) for s in char_style]
            attrs = char_style + [get_color(foreground, background)]
            window.chgat(row, col, 1, reduce(lambda a, b: a | b, attrs)) 

        if "HP:" in row_c:
            # Highlight health depending on much much is left.
            match = re.search("HP:(\\d+)\\((\\d+)\\)", row_c)
            if match is not None:
                hp, hp_max = match.groups()
                ratio = float(hp) / float(hp_max)

                if ratio <= 0.25:
                    attrs = [curses.A_BOLD, get_color(curses.COLOR_WHITE, curses.COLOR_RED)]
                elif ratio <= 0.5:
                    attrs = [curses.A_BOLD, get_color(curses.COLOR_YELLOW)]
                else:
                    attrs = [curses.A_BOLD, get_color(curses.COLOR_GREEN)]
                attrs = reduce(lambda a, b: a | b, attrs)
                window.chgat(row, match.start() + 3, match.end() - match.start() - 3, attrs)


    def redraw(self, window):
        """
        Repaint the screen with the new contents of our terminal emulator...
        """

        window.erase()
        for row_index in xrange(len(self.term.display)):
            self._redraw_row(window, row_index)

        # Don't forget to move the cursor to where it is in game...
        cur_x, cur_y = self.term.cursor()
        window.move(cur_y, cur_x)

        # Finally, redraw the whole thing.
        window.noutrefresh()

