import socket 
import json

import commands

class Server:
    BUF_SIZE = 2048

    def __init__(self, output_proxy, input_proxy, host="", port=31337):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        self.socket.bind((host, port))
        self.socket.listen(1)
        self.buffer = "" 
        self.client = None

        self.output_proxy = output_proxy
        self.input_proxy = input_proxy

    def fileno(self):
        return self.socket.fileno()

    def accept(self):
        conn, addr = self.socket.accept()

        if self.client != None:
            conn.send("There's already a client connected to this server")
            conn.close()
        else:
            self.client = conn 

            return (self.client, addr)

    def close(self):
        if self.client is not None:
            self.terminate("Server is quitting.\r\n")

        self.socket.close()

    def terminate(self, msg):
        try:
            self.client.send(msg)
        except socket.error, e:
            # Oh well, nothing to do if the client hung up unexpectadly
            pass

        self.client.close()

        self.client = None
        commands.unhandle(self)

    def _read(self):
        self.buffer += self.client.recv(Server.BUF_SIZE)

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
        # Loop through commands in a queue an execute them.
        for command in queue: 
            commands.handle(self, command)

    def process(self):
        try:
            self._execute(self._read())
        except ValueError, e:
            # If for some reason a command fails, let the client know why and
            # then close the connection.
            return self.terminate("Invalid command '%s'.\r\n" % e, self.client)
