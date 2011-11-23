import curses

from flexmock import flexmock

from noobhack.ui.common import size
from noobhack.ui.minimap import Minimap
from noobhack.game.mapping import Level, Map

from tests.utils import level_chain, MemoryPad

def get_color(_):
    return 0

def fixed_graph(levels=None):
    if levels is None:
        levels = level_chain(5, "main")
    dmap = Map(levels[0], 0, 0)
    dmap.levels = set(levels)
    return dmap

def newpad():
    pad = flexmock(MemoryPad())
    return pad

def test_color_doesnt_color_the_ellipsis():
    window = newpad()
    window.should_receive("chgat").times(3)

    m = Minimap()
    dungeon = fixed_graph()
    dungeon.current = [l for l in dungeon.levels if l.dlvl == 5][0]
    m.draw_dungeon(dungeon, window, 0, 0, get_color)

def test_color_only_the_text_not_the_border():
    window = newpad()
    window.should_receive("chgat").with_args(3, 1, 25, curses.A_BOLD | 0).times(1)
    window.should_receive("chgat").with_args(4, 1, 25, curses.A_BOLD | 0).times(1)
    window.should_receive("chgat").with_args(5, 1, 25, curses.A_BOLD | 0).times(1)

    m = Minimap()
    dungeon = fixed_graph()
    m.draw_dungeon(dungeon, window, 0, 0, get_color)

def test_drawing_the_graph_draws_the_current_level_in_a_different_color():
    window = newpad() 
    window.should_receive("chgat").times(3)

    m = Minimap()
    dungeon = fixed_graph()
    m.draw_dungeon(dungeon, window, 0, 0, get_color)

def test_drawing_a_graph_with_multiple_branches_colors_a_current_level_on_the_main_branch():
    levels = level_chain(3, "main")
    levels[1].change_branch_to("mines")

    window = newpad() 
    window.should_receive("chgat").with_args(3, 1, 25, curses.A_BOLD | 0).times(1)
    window.should_receive("chgat").with_args(4, 1, 25, curses.A_BOLD | 0).times(1)
    window.should_receive("chgat").with_args(5, 1, 25, curses.A_BOLD | 0).times(1)

    m = Minimap()
    dungeon = fixed_graph(levels)
    m.draw_dungeon(dungeon, window, 0, 0, get_color)

def test_drawing_a_graph_with_multiple_branches_colors_a_current_level_off_the_main_branche():
    levels = level_chain(3, "main")
    levels[1].change_branch_to("mines")

    window = newpad() 
    window.should_receive("chgat").with_args(5, 31, 25, curses.A_BOLD | 0).times(1)
    window.should_receive("chgat").with_args(6, 31, 25, curses.A_BOLD | 0).times(1)
    window.should_receive("chgat").with_args(7, 31, 25, curses.A_BOLD | 0).times(1)

    m = Minimap()
    dungeon = fixed_graph(levels)
    dungeon.current = levels[1]
    m.draw_dungeon(dungeon, window, 0, 0, get_color)

