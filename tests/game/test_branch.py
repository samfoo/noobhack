from noobhack.game.mapping import Branch

from tests.utils import level_chain

def test_single_level_chain_has_no_branches():
    levels = level_chain(5, "main")
    branch = Branch(levels[0])
    assert branch.sub_branches() == []

def test_level_chain_with_one_junction_should_have_one_subbranch():
    levels = level_chain(5, "main")
    levels[1].change_branch_to("mines")
    assert levels[0].has_a_branch() == True
    branch = Branch(levels[0])
    assert len(branch.sub_branches()) == 1
