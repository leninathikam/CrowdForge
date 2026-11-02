# Evidence-based self-assessment

This is the **pre-upgrade baseline assessment**. See [JUDGE_READINESS.md](JUDGE_READINESS.md) for the current audit, updated scores and final verification.

Official criteria are equally weighted. These are conservative internal scores out of ten, not judge predictions or a claim about other entries.

**Innovation / Idea — 6/10.** A streamer controls a survival runner while chat mutates the arena. The distinct mechanism is transactional validation with a non-damaging escape-path invariant and explainable rejection. The benchmark demonstrates the difference from unrestricted changes. Audience-controlled games and reachability algorithms already exist; no novelty search or patent claim was performed.

**Potential Impact — 5/10.** One-command voting, a visible countdown, an OBS view and no separate viewer installation offer a practical streamer experience. The game runs offline and has a sub-two-minute loop. One real broadcaster vote changed the live world. Independent community playtesting and retention evidence are absent; an authentic recorded demo remains a submission gate.

**Technological implementation — 6/10.** The server owns state and time, validates commands, enforces access boundaries, handles authenticated EventSub lifecycle, deduplicates votes, checkpoints deterministic replay evidence and passes automated tests. A real broadcaster's authenticated chat vote applied validated lava. See VERIFICATION.md. Docker Compose startup and persistent evidence across restart passed on CI. Public hosting and prolonged live refresh/reconnect remain unverified. The single-process deployment has explicit limits and active sessions do not survive restarts.

**Design — 7/10.** Original pixel-inspired terrain and player, a clear exit, three distinct audience mutations, visible integrity feedback, responsive layout, reduced-motion handling and a read-only OBS view are implemented. Automated browser tests and captured screenshots support basic usability. External streamer feedback and OBS capture quality remain unverified. Mobile controls are supplementary; desktop is the primary target.

Current weighted mean: **6/10**. Highest-value next work: run an independent-viewer community round, deploy/test a public persistent host, record the authentic under-three-minute video and obtain feedback. Optional AI proposals, extra cosmetics or a larger feature list would not close those gaps.
