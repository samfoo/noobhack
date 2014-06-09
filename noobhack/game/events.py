class Dispatcher:
    def __init__(self):
        self.listeners = {}

    def listen(self, event, function):
        if not self.listeners.has_key(event):
            self.listeners[event] = set() 

        self.listeners[event].add(function)

    def dispatch(self, event, *args):
        for listener in self.listeners.get(event, []):
            listener(event, *args)
