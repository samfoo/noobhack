from flexmock import flexmock

from noobhack.game.events import Dispatcher
from noobhack.game.manager import Manager

stats = u"Sam the Evoker            St:10 Dx:15 Co:11 In:17 Wi:12 Ch:10  Neutral"
stats_dict = {"St": 10, "Dx": 15, "Co": 11, "Wi": 12, "Ch": 10}

def mock_proxy():
    return flexmock(register=lambda _: None)

def mock_term():
    return flexmock(cursor=lambda: (0, 0),
                    display=[u" "])

def mock_events():
    return flexmock(listen=lambda _, __: None)

def test_dispatches_changes_in_stats():
    events = mock_events()
    events.should_receive("dispatch")
    events.should_receive("dispatch")\
            .with_args("stats-changed", stats_dict)\
            .once()

    manager = Manager(mock_term(), mock_proxy(), mock_proxy(), events)

    manager.process(stats)

def test_doesnt_dispatch_changes_in_stats_when_nothing_has_changed():
    events = mock_events()
    events.should_receive("dispatch")\
            .with_args("moved", (0, 0))

    manager = Manager(mock_term(), mock_proxy(), mock_proxy(), events)
    manager.stats = stats_dict

    manager.process(stats)

def test_doesnt_dispatch_changes_in_stats_when_no_stats_on_screen():
    events = mock_events()

    events.should_receive("dispatch")\
            .with_args("moved", (0, 0))

    manager = Manager(mock_term(), mock_proxy(), mock_proxy(), events)
    manager.stats = stats_dict

    manager.process("this string doesn't have stats")

