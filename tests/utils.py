from noobhack.game.mapping import Level

def level_chain(size, branch, start_at=1):
    def link(first, second):
        first.add_stairs(second, (first.dlvl, second.dlvl))
        second.add_stairs(first, (second.dlvl, first.dlvl))
        return second

    levels = [Level(i, branch) for i in xrange(start_at, size + start_at)]
    reduce(link, levels)
    return levels

class MemoryPad:
    def __init__(self):
        self.buf = []

    def chgat(self, *args):
        pass

    def addstr(self, y_offset, x_offset, text):
        if len(self.buf) <= y_offset:
            self.buf.extend([""] * (y_offset - len(self.buf) + 1))
        line = self.buf[y_offset]
        if len(line) <= (x_offset + len(text)):
            line += " " * ((x_offset + len(text)) - len(line))
        line = line[:x_offset] + text + line[x_offset+len(text):]
        self.buf[y_offset] = line

    def __str__(self):
        return "\n".join(self.buf) 

