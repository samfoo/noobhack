import re
import curses 
import locale

from noobhack.ui.common import styles, colors, get_color

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


