from flexmock import flexmock 

from noobhack.ui.minimap import Minimap
from noobhack.game.mapping import Level, Branch

def expect_dlvl_at_index(dlvl, index, branch):
    m = Minimap()
    indices, _ = m.unconnected_branch_as_buffer_with_indices("", branch)
    assert indices[dlvl] == index

def expect(branch, results):
    m = Minimap()
    _, buf = m.unconnected_branch_as_buffer_with_indices("Dungeons of Doom", branch)
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

def test_a_branch_with_only_a_single_level_can_reference_that_level_at_the_right_index():
    levels = [Level(1)]
    expect_dlvl_at_index(1, 3, levels)

def test_a_branch_with_disconnected_levels_has_the_furthest_at_the_right_index():
    levels = [Level(1), Level(5)]
    expect_dlvl_at_index(5, 8, levels)

def test_a_branch_with_multiple_adjacent_levels_has_the_furthest_at_the_right_index():
    levels = [Level(1), Level(2), Level(3)]
    expect_dlvl_at_index(3, 9, levels)
