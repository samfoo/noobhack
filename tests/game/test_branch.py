from noobhack.game.mapping import Branch

from tests.utils import level_chain

def test_single_level_chain_has_no_branches():
    levels = level_chain(5, "main")
    branch = Branch(levels[0])
    assert branch.sub_branches() == []

def test_single_level_chain_finds_start_when_initialized_with_middle_level():
    levels = level_chain(5, "main")
    branch = Branch(levels[3])
    assert branch.start == levels[0]

def test_complex_map_finds_start_of_sub_branch_when_initialized_with_middle_level():
    levels = level_chain(4, "main")
    levels[1].change_branch_to("mines")

    more_main = level_chain(3, "main", 2)
    more_main[0].add_stairs(levels[0], (5, 5))
    levels[0].add_stairs(more_main[0], (5, 5))

    sokoban = level_chain(2, "sokoban", 2)
    more_main[-1].add_stairs(sokoban[-1], (1, 1))
    sokoban[-1].add_stairs(more_main[-1], (2, 2))

    branch = Branch(levels[2])
    assert branch.start == levels[1]

def test_level_chain_with_one_junction_should_have_one_subbranch():
    levels = level_chain(5, "main")
    levels[1].change_branch_to("mines")
    assert levels[0].has_a_branch() == True
    branch = Branch(levels[0])
    assert len(branch.sub_branches()) == 1

def test_level_chain_with_two_junctions_has_two_subbranches():
    levels = level_chain(4, "main")
    levels[1].change_branch_to("mines")

    more_main = level_chain(3, "main", 2)
    more_main[0].add_stairs(levels[0], (5, 5))
    levels[0].add_stairs(more_main[0], (5, 5))

    sokoban = level_chain(2, "sokoban", 2)
    more_main[-1].add_stairs(sokoban[-1], (1, 1))
    sokoban[-1].add_stairs(more_main[-1], (2, 2))

    branch = Branch(levels[0])
    assert len(branch.sub_branches()) == 2
