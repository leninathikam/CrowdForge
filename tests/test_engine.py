import copy

import pytest

from apps.server.engine import Game, replay_round
from apps.server.world import Mutation, path, LAVA, WALL


def test_movement_collision_pause_and_win():
    game = Game(1847)
    assert not game.move(1, 0)
    assert game.control("start")
    assert not game.control("start")
    assert not game.move(1, 1)
    assert game.control("pause")
    game.tick(10)
    assert game.elapsed == 0
    assert not game.move(1, 0)
    assert game.control("resume")
    route = path(game.grid, game.player, game.exit)
    for point in route[1:]:
        old = game.player
        assert game.move(point[0] - old[0], point[1] - old[1])
        game.tick(.15)
    assert game.phase == "won"
    assert not game.control("resume")
    assert replay_round(game.replay()).digest() == game.digest()


def test_collision_rate_and_damage():
    game = Game()
    game.control("start")
    game.grid[13][3] = WALL
    assert not game.move(1, 0)
    assert game.move(0, -1)
    assert not game.move(0, 1)
    game.grid[12][2] = LAVA
    game.tick(1)
    assert game.health == 78
    assert game.control("rescue")
    assert game.health == 100
    assert game.grid[12][2] == 0
    game.tick(100)
    assert game.phase == "lost" and game.elapsed == 100


def test_transaction_rejection_does_not_change_world_or_version():
    game = Game()
    before, version = copy.deepcopy(game.grid), game.version
    event = game.mutate(Mutation(kind="wall", targets=[game.exit]), 1)
    assert not event["accepted"]
    assert game.grid == before and game.version == version
    assert event["protocol"] == ["PROPOSED", "VALIDATING", "REJECTED"]


def test_vote_window_lifecycle_replay_and_freeze():
    game = Game()
    game.control("start")
    assert game.cast("viewer", "a", "!lava")
    assert not game.cast("viewer", "a", "!wall")
    for _ in range(150):
        game.tick(.1)
    assert len(game.audit) == 1 and game.audit[0]["accepted"]
    assert game.window.number == 2
    assert game.total_votes == 1
    assert game.control("freeze")
    assert not game.cast("u", "b", "!wall")
    for _ in range(150):
        game.tick(.1)
    assert len(game.audit) == 1
    game.control("freeze")
    assert game.cast("u", "c", "!bridge")
    game.tick(.1)
    assert game.cast("v", "d", "!wall")
    record = game.replay()
    replayed = replay_round(record)
    assert replayed.digest() == game.digest()
    assert replayed.audit == game.audit
    assert "viewer" not in str(record)


@pytest.mark.parametrize("seed", range(20))
def test_full_simulation_stability_and_replay(seed):
    game = Game(seed)
    game.control("start")
    for i in range(1000):
        if i % 10 == 0:
            game.cast(f"user-{i}", f"msg-{i}", ["!lava", "!wall", "!bridge"][i // 10 % 3])
        game.tick(.1)
        assert path(game.grid, game.player, game.exit)
    assert game.phase == "lost"
    assert replay_round(game.replay()).digest() == game.digest()
