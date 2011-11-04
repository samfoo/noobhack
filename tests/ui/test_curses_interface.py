import curses

from flexmock import flexmock

import noobhack.ui.common
from noobhack.ui.common import get_color
from noobhack.ui.minimap import Minimap
from noobhack.game.mapping import Level, Map

def fixed_graph():
    levels = level_chain(5, "main")
    return Map(levels[0], 0, 0)

def level_chain(size, branch, start_at=1):
    def link(first, second):
        first.add_stairs(second, (0, 0))
        second.add_stairs(first, (0, 0))
        return second

    levels = [Level(i, branch) for i in xrange(start_at, size + start_at)]
    reduce(link, levels)
    return levels

def newpad():
    return flexmock(None)

def test_drawing_the_graph_draws_the_current_level_in_a_different_color():
    flexmock(get_color).and_return((6, 6))
    window = newpad() 
    window.should_receive("addstr")
    window.should_receive("chgat").times(1)

    m = Minimap()
    dungeon = fixed_graph()
    m.draw_dungeon(dungeon, window)
