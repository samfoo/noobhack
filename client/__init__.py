import json
import socket 
import select

import player

class Disconnected(Exception):
    pass

class Client:
    BUF_SIZE = 2048

    def __init__(self, host="localhost", port=31337):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client.connect((host, port))

        self.buffer = ""
        self.events = {}

    def add_event_listener(self, name, pattern, callback, data):
        if not self.events.has_key(pattern):
            self.events[name] = []

        self.events[name].append({"callback": callback, "data": data})

        command = {"name": name, "pattern": pattern}
        self.client.send(json.dumps(command) + "\r\n")

    def _read(self):
        recvd = self.client.recv(Client.BUF_SIZE)
        if len(recvd) == 0:
            raise Disconnected()

        self.buffer += recvd 

        print self.buffer

        # If what we received didn't end in a newline, then it's not a complete
        # command yet. Make sure that for the commands we're processing, we
        # don't try to deserialize incomplete commands.
        remains = ""
        lines = self.buffer.split("\r\n")
        if not self.buffer.endswith("\r\n"):
            remains = lines[-1]
            lines = lines[:-1]

        self.buffer = remains
        return [json.loads(l) for l in lines if l != ""]

    def _execute(self, queue):
        for message in queue:
            if message.has_key("callback"):
                event = message["callback"]
                for listener in self.events.get(event, []):
                    listener["callback"](event, message["data"], listener["data"])

    def _ready(self):
        self.client.send(json.dumps({"ready": "django"}) + "\r\n")

    def start(self):
        self._ready()
        try:
            while True:
                available = select.select([self.client.fileno()], [], [])[0]
                self._execute(self._read())
        except Disconnected:
            print "Server disconnected."

if __name__ == "__main__":
    client = Client()
    p = player.Player(client)
    client.start()
