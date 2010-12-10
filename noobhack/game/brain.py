"""
The brain manages events from the game. Other classes are responsible for 
consuming and processing those events in an intelligent way.
"""

import re

from noobhack.game.graphics import ibm
from noobhack.game import shops, status, resistances, sounds, dungeon
from noobhack.game.events import dispatcher

class Brain:
    """
    GrraaAAaaaAaaaa... braaaAAaaains...
    """

    def __init__(self, term, output_proxy):
        self.term = term
        output_proxy.register(self.process)

        self.last_move = None
        self.turn = 0
        self.dlvl = 0
        self.prev_cursor = (0, 0)

    def charisma(self):
        line = self._content()[-2]
        match = re.search("Ch:(\\d+)", line)
        if match is not None:
            return int(match.groups()[0])
        return None

    def sucker(self):
        return False

    def _dispatch_level_feature_events(self, data):
        match = re.search("There is an altar to .* \\((\\w+)\\) here.", data)
        if match is not None:
            dispatcher.dispatch("level-feature", "altar (%s)" % match.groups()[0])

        match = re.search("a (large box)|(chest).", data)
        if match is not None:
            dispatcher.dispatch("level-feature", "chest")

        for feature, messages in sounds.messages.iteritems():
            for message in messages:
                match = re.search(message, data, re.I | re.M)
                if match is not None:
                    dispatcher.dispatch("level-feature", feature)

    def _dispatch_resistance_events(self, data):
        for name, messages in resistances.messages.iteritems():
            for message in messages:
                match = re.search(message, data, re.I | re.M)
                if match is not None:
                    dispatcher.dispatch("resistance", name)

    def _dispatch_status_events(self, data):
        """
        Check the output stream for any messages that might indicate a status
        change event. If such a message is found, then dispatch a status event
        with the name of the status and it's value (either True or False).
        """

        for name, messages in status.messages.iteritems():
            for message, value in messages.iteritems():
                match = re.search(message, data, re.I | re.M)
                if match is not None:
                    dispatcher.dispatch("status", name, value)

    def _content(self):
        return [line.translate(ibm) for line in self.term.display if len(line.strip()) > 0]

    def _get_last_line(self):
        # The last line in the display is the one that contains the turn
        # information.
        for i in xrange(len(self.term.display)-1, -1, -1):
            line = self.term.display[i].translate(ibm).strip()
            if len(line) > 0:
                break
        return line

    def _dispatch_branch_change_event(self):
        level = [line.translate(ibm) for line in self.term.display]
        if self.last_move == "down" and 3 <= self.dlvl <= 5 and \
           dungeon.looks_like_mines(level): 
            # The only entrace to the mines is between levels 3 and 5 and
            # the player has to have been traveling down to get there. Also
            # count it if the dlvl didn't change, because it *might* take
            # a couple turns to identify the mines. Sokoban, by it's nature
            # however is instantly identifiable. 
            dispatcher.dispatch("branch-change", "mines")
        elif self.last_move == "up" and dungeon.looks_like_sokoban(level):
            # If the player traveled up and arrived at a level that looks
            # like sokoban, she's definitely in sokoban.
            dispatcher.dispatch("branch-change", "sokoban")

    def _dispatch_level_change_event(self):
        line = self._get_last_line()
        match = re.search("Dlvl:(\\d+)", line)
        if match is not None:
            dlvl = int(match.groups()[0])
            if dlvl != self.dlvl:
                if dlvl < self.dlvl:
                    self.last_move = "up"
                elif dlvl > self.dlvl:
                    self.last_move = "down"

                self.dlvl = dlvl
                dispatcher.dispatch("level-change", dlvl, self.prev_cursor, self.term.cursor())

    def _dispatch_trap_door_event(self, data):
        for message in dungeon.messages["trap-door"]:
            match = re.search(message, data)
            if match is not None:
                dispatcher.dispatch("trap-door")

    def _dispatch_turn_change_event(self):
        """
        Dispatch an even each time a turn advances.
        """

        line = self._get_last_line()
        match = re.search("T:(\\d+)", line)
        if match is not None:
            turn = int(match.groups()[0])
            if turn != self.turn:
                self.turn = turn
                dispatcher.dispatch("turn", self.turn)

    def _dispatch_shop_entered_event(self, data):
        match = re.search(shops.entrance, data, re.I | re.M)
        if match is not None:
            shop_type = match.groups()[1]
            for t, _ in shops.types.iteritems():
                match = re.search(t, shop_type, re.I)
                if match is not None:
                    dispatcher.dispatch("shop-type", t)

    def _dispatch_move_event(self):
        if self.term.cursor() != self.prev_cursor and self.cursor_is_on_player():
            dispatcher.dispatch("move", self.term.cursor())

    def cursor_is_on_player(self):
        return self.char_at(*self.term.cursor()) == "@"

    def char_at(self, x, y):
        row = self.term.display[y].translate(ibm)
        col = row[x]

        return col

    def process(self, data):
        """
        Callback attached to the output proxy.
        """

        self._dispatch_status_events(data)
        self._dispatch_resistance_events(data)
        self._dispatch_turn_change_event()
        self._dispatch_trap_door_event(data)
        self._dispatch_level_change_event()
        self._dispatch_level_feature_events(data)
        self._dispatch_branch_change_event()
        self._dispatch_shop_entered_event(data)
        self._dispatch_move_event()

        self.prev_cursor = self.term.cursor()
