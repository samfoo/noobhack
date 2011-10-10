from noobhack.game.mapping import Level

def level_chain(size, branch):
    def link(first, second):
        first.add_stairs(second, (0, 0))
        second.add_stairs(first, (0, 0))
        return second

    levels = [Level(i, branch) for i in xrange(1, size + 1)]
    reduce(link, levels)
    return levels

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

def test_changing_branch_to_sokoban_doesnt_change_children_branches():
    levels = level_chain(5, "main")
    sokoban = Level(3)
    levels[4].add_stairs(sokoban, (3, 3))
    sokoban.add_stairs(levels[4], (4, 4))
    sokoban.change_branch_to("sokoban")

    assert sokoban.branch == "sokoban"
    assert levels[4].branch == "main"
