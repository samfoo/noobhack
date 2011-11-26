"""
The events module is where all events based on gameplay are dispatched.
"""

class Dispatcher:
    """
    Simple event dispatcher. 
    """
    def __init__(self):
        self.listeners = {}

    def add_event_listener(self, event, function):
        """
        Add an event listener.

        :param event: string name of the event
        """

        if not self.listeners.has_key(event):
            self.listeners[event] = set() 

        self.listeners[event].add(function)

    def remove_event_listener(self, event, function):
        """
        Remove an event listener.

        :param event: string name of the event
        """

        if self.listeners.has_key(event):
            self.listeners[event].remove(function)

    def dispatch(self, event, *args):
        """
        Dispatch an event.
        """

        import sys
        sys.stderr.write("%s %r\n" % (event, args))

        for listener in self.listeners.get(event, []):
            listener(event, *args)

dispatcher = Dispatcher()
