from noobhack.ui.minimap import Minimap
from noobhack.game.mapping import Level

def expect(level, results):
    m = Minimap()
    buf = m.level_text_as_buffer(level)
    assert buf == results

def test_drawing_a_single_levels_buffer_with_an_empty_level_writes_nothing_interesting():
    level = Level(1)
    assert len(level.features) == 0
    expect(level, [
        "Level 1:",
        "  (nothing interesting)"
    ])

def test_drawing_a_single_level_draws_the_correct_dlvl():
    level = Level(5)
    expect(level, [
        "Level 5:",
        "  (nothing interesting)"
    ])

def test_drawing_a_single_level_draws_all_the_features():
    level = Level(1)
    level.features.add("Altar (neutral)") 
    level.features.add("Altar (chaotic)")
    expect(level, [
        "Level 1:",
        "  * Altar (chaotic)",
        "  * Altar (neutral)",
    ])

def test_drawing_features_sorts_them_first():
    from random import shuffle, seed
    seed(3141)

    level = Level(1)
    features = [str(i) for i in xrange(1, 10)]
    shuffle(features)
    assert features[0] != 1
    level.features.update(features)

    expected = [
        "Level 1:"
    ] + ["  * %s" % i for i in xrange(1, 10)]
    expect(level, expected)

def test_drawing_a_single_shop_indents_and_translates():
    level = Level(1)
    level.shops.add("random")

    expect(level, [
        "Level 1:",
        "  Shops:",
        "    * Random",
    ])

def test_drawing_features_and_shops_draws_the_shops_first():
    level = Level(1)
    level.features.update(["Fountain", "Oracle"])
    level.shops.add("90/10 arm/weap")

    expect(level, [
        "Level 1:",
        "  Shops:",
        "    * 90/10 arm/weap",
        "  * Fountain",
        "  * Oracle"
    ])

