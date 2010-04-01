import sys
import termios
import fcntl
import struct
import re
import os

def tty_size():
    s = struct.pack("HHHH", 0, 0, 0, 0)
    size = fcntl.ioctl(sys.stdout.fileno(), termios.TIOCGWINSZ, s)
    return struct.unpack("HHHH", size)[:2]

