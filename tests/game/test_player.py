from nose.tools import *

from noobhack.game.player import Player
from noobhack.game.events import Dispatcher

stats_dict = {"In": 17, "St": 10, "Dx": 15, "Co": 11, "Wi": 12, "Ch": 10}

def test_should_update_stats():
    events = Dispatcher()
    player = Player(events)
    player.listen()

    events.dispatch("stats-changed", stats_dict)

    assert_equals(stats_dict, player.stats)

def test_should_update_only_the_stat_that_changed():
    events = Dispatcher()
    player = Player(events)
    player.stats = stats_dict
    player.listen()

    changes = {"Ch": 100}
    events.dispatch("stats-changed", changes)

    assert_equals(dict(stats_dict.items() + changes.items()), player.stats)

