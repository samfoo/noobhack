from noobhack.game.mapping import Level

def level_chain(size, branch, start_at=1):
    def link(first, second):
        first.add_stairs(second, (0, 0))
        second.add_stairs(first, (0, 0))
        return second

    levels = [Level(i, branch) for i in xrange(start_at, size + start_at)]
    reduce(link, levels)
    return levels

__test__ = True 
