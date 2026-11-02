# Evaluation results

The integrity/transport measurements below were captured on 31 October 2026, Windows 11, Python 3.14.3. Final browser/build regression verification passed on 2 November with a clean Python 3.12.14 virtual environment. No number here is an estimate. Raw files are retained in the repository; timing changes with hardware and concurrent work.

## Independent integrity comparison

Command: `python benchmarks/competition.py`. Raw: [competition-results.json](../benchmarks/competition-results.json). Scenario seed 93017; **1,800 identical independent snapshots/proposals**, 300 each: bottleneck, reachable long detour, insufficient remaining time, duplicate-target conflict, partially legal multi-tile proposal, random proposal. Each engine sees the same original grid, player, exit, proposal and time context. An independently implemented BFS and policy oracle classify outcomes; production `path` and `validate` are not used as the oracle.

| Metric | Unrestricted writes | Integrity v1 policy | Integrity v2 |
|---|---:|---:|---:|
| Accepted proposals | 1,800 | 1,076 | 176 |
| Acceptance rate | 100% | 59.78% | 9.78% |
| Accepted proposals violating v2 policy | 1,624 | 900 | 0 |
| Invalid resulting world states | 1,090 | 600 | 0 |
| Invalid state rate / all scenarios | 60.56% | 33.33% | 0% |
| Unreachable safe exits | 489 | 0 | 0 |
| Input grids modified by validation | 0 | 0 | 0 |
| Median validation/write time (ms) | 0.0379 | 0.1570 | 0.0503 |
| p95 validation/write time (ms) | 0.0827 | 1.0033 | 1.9376 |

“Invalid resulting world” means an applied change leaves no safe route, changes a protected entity tile, exceeds a 12-step route increase, or exceeds the stated time estimate. “Policy violation” additionally includes illegal transformations/conflicting target proposals. **The original engine did not claim time/detour bounds:** its 600 world violations are against the new policy (300 long-detour + 300 deadline cases), not 600 broken reachability checks. The extra 300 v1 proposal violations are duplicate-target conflicts. Rules 1 preserves the original early-return validation semantics; this comparison is not a historical binary performance profile.

The low v2 acceptance is expected for a deliberately adversarial suite; it is not a measured natural-play rejection rate. The original 3,000-case workload still accepts **1,180/3,000 (39.33%)**, with zero invalid accepted proposals and zero unreachable exits, versus 1,820 invalid accepts and 694 unreachable exits for unrestricted writes. Its independent oracle now replaces the old self-checking classification. Raw: [results.json](../benchmarks/results.json). New timings on that workload: v2 median **0.0751ms**, p95 **3.2667ms**, max **7.3235ms**. These are measured under local concurrent work, not a latency improvement claim.

Validation timings include copying/checking and, in v2, route/exposure analysis. They exclude bounded target search, Twitch transport, database writes, network and paint. v2's lower median in the mixed suite reflects early conflict rejection; its higher p95 shows added work. Do not compare these as if they were identical successful-path workloads.

## Replay consistency

The competition script ran **100 seeded rounds**, each with at least 600 time inputs, synthetic votes, mode-window resets, pause/resume and freeze/unfreeze. **Zero final-digest or audit mismatches**. Tests also verify legacy rules-1 replay, full simulation rounds and explicit adversarial state transitions. No chat identity or message content is retained in aggregate replay.

In-app diagnostics reconstruct a paused or finished actual session on demand. The displayed digest, command count and measured reconstruction time come from the server's current record, not a fixture. Hash equality proves repeatability of these inputs/rules; it is not external attestation or a guarantee of every possible input sequence.

## State synchronization

Command: `python scripts/measure_sync.py http://127.0.0.1:8001`. Raw: [sync-results.json](../artifacts/sync-results.json).

- **8 read-only observer sockets**, 24 synthetic votes.
- **209 snapshot checks, zero synchronization failures**, covering vote fan-out, exact paused state, reset to a new round and reconnect.
- POST to all eight matching observers: **111.45ms median / 233.82ms p95**.
- New connection to first matching reset snapshot: **20.72ms**.

This is one local session, not eight independently hosted clients or a production load test. No Twitch delivery, public internet, rendering, OBS compositor or long soak is included. Client unit tests separately verify stale snapshot rejection across round resets; the browser delayed-response regression exercises the POST/socket race.

## Verification evidence and limits

The upgraded Python suite passed **197 tests** on Python 3.14 and again on Python 3.12 (22.33s); frontend validation/order tests passed **10 tests**. **All 3 final browser scenarios passed**, including the delayed-control regression, full gameplay and mobile diagnostics keyboard flow. The TypeScript/Vite build and exported winning replay CLI passed. Details are in JUDGE_READINESS.md; old and new environments are not conflated.

The first expanded browser run exposed an inaccessible mobile diagnostics button (hidden sidebar), now fixed with an integrity-panel entry. Its full gameplay scenario completed through reset but exceeded the former 60-second suite limit during final capture; the expanded integration scenario has a 120-second test budget. Assertions and the actual 15-second game vote window remain intact. Failures are not counted as passing evidence.

The first remote upgrade run passed unit/build/Docker checks but caught a browser-test race: it sampled the timer immediately after clicking Pause, before the server acknowledgment. The test now waits for the visible paused state before measuring a stopped timer; it does not relax the timer assertion.

Real Twitch evidence remains the earlier human-authorized broadcaster `!lava` vote applying three lava tiles, recorded in [LIVE_TWITCH_VERIFICATION.md](LIVE_TWITCH_VERIFICATION.md). The current adapter changes have automated mocked handoff/dedup/ping-option regression coverage. **No new live-account test, token-expiry soak, independent-viewer load, public deployment or OBS recording is inferred from those tests.**

Synthetic aggregation microbenchmarks accept 20k and reject 30k inputs at the 50k workload cap, around 5.28MB traced Python heap. These are not connected-viewer counts or RSS measurements. The earlier short renderer sample remains historical; no new GPU or end-to-end frame-rate improvement is claimed from animation smoothing.
