"""
The brain manages events from the game. Other classes are responsible for 
consuming and processing those events in an intelligent way.
"""

import re

import vt102

import ui 
import game.status
import game.sounds

from game.events import dispatcher

class Brain:
    """
    GrraaAAaaaAaaaa... braaaAAaaains...
    """

    def __init__(self, output_proxy):
        # Create an in-memory terminal screen and register it's stream
        # processor with the output proxy.
        self.stream = vt102.stream()

        self.term = vt102.screen(ui.size())
        self.term.attach(self.stream)
        output_proxy.register(self.stream.process)
        output_proxy.register(self.process)

        self.turn = 0
        self.dlvl = 0
        self.prev_cursor = (0, 0)

    def _dispatch_level_feature_events(self, data):
        for feature, messages in game.sounds.messages.iteritems():
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

        for name, messages in game.status.messages.iteritems():
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
        if 2 < self.dlvl <= 5:
            # Gnomish Mines:
            #
            # Since we don't get a message about being in the mines, we have to
            # guess whether we're in the mines or not. There are some features
            # unique to the mines that we can use to make a pretty educated
            # guess that we're there. First, the walls are irregular in the 
            # mines.
            #
            # e.g.
            #
            #     --   or  --  
            #    --         --
            # 
            # Would indicate that we're in the mines.

            def indices(row):
                # Find the indices of all double dashes in the string.
                found = []
                i = 0
                try:
                    while True: 
                        occurance = row.index("--", i)
                        found.append(occurance)
                        i = occurance + 1
                except ValueError:
                    pass

                return found

            def looks_like_mines(first, second):
                for index in first:
                    for other_index in second:
                        if index == other_index + 1 or \
                           other_index == index + 1 or \
                           index == other_index + 2 or \
                           other_index == index + 2:
                            return True
                return False

            scanned = [indices(row) for row in self.term.display]
            for i in xrange(len(scanned)):
                if i + 1 == len(scanned):
                    break
                above, below = scanned[i], scanned[i+1]
                if looks_like_mines(above, below):
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
        match = re.search(game.shops.entrance, data, re.I | re.M)
        if match is not None:
            shop_type = match.groups()[1]
            for t, info in game.shops.types.iteritems():
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
