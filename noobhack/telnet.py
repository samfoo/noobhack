import os
import telnetlib

class Telnet:
    """
    Runs and manages the input/output of a remote nethack game. The class 
    implements a telnet client in as much as the python telnetlib makes that
    possible (grumble, grumble, grumble).
    """

    def __init__(self, host="nethack.alt.org", port=23):
        self.host = host
        self.port = port
        self.conn = None

    def write(self, buf):
        self.conn.get_socket().send(buf)

    def read(self):
        return self.conn.read_very_eager()

    def open(self):
        self.conn = telnetlib.Telnet(self.host, self.port)
        self.conn.set_option_negotiation_callback(self.set_option)

    def close(self):
        self.conn.close()

    def fileno(self):
        return self.conn.get_socket().fileno()

    def set_option(self, socket, command, option):
        if command == telnetlib.DO and option == "\x18":
            # Promise we'll send a terminal type
            socket.send("%s%s\x18" % (telnetlib.IAC, telnetlib.WILL))
        elif command == telnetlib.DO and option == "\x01":
            # Pinky swear we'll echo
            socket.send("%s%s\x01" % (telnetlib.IAC, telnetlib.WILL))
        elif command == telnetlib.DO and option == "\x1f":
            # And we should probably tell the server we will send our window
            # size
            socket.send("%s%s\x1f" % (telnetlib.IAC, telnetlib.WILL))
        elif command == telnetlib.DO and option == "\x20":
            # Tell the server to sod off, we won't send the terminal speed
            socket.send("%s%s\x20" % (telnetlib.IAC, telnetlib.WONT))
        elif command == telnetlib.DO and option == "\x23":
            # Tell the server to sod off, we won't send an x-display terminal
            socket.send("%s%s\x23" % (telnetlib.IAC, telnetlib.WONT))
        elif command == telnetlib.DO and option == "\x27":
            # And we won't send the damn environmnet either (needy bastard)
            socket.send("%s%s\x27" % (telnetlib.IAC, telnetlib.WONT))
        elif self.conn.rawq == "\xff\xfa\x18\x01\xff\xf0":
            # We're being asked for the terminal type that we promised earlier
            socket.send("%s%s\x18\x00%s%s%s" % 
                        (telnetlib.IAC,
                         telnetlib.SB,
                         "vt102",
                         telnetlib.IAC,
                         telnetlib.SE))

