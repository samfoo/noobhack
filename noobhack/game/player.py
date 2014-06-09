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
        self.events.listen("status", self._status_handler)
        self.events.listen("intrinsic", self._intrinsic_handler)

    def _intrinsic_handler(self, event, name, value):
        if name in self.intrinsics and value == False:
            self.intrinsics.remove(name)
        elif name not in self.intrinsics and value == True:
            self.intrinsics.add(name)

    def _status_handler(self, event, name, value):
        if name in self.status and value == False:
            self.status.remove(name)
        elif name not in self.status and value == True:
            self.status.add(name)
