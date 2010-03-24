import sys
import curses
import termios
import fcntl
import struct

def tty_size():
    s = struct.pack("HHHH", 0, 0, 0, 0)
    size = fcntl.ioctl(sys.stdout.fileno(), termios.TIOCGWINSZ, s)
    return struct.unpack("HHHH", size)[:2]

class container:
    screen = None
    displaying = False

class buffer:
    game = ""

    @staticmethod
    def update_game_buffer(dungeon, output_from_game, matches):
        buffer.game += output_from_game
        height, width = tty_size()

        # Keep a buffer of four times the size of the screen. Hopefully this is
        # small enough that we don't run out of memory, but big enough that
        # everything will be displayed to the screen (including command 
        # characters).
        max_buf_size = height * width * 4
        if len(buffer.game) > max_buf_size:
            buffer.game = buffer.game[:max_buf_size]

def display():
    container.screen = curses.initscr()
    curses.noecho()
    curses.cbreak()
    curses.start_color()
    container.screen.clear()
    container.screen.refresh()

def undisplay():
    curses.reset_shell_mode()
    container.screen = None
    sys.stdout.write(buffer.game)
    sys.stdout.flush()
    
def toggle_display():
    if container.screen is not None:
        undisplay()
    else:
        display()
        
