import curses

from flexmock import flexmock

from noobhack.ui.common import size
from noobhack.ui.minimap import Minimap
from noobhack.game.mapping import Level, Map

from tests.utils import level_chain, MemoryPad

def get_color(_):
    return 0

def graph(levels=None):
    if levels is None:
        levels = level_chain(5, "main")
    dmap = Map(levels[0], 0, 0)
    dmap.levels = set(levels)
    return dmap

def expect(dungeon, results):
    m = Minimap()
    pad = flexmock(MemoryPad())
    pad.should_receive("chgat")
    m.draw_dungeon(dungeon, pad, 0, 0, get_color)
    print pad
    assert results == pad.buf

def test_drawing_a_graph_with_mines():
    levels = level_chain(3, "main")
    levels[1].change_branch_to("mines")

    dungeon = graph(levels)
    expect(dungeon, [
        ".-------------------------.",
        "| main                    |",
        "|=========================|   .-------------------------.",
        "| Level 1:                |\  | mines                   |",
        "|   (nothing interesting) | \ |=========================|",
        "|                         |  *| Level 2:                |",
        "' ...                     '   |   (nothing interesting) |",
        "                              |                         |",
        "                              | Level 3:                |",
        "                              |   (nothing interesting) |",
        "                              |                         |",
        "                              ' ...                     '",
    ])

def test_drawing_a_graph_with_mines_and_a_parallel_main():
    levels = level_chain(4, "main")
    levels[1].change_branch_to("mines")
    more_main = level_chain(3, "main", 2)
    more_main[0].add_stairs(levels[0], (5, 5))
    levels[0].add_stairs(more_main[0], (5, 5))

    dungeon = graph(levels + more_main)
    expect(dungeon, [
        ".-------------------------.",
        "| main                    |",
        "|=========================|   .-------------------------.",
        "| Level 1:                |\  | mines                   |",
        "|   (nothing interesting) | \ |=========================|",
        "|                         |  *| Level 2:                |",
        "| Level 2:                |   |   (nothing interesting) |",
        "|   (nothing interesting) |   |                         |",
        "|                         |   | Level 3:                |",
        "| Level 3:                |   |   (nothing interesting) |",
        "|   (nothing interesting) |   |                         |",
        "|                         |   | Level 4:                |",
        "| Level 4:                |   |   (nothing interesting) |",
        "|   (nothing interesting) |   |                         |",
        "|                         |   ' ...                     '",
        "' ...                     '",
    ])

def test_drawing_a_graph_with_mines_that_have_a_branch_themselves():
    levels = level_chain(4, "main")
    levels[1].change_branch_to("mines")
    levels[2].change_branch_to("other")
    more_main = level_chain(3, "main", 2)
    more_main[0].add_stairs(levels[0], (5, 5))
    levels[0].add_stairs(more_main[0], (5, 5))

    dungeon = graph(levels + more_main)
    expect(dungeon, [
        ".-------------------------.",
        "| main                    |",
        "|=========================|   .-------------------------.",
        "| Level 1:                |\  | mines                   |",
        "|   (nothing interesting) | \ |=========================|   .-------------------------.",
        "|                         |  *| Level 2:                |\  | other                   |",
        "| Level 2:                |   |   (nothing interesting) | \ |=========================|",
        "|   (nothing interesting) |   |                         |  *| Level 3:                |",
        "|                         |   ' ...                     '   |   (nothing interesting) |",
        "| Level 3:                |                                 |                         |",
        "|   (nothing interesting) |                                 | Level 4:                |",
        "|                         |                                 |   (nothing interesting) |",
        "| Level 4:                |                                 |                         |",
        "|   (nothing interesting) |                                 ' ...                     '",
        "|                         |",
        "' ...                     '",
    ])

def test_drawing_a_graph_with_sokoban():
    main = level_chain(3, "main")
    sokoban = level_chain(2, "sokoban")

    main[2].add_stairs(sokoban[-1], (1, 1))
    sokoban[-1].add_stairs(main[2], (2, 2))

    dungeon = graph(main + sokoban)
    expect(dungeon, [
        ".-------------------------.",
        "| main                    |",
        "|=========================|   .-------------------------.",
        "| Level 1:                |   | sokoban                 |",
        "|   (nothing interesting) |   |=========================|",
        "|                         |   | Level 2:                |",
        "| Level 2:                |   |   (nothing interesting) |",
        "|   (nothing interesting) |  *|                         |",
        "|                         | / '-------------------------'",
        "| Level 3:                |/",
        "|   (nothing interesting) |",
        "|                         |",
        "' ...                     '",
    ])
