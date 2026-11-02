"""Independent policy oracle, identical cases, v1/v2 comparison and replay properties.

Run: python benchmarks/competition.py. No network, no claimed viewer capacity.
"""
from collections import deque
import copy
import json
from pathlib import Path
import platform
import random
import statistics
import sys
import time

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from apps.server.world import generate, Mutation, validate
from apps.server.engine import Game, replay_round


def distance(grid, start, end):
    """Separate BFS implementation; never calls the production path/validator."""
    if grid[start[1]][start[0]] not in (0, 3) or grid[end[1]][end[0]] not in (0, 3): return None
    queue, seen = deque([(start, 0)]), {start}
    while queue:
        (x, y), steps = queue.popleft()
        if (x, y) == end: return steps
        for dx, dy in ((0, 1), (0, -1), (1, 0), (-1, 0)):
            point = (x + dx, y + dy)
            a, b = point
            if 0 <= b < len(grid) and 0 <= a < len(grid[0]) and grid[b][a] in (0, 3) and point not in seen:
                seen.add(point); queue.append((point, steps + 1))
    return None


def oracle(grid, player, exit, proposal, remaining=None, rules=2):
    candidate = copy.deepcopy(grid)
    if rules >= 2 and len(set(proposal.targets)) != len(proposal.targets): return False
    for x, y in proposal.targets:
        if x <= 0 or y <= 0 or x >= len(grid[0]) - 1 or y >= len(grid) - 1: return False
        if (x, y) in (player, exit): return False
        if proposal.kind == "lava" and abs(x - player[0]) + abs(y - player[1]) <= 1: return False
        if grid[y][x] not in ((1, 2) if proposal.kind == "bridge" else (0, 3)): return False
        candidate[y][x] = {"wall": 1, "lava": 2, "bridge": 3}[proposal.kind]
    before, after = distance(grid, player, exit), distance(candidate, player, exit)
    if after is None: return False
    return rules < 2 or ((before is None or after - before <= 12) and (remaining is None or after * .2 + .5 <= remaining))


def scenarios(count=1800):
    rng = random.Random(93017)
    for i in range(count):
        grid = generate(i)
        player, exit, remaining = (2, 13), (21, 2), 100
        kind = rng.choice(["lava", "wall", "bridge"])
        targets = [(rng.randrange(1, 23), rng.randrange(1, 15))]
        category = ["bottleneck", "long_detour", "deadline", "conflict", "mixed_atomic", "random"][i % 6]
        if category == "bottleneck":
            grid = [[1] * 24 for _ in range(16)]
            for x in range(2, 22): grid[13][x] = 0
            for y in range(2, 14): grid[y][21] = 0
            targets = [(rng.randrange(3, 21), 13)]
        elif category == "long_detour":
            grid = [[1] * 24 for _ in range(16)]
            for x in range(2, 22): grid[2][x] = grid[12][x] = 0
            for y in range(2, 13): grid[y][2] = grid[y][21] = 0
            player, exit, kind, targets = (2, 2), (21, 2), "wall", [(12, 2)]
        elif category == "deadline":
            remaining, kind, targets = .5, "wall", [(2, 14)]
        elif category == "conflict":
            kind, targets = "wall", [(2, 14), (2, 14)]
        elif category == "mixed_atomic":
            kind, targets = "wall", [(2, 14), exit]
        yield grid, player, exit, Mutation(kind=kind, targets=targets), remaining, category


def run():
    cases = list(scenarios())
    output = {"seed": 93017, "scenarios": len(cases), "categories": {name: 300 for name in ["bottleneck", "long_detour", "deadline", "conflict", "mixed_atomic", "random"]},
              "python": platform.python_version(), "platform": platform.platform(), "engines": {},
              "method": "Identical independent snapshots; independent BFS/policy oracle. Adversarial mix, not natural-play frequency. Latency includes copy and validation, excludes target search and network."}
    for name in ("unrestricted", "integrity_v1", "integrity_v2"):
        timings, accepted, invalid, unreachable, mutated_input, oracle_mismatch, invalid_world = [], 0, 0, 0, 0, 0, 0
        for grid, player, exit, proposal, remaining, _ in cases:
            before = copy.deepcopy(grid)
            allowed = oracle(grid, player, exit, proposal, remaining)
            begin = time.perf_counter_ns()
            if name == "unrestricted":
                candidate = copy.deepcopy(grid)
                for x, y in proposal.targets: candidate[y][x] = {"wall": 1, "lava": 2, "bridge": 3}[proposal.kind]
                applied = True
            else:
                result = validate(grid, player, exit, proposal, remaining if name == "integrity_v2" else None, 2 if name == "integrity_v2" else 1)
                applied, candidate = result.accepted, result.grid if result.accepted else grid
            timings.append((time.perf_counter_ns() - begin) / 1e6)
            accepted += applied
            invalid += applied and not allowed
            after_distance = distance(candidate, player, exit)
            before_distance = distance(grid, player, exit)
            unreachable += after_distance is None
            invalid_world += applied and (after_distance is None or candidate[player[1]][player[0]] != grid[player[1]][player[0]] or
                candidate[exit[1]][exit[0]] != grid[exit[1]][exit[0]] or after_distance - before_distance > 12 or after_distance * .2 + .5 > remaining)
            mutated_input += before != grid
            oracle_mismatch += applied != allowed
        output["engines"][name] = {"accepted": accepted, "acceptance_rate": accepted / len(cases),
            "invalid_accepted": invalid, "policy_violation_rate": invalid / len(cases), "invalid_world_states": invalid_world,
            "invalid_state_rate": invalid_world / len(cases), "unreachable_exits": unreachable,
            "input_mutations": mutated_input, "oracle_disagreements": oracle_mismatch,
            "latency_ms_median": round(statistics.median(timings), 4), "latency_ms_p95": round(sorted(timings)[int(.95 * len(timings))], 4)}
    failures = 0
    for seed in range(100):
        game = Game(seed)
        game.control("start")
        for i in range(600):
            if i in (20, 150): game.restart_vote()
            if i % 10 == 0: game.cast(str(i), str(i), ["!lava", "!bridge", "!wall"][i // 10 % 3])
            if i == 80:
                game.control("pause"); game.control("resume")
            if i in (320, 340): game.control("freeze")
            game.tick(.1)
        game.control("pause")
        replayed = replay_round(game.replay())
        failures += replayed.digest() != game.digest() or replayed.audit != game.audit
    output["replay"] = {"rounds": 100, "digest_or_audit_failures": failures, "inputs_per_round_minimum": 600,
                        "scope": "Seeded aggregate input replay with mode switches, pause and freeze; no live identities or network."}
    return output


if __name__ == "__main__":
    result = run()
    Path("benchmarks/competition-results.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))
    assert result["engines"]["integrity_v2"]["oracle_disagreements"] == 0
    assert result["replay"]["digest_or_audit_failures"] == 0
