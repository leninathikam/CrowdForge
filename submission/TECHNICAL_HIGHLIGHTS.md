# Technical highlights

## Audit upgrades

- Rules 2 limits safe-route detours to 12 added steps and checks remaining time using an explicit movement estimate; reports route length, lava adjacency and atomic tile diffs. It rejects duplicate-target conflicts.
- Mode changes are replay inputs; the digest covers window/control/audit state. The owner can reconstruct and verify a paused or finished actual round in-app, while old records retain rules-1 behavior.
- One session-wide sequence orders socket and POST snapshots across reset. Pending streamer controls survive delayed requests. Twitch client-initiated pings are disabled, and real receipt/dedup counters are visible without exposing chat identities.
- Independent-oracle comparison: 1,800 adversarial cases; v1 kept all exits reachable but accepted 600 states violating the new detour/time policy. v2 accepted zero. 100 replay rounds and 209 checks across eight observer sockets had zero mismatches. See [evaluation](../docs/EVALUATION_RESULTS.md) for acceptance rates, latency and limitations.

The original-build highlights below remain context; historical timings and CI links are not final-upgrade measurements.

- **Transactional terrain:** typed proposals validate on a copy. Protected entities, legal terrain transitions and safe BFS reachability all pass before one authoritative grid assignment commits the change. Rejection preserves the map/version and emits an explanation.
- **A genuinely safe path:** lava is traversable for the runner but excluded from the escape invariant. “You can walk there” is weaker than “the game leaves a safe escape.”
- **Deterministic evidence:** seeded maps, deterministic bounded target selection, logged control/tick decisions and a final-state digest allow reconstruction without keeping viewer identities.
- **Fair voting:** one choice per user, configurable replacements, cooldowns, message deduplication, timestamp checks, rotating ties, no-vote no-op and explicit resource caps.
- **Twitch lifecycle:** authorization code grant, state bound to an HTTP-only browser cookie, least-privilege user:read:chat, server-only refresh, hourly validation, keepalive timeout handling, inherited-subscription handoff and fresh subscriptions after unexpected loss.
- **Authority boundary:** browser components only render snapshots and send intentions. OBS gets a separate view token, never streamer authority. Origin checks protect mutations and WebSocket access.
- **Reproducible comparison:** the same snapshots/proposals yield 694 unsafe exits under unrestricted writes and none under checking across 3,000 intentionally adversarial cases. Raw timing, throughput and Python allocation output are included with workload limits.
- **Real integration evidence:** broadcaster OAuth and EventSub were connected, and one human-authorized real !lava message counted and applied three validated lava tiles. This was not a synthetic vote or an independent-viewer load test.
- **Clear limits:** one server process, ephemeral active sessions, no claimed public deployment or recorded OBS demo, no claim of thousands of simultaneously connected viewers.

See docs/VERIFICATION.md for actual test totals and final measured results. CI has executed successfully, including Compose restart and persistent evidence checks: https://github.com/leninathikam/CrowdForge/actions/runs/41215265874.
