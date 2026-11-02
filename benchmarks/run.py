"""Same independent seeded scenarios for an unrestricted baseline and CrowdForge."""
import json
from pathlib import Path
import platform
import random
import statistics
import sys
import time
import tracemalloc

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from apps.server.world import generate, Mutation, validate, path, FLOOR, WALL, LAVA, BRIDGE
from apps.server.voting import VoteWindow
from competition import oracle


def run(scenarios=3000):
    rng = random.Random(93017)
    data = []
    for i in range(scenarios):
        grid = generate(i)
        if i % 4 == 0:
            # Adversarial bottleneck: demonstrate the failure the integrity engine prevents.
            grid = [[WALL] * 24 for _ in range(16)]
            for x in range(2, 22): grid[13][x] = FLOOR
            for y in range(2, 14): grid[y][21] = FLOOR
            targets = [(rng.randrange(3, 21), 13)]
        elif i % 7 == 0:
            targets = [(2, 13)]
        else:
            targets = [(rng.randrange(1, 23), rng.randrange(1, 15))]
        proposal = Mutation(kind=rng.choice(["wall", "lava", "bridge"]), targets=targets)
        data.append((grid, proposal))
    output = {"seed": 93017, "scenarios": scenarios, "python": platform.python_version(), "platform": platform.platform(),
              "method": "Independent identical snapshots and proposals; lava is excluded from safe reachability. Timings cover copy/validation, not rendering or network."}
    for name in ("unrestricted", "crowdforge"):
        timings, accepted, rejected, invalid, unreachable, errors = [], 0, 0, 0, 0, 0
        for grid, proposal in data:
            truth = oracle(grid, (2, 13), (21, 2), proposal)
            begin = time.perf_counter_ns()
            try:
                if name == "unrestricted":
                    candidate = [row[:] for row in grid]
                    for x, y in proposal.targets: candidate[y][x] = {"wall": WALL, "lava": LAVA, "bridge": BRIDGE}[proposal.kind]
                    applied = True
                else:
                    result = validate(grid, (2, 13), (21, 2), proposal)
                    applied, candidate = result.accepted, result.grid if result.accepted else grid
                timings.append((time.perf_counter_ns() - begin) / 1e6)
                accepted += applied
                rejected += not applied
                invalid += applied and not truth
                unreachable += not bool(path(candidate, (2, 13), (21, 2)))
            except Exception:
                errors += 1
        ordered = sorted(timings)
        output[name] = {"successful_mutations": accepted, "rejected_mutations": rejected, "invalid_mutations_accepted": invalid,
                        "unreachable_exit_states": unreachable, "stability_errors": errors,
                        "latency_ms_median": round(statistics.median(timings), 4), "latency_ms_p95": round(ordered[int(len(ordered) * .95)], 4), "latency_ms_max": round(max(timings), 4)}
    output["vote_workloads"] = []
    for count in (1000, 5000, 20000, 50000):
        window = VoteWindow(1, 0, 15)
        tracemalloc.start()
        begin = time.perf_counter()
        for i in range(count): window.cast(str(i), str(i), "!lava", 1, 1)
        elapsed = time.perf_counter() - begin
        _, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        output["vote_workloads"].append({"events": count, "accepted": len(window.votes), "limited": window.limited, "elapsed_seconds": round(elapsed, 4), "events_per_second": round(count / elapsed), "python_heap_peak_bytes": peak})
    return output


if __name__ == "__main__":
    output = run()
    target = Path(__file__).with_name("results.json")
    target.write_text(json.dumps(output, indent=2) + "\n")
    print(json.dumps(output, indent=2))
