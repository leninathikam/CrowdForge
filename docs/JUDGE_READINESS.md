# Judge readiness — 2 November 2026

**Verdict: NOT READY TO SUBMIT until the authentic public YouTube video, personal eligibility confirmation and final Devpost form are complete.** The working repository can satisfy the rules' access route; a separately hosted public app is desirable, not explicitly mandatory. Deadline rechecked against the [official rules](https://twitchcon-codex.devpost.com/rules): **today at 2 p.m. PST / 5 p.m. EST / 22:00 UTC**.

## Score before and after

These are conservative internal judgments, not external playtest results. Equal-weight criteria:

| Official criterion | Baseline | Updated | Supporting implementation and evidence |
|---|---:|---:|---|
| Innovation / Idea | 6 | 6.5 | `world.py::validate/route_metrics` adds explicit detour/time fairness to safe terrain transactions; `Diagnostics.tsx` exposes actual rejection and tile-diff proof. `test_integrity_v2.py` and the independent 1,800-case comparison substantiate behavior. BFS, replay and audience voting are established techniques; no novelty search is claimed. |
| Potential Impact | 5 | 5 | `VotingPanel.tsx` and read-only OBS lower audience friction; a real prior broadcaster vote worked. No independent-streamer feedback, retention data or multi-viewer rehearsal was added. The fixed corridor can be escaped before the first vote. Reliability work alone does not justify an impact increase. |
| Technological implementation | 6 | 7.5 | Replay covers mode changes and hashes control/window/audit state; sequence ordering spans reset; Twitch unsolicited pings disabled; checkpoint errors isolated; owner-only proof. 197 Python tests, 10 frontend tests, 100 replay rounds and 209 multi-observer comparisons support the improvement. Real soak, multi-process recovery and public abuse protection remain gaps. |
| Design | 7 | 7 | `Arena.tsx` interpolates acknowledged moves and signals damage; `ArenaPanel.tsx` adds a final-three-second forge cue; `Dialogs.tsx` contains keyboard focus/Escape; diagnostics stays optional and is reachable on mobile. These are useful improvements, but no fresh audience usability evidence justifies raising the score yet. |

**Mean: 6.0 → 6.5 / 10.** Stronger technical proof; still modest product differentiation. A visually polished shell does not solve pacing or retention.

Technical judge: fewer correctness holes, measurable guardrails, bounded single-writer design; still synchronous work in the event loop and limited failure/real-load evidence. Product judge: understandable commands and streamer controls; still no reason demonstrated for a community to return after several rounds. Skeptical judge: actual game and genuine earlier Twitch evidence, with new proof visible in-app; no AI wrapper, but established algorithms and one small arena require an excellent authentic demo to stand out.

## Implemented upgrades

- Integrity rules 2: duplicate-target conflict rejection, safe-route/exposure metrics, 12-step detour limit and remaining-time feasibility check, atomic tile diffs and informative rejection.
- Replay: explicit mode-window reset inputs; fuller digest; legacy rules replay; owner-only in-app reconstruction.
- Reliability: ordered POST/socket snapshots across round reset, pending streamer controls retained behind a delayed request, SQLite checkpoint failure visibility, Twitch client ping correction and real transport counters.
- Experience: 90ms server-acknowledged movement interpolation, restrained damage border, forging countdown, keyboard modal containment/Escape and mobile diagnostics entry.
- Evidence: independent baseline/v1/v2 oracle, 100 replay scenarios and real eight-observer transport verification; new checks included in CI.

## Verification ledger

Final local verification on 2 November: **197 Python tests passed in 22.33s** under a fresh Python 3.12.14 environment (earlier upgraded run also passed on 3.14.3); **10 Vitest tests passed**; **3 Playwright scenarios passed**, including delayed movement/Pause ordering, complete gameplay/proof/OBS/reload/win/export/reset, and mobile modal focus containment. The extended gameplay scenario took 49.3s. TypeScript/Vite production build passed: JS 267.62kB / 85.72kB gzip, CSS 29.77kB / 7.29kB gzip.

Exported winning replay verified at 26.0 round seconds, digest `ab3c136af62f278d6ac3ecbf77b4bf9d9e3bffe9e1d72a0601415f165189ef13`. Desktop and mobile diagnostics screenshots were inspected; the proof and actual tile diff are legible and mobile content scrolls without horizontal overflow. One upstream Starlette/httpx deprecation warning remains. During environment recovery, an initial test collection ran before dependency installation finished; the complete post-install run above passed.

See [EVALUATION_RESULTS.md](EVALUATION_RESULTS.md) for raw measurements and [CURRENT_STATE_AUDIT.md](CURRENT_STATE_AUDIT.md) for baseline findings. Earlier CI links in VERIFICATION.md refer to the pre-upgrade source; final upgrade CI is recorded separately.

## Deadline plan

1. Reconnect Twitch in the updated local build, use a genuine viewer or clearly identify a broadcaster test, and capture a vote closing into a real mutation. Preserve the replay before closing the server. No additional public chat posts have been authorized or sent during this audit.
2. Record the revised 2:45 script: gameplay, real Twitch receipt, safety rejection, replay proof, measured benchmark and actual Codex work. Upload to **public YouTube**, verify signed-out access and paste the real watch URL into the form. A generated/mock video cannot substitute.
3. Confirm entrant/team eligibility personally, review the factual story/source and session ID, then submit Devpost before the cutoff. Submission accepts official terms and remains a user action.
4. Maintain free source/run access through 15 November, 5 p.m. Pacific. Public hosting is optional if the runnable-repository route is adequate; do not spend the remaining submission window rewriting deployment architecture.

## Remaining risks and deferred work

No active-session recovery after restart, no fresh real token-expiry/reconnect soak, no independent-viewer retention/playtest, no confirmed public host/TLS or real OBS recording. Fixed-step ticker can drift under event-loop load; SQLite and proof work are synchronous. Anonymous creation requires edge limits; owner command logs can grow through repeated paused controls. Decoder validates core snapshot shape, not every nested diagnostic. Canvas is not fully nonvisual accessible. Exposure and escape timing are explicit approximations, not guarantees of human survival.

Factions/resources, adaptive director, route-aware strategic selection, full replay scrubber, extra maps/progression and runtime AI are deferred. Their implementation and balancing risk exceeds their demonstrated benefit before today's deadline.
