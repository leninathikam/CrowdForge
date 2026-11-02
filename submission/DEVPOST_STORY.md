# CrowdForge: The World Fights Back

## Inspiration

Twitch chat is good at turning a simple task into a shared event. We wanted the audience to shape the place a streamer was playing in, while keeping the result fair enough that the streamer could still react and make decisions.

## What it does

The streamer has 100 seconds to reach a portal in a small survival arena. Viewers vote with !lava, !wall or !bridge. Every fifteen seconds the winning choice changes the actual map. Lava damages the runner, walls change the route, and bridges open safe terrain.

The interesting part is the World Integrity Engine. It validates each proposal on a copy of the map and runs a breadth-first search before committing the change. If a mutation would remove the last route made of safe tiles, it is rejected with an explanation. It also protects the player, exit and boundaries, and keeps new lava away from the runner.

The audited version also limits added detours and checks the route against an explicit remaining-time estimate. An optional diagnostics view exposes real transport counters, validation timings and before/after tiles, and reconstructs a paused round to verify its state and mutation history. It does not guarantee human survival or pretend that a route-adjacency metric predicts damage.

## How we built it

React and TypeScript render a procedural canvas arena. A Python/FastAPI server owns the world, timer, movement and voting. Full versioned snapshots stream over WebSockets. The Twitch adapter uses the authorization code grant and EventSub channel.chat.message subscriptions. Tokens stay on the server, and votes are deduplicated and bounded per window.

There is also a clearly labeled offline simulation for development. It uses the same vote aggregation and mutation engine, but it is never presented as live Twitch chat. Completed round evidence can be exported and reconstructed from the seed and recorded inputs without retaining chat identities.

## How Codex was used

Codex built this project in the principal session recorded in docs/CODEX_EVIDENCE.md: rules research, repository setup, deterministic engine, Twitch adapter, frontend, automated tests, benchmark, deployment files and these submission drafts. The user configured the Twitch app and completed account consent. One authorized real broadcaster !lava message counted and applied three validated tiles. Human review and a recorded live demo are still needed before submission.

## Challenges

The hardest boundary was allowing chaos without allowing impossible terrain. Checking only collision-free reachability is insufficient: a path through lava can be technically traversable and still unfair. The validator instead requires a safe route.

Another challenge was handling network behavior honestly. EventSub reconnect handoff inherits subscriptions; unexpected connection loss requires a fresh subscription, and missed messages are not replayed by Twitch. Duplicate chat messages and older replacement votes must not count twice or overturn a newer vote.

Browser testing also exposed a real input race: the first movement could arrive while the start request was still pending. Queuing the latest movement fixed that interaction.

The audit found additional races: mode switches were missing from replay, and late POST responses could overwrite newer socket snapshots. Recorded window-reset inputs and a session-wide snapshot sequence now cover those cases; a delayed-response browser regression verifies that Pause is retained while movement is pending.

## Accomplishments and evidence

The offline gameplay loop works, the production frontend builds, and a real authenticated broadcaster vote changed the arena through EventSub. Automated tests exercise the engine, API, mocked Twitch transport and browser. In 3,000 adversarial seeded scenarios, unrestricted terrain writes produced 694 states without a safe exit; constraint checking produced zero. This is a controlled safety comparison, not a live audience capacity claim. Current raw measurements and verification status are in the repository.

The new independent-oracle evaluation compares identical proposals under unrestricted, original and upgraded policies. Across 1,800 intentionally adversarial cases, the original checker kept exits reachable but permitted 600 excessive-detour or time-budget outcomes; the upgraded policy permitted zero. It accepted only 9.78% of that hostile workload, so this is not a natural-play acceptance estimate. One hundred replay rounds and 209 checks with eight local observers produced zero mismatches. Final local checks passed 197 Python tests, 10 frontend tests and three browser scenarios.

## What we learned

A small deterministic system can make an interactive world feel unpredictable without giving up testability. Clear mode labels and visible failure states matter as much as the successful path, especially when demonstrating a live integration.

## Next steps

Finish deployment and the authentic recorded demo, gather independent-viewer feedback, and exercise prolonged token/reconnect behavior before considering adaptive mutation selection or a richer replay viewer. Natural-language proposals are optional; the core game works without an LLM.

## Submission links — fill only with verified values

- Repository URL: https://github.com/leninathikam/CrowdForge.
- Deployed application URL: not yet verified.
- Public YouTube demo URL: not yet recorded/uploaded.
- Codex session ID: `01a18fdb-87c8-7b72-a965-3fb9438d3c18` (actual environment metadata).

**Before submission:** add the final authentic Twitch rehearsal and recording results to the verified one-vote integration evidence. Do not remove caveats until their checks have been completed.
