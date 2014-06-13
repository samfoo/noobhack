import re
import curses
import locale

from noobhack.ui.common import styles, colors, get_color

class Game:
    """
    Draw the game in the terminal.
    """

    def __init__(self, term, plugins):
        self.term = term
        self.plugins = plugins
        self.code = locale.getpreferredencoding()

    def _write_text(self, window, row, row_str):
        max_y, max_x = window.getmaxyx()
        if row == max_y -1:
           window.addstr(row, 0, row_str[:-1])
           window.insch(row_str[-1])
        else:
           window.addstr(row, 0, row_str)

    def _write_attrs(self, window, row):
        row_a = self.term.attributes[row]
        for col, (char_style, foreground, background) in enumerate(row_a):
            char_style = set(char_style)
            foreground = colors.get(foreground, -1)
            background = colors.get(background, -1)
            char_style = [styles.get(s, curses.A_NORMAL) for s in char_style]
            attrs = char_style + [get_color(foreground, background)]
            window.chgat(row, col, 1, reduce(lambda a, b: a | b, attrs)) 

    def _redraw_row(self, window, row):
        """
        Draw a single game-row in the curses display window. This means writing
        the text from the in-memory terminal out and setting the color/style
        attributes appropriately.
        """
        row_str = self.term.display[row].encode(self.code)

        self._write_text(window, row, row_str)
        self._write_attrs(window, row)

    def redraw(self, window):
        """
        Repaint the screen with the new contents of our terminal emulator...
        """

        window.erase()

        for plugin in self.plugins:
            plugin.redraw(self.term)

        for row_index in xrange(len(self.term.display)):
            self._redraw_row(window, row_index)

        # Don't forget to move the cursor to where it is in game...
        cur_x, cur_y = self.term.cursor()
        window.move(cur_y, cur_x)

        # Finally, redraw the whole thing.
        window.noutrefresh()


