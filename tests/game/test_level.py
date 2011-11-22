import sys
from noobhack.game.mapping import Level

from tests.utils import level_chain

def test_changing_branches_changes_my_branch():
    l = Level(1, "main")
    l.change_branch_to("mines")
    assert l.branch == "mines"

def test_changing_branches_changes_my_childrens_branch():
    levels = level_chain(3, "main")
    levels[0].change_branch_to("mines")

    assert all(l.branch == "mines" for l in levels)

def test_changing_branches_changes_only_those_levels_that_are_below_the_branch_that_changed():
    levels = level_chain(5, "main")
    levels[1].change_branch_to("mines")

    assert all(l.branch == "mines" for l in levels if l.dlvl > 1)
    assert levels[0].branch == "main"

def test_level_with_branch_has_a_branch():
    levels = level_chain(2, "main")
    levels[1].change_branch_to("mines")
    first = levels[0]

    assert first.has_a_branch() == True
    assert first.branches() == [levels[1]]

def test_level_with_no_children_doesnt_have_a_branch():
    l = Level(1, "main")

    assert l.has_a_branch() == False

def test_level_with_only_one_child_that_doesnt_have_a_branch_has_no_branch():
    levels = level_chain(2, "main")
    first = levels[0]

    assert first.has_a_branch() == False

def test_changing_branch_to_sokoban_doesnt_change_children_branches():
    levels = level_chain(5, "main")
    sokoban = Level(3)
    levels[4].add_stairs(sokoban, (3, 3))
    sokoban.add_stairs(levels[4], (4, 4))
    sokoban.change_branch_to("sokoban")

    assert sokoban.branch == "sokoban"
    assert levels[4].branch == "main"

def test_is_a_junction_when_there_are_two_children():
    main = level_chain(2, "main")
    mines = level_chain(2, "mines", start_at=2)
    main[0].add_stairs(mines[0], (2, 2))
    mines[0].add_stairs(main[0], (1, 1))
    
    assert main[0].is_a_junction()

def test_is_not_a_junction_when_there_is_only_one_child():
    main = level_chain(2, "main")

    assert not main[0].is_a_junction()

def test_a_level_with_a_parent_and_a_child_is_not_a_junction():
    main = level_chain(3, "main")

    assert not main[1].is_a_junction()

def test_a_level_with_two_parents_is_a_junction():
    main = level_chain(3, "main")
    sokoban = level_chain(2, "sokoban")

    main[2].add_stairs(sokoban[-1], (1, 1))
    sokoban[-1].add_stairs(main[2], (2, 2))

    assert main[2].is_a_junction()
