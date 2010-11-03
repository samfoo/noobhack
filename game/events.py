import re

import status 

class Queue:
    def __init__(self, dispatcher):
        self.dispatcher = dispatcher

    def _dispatch_status_event(self, name, value):
        self.dispatcher.dispatch("status", name=name, value=value)

    def process(self, data):
        for name, messages in status.messages.iteritems():
            for message, value in messages.iteritems():
                match = re.search(message, data, re.I | re.M)
                if match is not None:
                    self._dispatch_status_event(name, value)

class Dispatcher:
    def __init__(self):
        self.listeners = {}

    def add_event_listener(self, event, function):
        if not self.listeners.has_key(event):
            self.listeners[event] = []

        self.listeners[event].append(function)

    def remove_event_listener(self, event, function):
        pass

    def dispatch(self, event, **kwargs):
        for l in self.listeners.get(event, []):
            l(event, kwargs)

dispatcher = Dispatcher()
queue = Queue(dispatcher)
