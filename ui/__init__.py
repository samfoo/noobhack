import sys
import curses

import util

class container:
    screen = None

class buffer:
    game = ""

    @staticmethod
    def update_game_buffer(dungeon, output_from_game, matches):
        buffer.game += output_from_game
        height, width = util.tty_size()

        # Keep a buffer of four times the size of the screen. Hopefully this is
        # small enough that we don't run out of memory, but big enough that
        # everything will be displayed to the screen (including command 
        # characters).
        max_buf_size = height * width * 4
        if len(buffer.game) > max_buf_size:
            buffer.game = buffer.game[:max_buf_size]

class info:
    @staticmethod
    def display():
        container.screen = curses.initscr()
        curses.noecho()
        curses.cbreak()
        curses.start_color()
        container.screen.clear()
        container.screen.refresh()

    @staticmethod
    def undisplay():
        container.screen.clear()
        container.screen.refresh()
        curses.reset_shell_mode()
        container.screen = None
        sys.stdout.write(buffer.game)
        sys.stdout.flush()

def is_displayed():
    return container.screen != None
    
def toggle_display():
    if container.screen is not None:
        info.undisplay()
    else:
        info.display()
        
