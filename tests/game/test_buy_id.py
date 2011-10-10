from noobhack.game.shops import buy_identify

def test_sucker_penalty():
    assert set([
        ("orcish dagger", 5, 12, "crude dagger"), 
        ("orcish dagger", 7, 12, "crude dagger")
    ]) == buy_identify(11, "crude dagger", 6, True)

def test_appearance_identify():
    assert set([
        ("orcish dagger", 5, 12, "crude dagger"), 
        ("orcish dagger", 4, 12, "crude dagger")
    ]) == buy_identify(11, "crude dagger", 4)

def test_appearch_id_with_random_markup():
    assert set([
        ("orcish dagger", 5, 12, "crude dagger"), 
        ("orcish dagger", 4, 12, "crude dagger")
    ]) == buy_identify(11, "crude dagger", 5)

def test_random_markup():
    assert set([
        ("death", 667, 5, None), 
        ("wishing", 667, 5, None)
    ]) == buy_identify(11, "wand", 666)

def test_charisma_modifier():
    assert set([
        ("death", 1000, 5, None), 
        ("wishing", 1000, 5, None)
    ]) == buy_identify(5, "wand", 1000)

    assert set([
        ("death", 750, 5, None), 
        ("wishing", 750, 5, None)
    ]) == buy_identify(6, "wand", 750)

    assert set([
        ("death", 667, 5, None), 
        ("wishing", 667, 5, None)
    ]) == buy_identify(8, "wand", 666)

    assert set([
        ("death", 500, 5, None), 
        ("wishing", 500, 5, None)
    ]) == buy_identify(11, "wand", 500)

    assert set([
        ("death", 375, 5, None), 
        ("wishing", 375, 5, None)
    ]) == buy_identify(16, "wand", 375)

    assert set([
        ("death", 333, 5, None), 
        ("wishing", 333, 5, None)
    ]) == buy_identify(18, "wand", 334)

    assert set([
        ("death", 250, 5, None), 
        ("wishing", 250, 5, None)
    ]) == buy_identify(19, "wand", 250)
