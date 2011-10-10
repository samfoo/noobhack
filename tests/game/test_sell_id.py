from noobhack.game.shops import sell_identify

def test_sucker_penalty():
    assert set([
        ("orcish dagger", 1, 12, "crude dagger")
    ]) == sell_identify("crude dagger", 1, True)

def test_appearance_identify():
    # the shop functions return both(all) the possible prices. Updated test to match
    assert set([
        ("orcish dagger", 2, 12, "crude dagger"), 
        ("orcish dagger", 1, 12, "crude dagger")
    ]) == sell_identify("crude dagger", 2)

def test_random_markdown():
    assert set([
        ("death", 125, 5, None), 
        ("wishing", 125, 5, None)
    ]) == sell_identify("wand", 125)
