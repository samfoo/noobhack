"""
The brain manages events from the game. Other classes are responsible for 
consuming and processing those events in an intelligent way.
"""

import re

import vt102

import noobhack

from noobhack.game import shops, status, sounds, dungeon
from noobhack.game.events import dispatcher

class Brain:
    """
    GrraaAAaaaAaaaa... braaaAAaaains...
    """

    def __init__(self, output_proxy):
        # Create an in-memory terminal screen and register it's stream
        # processor with the output proxy.
        self.stream = vt102.stream()

        self.term = vt102.screen(noobhack.ui.size())
        self.term.attach(self.stream)
        output_proxy.register(self.stream.process)
        output_proxy.register(self.process)

        self.turn = 0
        self.dlvl = 0
        self.prev_cursor = (0, 0)

    def _dispatch_level_feature_events(self, data):
        match = re.search("There is an altar to \\w+ \\((\\w+)\\) here.", data)
        if match is not None:
            dispatcher.dispatch("level-feature", "altar (%s)" % match.groups()[0])

        for feature, messages in sounds.messages.iteritems():
            for message in messages:
                match = re.search(message, data, re.I | re.M)
                if match is not None:
                    dispatcher.dispatch("level-feature", feature)

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

    def _get_last_line(self):
        # The last line in the display is the one that contains the turn
        # information.
        for i in xrange(len(self.term.display)-1, -1, -1):
            line = self.term.display[i].strip()
            if len(line) > 0:
                break
        return line

    def _dispatch_branch_change_event(self):
        if 2 < self.dlvl <= 5 and dungeon.looks_like_mines(self.term.display):
            dispatcher.dispatch("branch-change", "mines")

    def _dispatch_level_change_event(self):
        line = self._get_last_line()
        match = re.search("Dlvl:(\\d+)", line)
        if match is not None:
            dlvl = int(match.groups()[0])
            if dlvl != self.dlvl:
                self.dlvl = dlvl
                dispatcher.dispatch("level-change", dlvl, self.prev_cursor, self.term.cursor())

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
            for t, info in shops.types.iteritems():
                match = re.search(t, shop_type, re.I)
                if match is not None:
                    dispatcher.dispatch("shop-type", t)

    def process(self, data):
        """
        Callback attached to the output proxy.
        """

        self._dispatch_status_events(data)
        self._dispatch_turn_change_event()
        self._dispatch_level_change_event()
        self._dispatch_level_feature_events(data)
        self._dispatch_branch_change_event()
        self._dispatch_shop_entered_event(data)

        self.prev_cursor = self.term.cursor()
