import copy
import random

import pytest
from pydantic import ValidationError

from apps.server.world import FLOOR, WALL, LAVA, BRIDGE, HEIGHT, WIDTH, Mutation, generate, path, select_target, validate


@pytest.mark.parametrize("seed", range(100))
def test_seeded_maps_and_mutation_invariants(seed):
    grid = generate(seed)
    player, exit = (2, HEIGHT - 3), (WIDTH - 3, 2)
    assert grid == generate(seed)
    assert len(grid) == HEIGHT and all(len(row) == WIDTH for row in grid)
    assert path(grid, player, exit)
    rng = random.Random(seed)
    for _ in range(30):
        before = copy.deepcopy(grid)
        proposal = Mutation(kind=rng.choice(["lava", "wall", "bridge"]), targets=[(rng.randrange(-1, WIDTH + 1), rng.randrange(-1, HEIGHT + 1))])
        result = validate(grid, player, exit, proposal)
        assert grid == before, "Validation must never mutate its input, even on acceptance"
        if result.accepted:
            grid = result.grid
            assert path(grid, player, exit)
            assert grid[player[1]][player[0]] in (FLOOR, BRIDGE)
            assert grid[exit[1]][exit[0]] in (FLOOR, BRIDGE)
        else:
            assert result.grid is None


def test_last_route_is_protected_and_bridge_opens_it():
    grid = [[WALL] * 7 for _ in range(5)]
    for x in range(1, 6):
        grid[2][x] = FLOOR
    result = validate(grid, (1, 2), (5, 2), Mutation(kind="wall", targets=[(3, 2)]))
    assert not result.accepted and "last safe route" in result.reason
    grid[1][3] = LAVA
    result = validate(grid, (1, 2), (5, 2), Mutation(kind="bridge", targets=[(3, 1)]))
    assert result.accepted and result.grid[1][3] == BRIDGE


@pytest.mark.parametrize("targets", [[(2, 13)], [(3, 13)], [(21, 2)], [(-1, 2)], [(24, 16)]])
def test_protected_lava(targets):
    assert not validate(generate(0), (2, 13), (21, 2), Mutation(kind="lava", targets=targets)).accepted


@pytest.mark.parametrize("body", [{"kind": "lava", "targets": [[1.5, 2]]}, {"kind": "unknown", "targets": [[1, 2]]}, {"kind": "wall", "targets": []}, {"kind": "wall", "targets": [[True, 3]]}, {"kind": "wall", "targets": [[1, 2]], "extra": True}])
def test_schema_rejects_invalid_commands(body):
    with pytest.raises(ValidationError):
        Mutation.model_validate(body)


@pytest.mark.parametrize("kind", ["lava", "wall", "bridge"])
def test_deterministic_target_selection(kind):
    grid = generate(1847)
    one = select_target(grid, (2, 13), (21, 2), kind, 7)
    assert one == select_target(grid, (2, 13), (21, 2), kind, 7)
    assert validate(grid, (2, 13), (21, 2), one).accepted
