# Submission readiness

**Current verdict: NOT READY.** The local game and evidence are implemented; account-dependent acceptance gates remain.

Deadline: **November 2, 2026 at 2 p.m. PST / 5 p.m. EST / 22:00 UTC**. Confirm the latest official rules immediately before submitting.

- [x] Project created from an empty repository during the submission period
- [x] Original game artwork and source
- [x] Working offline game, voting and constraint checks
- [x] Authenticated Twitch adapter implemented against official documentation
- [x] Production frontend build
- [x] Automated tests and raw benchmark evidence
- [x] Setup, deployment and OBS instructions
- [x] Devpost story, technical highlights, shot list and demo script
- [x] Actual principal Codex session ID preserved
- [ ] Entrant/team eligibility personally confirmed
- [x] Twitch app credentials configured in ignored local .env (values not included in evidence)
- [x] Real broadcaster authorization completed (leninathikam)
- [x] A real chat vote reaches the backend and changes the game (one explicitly authorized broadcaster test vote; independent-viewer playtest still pending)
- [ ] Real-account disconnect, refresh and reconnect behavior verified
- [x] Docker image/Compose runtime and persistent evidence exercised on [CI](https://github.com/leninathikam/CrowdForge/actions/runs/41215265874)
- [ ] Persistent public host configured, deployed and tested at its real URL
- [x] [Public source pushed](https://github.com/leninathikam/CrowdForge); public visibility and unauthenticated HTTP 200 verified
- [ ] Public YouTube demo under three minutes recorded and verified
- [ ] Final story updated with the measured live run and verified links
- [ ] Devpost form submitted before deadline
- [ ] Access maintained through judging; use later rules date Nov 15 absent organizer clarification

## Current external blockers

Twitch app credentials are now present in the ignored local .env, and real broadcaster authorization plus one chat-driven lava mutation were verified. Independent-viewer playtesting and a recorded live demo remain. GitHub was reauthenticated and the public repository was created at https://github.com/leninathikam/CrowdForge. Source was pushed and unauthenticated access returned HTTP 200. No persistent hosting credentials or public application URL are available. Docker is not installed on the workstation; Docker Compose and SQLite persistence passed on the CI runner. These do not prevent building, offline play, mocked integration testing or preparing deployment files, but they prevent declaring the project submission-ready.

## Values to submit

Repository / public application / YouTube: enter verified URLs only.

Codex session: `01a18fdb-87c8-7b72-a965-3fb9438d3c18`.

The official overview documents `/status` as a manual session-ID retrieval method. This repository's value was read from actual CODEX_SESSION_ID and CODEX_THREAD_ID metadata, with both matching.
