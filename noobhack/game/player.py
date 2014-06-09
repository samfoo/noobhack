class Player:
    """
    The player keeps track of various player states that are helpful to know
    but either not displayed in the nethack UI or displayed with less
    information than we might be able to infer about it.
    """

    def __init__(self, events):
        self.status = set()
        self.intrinsics = set()
        self.events = events

    def __getstate__(self):
        d = self.__dict__.copy()
        del d['events']
        return d

    def listen(self):
        self.events.listen("status-changed", self._status_changed)
        self.events.listen("intrinsic-changed", self._intrinsic_changed)

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
