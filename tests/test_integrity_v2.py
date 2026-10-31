import copy
import json
from pathlib import Path

import pytest

from apps.server.engine import Game, replay_round
from apps.server.world import FLOOR, WALL, Mutation, generate, path, validate


def detour_world():
    grid = [[WALL] * 24 for _ in range(16)]
    for x in range(2, 22):
        grid[2][x] = grid[12][x] = FLOOR
    for y in range(2, 13):
        grid[y][2] = grid[y][21] = FLOOR
    return grid


def test_reachable_but_excessive_detour_is_rejected_atomically():
    grid = detour_world()
    before = copy.deepcopy(grid)
    proposal = Mutation(kind="wall", targets=[(12, 2)])
    assert validate(grid, (2, 2), (21, 2), proposal, rules=1).accepted
    result = validate(grid, (2, 2), (21, 2), proposal)
    assert not result.accepted and "12-step" in result.reason
    assert result.metrics["path_delta"] == 20
    assert result.metrics["before"]["steps"] == 19
    assert result.metrics["after"]["steps"] == 39
    assert grid == before and result.grid is None


def test_time_budget_duplicate_targets_and_mixed_proposal_rollback():
    grid = generate(1847)
    player, exit = (2, 13), (21, 2)
    proposal = Mutation(kind="wall", targets=[(2, 14)])
    assert validate(grid, player, exit, proposal, remaining=100).accepted
    result = validate(grid, player, exit, proposal, remaining=.5)
    assert not result.accepted and "time budget" in result.reason
    duplicate = Mutation(kind="wall", targets=[(2, 14), (2, 14)])
    assert "Conflicting" in validate(grid, player, exit, duplicate).reason
    original = copy.deepcopy(grid)
    result = validate(grid, player, exit, Mutation(kind="wall", targets=[(2, 14), exit]))
    assert not result.accepted and grid == original


@pytest.mark.parametrize("seed", range(30))
def test_replay_covers_mode_switches_pause_freeze_and_tile_evidence(seed):
    game = Game(seed)
    game.control("start")
    for i in range(230):
        if i == 20:
            game.restart_vote()
        if i == 50:
            game.control("pause")
            game.restart_vote()
            game.control("resume")
        if i % 10 == 0:
            game.cast(str(i), str(i), "!lava")
        game.tick(.1)
    game.control("pause")
    replayed = replay_round(game.replay())
    assert replayed.digest() == game.digest()
    assert replayed.audit == game.audit
    assert game.audit
    for event in game.audit:
        if event["accepted"]:
            assert event["metrics"]["after"]["steps"] is not None
            assert event["metrics"]["minimum_escape_seconds"] <= event["metrics"]["remaining_seconds"]
            assert all(tile["before"] != tile["after"] for tile in event["changes"])
    assert path(game.grid, game.player, game.exit)


def test_legacy_replay_still_verifies():
    game = Game(1847, rules=1)
    game.control("start")
    game.cast("u", "m", "!wall")
    for _ in range(150): game.tick(.1)
    record = game.replay()
    record.pop("rules")
    assert replay_round(record).digest() == game.digest()
