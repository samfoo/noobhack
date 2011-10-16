from flexmock import flexmock 

from noobhack.ui.minimap import Minimap
from noobhack.game.mapping import Level, Branch

def expect(branch, results):
    m = Minimap()
    buf = m.unconnected_branch_as_buffer("Dungeons of Doom", branch)
    #for l in buf: print l
    #print "---------------"
    #for l in results: print l
    assert buf == results

def test_drawing_a_branch_draws_the_header_and_the_border():
    level = Level(1)
    expect([level], [
        ".-------------------------.",
        "| Dungeons of Doom        |",
        "|=========================|",
        "| Level 1:                |",
        "|   (nothing interesting) |",
        "|                         |",
        "' ...                     '"
    ])

def test_drawing_a_branch_with_multiple_levels_draws_all_the_levels():
    levels = [Level(1), Level(2), Level(3)]
    expect(levels, [
        ".-------------------------.",
        "| Dungeons of Doom        |",
        "|=========================|",
        "| Level 1:                |",
        "|   (nothing interesting) |",
        "|                         |",
        "| Level 2:                |",
        "|   (nothing interesting) |",
        "|                         |",
        "| Level 3:                |",
        "|   (nothing interesting) |",
        "|                         |",
        "' ...                     '"
    ])

def test_drawing_a_branch_with_multiple_levels_that_arent_monotonically_increasing_puts_an_ellipses_between_disjoins():
    levels = [Level(1), Level(5)]
    expect(levels, [
        ".-------------------------.",
        "| Dungeons of Doom        |",
        "|=========================|",
        "| Level 1:                |",
        "|   (nothing interesting) |",
        "|                         |",
        "| ...                     |",
        "|                         |",
        "| Level 5:                |",
        "|   (nothing interesting) |",
        "|                         |",
        "' ...                     '"
    ])
