# Verification evidence

**Historical baseline below.** For the October 31–November 2 upgrades, see [EVALUATION_RESULTS.md](EVALUATION_RESULTS.md) and [JUDGE_READINESS.md](JUDGE_READINESS.md). New raw benchmark files supersede historical timings below. Public hosting is recommended, not an explicit requirement separate from runnable repository access.

Local verification performed during the October 30–31, 2026 build session (America/New_York). Results below are observed, not projected. No remote CI execution, public deployment or real Twitch chat is inferred from local tests.

## Implemented and tested

- Python core/API/Twitch mock suite: **162 passed in 33.82 seconds**, including logging and SQLite checkpoint regressions. Tests cover 100 map seeds × 30 random proposals, 20 full simulated rounds, deterministic replay, movement, collision, health, timer/state transitions, fair voting, OAuth state, mocked token refresh and EventSub handoff, origin/owner checks and observer synchronization.
- Frontend Vitest: **8 passed**. Versioned snapshots reject incompatible schemas, invalid maps/entities, bad vote counters and missing state before rendering.
- Playwright: **2 passed**. The main browser scenario loads the landing arena, starts, moves, pauses/resumes, casts a synthetic vote, waits for real server mutation, freezes/unfreezes, opens the read-only overlay, reconnects with a page reload, follows the safe route to win, exports replay and resets. The paused timeline is also exercised without its pause curtain blocking navigation. The second exercises narrower desktop layout, seed settings, help, unconfigured-Twitch setup and a 390-pixel layout with no horizontal overflow.
- A separate browser run also exercised an injected WebSocket interruption through Playwright's proxy and passed; the retained suite uses actual page reconnection to avoid proxy teardown delays. No simultaneous-observer capacity claim follows from this.
- Production `npm run build`: TypeScript and Vite passed. Final build approximately **261 kB JavaScript / 83 kB gzip**, **28 kB CSS / 7 kB gzip**.
- Replay CLI verified the exported winning round against its stored SHA-256 digest. Raw aggregate replay is retained at `artifacts/e2e-replay.json`.
- npm production dependency audit: **zero known advisories reported**. This is not a complete security audit or a guarantee that dependencies contain no vulnerabilities.
- Backend started cleanly, `/api/health` and production frontend served, and screenshots were visually inspected. Full-HD layout fits the game, voting, event feed and footer; overlay controls are read-only. Original art is procedural.

The full Python run emits one upstream Starlette deprecation warning about TestClient's current httpx compatibility path. It does not fail tests; migration should be checked when upgrading the framework.

## Measured benchmark

See `benchmarks/results.json` and methodology in `benchmarks/README.md`.

3,000 identical adversarial snapshots/proposals: unrestricted writes accepted 1,820 invariant violations and produced 694 states without a safe exit. CrowdForge accepted zero invalid proposals and produced zero unsafe exits. It accepted 1,180 mutations and rejected 1,820. Observed validator median / p95 / maximum: **0.0153 / 0.5551 / 5.7166 ms**. Both systems completed without stability exceptions. The validation adds cost; no speed improvement is claimed.

Synthetic vote microbenchmarks processed 1k, 5k, 20k and 50k inputs. At 50k inputs, 20k were accepted and 30k limited, with about 5.3 MB peak traced Python allocation. These are aggregation measurements, not live viewers or total process memory.

Real loopback transport, 30 synthetic vote samples, one observer: **105.94 ms median**, **445.21 ms p95** authenticated POST → matching WebSocket snapshot. New connection → first synchronized snapshot: **15.19 ms**, preserving all 30 votes. Source: `artifacts/transport-results.json`. Excludes Twitch, internet latency, DOM paint and OBS. Local concurrent test/build activity was present; the p95 is reported rather than hidden.

Headless Chromium at 1920 × 1080 measured 120 requestAnimationFrame intervals over 2,050 ms: 58.54 effective frames/second, 16.7 ms median interval and 16.8 ms p95. Source: `artifacts/browser-performance.json`. This short rendering sample does not measure GPU completion, live Twitch load or OBS compositor performance.

## External verification and remaining gates

- **Verified live:** real broadcaster OAuth, token validation, EventSub subscription, one real !lava chat vote, vote close, accepted three-tile lava mutation and score 30. Simulation was disabled. See LIVE_TWITCH_VERIFICATION.md. **Still unverified live:** independent-viewer traffic, token expiry/revocation, long-duration reconnect and OBS recording. Credentials are ignored by Git and were not printed.
- **Verified on CI:** Docker/Compose build, packaged frontend and authenticated HTTP actions, health checks, container restart and persistent SQLite evidence. Code revision `e6cf0477a4b762d807b959db1bd90d18be8d1336`; [successful run](https://github.com/leninathikam/CrowdForge/actions/runs/41215265874). Docker remains unavailable on this workstation.
- GitHub Actions: both verify and docker jobs passed. The verify job ran Python/frontend/browser tests, the production build, replay verification and the benchmark from a clean runner.
- Public host, TLS proxy, internet latency and OBS capture: not verified. No public deployment URL is supplied.
- Public source repository created: https://github.com/leninathikam/CrowdForge. Local implementation commits and the source push are recorded in Git; remote CI results are separate from local tests.

## Scope and limitations

One persistent Python process owns state. Active games/auth sessions disappear on restart; SQLite checkpoints replay evidence on mutations, pauses, terminal rounds and graceful shutdown; it does not restore active sessions or tokens. Limits are 100 arenas/process, five/owner cookie, eight observer sockets/arena, 20k vote-message IDs/window, bounded transport queues and a bounded deduplication cache. Anonymous creation needs edge request limits for broad internet exposure. No thousands-of-connected-viewers claim, distributed-state claim or long soak result is made.

The browser timeline and exported reconstruction are implemented. Optional Supply Drop, Adaptive Chaos Director, natural-language proposals, extra maps/cosmetics and an interactive frame-by-frame replay player were deliberately left out. The core works without an LLM. Keyboard accessibility and reduced motion are supported, but the visual arena is not a complete nonvisual game experience.

## Verdict

**NOT READY FOR SUBMISSION** until the authentic public YouTube demo, eligibility confirmation and final Devpost form are complete. Public source, Compose persistence and one real Twitch mutation were verified before this audit. The rules permit runnable repository access; separate hosting is recommended, not mandatory. See `submission/SUBMISSION_CHECKLIST.md`.

CI emits upstream action-runtime deprecation and runner-image migration notices; the jobs pass. These notices are separate from application console checks.
