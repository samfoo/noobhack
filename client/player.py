import status

class Player:
    def __init__(self, client):
        self.client = client
        self.status = set() 

        self._setup_status_listeners()

    def _status_handler(self, name, _, data):
        for name, value in data.iteritems():
            if name in self.status and value == False:
                self.status.remove(name)
            elif name not in self.status and value == True:
                self.status.add(name)

    def _setup_status_listeners(self):
        for name, messages in status.messages.iteritems():
            for pattern, value in messages.iteritems():
                self.client.add_event_listener(
                    "status", 
                    pattern, 
                    self._status_handler, 
                    {name: value}
                )
