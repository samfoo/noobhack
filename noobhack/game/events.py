"""
The events module is where all events based on gameplay are dispatched.
"""

class Dispatcher:
    """
    Simple event dispatcher. 
    """
    def __init__(self):
        self.listeners = {}

    def listen(self, event, function):
        """
        Add an event listener.

        :param event: string name of the event
        """

        if not self.listeners.has_key(event):
            self.listeners[event] = set() 

        self.listeners[event].add(function)

    def dispatch(self, event, *args):
        """
        Dispatch an event.
        """

        for listener in self.listeners.get(event, []):
            listener(event, *args)
