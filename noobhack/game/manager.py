import re

from noobhack.game.graphics import ibm
from noobhack.game import shops, status, intrinsics, sounds, dungeon, save, player

class Manager:
    def __init__(self, term, output_proxy, input_proxy, events):
        self.term = term
        output_proxy.register(self.process)

        self.last_move = None
        self.turn = 0
        self.dlvl = 0
        self.prev_cursor = (0, 0)
        self.events = events

        self.stats = {"St": None, "Dx": None, "Co": None, "In": None,
                      "Wi": None, "Ch": None}

        self.player = player.Player(self.events)
        self.dungeon = dungeon.Dungeon(self.events)

        self.player.listen()
        self.dungeon.listen()

    def sucker(self):
        """
        Return whether or not the player is considered a 'sucker'. A level 14
        or lower tourists or anyone wearing a shirt with no armor or cloak over
        it. Confers a 33% penalty to the price of an object. Necessary when
        price identifying.
        """
        return False

    def _level_feature_events(self, data):
        match = re.search("There is an altar to .* \\((\\w+)\\) here.", data)
        if match is not None:
            self.events.dispatch("feature-found", "altar (%s)" % match.groups()[0])

        match = re.search("a (large box)|(chest).", data)
        if match is not None:
            self.events.dispatch("feature-found", "chest")

        for feature, messages in sounds.messages.iteritems():
            for message in messages:
                match = re.search(message, data, re.I | re.M)
                if match is not None:
                    self.events.dispatch("feature-found", feature)

    def _intrinsic_events(self, data):
        for name, messages in intrinsics.messages.iteritems():
            for message, value in messages.iteritems():
                match = re.search(message, data, re.I | re.M)
                if match is not None:
                    self.events.dispatch("intrinsic-changed", name, value)

    def _status_events(self, data):
        """
        Check the output stream for any messages that might indicate a status
        change event. If such a message is found, then dispatch a status event
        with the name of the status and it's value (either True or False).
        """

        for name, messages in status.messages.iteritems():
            for message, value in messages.iteritems():
                match = re.search(message, data, re.I | re.M)
                if match is not None:
                    self.events.dispatch("status-changed", name, value)

    def _content(self):
        return [line.translate(ibm) for line
                in self.term.display
                if len(line.strip()) > 0]

    def _get_last_line(self):
        # The last line in the display is the one that contains the turn
        # information.
        for i in xrange(len(self.term.display)-1, -1, -1):
            line = self.term.display[i].translate(ibm).strip()
            if len(line) > 0:
                break
        return line

    def _branch_change_event(self, data):
        level = [line.translate(ibm) for line in self.term.display]
        if 6 <= self.dlvl <= 10 and dungeon.looks_like_sokoban(level):
            # If the player arrived at a level that looks like sokoban, she's
            # definitely in sokoban.
            self.events.dispatch("branch-changed", "sokoban")
        elif self.last_move == "down" and 3 <= self.dlvl <= 6 and \
           dungeon.looks_like_mines(level):
            # The only entrace to the mines is between levels 3 and 5 and
            # the player has to have been traveling down to get there. Also
            # count it if the dlvl didn't change, because it *might* take
            # a couple turns to identify the mines. Sokoban, by it's nature
            # however is instantly identifiable.
            self.events.dispatch("branch-changed", "mines")

    def _level_change_event(self, data):
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
                self.events.dispatch(
                    "level-changed", dlvl,
                    self.prev_cursor, self.term.cursor()
                )
                return

        # Couldn't find the dlvl line... this means we're somewhere outside
        # of the dungeon. Either in the end game, ft. ludios or in your quest.
        match = re.search("Home (\\d+)", line)
        if match is not None:
            dlvl = int(match.groups()[0])
            self.dlvl = dlvl + self.dlvl - 1
            if dlvl == 1:
                self.events.dispatch("branch-port", "quest")
            else:
                self.events.dispatch(
                    "level-changed", self.dlvl,
                    self.prev_cursor, self.term.cursor()
                )
            return

        match = re.search("Fort Ludios", line)
        if match is not None:
            self.events.dispatch("branch-port", "ludios")
            return

    def _level_teleport_event(self, data):
        for message in dungeon.messages["level-teleport"]:
            match = re.search(message, data)
            if match is not None:
                self.events.dispatch("level-teleported")

    def _trap_door_event(self, data):
        for message in dungeon.messages["trap-door"]:
            match = re.search(message, data)
            if match is not None:
                self.events.dispatch("trap-door-fell")

    def _turn_change_event(self, data):
        """
        Dispatch an even each time a turn advances.
        """

        line = self._get_last_line()
        match = re.search("T:(\\d+)", line)
        if match is not None:
            turn = int(match.groups()[0])
            if turn != self.turn:
                self.turn = turn
                self.events.dispatch("turn", self.turn)

    def _shop_entered_event(self, data):
        match = re.search(shops.entrance, data, re.I | re.M)
        if match is not None:
            shop_type = match.groups()[1]
            for t, _ in shops.types.iteritems():
                match = re.search(t, shop_type, re.I)
                if match is not None:
                    self.events.dispatch("shop-entered", t)

    def _move_event(self, data):
        if self.cursor_is_on_player():
            self.events.dispatch("moved", self.term.cursor())

    def cursor_is_on_player(self):
        """ Return whether or not the cursor is currently on the player. """

        first = self.term.display[0].translate(ibm)
        return \
            "To what position do you want to be teleported?" not in first and \
            "Please move the cursor to an unknown object." not in first and \
            self.char_at(*self.term.cursor()) != " "

    def char_at(self, x, y):
        """ Return the glyph at the specified coordinates """
        row = self.term.display[y].translate(ibm)
        col = row[x]

        return col

    def save(self, save_file):
        save.save(save_file, self.player, self.dungeon)

    def load(self, save_file):
        self.player, self.dungeon = save.load(save_file)
        self.player.events = self.events
        self.dungeon.events = self.events

        self.player.listen()
        self.dungeon.listen()

    def _parse_stats(self, data):
        results = {}
        for st in ["Ch", "St", "Dx", "Co", "Wi", "In"]:
            match = re.search("%s:(\\d+)" % st, data)
            if match is not None:
                results[st] = int(match.groups()[0])

        return results

    def _stats_changed_event(self, data):
        stats = self._parse_stats(data)
        dicts = [stats, self.stats]

        changes = dict(set.difference(*(set(d.iteritems()) for d in dicts)))

        if len(changes) > 0:
            self.events.dispatch(
                "stats-changed",
                changes
            )

    def process(self, data):
        self._stats_changed_event(data)
        self._status_events(data)
        self._intrinsic_events(data)
        self._turn_change_event(data)
        self._trap_door_event(data)
        self._level_change_event(data)
        self._level_feature_events(data)
        self._branch_change_event(data)
        self._shop_entered_event(data)
        self._move_event(data)

        if "--More--" not in self.term.display[self.term.cursor()[1]]:
            self.prev_cursor = self.term.cursor()

