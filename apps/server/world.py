"""Deterministic grid generation and transactional mutation validation."""
from collections import deque
from dataclasses import dataclass
import random
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, StrictInt

WIDTH, HEIGHT = 24, 16
FLOOR, WALL, LAVA, BRIDGE = 0, 1, 2, 3
KINDS = ("lava", "wall", "bridge")
Point = tuple[int, int]


class Mutation(BaseModel):
    model_config = ConfigDict(extra="forbid")
    kind: Literal["lava", "wall", "bridge"]
    targets: list[tuple[StrictInt, StrictInt]] = Field(min_length=1, max_length=12)


def path(grid: list[list[int]], start: Point, end: Point) -> list[Point]:
    """A safe escape path excludes damaging lava, not merely solid obstacles."""
    for x, y in (start, end):
        if not (0 <= y < len(grid) and 0 <= x < len(grid[0])) or grid[y][x] not in (FLOOR, BRIDGE):
            return []
    queue = deque([start])
    previous: dict[Point, Point | None] = {start: None}
    while queue:
        point = queue.popleft()
        if point == end:
            route = []
            while point is not None:
                route.append(point)
                point = previous[point]
            return route[::-1]
        x, y = point
        for nxt in ((x + 1, y), (x, y - 1), (x - 1, y), (x, y + 1)):
            a, b = nxt
            if 0 <= b < len(grid) and 0 <= a < len(grid[0]) and grid[b][a] in (FLOOR, BRIDGE) and nxt not in previous:
                previous[nxt] = point
                queue.append(nxt)
    return []


def generate(seed: int) -> list[list[int]]:
    rng = random.Random(seed)
    grid = [[WALL if x in (0, WIDTH - 1) or y in (0, HEIGHT - 1) else FLOOR for x in range(WIDTH)] for y in range(HEIGHT)]
    for y in range(2, HEIGHT - 2):
        for x in range(3, WIDTH - 3):
            value = rng.random()
            grid[y][x] = WALL if value < .17 else LAVA if value < .25 else FLOOR
    # An initial guaranteed corridor; later proposals must independently preserve reachability.
    for x in range(2, WIDTH - 2):
        grid[HEIGHT - 3][x] = FLOOR
    for y in range(2, HEIGHT - 2):
        grid[y][WIDTH - 3] = FLOOR
    return grid


@dataclass(frozen=True)
class Validation:
    accepted: bool
    reason: str
    grid: list[list[int]] | None = None
    metrics: dict | None = None


def route_metrics(grid: list[list[int]], route: list[Point]) -> dict:
    """Exposure counts safe route tiles adjacent to lava, not predicted HP loss."""
    exposed = sum(any(0 <= ny < len(grid) and 0 <= nx < len(grid[0]) and grid[ny][nx] == LAVA
                      for nx, ny in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1))) for x, y in route)
    return {"steps": len(route) - 1 if route else None, "hazard_adjacent_tiles": exposed,
            "required_lava_tiles": 0 if route else None}


def validate(grid: list[list[int]], player: Point, exit: Point, proposal: Mutation,
             remaining: float | None = None, rules: int = 2) -> Validation:
    candidate = [row[:] for row in grid]
    replacement = {"lava": LAVA, "wall": WALL, "bridge": BRIDGE}[proposal.kind]
    changed = False
    if rules >= 2 and len(set(proposal.targets)) != len(proposal.targets):
        return Validation(False, "Conflicting proposal: a tile appears more than once.")
    for x, y in proposal.targets:
        if not (0 < x < len(grid[0]) - 1 and 0 < y < len(grid) - 1):
            return Validation(False, "Arena boundary is protected.")
        if (x, y) in (player, exit):
            return Validation(False, "Player and exit tiles are protected.")
        if proposal.kind == "lava" and abs(x - player[0]) + abs(y - player[1]) <= 1:
            return Validation(False, "Lava needs a one-tile safety buffer around the player.")
        old = grid[y][x]
        allowed = (FLOOR, BRIDGE) if proposal.kind != "bridge" else (WALL, LAVA)
        if old not in allowed:
            return Validation(False, "That terrain cannot be transformed by this mutation.")
        candidate[y][x] = replacement
        changed |= old != replacement
    if not changed:
        return Validation(False, "No terrain would change.")
    after = path(candidate, player, exit)
    if not after:
        return Validation(False, "Rejected: this would remove the last safe route to the exit.")
    if rules < 2:
        return Validation(True, "Safe route preserved. World mutation committed.", candidate)
    before = path(grid, player, exit)
    metrics = {"before": route_metrics(grid, before), "after": route_metrics(candidate, after),
               "path_delta": len(after) - len(before) if before else None,
               "minimum_escape_seconds": round((len(after) - 1) * .2 + .5, 2),
               "remaining_seconds": remaining}
    if rules >= 2:
        if before and len(after) - len(before) > 12:
            return Validation(False, "Rejected: detour exceeds the 12-step fairness limit.", metrics=metrics)
        if remaining is not None and metrics["minimum_escape_seconds"] > remaining:
            return Validation(False, "Rejected: the safe route exceeds the remaining time budget.", metrics=metrics)
    return Validation(True, "Safe route preserved. World mutation committed.", candidate, metrics)


def select_target(grid: list[list[int]], player: Point, exit: Point, kind: str, seed: int,
                  remaining: float | None = None, rules: int = 2) -> Mutation:
    rng = random.Random(seed)
    points = [(x, y) for y in range(1, HEIGHT - 1) for x in range(1, WIDTH - 1)]
    rng.shuffle(points)
    # Prefer meaningful targets near the player; the stable shuffle breaks equal-distance ties.
    points.sort(key=lambda p: abs(abs(p[0] - player[0]) + abs(p[1] - player[1]) - 5))
    informative_rejection = None
    for x, y in points[:240]:
        targets = [(x, y)] if kind == "bridge" else [(x, y), (x + 1, y), (x, y + 1)]
        proposal = Mutation(kind=kind, targets=targets)
        result = validate(grid, player, exit, proposal, remaining, rules)
        if result.accepted:
            return proposal
        if result.metrics and informative_rejection is None:
            informative_rejection = proposal
    # A bounded unsuccessful proposal is still audited and explained by the same validator.
    return informative_rejection or Mutation(kind=kind, targets=[exit])
