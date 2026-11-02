# Reproducible integrity benchmark

**Current evaluation:** [EVALUATION_RESULTS.md](../docs/EVALUATION_RESULTS.md) distinguishes this reachability workload from the new 1,800-case policy comparison. Run `python benchmarks/competition.py` for identical unrestricted/v1/v2 cases with an independent BFS oracle and 100 replays. Run `python scripts/measure_sync.py` against a running server for eight-observer fan-out/reset/reconnect. Timings below are historical; current raw results are in JSON and the evaluation document.

Run `python benchmarks/run.py`. The tracked `results.json` is raw measured output from this workstation, not an estimate.

3,000 independent initial map snapshots and identical proposals are supplied to both implementations. Scenario seed is 93017. A quarter are intentionally narrow corridors; every seventh remaining case targets the player; other proposals use random interior coordinates. Kinds are deterministically randomized. This deliberately adversarial distribution demonstrates guardrails; it is not a prediction of natural Twitch chat behavior.

The unrestricted baseline clones and writes terrain directly. CrowdForge validates bounds, transformations, entities and BFS reachability before committing. Invalid proposals are now classified by the separate oracle in `competition.py`, replacing the original production-validator self-check. Safe reachability excludes lava. Independent scenarios prevent either engine benefiting from a different evolving map history. No baseline crashes were observed.

Recorded run: unrestricted accepted 3,000 proposals, including 1,820 invariant violations, and left 694 exits without a safe route. CrowdForge accepted 1,180 proposals, rejected 1,820, and accepted zero invariant violations or unreachable exits. Both completed without stability exceptions.

Median / p95 operation latency was 0.0027 / 0.0073 ms for unrestricted assignment and 0.0153 / 0.5551 ms for CrowdForge validation. Validation adds work; no speedup is claimed. Its observed maximum was 5.7166 ms. Timings use Python perf_counter_ns and cover only local copy/write/validation, excluding target selection, Twitch delivery, network and rendering. Repeat runs will vary.

The vote microbenchmark feeds 1,000, 5,000, 20,000 and 50,000 synthetic messages into one window while tracemalloc is active. The final workload accepts 20,000 and limits 30,000 as designed. Measured throughput ranged roughly 36k–50k input events/second, with a peak Python allocation near 5.3 MB at capacity. These are bounded aggregation measurements, not proof of equivalent live Twitch traffic or simultaneously connected viewers. tracemalloc peak is not total process RSS.

`python scripts/measure_transport.py` measures actual localhost authenticated POST → WebSocket snapshot latency and reconnect → first snapshot. Output is written to `artifacts/transport-results.json`; it excludes DOM paint, Twitch and internet latency. Frame rate and public deployment latency must be measured separately on the target setup.

Limits: one workstation, one process, synthetic messages, no real EventSub delivery, no distributed clients, no OBS compositor, no long-duration soak and no public network. Use these results as technical evidence of the invariant, never as a thousands-of-viewers capacity claim.
