# Deployment and live verification

This repository prepares a persistent single-process deployment. No public application URL has been verified. Docker is unavailable on the development workstation; the container and Compose files have not been executed here.

## Persistent host

Choose a host that runs a persistent Docker process with outbound HTTPS/WSS and inbound HTTPS/WebSocket support. Check its current pricing, sleep policies and persistent-volume behavior before purchasing; no free-tier assumptions are made. A static frontend host alone cannot run this Python authoritative server or its persistent Twitch EventSub connection. For that reason this build is not published as a disconnected static Sites page.

1. The source repository is public at https://github.com/leninathikam/CrowdForge. Clone it onto a host you control. Verify that judges can access the submitted source revision and installation instructions.
2. Install Docker/Compose on your chosen persistent host. Copy `.env.example` to `.env` on that host, outside version control.
3. Set `PUBLIC_URL=https://your-domain.example`, `ALLOWED_ORIGINS=https://your-domain.example`, `TWITCH_REDIRECT_URI=https://your-domain.example/api/auth/callback`, and your registered Twitch client ID and secret. Keep DATABASE_PATH at `/app/data/rounds.sqlite3` inside the container (omit DATABASE_PATH from the host .env or set it explicitly).
4. Register that **exact** redirect URI in Twitch's app console. A trailing slash or hostname difference breaks browser-bound OAuth.

   The server also accepts `/auth/twitch/callback` for an application already registered with that path. In that case set TWITCH_REDIRECT_URI to that exact URI, and set PUBLIC_URL to the same origin. The local account test used `http://localhost:8000/auth/twitch/callback`; use `http://localhost:8000` for the game with that configuration. Do not mix localhost and 127.0.0.1 during authorization.
5. Run `docker compose up --build -d`. Run one worker/replica only. The named `rounds` volume persists completed and reset-round evidence, not active sessions or access tokens.
6. Terminate TLS with your host's reverse proxy. Proxy `/` to `127.0.0.1:8000`, forward WebSocket upgrades and use an idle timeout comfortably above a minute. Do not cache `/api` or query-token overlay pages. Disable access logging of query strings on the proxy; OAuth callback URLs contain single-use codes and overlay URLs contain view tokens. Uvicorn access logging is already disabled.
7. Apply host-level request limits to session creation. Memory limits are bounded in-process but anonymous arena creation is not an internet-scale anti-abuse system. Never put a client secret into a VITE_* variable.
8. Test `https://your-domain.example/api/health`, then the actual frontend, login callback, real Twitch messages, end-to-end mutation, reconnect and overlay in OBS.
9. Keep the host running for judges through November 15, 2026, 5 p.m. Pacific, unless the organizer clarifies the inconsistent judging dates. Back up the named volume before replacing it.

## Minimum public smoke test

- Frontend returns 200 and builds match current source.
- `/api/health` returns status ok.
- A new arena starts, movement works and the runner can win.
- Allowed same-origin POSTs work; foreign-origin POSTs are rejected.
- Owner cookie has HttpOnly, SameSite=Lax and Secure over HTTPS.
- OAuth denial is handled, successful state is single-use, and a callback copied into another browser fails.
- Twitch shows authenticated connection status; another genuine viewer's message increments the vote.
- Window close visibly changes the map; no synthetic input is used during this live test.
- Disconnect/reconnect is visible and the current browser receives a full snapshot.
- Overlay URL displays without streamer controls and cannot perform POST actions without the owner cookie.
- Restart requires a fresh arena and Twitch authorization; completed-round evidence remains in SQLite.

Only mark deployment successful after testing its real URL. Localhost checks and CI configuration are not public deployment proof.
