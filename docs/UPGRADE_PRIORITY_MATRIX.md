# Upgrade priority matrix

Planning estimates are engineering effort ranges, not recorded hours or promises. Deadline verified: 2 November 2026, 22:00 UTC. P0 closes correctness/proof gaps; P1 improves demonstration; P2 is optional after actual viewer feedback. The user's audit-and-upgrade request authorizes deadline-feasible implementation; no additional approval gate was inferred.

| Feature | Initial status | Judging benefit | Difficulty | Estimated hours | Regression risk | Demo impact | Priority / result |
|---|---|---|---|---:|---|---|---|
| Replay mode changes + broader digest | Replay existed; transitions missing | Technology: closes reproducible correctness gap | Medium | 1–2 | Medium; preserve v1 | High: verifiable proof | P0 / implemented |
| POST/socket/reset ordering | Full snapshots, no common sequence | Technology/design: avoids visual rollback | Low | 0.5–1 | Low | Medium | P0 / implemented |
| Twitch ping behavior + diagnostics | Real adapter; default client pings | Technology: protocol compliance | Low | 0.5–1 | Low; mocked handoff test | High for real reliability | P0 / implemented |
| Detour/time bounds + exposure evidence | Reachability only | Innovation/technology: more meaningful fairness | Medium | 2–4 | Medium; policy can reject more | High with adversarial proof | P0 / implemented |
| Independent oracle + v1/v2 evaluation | Shared production checker | Technology: credible measurement | Medium | 2–3 | Low; offline only | High | P0 / implemented |
| Diagnostics/replay proof/tile diffs | Hidden logs + CLI | Technology/design: judge-visible evidence | Medium | 2–4 | Low; separate owner view | High | P0 / implemented |
| SQLite error isolation | Unhandled checkpoint failure | Technology: ticker survives storage fault | Low | 0.5–1 | Low | Low unless failure injected | P0 / implemented |
| Eight-observer reset/reconnect test | One observer timing only | Technology: bounded fan-out evidence | Low–medium | 1–2 | Low | Medium | P1 / implemented |
| Movement/damage/countdown + modal keyboard UX | Snap movement, weak damage cue | Design: watchability and usability | Low–medium | 1–3 | Low; browser regression | High | P1 / implemented |
| Authentic independent-viewer rehearsal/video | One broadcaster test, no video | Impact/design plus required submission artifact | Medium; human/account dependent | 2–4 | Low code risk | Essential | P0 / still required |
| Working judging access / public host | Runnable repo, old Compose CI | Reduces adoption friction | Medium; infrastructure dependent | 1–3 | Medium; TLS/config | High | P1 / public host unverified, repository route allowed |
| Route-aware adaptive director | Absent | Potential innovation/engagement | High | 8–16 | High; balance/replay/fairness | High if balanced | P2 / deferred |
| Factions and finite resources | Absent | Potential impact/strategy | High | 12–24 | High; abuse/balance/UI | High if understood | P2 / deferred |
| Full graphical replay scrubber | CLI + timeline | Design and proof | Medium–high | 6–10 | Medium | Medium–high | P2 / deferred |
| Durable distributed sessions | In-memory process | Operational reliability | High | 12–24+ | Very high near deadline | Low | Defer |
| Runtime AI mutation proposals | Absent | No demonstrated judging benefit | High | 8–16+ | High; latency/safety/cost | Uncertain | Reject for deadline |

Remaining time should go first to a genuine multi-person Twitch round, a clear public video, and final submission checks. Adding features cannot substitute for those artifacts.
