import re
import sys
import fcntl
import curses 
import struct
import locale
import termios

from noobhack.ui.common import *

class Minimap:
    branch_display_names = {
        "main": "Dungeons of Doom",
    }

    def __init__(self):
        self.dungeon = None

    def shop_text_as_buffer(self, shops):
        if len(shops) > 0:
            return ["  Shops:"] + ["    * %s" % s for s in shops]
        else:
            return []

    def feature_text_as_buffer(self, features):
        return ["  * %s" % f for f in sorted(features)]

    def level_text_as_buffer(self, level):
        buf = self.shop_text_as_buffer(level.shops) + \
              self.feature_text_as_buffer(level.features)
        return ["Level %s:" % level.dlvl] + (buf or ["  (nothing interesting)"])

    def line_to_display(self, text, width, border="|", padding=" "):
        if len(text) > (width + len(border) * 2  + len(padding) * 2):
            # If the text is too long to fit in the width, then trim it.
            text = text[:(width + len(border) * 2 + 2)]
        return "%s%s%s%s%s" % (
            border, padding, 
            text + padding * (width - len(text) - len(border) * 2 - len(padding) * 2), 
            padding, border
        )

    def layout_level_text_buffers(self, levels):
        result = []
        last_level = None
        indices = {}
        for level in levels:
            if last_level is not None and level.dlvl > (last_level.dlvl + 1):
                level_display_buffer = ["...", ""] + \
                                       self.level_text_as_buffer(level) + \
                                       [""]
                indices[level.dlvl] = len(result) + 2
                result += level_display_buffer
            else:
                level_display_buffer = self.level_text_as_buffer(level) + [""]
                indices[level.dlvl] = len(result)
                result += level_display_buffer

            last_level = level

        return indices, result 

    def header_as_buffer(self, text, width):
        return [
            self.line_to_display("-" * (width - 2), width, ".", ""),
            self.line_to_display(text, width),
            self.line_to_display("=" * (width - 2), width, padding=""),
        ]

    def footer_as_buffer(self, width):
        return [self.line_to_display("...", width, "'")]


    def unconnected_branch_as_buffer_with_indices(self, display_name, branch):
        indices, level_texts = self.layout_level_text_buffers(branch)
        max_level_text_width = len(max(level_texts, key=len))

        # The '4' comes from two spaces of padding and two border pipes.
        width = 4 + max(len(display_name), max_level_text_width)

        header = self.header_as_buffer(display_name, width)
        body = [self.line_to_display(t, width) for t in level_texts]
        footer = self.footer_as_buffer(width)

        # Adjust the indices to account for the header
        indices = dict([(dlvl, index + len(header)) 
                       for dlvl, index 
                       in indices.iteritems()])

        return (indices, header + body + footer) 

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

