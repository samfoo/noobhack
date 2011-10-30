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
            return ["  Shops:"] + ["    * %s" % s.capitalize() for s in shops]
        else:
            return []

    def feature_text_as_buffer(self, features):
        return ["  * %s" % f.capitalize() 
                for f in sorted(features) 
                if f != "shop"]

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

    def get_plane_for_map(self, levels):
        # Hopefully 10 lines per dungeon level on average is large enough...
        max_height = max(size()[0], len(levels) * 10)
        max_width = size()[1]
        return curses.newpad(max_height, max_width)

    def display(self, dungeon, window, close="`"):
        plane = self.get_plane_for_map(dungeon)
        _, buf = self.unconnected_branch_as_buffer_with_indices(
            "Dungeons of Doom", 
            dungeon
        )

        for i, line in enumerate(buf):
            plane.addstr(i, 0, line)

        scroll_y = 0

        while True:
            plane.noutrefresh(scroll_y, 0, 0, 0, size()[0] - 1, size()[1] - 1)

            # For some reason, curses *really* wants the cursor to be below to the
            # main window, no matter who used it last. Regardless, just move it
            # to the lower left so it's out of the way.
            window.move(window.getmaxyx()[0] - 1, 0)
            window.noutrefresh()

            curses.doupdate()

            # Wait around until we get some input.
            key = sys.stdin.read(1)
            if key == "k":
                scroll_y = max(scroll_y - 1, 0) 
            elif key == "j":
                scroll_y = min(scroll_y + 1, size()[0])
            elif key == close or key == "\x1b":
                break
