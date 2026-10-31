"""Official OAuth + EventSub WebSockets. Tokens never leave this module."""
import asyncio
from collections import OrderedDict
from contextlib import suppress
from datetime import datetime, timezone
import json
import logging
import time
from urllib.parse import urlparse

import httpx
from websockets.asyncio.client import connect

log = logging.getLogger("crowdforge.twitch")
EVENTSUB_URL = "wss://eventsub.wss.twitch.tv/ws"


class TwitchFailure(Exception):
    """Safe, user-readable failure without request URLs or credentials."""


def valid_reconnect_url(url: str) -> bool:
    parsed = urlparse(url)
    return parsed.scheme == "wss" and parsed.hostname == "eventsub.wss.twitch.tv" and parsed.port in (None, 443) and parsed.username is None


class TwitchConnection:
    def __init__(self, client_id: str, secret: str, tokens: dict, on_message, status: dict):
        self.client_id, self.secret = client_id, secret
        self._tokens = tokens
        self._expires = time.monotonic() + tokens.get("expires_in", 0)
        self._validated = 0.0
        self._refresh_lock = asyncio.Lock()
        self.on_message = on_message
        self.status = status
        self.http = httpx.AsyncClient(timeout=15)
        self.task: asyncio.Task | None = None
        self.user_id = ""
        self.subscription_id: str | None = None
        self.seen: OrderedDict[str, float] = OrderedDict()

    async def validate_token(self):
        async with self._refresh_lock:
            if time.monotonic() > self._expires - 120:
                response = await self.http.post("https://id.twitch.tv/oauth2/token", data={
                    "grant_type": "refresh_token", "refresh_token": self._tokens["refresh_token"],
                    "client_id": self.client_id, "client_secret": self.secret})
                if response.status_code != 200:
                    raise TwitchFailure("Twitch authorization expired. Please reconnect.")
                self._tokens = response.json()
                self._expires = time.monotonic() + self._tokens["expires_in"]
            response = await self.http.get("https://id.twitch.tv/oauth2/validate", headers={"Authorization": "OAuth " + self._tokens["access_token"]})
            if response.status_code != 200:
                raise TwitchFailure("Twitch revoked authorization. Please reconnect.")
            identity = response.json()
            if identity.get("client_id") != self.client_id or "user:read:chat" not in identity.get("scopes", []):
                raise TwitchFailure("Twitch authorization is missing the required chat permission.")
            if self.user_id and self.user_id != identity["user_id"]:
                raise TwitchFailure("Twitch identity changed. Please reconnect.")
            self.user_id = identity["user_id"]
            self.status["channel"] = identity["login"]
            self._expires = time.monotonic() + identity.get("expires_in", 0)
            self._validated = time.monotonic()

    async def subscribe(self, session_id: str):
        response = await self.http.post("https://api.twitch.tv/helix/eventsub/subscriptions", headers={
            "Authorization": "Bearer " + self._tokens["access_token"], "Client-Id": self.client_id}, json={
            "type": "channel.chat.message", "version": "1",
            "condition": {"broadcaster_user_id": self.user_id, "user_id": self.user_id},
            "transport": {"method": "websocket", "session_id": session_id}})
        if response.status_code != 202:
            raise TwitchFailure(f"Twitch chat subscription failed (HTTP {response.status_code}). Reconnect to retry.")
        self.subscription_id = response.json()["data"][0]["id"]

    async def _reader(self, socket, queue: asyncio.Queue, timeout: float):
        try:
            while True:
                raw = await asyncio.wait_for(socket.recv(), timeout=timeout + 2)
                packet = json.loads(raw)
                await queue.put((socket, packet))
        except asyncio.CancelledError:
            raise
        except Exception:
            await queue.put((socket, None))

    async def listen(self):
        """Reconnect handoff keeps the old reader alive until the new welcome arrives."""
        queue: asyncio.Queue = asyncio.Queue(maxsize=1000)
        readers: dict = {}
        active = None
        try:
            active = await connect(EVENTSUB_URL, max_size=65536, max_queue=32, open_timeout=15)
            welcome = json.loads(await asyncio.wait_for(active.recv(), 15))
            if welcome.get("metadata", {}).get("message_type") != "session_welcome":
                raise TwitchFailure("Unexpected Twitch welcome message.")
            session = welcome["payload"]["session"]
            await self.subscribe(session["id"])
            readers[active] = asyncio.create_task(self._reader(active, queue, session["keepalive_timeout_seconds"]))
            self.status.update(state="connected", detail="Authenticated Twitch chat is live.")
            while True:
                try:
                    socket, packet = await asyncio.wait_for(queue.get(), timeout=60)
                except asyncio.TimeoutError:
                    await self.validate_token()
                    continue
                if time.monotonic() - self._validated > 3500 or time.monotonic() > self._expires - 120:
                    await self.validate_token()
                if packet is None:
                    if socket == active:
                        raise TwitchFailure("Twitch connection interrupted. Reconnecting…")
                    continue
                meta = packet.get("metadata", {})
                kind = meta.get("message_type")
                if kind == "notification":
                    payload = packet.get("payload", {})
                    sub = payload.get("subscription", {})
                    event = payload.get("event", {})
                    if sub.get("id") != self.subscription_id or sub.get("type") != "channel.chat.message" or sub.get("version") != "1":
                        continue
                    if event.get("broadcaster_user_id") != self.user_id:
                        continue
                    # Use transport timestamp plus chat message ID for window membership and retries.
                    stamp = datetime.fromisoformat(meta["message_timestamp"].replace("Z", "+00:00")).timestamp()
                    if abs(time.time() - stamp) > 60:
                        continue
                    message_id = event.get("message_id", "")
                    while self.seen and time.time() - next(iter(self.seen.values())) > 65:
                        self.seen.popitem(last=False)
                    if not message_id or message_id in self.seen or len(self.seen) >= 50000:
                        continue
                    self.seen[message_id] = time.time()
                    self.on_message(event.get("chatter_user_id", ""), event.get("message_id", ""), event.get("message", {}).get("text", ""), stamp)
                elif kind == "session_reconnect":
                    url = packet["payload"]["session"]["reconnect_url"]
                    if not valid_reconnect_url(url):
                        raise TwitchFailure("Twitch supplied an invalid reconnect endpoint.")
                    self.status.update(state="reconnecting", detail="Migrating Twitch connection…")
                    new = await connect(url, max_size=65536, max_queue=32, open_timeout=15)
                    try:
                        message = json.loads(await asyncio.wait_for(new.recv(), 15))
                        if message.get("metadata", {}).get("message_type") != "session_welcome":
                            raise TwitchFailure("Twitch reconnection did not receive a welcome.")
                    except BaseException:
                        await new.close()
                        raise
                    old, active = active, new
                    timeout = message["payload"]["session"]["keepalive_timeout_seconds"] or 10
                    readers[new] = asyncio.create_task(self._reader(new, queue, timeout))
                    # Old packets already enqueued are still processed and deduplicated by VoteWindow.
                    await old.close()
                    self.status.update(state="connected", detail="Authenticated Twitch chat is live.")
                elif kind == "revocation":
                    raise TwitchFailure("Twitch revoked the chat subscription. Reauthorize your account.")
        finally:
            for socket, task in readers.items():
                task.cancel()
                with suppress(asyncio.CancelledError):
                    await task
                await socket.close()
            if active:
                await active.close()

    async def run(self):
        delay = 1
        try:
            while True:
                try:
                    await self.validate_token()
                    await self.listen()
                except TwitchFailure as error:
                    if "revoked" in str(error) or "expired" in str(error) or "permission" in str(error):
                        self.status.update(state="error", detail=str(error))
                        return
                    self.status.update(state="reconnecting", detail=str(error))
                except (OSError, ValueError, KeyError, httpx.HTTPError, asyncio.TimeoutError):
                    self.status.update(state="reconnecting", detail="Twitch unavailable. Retrying with backoff.")
                except Exception:
                    # No exception body: upstream request objects can contain access tokens.
                    log.warning('{"event":"eventsub_transport_error"}')
                    self.status.update(state="reconnecting", detail="Twitch transport interrupted. Retrying.")
                await asyncio.sleep(delay)
                delay = min(30, delay * 2)
        except asyncio.CancelledError:
            raise

    async def close(self, revoke: bool = False):
        if self.task:
            self.task.cancel()
            with suppress(asyncio.CancelledError):
                await self.task
        if revoke:
            try:
                await self.http.post("https://id.twitch.tv/oauth2/revoke", data={"client_id": self.client_id, "token": self._tokens["access_token"]})
            except httpx.HTTPError:
                log.warning('{"event":"twitch_revoke_unavailable"}')
        self._tokens.clear()
        await self.http.aclose()
