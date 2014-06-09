class Player:
    """
    The player keeps track of various player states that are helpful to know
    but either not displayed in the nethack UI or displayed with less
    information than we might be able to infer about it.
    """

    def __init__(self, events):
        self.status = set()
        self.intrinsics = set()
        self.stats = {"St": None, "Dx": None, "Co": None, "In": None,
                      "Wi": None, "Ch": None}

        self.events = events

    def intelligence(self):
        return self.stats["In"]

    def charisma(self):
        return self.stats["Ch"]

    def strength(self):
        return self.stats["St"]

    def wisdom(self):
        return self.stats["Wi"]

    def dexterity(self):
        return self.stats["Dx"]

    def constitution(self):
        return self.stats["Co"]

    def __getstate__(self):
        d = self.__dict__.copy()
        del d['events']
        return d

    def listen(self):
        self.events.listen("status-changed", self._status_changed)
        self.events.listen("intrinsic-changed", self._intrinsic_changed)
        self.events.listen("stats-changed", self._stats_changed)

    def _stats_changed(self, event, changes):
        self.stats = dict(self.stats.items() + changes.items())

    def _intrinsic_changed(self, event, name, value):
        if name in self.intrinsics and value == False:
            self.intrinsics.remove(name)

        elif name not in self.intrinsics and value == True:
            self.intrinsics.add(name)

    def _status_changed(self, event, name, value):
        if name in self.status and value == False:
            self.status.remove(name)

        elif name not in self.status and value == True:
            self.status.add(name)
