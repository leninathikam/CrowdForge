# Feature inventory

## Implemented

- Original 24 × 16 seeded arena, procedural pixel terrain/player/portal, WASD/arrows and supplementary touch movement.
- Server-authoritative collision, damaging lava, 100 HP, 100-second timer, exit win, timeout/health loss, reset and pause/resume.
- Visible emergency rescue, vote freeze/unfreeze and an explicitly labeled integrity diagnostic.
- Lava Surge, Wall Forge and Bridge Builder with legal-transform rules, entity/boundary protection, a lava safety buffer, safe BFS reachability and atomic commit/rejection audit.
- Fifteen-second vote windows, one vote per user, optional vote changes, cooldown, out-of-order rejection, message deduplication, rotating ties, no-vote no-op and capacity limits.
- Real Twitch OAuth, single-use browser-bound state, server-only secrets/tokens, token validation/refresh, EventSub chat subscription, keepalive/reconnect/revocation handling, status and disconnect.
- Labeled simulation adapter, synthetic votes disabled in live mode, versioned WebSocket snapshots, full-state browser reconnection and separate observer access.
- Welcome/landing arena, Twitch setup, voting choices and counts, health/timer, mutation feedback, world feed, round results, settings/help and read-only OBS view.
- Event timeline, aggregate replay export and deterministic CLI reconstruction/digest verification; transparent chaos score.
- SQLite evidence checkpoints on mutations/pauses, terminal/reset rounds and graceful shutdown; active sessions remain memory-resident.
- Production build, health endpoint, origin/owner checks, bounded queues/actions/sessions, log redaction, Docker/Compose preparation, CI, benchmark and submission drafts.

## Verified

Automated engine/API/mock-transport/frontend/browser tests, actual local production serving, deterministic exported replay, synthetic mutation/vote benchmarks, loopback transport timing, short headless rendering timing, responsive screenshots and one **real broadcaster Twitch vote applying a lava mutation**. See VERIFICATION.md and LIVE_TWITCH_VERIFICATION.md.

## Prepared but externally unverified

Public deployment, remotely executed CI, Docker runtime/Compose volume behavior, real OBS capture, extended live token/reconnect behavior, independent-viewer load and a public YouTube demo. Remote source publication needs a working GitHub/GitLab/Bitbucket login.

## Deliberately omitted optional work

Supply Drop, Adaptive Chaos Director, natural-language/LLM proposals, cosmetics/progression, extra maps and a frame-by-frame graphical replay player. The implemented timeline and CLI reconstruction provide the replay evidence. No optional feature is presented as complete.
