from flexmock import flexmock
from nose.tools import *

from noobhack.game.plugins.hp_color import *

def test_text_should_be_white_on_red_when_ratio_is_less_or_equal_to_25_percent():
    assert_equal(
        (["bold"], "white", "red"),
        color_for_ratio(0.15)
    )
    assert_equal(
        (["bold"], "white", "red"),
        color_for_ratio(0.25)
    )

def test_text_should_be_yellow_when_ratio_is_less_or_equal_to_50_percent():
    assert_equal(
        (["bold"], "yellow", "default"),
        color_for_ratio(0.5)
    )
    assert_equal(
        (["bold"], "yellow", "default"),
        color_for_ratio(0.3)
    )

def test_text_should_be_green_when_ratio_is_greater_than_50_percent():
    assert_equal(
        (["bold"], "green", "default"),
        color_for_ratio(0.51)
    )


def test_redraw_should_set_the_attributes_on_the_hp_text_in_terminal():
    with_hp = "Dlvl:1  $:0  HP:16(16) Pw:6(6) AC:3  Xp:1/0 T:1"
    term = flexmock(display=[with_hp],
                    attributes=[[()] * len(with_hp)])

    redraw(term)

    expected = (['bold'], 'green', 'default')
    assert_equal([expected] * 6, term.attributes[0][16:22])
