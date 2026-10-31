import asyncio
from contextlib import asynccontextmanager, suppress
from dataclasses import dataclass, field
import json
import logging
import os
from pathlib import Path
import secrets
import time
from urllib.parse import urlencode

import httpx
from fastapi import FastAPI, HTTPException, Request, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, ConfigDict, Field

from .engine import Game
from .logging_utils import TransportLogFilter
from .storage import RoundStore
from .twitch import TwitchConnection, TwitchFailure

logging.basicConfig(level=logging.INFO, format="%(message)s")
# HTTPX informational request logs could include the OAuth callback code in a URL.
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("httpcore").setLevel(logging.WARNING)
logging.getLogger("uvicorn.error").addFilter(TransportLogFilter())
ROOT = Path(__file__).resolve().parents[2]
PUBLIC_URL = os.getenv("PUBLIC_URL", "http://localhost:5173").rstrip("/")
ORIGINS = set(os.getenv("ALLOWED_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173,http://localhost:8000,http://127.0.0.1:8000").split(","))
CLIENT_ID = os.getenv("TWITCH_CLIENT_ID", "")
CLIENT_SECRET = os.getenv("TWITCH_CLIENT_SECRET", "")
REDIRECT_URI = os.getenv("TWITCH_REDIRECT_URI", PUBLIC_URL + "/api/auth/callback")
SECURE = PUBLIC_URL.startswith("https://")
sessions: dict[str, "Session"] = {}
oauth_states: dict[str, tuple[str, str, float]] = {}
store: RoundStore | None = None


@dataclass
class Session:
    owner: str
    game: Game
    overlay: str = field(default_factory=lambda: secrets.token_urlsafe(24))
    mode: str = "simulation"
    twitch_status: dict = field(default_factory=lambda: {"state": "disconnected", "channel": "", "detail": "Simulation Mode — no live Twitch connection."})
    twitch: TwitchConnection | None = None
    activity: float = field(default_factory=time.monotonic)
    saved: bool = False
    simulation_sequence: int = 0
    sockets: int = 0
    action_tokens: float = 20
    action_refill: float = field(default_factory=time.monotonic)
    live_eligible_after: float = field(default_factory=time.time)
    persisted_audits: int = 0

    def snapshot(self):
        state = self.game.state()
        state.update(mode=self.mode, twitch=self.twitch_status, twitch_configured=bool(CLIENT_ID and CLIENT_SECRET), twitch_redirect_uri=REDIRECT_URI)
        return state


def checkpoint(key: str, session: Session):
    if store:
        store.save(key, session.game, {"mode": session.mode, "twitch_connected": session.twitch_status["state"] == "connected", "channel": session.twitch_status["channel"]})
        session.persisted_audits = len(session.game.audit)


async def ticker():
    while True:
        await asyncio.sleep(.1)
        for key, session in list(sessions.items()):
            session.game.tick(.1)
            if len(session.game.audit) > session.persisted_audits:
                checkpoint(key, session)
            if session.game.phase in ("won", "lost") and not session.saved and store:
                checkpoint(key, session)
                session.saved = True
            if time.monotonic() - session.activity > 3600:
                if session.twitch:
                    await session.twitch.close()
                sessions.pop(key, None)
        for state, (_, _, created) in list(oauth_states.items()):
            if time.monotonic() - created > 600:
                oauth_states.pop(state, None)


@asynccontextmanager
async def lifespan(app: FastAPI):
    global store
    store = RoundStore(os.getenv("DATABASE_PATH", str(ROOT / "data" / "rounds.sqlite3")))
    task = asyncio.create_task(ticker())
    yield
    task.cancel()
    with suppress(asyncio.CancelledError):
        await task
    for key, session in sessions.items():
        checkpoint(key, session)
        if session.twitch:
            await session.twitch.close()
    store.close()
    sessions.clear()


app = FastAPI(title="CrowdForge", version="1.0.0", lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=list(ORIGINS), allow_credentials=True, allow_methods=["GET", "POST"], allow_headers=["Content-Type"])


@app.middleware("http")
async def security_headers(request: Request, call_next):
    if request.method == "POST" and request.headers.get("origin") not in ORIGINS:
        from fastapi.responses import JSONResponse
        return JSONResponse({"detail": "Request origin is not allowed."}, status_code=403)
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["Referrer-Policy"] = "no-referrer"
    if request.url.path.startswith("/api"):
        response.headers["Cache-Control"] = "no-store"
    return response


def get_session(key: str) -> Session:
    if key not in sessions:
        raise HTTPException(404, "Session expired. Create a new arena.")
    session = sessions[key]
    session.activity = time.monotonic()
    return session


def owner_session(key: str, request: Request) -> Session:
    session = get_session(key)
    if not secrets.compare_digest(session.owner, request.cookies.get("cf_owner", "")):
        raise HTTPException(403, "Streamer authorization required.")
    return session


class Create(BaseModel):
    model_config = ConfigDict(extra="forbid")
    seed: int = Field(default=1847, ge=0, le=2147483647)
    allow_changes: bool = True


class Action(BaseModel):
    model_config = ConfigDict(extra="forbid")
    action: str = Field(max_length=30)
    dx: int = Field(default=0, ge=-1, le=1)
    dy: int = Field(default=0, ge=-1, le=1)
    choice: str = Field(default="lava", pattern="^(lava|wall|bridge)$")
    count: int = Field(default=1, ge=1, le=20)


@app.get("/api/health")
async def health():
    return {"status": "ok", "schema": 1}


@app.post("/api/sessions")
async def create_session(body: Create, request: Request):
    if len(sessions) >= 100:
        raise HTTPException(503, "All arena slots are occupied. Try again later.")
    owner = request.cookies.get("cf_owner") or secrets.token_urlsafe(32)
    if sum(s.owner == owner for s in sessions.values()) >= 5:
        raise HTTPException(429, "Five arenas already open. Reuse your existing arena.")
    key = secrets.token_urlsafe(16)
    session = Session(owner, Game(body.seed, body.allow_changes))
    sessions[key] = session
    from fastapi.responses import JSONResponse
    response = JSONResponse({"id": key, "overlay_token": session.overlay, "state": session.snapshot()})
    response.set_cookie("cf_owner", owner, httponly=True, secure=SECURE, samesite="lax", max_age=86400)
    return response


@app.get("/api/sessions/{key}")
async def read_session(key: str, request: Request, token: str = ""):
    session = get_session(key)
    if not secrets.compare_digest(token, session.overlay):
        owner_session(key, request)
    return session.snapshot()


@app.post("/api/sessions/{key}/action")
async def act(key: str, body: Action, request: Request):
    session = owner_session(key, request)
    now = time.monotonic()
    session.action_tokens = min(20, session.action_tokens + (now - session.action_refill) * 20)
    session.action_refill = now
    if session.action_tokens < 1:
        raise HTTPException(429, "Streamer action rate exceeded.")
    session.action_tokens -= 1
    game = session.game
    if body.action in ("start", "resume", "reset", "freeze", "disconnect"):
        session.live_eligible_after = time.time()
    if body.action == "move":
        game.move(body.dx, body.dy)
    elif body.action == "reset":
        if store:
            store.save(key + ":" + secrets.token_hex(4), game)
        session.game = Game(game.seed, game.allow_changes)
        session.saved = False
        session.persisted_audits = 0
    elif body.action == "simulate":
        if session.mode != "simulation":
            raise HTTPException(409, "Synthetic votes are disabled while connected to Twitch.")
        for _ in range(body.count):
            session.simulation_sequence += 1
            seq = session.simulation_sequence
            game.cast(f"sim-{seq}", f"sim-message-{seq}", "!" + body.choice)
    elif body.action == "integrity_probe":
        if game.phase != "running":
            raise HTTPException(409, "Start a round before running the integrity diagnostic.")
        from .world import Mutation
        game.note("system", "Streamer requested an integrity diagnostic; this is not an audience vote.")
        game.mutate(Mutation(kind="wall", targets=[game.exit]), source=0)
    elif body.action == "disconnect":
        if session.twitch:
            await session.twitch.close(revoke=True)
            session.twitch = None
        session.mode = "simulation"
        session.twitch_status.update(state="disconnected", channel="", detail="Simulation Mode — Twitch disconnected.")
        if game.window:
            game.window.votes.clear()
    elif not game.control(body.action):
        raise HTTPException(409, "That control is unavailable in the current round state.")
    if body.action in ("pause", "integrity_probe"):
        checkpoint(key, session)
    return session.snapshot()


@app.get("/api/sessions/{key}/replay")
async def export_replay(key: str, request: Request):
    return owner_session(key, request).game.replay()


@app.websocket("/api/sessions/{key}/ws")
async def websocket_state(websocket: WebSocket, key: str, token: str = ""):
    session = sessions.get(key)
    if not session or websocket.headers.get("origin") not in ORIGINS:
        return await websocket.close(code=1008)
    if not (secrets.compare_digest(session.owner, websocket.cookies.get("cf_owner", "")) or secrets.compare_digest(session.overlay, token)):
        return await websocket.close(code=1008)
    if session.sockets >= 8:
        return await websocket.close(code=1013)
    await websocket.accept()
    session.sockets += 1
    try:
        while True:
            session.activity = time.monotonic()
            # Full snapshots provide bounded memory and reconnect synchronization.
            await asyncio.wait_for(websocket.send_json(session.snapshot()), timeout=2)
            try:
                message = await asyncio.wait_for(websocket.receive(), timeout=.1)
                if message["type"] == "websocket.disconnect":
                    break
                # This transport is read-only; control actions use authenticated POSTs.
                await websocket.close(code=1008)
                break
            except asyncio.TimeoutError:
                continue
    except (WebSocketDisconnect, RuntimeError, OSError, asyncio.TimeoutError):
        pass
    finally:
        session.sockets -= 1


@app.get("/api/auth/start")
async def auth_start(session: str, request: Request):
    owner_session(session, request)
    if not CLIENT_ID or not CLIENT_SECRET:
        raise HTTPException(503, "Set TWITCH_CLIENT_ID and TWITCH_CLIENT_SECRET on the server, then restart. See README.md.")
    if len(oauth_states) >= 500:
        raise HTTPException(429, "Too many pending authorization requests.")
    state = secrets.token_urlsafe(32)
    oauth_states[state] = (session, request.cookies["cf_owner"], time.monotonic())
    response = RedirectResponse("https://id.twitch.tv/oauth2/authorize?" + urlencode({"client_id": CLIENT_ID, "redirect_uri": REDIRECT_URI,
        "response_type": "code", "scope": "user:read:chat", "state": state, "force_verify": "true"}), status_code=303)
    response.set_cookie("cf_oauth", state, max_age=600, httponly=True, secure=SECURE, samesite="lax")
    return response


@app.get("/api/auth/callback")
@app.get("/auth/twitch/callback")
async def auth_callback(request: Request, state: str = "", code: str = "", error: str = ""):
    entry = oauth_states.pop(state, None)
    if not entry or not secrets.compare_digest(request.cookies.get("cf_oauth", ""), state) or not secrets.compare_digest(request.cookies.get("cf_owner", ""), entry[1]) or time.monotonic() - entry[2] > 600:
        raise HTTPException(400, "OAuth state is invalid or expired. Start authorization again.")
    session = get_session(entry[0])
    if error or not code:
        session.twitch_status.update(state="error", detail="Twitch authorization was declined. You can retry.")
    else:
        connection = None
        try:
            async with httpx.AsyncClient(timeout=15) as http:
                response = await http.post("https://id.twitch.tv/oauth2/token", data={"client_id": CLIENT_ID, "client_secret": CLIENT_SECRET,
                    "code": code, "grant_type": "authorization_code", "redirect_uri": REDIRECT_URI})
            if response.status_code != 200:
                raise TwitchFailure("Twitch rejected the authorization code. Try connecting again.")
            def ingest(user, message, text, timestamp):
                if timestamp < session.live_eligible_after:
                    return
                # Translate real UTC event time into the paused, authoritative round clock.
                sent = session.game.elapsed - max(0, time.time() - timestamp)
                session.game.cast(user, message, text, sent)
            connection = TwitchConnection(CLIENT_ID, CLIENT_SECRET, response.json(), ingest, session.twitch_status)
            await connection.validate_token()
            if session.twitch:
                await session.twitch.close()
            session.twitch = connection
            session.mode = "live"
            session.live_eligible_after = time.time()
            # Prevent synthetic votes from carrying into the first live vote.
            if session.game.window:
                from .voting import VoteWindow
                game = session.game
                game.window = VoteWindow(game.window.number + 1, game.elapsed, game.elapsed + 15, game.allow_changes)
            session.twitch_status.update(state="connecting", detail="Authorised. Connecting to Twitch EventSub…")
            connection.task = asyncio.create_task(connection.run())
        except (TwitchFailure, httpx.HTTPError, ValueError, KeyError) as failure:
            if connection:
                await connection.close()
            session.twitch_status.update(state="error", detail=str(failure) if isinstance(failure, TwitchFailure) else "Twitch authorization could not complete. Retry connection.")
    result = RedirectResponse(PUBLIC_URL + "/?session=" + entry[0], status_code=303)
    result.delete_cookie("cf_oauth")
    return result


if (ROOT / "dist" / "assets").exists():
    app.mount("/assets", StaticFiles(directory=ROOT / "dist" / "assets"), name="assets")


@app.get("/")
@app.get("/overlay")
async def frontend():
    if (ROOT / "dist" / "index.html").exists():
        return FileResponse(ROOT / "dist" / "index.html")
    raise HTTPException(503, "Build the frontend with npm run build, or open the Vite dev server on port 5173.")
