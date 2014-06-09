import re
import curses 

from noobhack.game import shops, status
from noobhack.ui.common import get_color

class Helper:
    """
    Maintain the state of the helper UI and draw it to a curses screen when
    `redraw` is called.
    """

    intrinsic_width = 25
    status_width = 12
    level_width = 25 

    def __init__(self, manager):
        self.manager = manager

        self.player = manager.player
        self.dungeon = manager.dungeon

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

        for i in xrange(len(self.manager.term.display)-1, -1, -1):
            row = i
            line = self.manager.term.display[i].strip()
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
        line = self.manager.term.display[0]
        match = re.search(shops.offer, line, re.I)
        if match is not None:
            price = int(match.groups()[0])
            item = match.groups()[1]

            return (item, price)

        return None

    def _things_to_buy_identify(self):
        # TODO: Make sure that unpaid prices can only ever appear on the first
        # line. I might have to check the second line too.
        line = self.manager.term.display[0]
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
            if self.manager.char_at(x, y) not in [".", "#", " "]: 
                # Ignore anything that's not something we can step on.
                continue

            if self.manager.char_at(x, y) == " ":
                window.addch(y, x, ".")

            window.chgat(y, x, 1, curses.A_BOLD | get_color(curses.COLOR_MAGENTA))

        cur_x, cur_y = self.manager.term.cursor()
        window.move(cur_y, cur_x)

    def redraw(self, window, breadcrumbs=False):
        """
        Repaint the screen with the helper UI.
        """

        if self.manager.cursor_is_on_player() and breadcrumbs:
            self._breadcrumbs(window)

        if self._things_to_buy_identify() is not None:
            item, price = self._things_to_buy_identify()
            items = shops.buy_identify(self.player.charisma(), item, price, self.player.sucker())

            identify_frame = self._identify_box(items)
            identify_frame.overwrite(window)
        elif self._things_to_sell_identify() is not None:
            item, price = self._things_to_sell_identify()
            items = shops.sell_identify(item, price, self.player.sucker())

            identify_frame = self._identify_box(items)
            identify_frame.overwrite(window)

        status_frame = self._status_box()
        dungeon_frame = self._level_box()
        intrinsic_frame = self._intrinsic_box()

        status_frame.overwrite(window)
        dungeon_frame.overwrite(window)
        intrinsic_frame.overwrite(window)

        window.noutrefresh()

