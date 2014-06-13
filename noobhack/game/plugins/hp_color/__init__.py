import re
import locale

ENCODING = locale.getpreferredencoding()

def color_hp(row, col, length, color, term):
    for i in xrange(length):
        term.attributes[row][col+i] = color

def color_for_ratio(ratio):
    bg = "default"

    if ratio <= 0.25:
        fg = "white"
        bg = "red"
    elif ratio <= 0.5:
        fg = "yellow"
    else:
        fg = "green"

    return (["bold"], fg, bg)

def redraw(term):
    """
    Highlight health depending on much much is left:

        * Less than 25% - red
        * Less than 50% - yellow
        * More than 50% - green
    """

    for row in xrange(len(term.display)):
        row_str = term.display[row].encode(ENCODING)

        if "HP:" in row_str:
            match = re.search("HP:(\\d+)\\((\\d+)\\)", row_str)
            if match is not None:
                hp, hp_max = match.groups()
                ratio = float(hp) / float(hp_max)

                color = color_for_ratio(ratio)

                color_hp(row,
                         match.start() + 3,
                         match.end() - match.start() - 3,
                         color,
                         term)

