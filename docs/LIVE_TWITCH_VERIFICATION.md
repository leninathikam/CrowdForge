# Real Twitch verification

The principal Codex session observed a genuine Twitch account authorization and chat-driven mutation. This was not the Simulation Lab.

The user configured the application's client ID/secret in the ignored local `.env`. Twitch reported that the registered callback was `http://localhost:8000/auth/twitch/callback`, so the local configuration was aligned to that URI and the backend now accepts that callback alias alongside `/api/auth/callback`. PUBLIC_URL was aligned to `http://localhost:8000` to keep browser cookies on the same origin.

After human account sign-in and explicit authorization, CrowdForge displayed **TWITCH CONNECTED** for `leninathikam`, and the adapter reported authenticated chat live. The Simulation Lab controls were absent and the UI stated that synthetic votes were disabled.

An initial real `!lava` message arrived while the arena was Ready and was not counted. The user then explicitly authorized one additional `!lava` broadcaster test message during a running round. The Twitch chat showed that real message, and CrowdForge's current lava vote count became **1**.

At round time **00:15**, the vote closed, the UI showed **LAVA FORGED**, and the feed recorded **“Lava applied. Safe route preserved. World mutation committed.”** The mutation changed three tiles and the chaos score became **30**. The impact timeline showed one counted vote. The round was paused after observation.

This proves the path: human-authorized real Twitch message → official EventSub transport → vote aggregation → window close → integrity validation → authoritative mutation → visible browser state.

## Evidence limits

- This was one broadcaster test vote, not multiple independent viewers or a community load test.
- The observation is recorded in the principal Codex chat and `artifacts/live-twitch-verification.json`.
- The raw replay for that paused round was not downloaded before the interrupted continuation reset the local process. The observational JSON is explicitly not a fabricated replay. Automated winning-round replay evidence is available separately.
- To avoid losing future evidence, SQLite now checkpoints every mutation and pause, plus terminal rounds and graceful shutdown. OAuth tokens and chat identities remain excluded.
- Live token expiry, revocation, extended reconnect behavior, independent-viewer playtesting, public hosting and an OBS/YouTube recording remain separate verification work.
- A server restart still requires a new game session and Twitch authorization. Use the PUBLIC_URL configured in `.env`; for this tested app that is `http://localhost:8000`.

No client secret, access token, refresh token, owner cookie or view token is included in this record.
