# CrowdForge: The World Fights Back

**One streamer. One world. Thousands of unpredictable architects.**

A working browser survival game. You run to the portal; Twitch chat votes every 15 seconds to forge lava, walls or bridges. The server checks every change against a safe-path invariant before committing it.

**Readiness: NOT READY for hackathon submission until an authentic demo recording and public application deployment verification are completed. Real broadcaster authorization and one live chat-driven mutation have been verified.** Offline gameplay, production builds and test evidence are separate from that acceptance gate. See [verification](docs/VERIFICATION.md).

## Run locally

Requires Node 22.12+ and Python 3.14 (the tested Python version). Use a fresh virtual environment.

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
npm ci
npm run build
Copy-Item .env.example .env
python scripts/serve.py
```

Open **http://127.0.0.1:8000**. The default is explicitly labeled **Simulation Mode**. Click **Enter the arena**, move with WASD/arrows, and use the three Simulation Lab buttons to cast synthetic votes. A winning mutation appears after 15 seconds. Space pauses the game and vote timer. Reach the cyan portal within 100 seconds. Lava deals 22 HP/second; walls block movement; bridges are safe.

On macOS/Linux activate with `source .venv/bin/activate`; copy the environment file with `cp .env.example .env`.

For frontend hot reload, set `PUBLIC_URL=http://localhost:5173` and `TWITCH_REDIRECT_URI=http://localhost:5173/api/auth/callback` in `.env`; run `python scripts/serve.py` and `npm run dev` in separate terminals, then open http://localhost:5173. Vite proxies API and WebSocket traffic. Always use one consistent hostname: OAuth cookies bind the login to that browser origin.

The launcher loads simple `KEY=value` assignments from `.env`, optionally quoted, without executing shell code or expanding variables. Existing environment variables take precedence. Direct `uvicorn` commands do not load `.env`; pass environment variables explicitly or use the launcher.

## Connect real Twitch chat

1. Register a Twitch app at https://dev.twitch.tv/console/apps. Twitch requires the account prerequisites shown in that console, including 2FA where required.
2. Add the exact redirect URI: `http://127.0.0.1:8000/api/auth/callback` for the default local setup.
3. Put `TWITCH_CLIENT_ID`, `TWITCH_CLIENT_SECRET`, `PUBLIC_URL` and `TWITCH_REDIRECT_URI` in `.env`. Never put the secret in a frontend variable or commit `.env`.
4. Restart the server. Click **Connect Twitch**, sign in as the channel's broadcaster, and grant the single `user:read:chat` scope. The broadcaster is also the reading user; no separate bot account or chat-write scope is required.
5. Wait for **TWITCH CONNECTED**, start a round, and have real viewers send `!lava`, `!wall`, `!bridge` or `!vote 1`, `!vote 2`, `!vote 3`.
6. Watch counts and the world change. Synthetic votes are disabled in live mode. Disconnect revokes the access token and returns to labeled simulation.

This integration uses Twitch's official authorization code grant and EventSub `channel.chat.message` version 1 over an outbound TLS WebSocket. OAuth state is single-use, expires after ten minutes and is bound to the browser's HTTP-only owner cookie. Tokens stay in server memory, refresh before expiry and validate on connection and at least hourly. A server restart requires reauthorization; no OAuth tokens are stored in SQLite. Session cookies use Secure when PUBLIC_URL is HTTPS.

Votes count once per user per window, with optional changes after a one-second cooldown. Older replacement messages cannot overwrite newer votes. Ties rotate lava → wall → bridge by window number. No votes means no mutation. Windows use authoritative round time; delayed events from a closed window or a paused/resumed interval are rejected. Twitch does not replay messages lost during an outage. Reconnect status is visible.

`!help` is explained in the in-app guide. This read-only connection does **not** send automatic chat replies.

## OBS

Click the broadcast icon in the left rail. Copy the **read-only overlay URL**, add an OBS **Browser** source, set 1920 × 1080, and paste the URL. The overlay shows the arena, votes, integrity indicator and event feed; streamer controls remain in the original tab. Use that original tab for keyboard movement. Enable OBS's interact/focus options only when appropriate to your scene; OBS is not required to play.

The overlay token grants viewing only. It cannot reset, move, cast synthetic votes, export replays or connect Twitch. Reset keeps the overlay URL; creating a new arena changes it. Tokens expire with the in-memory session (one hour without activity or a process restart). Do not put the streamer owner cookie into OBS.

## Architecture

React + TypeScript + Vite render an original procedural canvas arena. Canvas 2D is sufficient for a 24 × 16 grid, so Phaser and a CSS framework were intentionally unnecessary. FastAPI owns all game state, movement, timers, voting and world changes. Browser POSTs send streamer intentions; a read-only WebSocket delivers full versioned state at approximately 10 Hz. Reconnection receives a complete current snapshot.

`world.py` owns seeded map generation, BFS safe reachability, schema checks and copy-before-commit validation. `engine.py` owns the round state machine and replay commands. `voting.py` owns fairness and bounded aggregation. `twitch.py` owns OAuth tokens and the EventSub lifecycle. `main.py` owns origin/owner checks, session lifecycle and transport. SQLite checkpoints mutations, pauses, completed/reset rounds and graceful shutdown evidence without chat identities or tokens.

The mutation protocol is PROPOSED → VALIDATING → ACCEPTED → APPLIED, or PROPOSED → VALIDATING → REJECTED. Audit records carry a round-scoped unique ID, source window, target tiles, explanation, round-clock timestamp and before/after versions. Rejection changes only audit statistics and feed entries; the grid and world version stay unchanged. Lava cannot appear on or adjacent to the player. The exit and boundary are immutable. Bridges turn wall/lava into safe terrain. The validator requires a route with **no lava**, not just a technically traversable damaging route. Bounded target selection tries at most 240 candidates. BFS is appropriate for an unweighted 384-tile map; A* and connected-component infrastructure add no benefit here.

One process is authoritative. Run **one Uvicorn worker** and one replica. Active games are memory-resident and do not survive a server restart. Sessions are capped at 100 per process and five per owner cookie; each has eight observer socket slots. Creation is unauthenticated, so use infrastructure request limits before exposing this beyond a controlled judging deployment. Streamer actions use a 20/second token bucket with a burst of 20, in addition to the movement cooldown. Voting is capped at 20,000 distinct message IDs per window; transport deduplication is bounded at 50,000 IDs over 65 seconds. Socket queues are bounded; slow viewers disconnect after a two-second send timeout. These are resource limits, not verified simultaneous-viewer claims.

## Test and reproduce evidence

```powershell
python -m pytest -q
npm test
npm run build
# Start the server in another terminal first:
npx playwright install chromium
npm run test:e2e
python scripts/replay.py artifacts/e2e-replay.json
python benchmarks/run.py
```

Tests cover movement, collision, health, timers, transitions, generated maps, atomic mutation rejection, vote deduplication/order/cooldowns/ties/capacity, OAuth state, simulated EventSub handoff/revocation, access controls, WebSocket synchronization, frontend snapshot validation and the complete browser gameplay loop. Mocked EventSub tests alone do not prove a real Twitch account has connected. A separate real broadcaster test was observed in this build: one !lava vote applied three validated lava tiles; see docs/LIVE_TWITCH_VERIFICATION.md.

Download a replay from the Audience Impact Timeline. `python scripts/replay.py path/to/download.json` reconstructs the initial seed and recorded server inputs and verifies the final SHA-256 state digest. Replays retain aggregate votes, not Twitch chatter identities. The UI timeline shows the key events; the CLI performs the deterministic reconstruction.

Chaos score = 10 × changed distinct tiles + 2 × positive safe-path length increase, accumulated for accepted mutations. It is a transparent game score, not a scientific attribution metric. Emergency rescue and rejected proposals do not add points.

Raw measurements and methodology are in [benchmarks](benchmarks/README.md). Results depend on the machine and workload. No claim of thousands of simultaneously connected viewers is made.

## Deploy

Copy `.env.example`, set your HTTPS PUBLIC_URL, exact ALLOWED_ORIGINS and Twitch redirect URI, then:

```sh
docker compose up --build -d
```

The container serves both frontend and backend, exposes `/api/health`, uses a non-root account and persists round evidence in a named volume. Put a TLS reverse proxy in front of the loopback-bound port and enable WebSocket upgrades. See [deployment instructions](docs/DEPLOYMENT.md). Docker is unavailable on this workstation, but [CI](https://github.com/leninathikam/CrowdForge/actions/runs/41215265874) successfully built and launched Compose, exercised real HTTP controls, restarted the service and verified SQLite evidence persisted in the named volume.

Public source repository: https://github.com/leninathikam/CrowdForge. No public application deployment or YouTube video is claimed. [Submission materials](submission/SUBMISSION_CHECKLIST.md) list exact remaining steps and the actual Codex session evidence.

## Assets and ownership

Game tiles, the knight, portal and effects are procedural artwork authored in this repository. No copyrighted game assets or music are used. Code is MIT licensed. Lucide icons are ISC licensed; React, Vite and TypeScript carry their upstream licenses. The optional Google Fonts CSS requests Barlow Condensed, DM Sans and IBM Plex Mono (SIL Open Font License); offline browsers use system fallbacks. Their unmodified upstream font service remains external. Review dependency license notices before distribution.
