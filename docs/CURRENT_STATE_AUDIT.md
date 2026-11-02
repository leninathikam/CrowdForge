# Competition audit — 31 October 2026

Audit baseline: public commit `0bdd0ec`. Began 31 October, completed with final verification on 2 November. This audits the existing project. Final changes and verification are in EVALUATION_RESULTS.md and JUDGE_READINESS.md. Scores are internal assessments, not organizer predictions. Rules were rechecked on 2 November and the deadline was unchanged.

## Official requirements checked

The [official rules](https://twitchcon-codex.devpost.com/rules), checked 31 October, set the deadline at **2 November 2026, 2 p.m. PST / 5 p.m. EST / 22:00 UTC**. Innovation/Idea, Potential Impact, Technological implementation (including Codex use), and Design are equally weighted. The project must be new work in the submission period, built with Codex, and connect interactively to Twitch. Submit source/assets/run instructions, an English description, the actual Codex session ID, and a public YouTube demonstration under three minutes showing both functioning Twitch integration and Codex development. Preserve free judging access through 15 November, 5 p.m. Pacific.

**Correction to earlier readiness wording:** a separately hosted public application is not explicitly mandatory; the rules permit access through a runnable repository. Public hosting is a recommended adoption/judging improvement, not itself a universal disqualification condition. Video, working access, eligibility and final submission remain actual gates. Additional runtime AI is not a judging requirement.

## Component-by-component findings at baseline

| Component / code | Functional evidence | Weakness / status |
|---|---|---|
| React shell, `main.tsx`, `useGame.ts`, `wire.ts` | Real POST controls and full WebSocket snapshots; startup-move queue; 8 decoding tests | Older POST replies could overwrite newer socket state. Busy requests can drop non-movement controls. Decoder validates core shape, not every nested field. |
| Canvas game, `Arena.tsx`, `ArenaPanel.tsx` | Original procedural renderer; real movement/collision/HP/escape; browser escape test | Tile movement snapped; damage feedback mostly numeric. Canvas is not a fully nonvisual playable interface. |
| Authoritative engine, `engine.py::Game` | Server-owned ready/running/paused/won/lost states; freeze/rescue; replay | Tick is fixed .1s after a sleep, so overloaded wall-clock play can slow. Full vote recounts add work at capacity. |
| Maps/mutations, `world.py::generate/validate/select_target` | Seeded 24×16 maps, strict proposal schema, copy/validate/commit, protected entities, safe BFS, bounded selection | Reachable did not mean time-feasible. No detour ceiling; duplicate targets accepted. Target selection favors distance, not strategic impact. |
| Vote fairness, `voting.py::VoteWindow.cast` | Identity/message dedup, replacement cooldown, timestamp bounds, rotating ties, no-vote no-op, 20k cap | Capacity is a resource cap, not measured live capacity. Same-kind re-votes consume receipt capacity. No factions/resources. |
| OAuth/API, `main.py::auth_start/auth_callback/act` | Browser-bound expiring single-use state, owner cookie, origins, read-only observer token, action limit | Anonymous session creation needs edge limits. Active state/tokens disappear on restart. Mode changes edited vote windows outside replay. |
| EventSub, `twitch.py::listen/run/validate_token` | Real auth-code flow and one earlier real broadcaster vote; mocked refresh/dedup/handoff/revocation | Default library client ping interval was enabled, contrary to Twitch's outgoing-only connection rule. Long real-account soak/refresh not demonstrated. |
| Real-time transport, `main.py::websocket_state` | Full snapshots, origin/owner checks, 8 observers, slow-send timeout, reconnection tests | No session-wide ordering across POST/socket/reset. Single-process limits; no distributed recovery or internet-load evidence. |
| Persistence, `storage.py::RoundStore`, `main.py::checkpoint` | SQLite mutation/pause/end/shutdown checkpoints; earlier Compose restart CI | Evidence archive, not session restoration. A SQLite exception could terminate ticker. Synchronous writes can stall loop. |
| Timeline/replay, `engine.py::replay_round`, `scripts/replay.py` | Seeded deterministic aggregate replay; exported winning round tested | No graphical playback. Digest omitted voting-window/control metadata; no in-app verification. Earlier live raw replay was not saved. |
| UI/OBS, `VotingPanel.tsx`, `Dialogs.tsx`, `style.css` | Responsive custom indie styling, commands/countdown, simulation/live distinction, view-only overlay | Help/settings dialogs lacked focus containment/Escape. Small secondary text, dense shell. “Always a safe way out” overstated a mutation-time invariant. No genuine OBS capture verified. |
| Tests/benchmarks, `tests/`, `benchmarks/run.py` | 162 Python + 8 frontend baseline tests, seeded invariant tests; existing two-browser-test suite | Benchmark classified invalid changes with the same production validator under evaluation. No v1/v2 comparison or multi-observer reset/reconnect measurement. Twitch tests use mocks. |
| Deployment, `Dockerfile`, Compose, CI | Non-root image, single process, loopback binding, named volume; previous remote CI green | Local Docker absent. No public application host; reverse proxy/TLS/external abuse controls still operator work. |
| Submission/docs | Source public, real Codex ID, original assets, honest one-vote record, demo drafts | Public YouTube recording, final Devpost form, personal eligibility and independent-viewer feedback missing. Older docs overstate hosting as mandatory. |

Major source modules, scripts, test suites, workflow/container files, benchmark methodology, README, verification/compliance and submission materials were inspected. `.env` values are excluded from evidence. Generated/vendor code was not treated as authored application code.

## Strict baseline assessment

| Lens | Innovation | Impact | Technology | Design | Rationale |
|---|---:|---:|---:|---:|---|
| Technical judge | 6 | 5 | 6 | 7 | `world.validate` is correct for its narrow invariant; `test_seeded_maps_and_mutation_invariants` and replay tests are useful. New timing and transport gaps prevent a higher reliability score. |
| Product judge | 5 | 5 | 6 | 6 | `VotingPanel` removes viewer installation friction, but a practiced runner can finish the fixed safe corridor before the first 15s vote. No retention/community study supports adoption. |
| Skeptical hackathon judge | 5 | 4 | 6 | 6 | The UI is real, not a mock, and EventSub has genuine one-vote evidence. BFS and chat-controlled games are established techniques; many votes may change irrelevant nearby tiles. A proof view and authentic video matter more than AI branding. |

Working baseline score for planning: **Innovation 6, Impact 5, Technology 6, Design 7; equal-weight mean 6.0/10** (same rubric as the earlier self-assessment). The harsher lenses show uncertainty rather than three independent human reviews.

## Functional, mocked and missing distinctions

Functional: the whole offline loop, server authority, validated mutations, replay export, owner/observer boundary, OAuth/EventSub implementation, persistence evidence and builds. Previously observed live: one authorized broadcaster `!lava` changed three tiles. Mocked: EventSub failure/lifecycle unit tests and all synthetic audience throughput. Missing: factions, adaptive director, full visual replay, durable session recovery, community retention evidence and public demo recording. Nothing in the new diagnostics may represent synthetic inputs as live receipts.

DevRelay community research was attempted through the installed skill; the connector returned “Not connected to MLH.” No community citations or consensus were invented. Architecture decisions here rely on inspected source, measured tests and [Twitch's primary transport documentation](https://dev.twitch.tv/docs/eventsub/handling-websocket-events/).
