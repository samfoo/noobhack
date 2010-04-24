import socket 
import json

class Server:
    BUF_SIZE = 2048

    def __init__(self, host="", port=31337):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        self.socket.bind((host, port))
        self.socket.listen(1)
        self.connections = []
        self.buffers = {}

    def fileno(self):
        return self.socket.fileno()

    def accept(self):
        conn, addr = self.socket.accept()

        # This shouldn't actually be necessary, but in case we some, crazy, how
        # manage to get a connection in the process method that hasn't been
        # cleared as having data available, it's best not to halt *everything*
        # with blocking anyway.
        conn.setblocking(False)

        self.connections.append(conn)
        self.buffers[conn.fileno()] = ""

        return (conn, addr)

    def close(self):
        self.socket.close()

    def terminate(self, msg, conn):
        conn.send(msg)
        self.connections.remove(conn)
        del self.buffers[conn.fileno()]
        conn.close()

    def process(self, conn):
        client_buf = self.buffers[conn.fileno()]
        client_buf += conn.recv(Server.BUF_SIZE)

        # If what we received didn't end in a newline, then it's not a complete
        # command yet. Make sure that for the commands we're processing, we
        # don't try to deserialize incomplete commands.
        remains = ""
        lines = client_buf.split("\r\n")
        if not client_buf.endswith("\r\n"):
            remains = lines[-1]
            lines = lines[:-1]

        try:
            commands = [json.loads(l) for l in lines if l != ""]

            for command in commands:
                self._process_command(conn, command)

            self.buffers[conn.fileno()] = remains
        except ValueError, e:
            # If for some reasona command fails, let the client know why and
            # then close the connection.
            return self.terminate("Invalid command '%s'.\r\n" % e, conn)

    def _process_command(self, conn, command):
        conn.send("command '%r' received\r\n" % command)
