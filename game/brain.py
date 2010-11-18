"""
The brain manages events from the game. Other classes are responsible for 
consuming and processing those events in an intelligent way.
"""

import re

import vt102

import ui 
import game.status

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
                    dispatcher.dispatch("status", name=name, value=value)

    def _dispatch_turn_change_event(self):
        """
        Dispatch an even each time a turn advances.
        """

        # The last line in the display is the one that contains the turn
        # information.
        for i in xrange(len(self.term.display)-1, -1, -1):
            line = self.term.display[i].strip()
            if len(line) > 0:
                break

        match = re.search("T:(\\d+)", line)
        if match is not None:
            turn = int(match.groups()[0])
            if turn != self.turn:
                self.turn = turn
                dispatcher.dispatch("turn", value=self.turn)

    def process(self, data):
        self._dispatch_status_events(data)
        self._dispatch_turn_change_event()
