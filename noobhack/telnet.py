import os
import telnetlib
from struct import pack

class Telnet:
    """
    Runs and manages the input/output of a remote nethack game. The class 
    implements a telnet client in as much as the python telnetlib makes that
    possible (grumble, grumble, grumble).
    """

    def __init__(self, host="nethack.alt.org", port=23,size=(80,24)):
        self.host = host
        self.port = port
        self.conn = None
        self.size = size

    def write(self, buf):
        """ Proxy input to the telnet process' stdin. """
        self.conn.get_socket().send(buf)

    def read(self):
        """ 
        Proxy output from the telnet process' stdout. This shouldn't block 
        """
        try:
            return self.conn.read_very_eager()
        except EOFError, ex:
            # The telnet connection closed.
            raise IOError(ex)

    def open(self):
        """ Open a connection to a telnet server.  """

        self.conn = telnetlib.Telnet(self.host, self.port)
        self.conn.set_option_negotiation_callback(self.set_option)
        self.conn.get_socket().sendall(pack(">ccc", telnetlib.IAC, telnetlib.WILL, telnetlib.NAWS))

    def close(self):
        """ Close the connection. """
        self.conn.close()

    def fileno(self):
        """ Return the fileno of the socket.  """
        return self.conn.get_socket().fileno()

    def set_option(self, socket, command, option):
        """ Configure our telnet options. This is magic. Don't touch it. """

        if command == telnetlib.DO and option == "\x18":
            # Promise we'll send a terminal type
            socket.send("%s%s\x18" % (telnetlib.IAC, telnetlib.WILL))
        elif command == telnetlib.DO and option == "\x01":
            # Pinky swear we'll echo
            socket.send("%s%s\x01" % (telnetlib.IAC, telnetlib.WILL))
        elif command == telnetlib.DO and option == "\x1f":
            # And we should probably tell the server we will send our window
            # size
            socket.sendall(pack(">cccHHcc", telnetlib.IAC, telnetlib.SB, telnetlib.NAWS, self.size[1], self.size[0], telnetlib.IAC, telnetlib.SE))
        elif command == telnetlib.DO and option == "\x20":
            # Tell the server to sod off, we won't send the terminal speed
            socket.send("%s%s\x20" % (telnetlib.IAC, telnetlib.WONT))
        elif command == telnetlib.DO and option == "\x23":
            # Tell the server to sod off, we won't send an x-display terminal
            socket.send("%s%s\x23" % (telnetlib.IAC, telnetlib.WONT))
        elif command == telnetlib.DO and option == "\x27":
            # We will send the environment, though, since it might have nethack
            # specific options in it.
            socket.send("%s%s\x27" % (telnetlib.IAC, telnetlib.WILL))
        elif self.conn.rawq.startswith("\xff\xfa\x27\x01\xff\xf0\xff\xfa"):
            # We're being asked for the environment settings that we promised
            # earlier
            socket.send("%s%s\x27\x00%s%s%s" %
                        (telnetlib.IAC,
                         telnetlib.SB,
                         '\x00"NETHACKOPTIONS"\x01"%s"' % os.environ.get("NETHACKOPTIONS", ""),
                         telnetlib.IAC,
                         telnetlib.SE))
            # We're being asked for the terminal type that we promised earlier
            socket.send("%s%s\x18\x00%s%s%s" % 
                        (telnetlib.IAC,
                         telnetlib.SB,
                         "xterm-color",
                         telnetlib.IAC,
                         telnetlib.SE))
