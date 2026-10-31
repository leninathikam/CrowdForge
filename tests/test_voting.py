import pytest

from apps.server.voting import VoteWindow, parse_vote


@pytest.mark.parametrize("text,expected", [(" !LAVA ", "lava"), ("!vote 2", "wall"), ("!vote 3", "bridge"), ("!lava extra", None), ("!help", None), ("!vote 4", None), ("hello !lava", None)])
def test_commands(text, expected):
    assert parse_vote(text) == expected


def test_vote_change_cooldown_timestamp_and_dedup():
    vote = VoteWindow(1, 0, 15)
    assert vote.cast("u", "1", "!lava", 0, 0)
    assert not vote.cast("u", "1", "!wall", 2, 2)
    assert not vote.cast("u", "2", "!wall", .2, .2)
    assert vote.cast("u", "3", "!wall", 2, 2)
    assert not vote.cast("u", "4", "!bridge", 1, 4)
    assert vote.counts() == {"lava": 0, "wall": 1, "bridge": 0}
    assert not vote.cast("other", "5", "!bridge", -1, 4)
    assert not vote.cast("other", "6", "!bridge", 15, 15)


def test_disabled_changes_capacity_and_ties():
    window = VoteWindow(1, 0, 15, allow_changes=False, capacity=2)
    assert window.winner() is None
    assert window.cast("one", "a", "!wall", 0, 0)
    assert not window.cast("one", "b", "!lava", 2, 2)
    assert not window.cast("two", "c", "!lava", 2, 2)
    assert window.limited == 1
    for number, winner in [(1, "lava"), (2, "wall"), (3, "bridge")]:
        vote = VoteWindow(number, 0, 15)
        for kind in ("lava", "wall", "bridge"):
            vote.cast(kind, kind, "!" + kind, 0, 0)
        assert vote.winner() == winner
