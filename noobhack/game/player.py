from noobhack.game import events

class Player:
    """
    The player keeps track of various player states that are helpful to know
    but either not displayed in the nethack UI or displayed with less
    information than we might be able to infer about it.
    """

    def __init__(self):
        self.status = set() 
        self.resistances = set()

    def listen(self):
        events.dispatcher.add_event_listener("status", self._status_handler)

    def _resistance_handler(self, event, name):
        self.resistances.add(name)

    def _status_handler(self, event, name, value):
        if name in self.status and value == False:
            self.status.remove(name)
        elif name not in self.status and value == True:
            self.status.add(name)
