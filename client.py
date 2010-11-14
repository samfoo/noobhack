import json
import signal
import socket 
import select
import curses
import curses.wrapper

import game
import game.events
import game.player

class Disconnected(Exception):
    pass

class Client:
    BUF_SIZE = 2048

    def __init__(self, host="localhost", port=31337):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client.connect((host, port))

        self.buffer = ""
        self.events = {}

    def _read(self):
        recvd = self.client.recv(Client.BUF_SIZE)
        if len(recvd) == 0:
            raise Disconnected()

        self.buffer += recvd 

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
            if message.has_key("read"):
                game.events.queue.process(message["read"])

    def iterate(self):
        try:
            available = select.select([self.client.fileno()], [], [])[0]
            self._execute(self._read())
        except select.error, e:
            if e.args[0] != 4:
                # If the errno is '4' the error is just an interruption. Most
                # likely a signal about resizing the console window or
                # something. We can ignore those, but if it's anything else,
                # it's probably some *actual* problem that we have to die for.
                raise e

PADDING = 2 
COLORS = [curses.COLOR_RED, curses.COLOR_GREEN]
STATUS = {
    "bad": 1, 
    "good": 2 
}

def layout(screen):
    # Create two subwindows that horizontally divied the screen in two.
    height, width = screen.getmaxyx()
    half = height / 2

    # Create the top screen.
    top = curses.newwin(half, width, 0, 0)

    # Create the bottom screen.
    bottom = curses.newwin(half, width, half, 0)

    return (top, bottom)

def update_player(screen, player):
    # Rip out anything we already have. Probably not really the best way of
    # doing this, but perf isn't an issue yet.
    screen.clear()
    screen.border()
    screen.addstr(0, PADDING, " Player ")

    # Sort statuses first by their type (good, bad, neutral) and then second 
    # alphabetically. 
    def sort_statuses(left, right):
        diff = cmp(game.status.type(left), game.status.type(right))
        if diff == 0:
            diff = cmp(left, right)
        return diff

    statuses = sorted(player.status, sort_statuses) 

    for y, item in enumerate(statuses, 1): 
        type = game.status.type(item)

        attrs = [curses.A_BOLD]
        if type != "neutral":
            attrs.append(curses.color_pair(STATUS[type]))

        screen.insstr(y, PADDING, item, reduce(lambda a, b: a | b, attrs))

    screen.refresh()

def update_dungeon(screen, client):
    screen.clear()
    screen.border()
    screen.addstr(0, PADDING, " Dungeon ")

    screen.refresh()

def run(screen):
    # We prefer to let the console pick the colors for the bg/fg instead of
    # using what curses thinks looks good.
    curses.use_default_colors()

    # Initialize all the colors that we're going to use for text and use the
    # default background.
    for i, color in enumerate(COLORS, 1):
        curses.init_pair(i, color, -1) 

    # Create both player and dung
    player_win, dungeon_win = layout(screen)

    player = game.player.Player()
    client = Client()

    while True:
        update_player(player_win, player)
        update_dungeon(dungeon_win, None)
        client.iterate()

if __name__ == "__main__":
    curses.wrapper(run)

