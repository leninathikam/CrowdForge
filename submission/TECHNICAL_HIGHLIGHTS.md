# Technical highlights

- **Transactional terrain:** typed proposals validate on a copy. Protected entities, legal terrain transitions and safe BFS reachability all pass before one authoritative grid assignment commits the change. Rejection preserves the map/version and emits an explanation.
- **A genuinely safe path:** lava is traversable for the runner but excluded from the escape invariant. “You can walk there” is weaker than “the game leaves a safe escape.”
- **Deterministic evidence:** seeded maps, deterministic bounded target selection, logged control/tick decisions and a final-state digest allow reconstruction without keeping viewer identities.
- **Fair voting:** one choice per user, configurable replacements, cooldowns, message deduplication, timestamp checks, rotating ties, no-vote no-op and explicit resource caps.
- **Twitch lifecycle:** authorization code grant, state bound to an HTTP-only browser cookie, least-privilege user:read:chat, server-only refresh, hourly validation, keepalive timeout handling, inherited-subscription handoff and fresh subscriptions after unexpected loss.
- **Authority boundary:** browser components only render snapshots and send intentions. OBS gets a separate view token, never streamer authority. Origin checks protect mutations and WebSocket access.
- **Reproducible comparison:** the same snapshots/proposals yield 694 unsafe exits under unrestricted writes and none under checking across 3,000 intentionally adversarial cases. Raw timing, throughput and Python allocation output are included with workload limits.
- **Real integration evidence:** broadcaster OAuth and EventSub were connected, and one human-authorized real !lava message counted and applied three validated lava tiles. This was not a synthetic vote or an independent-viewer load test.
- **Clear limits:** one server process, ephemeral active sessions, no claimed public deployment or recorded OBS demo, no claim of thousands of simultaneously connected viewers.

See docs/VERIFICATION.md for actual test totals and final measured results. CI includes a container smoke test, but a configured workflow is not an executed CI result.
