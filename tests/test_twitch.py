import asyncio
from datetime import datetime, timezone
import json

import httpx
import pytest

from apps.server import twitch


@pytest.mark.parametrize("url,valid", [("wss://eventsub.wss.twitch.tv/ws?token=abc", True), ("wss://evil.example/ws", False), ("ws://eventsub.wss.twitch.tv/ws", False), ("wss://eventsub.wss.twitch.tv.evil.example", False), ("wss://user@eventsub.wss.twitch.tv", False)])
def test_reconnect_origin(url, valid):
    assert twitch.valid_reconnect_url(url) == valid


def test_token_validation_refresh_and_permission_errors():
    async def scenario():
        calls = []
        def handler(request):
            calls.append(request.url.path)
            if request.url.path.endswith("token"):
                return httpx.Response(200, json={"access_token": "refreshed", "refresh_token": "r2", "expires_in": 3600})
            return httpx.Response(200, json={"client_id": "client", "user_id": "123", "login": "runner", "scopes": ["user:read:chat"], "expires_in": 3600})
        connection = twitch.TwitchConnection("client", "secret", {"access_token": "expired", "refresh_token": "r", "expires_in": 0}, lambda *a: None, {})
        await connection.http.aclose()
        connection.http = httpx.AsyncClient(transport=httpx.MockTransport(handler))
        await connection.validate_token()
        assert connection.user_id == "123"
        assert calls == ["/oauth2/token", "/oauth2/validate"]
        await connection.close()
        assert not connection._tokens
    asyncio.run(scenario())


def test_eventsub_handoff_notification_dedup_and_subscription(monkeypatch):
    async def scenario():
        received, status, subscriptions = [], {}, []
        def packet(kind, payload):
            return {"metadata": {"message_type": kind, "message_timestamp": datetime.now(timezone.utc).isoformat()}, "payload": payload}
        welcome = packet("session_welcome", {"session": {"id": "session1", "keepalive_timeout_seconds": 10}})
        notification = packet("notification", {"subscription": {"id": "sub1", "type": "channel.chat.message", "version": "1"}, "event": {"broadcaster_user_id": "123", "chatter_user_id": "456", "message_id": "chat1", "message": {"text": "!wall"}}})
        reconnect = packet("session_reconnect", {"session": {"reconnect_url": "wss://eventsub.wss.twitch.tv/ws?reconnect=1"}})
        revoked = packet("revocation", {"subscription": {"status": "authorization_revoked"}})
        class Socket:
            def __init__(self, messages):
                self.messages = asyncio.Queue()
                for message in messages:
                    self.messages.put_nowait(json.dumps(message))
                self.closed = False
            async def recv(self):
                return await self.messages.get()
            async def close(self):
                self.closed = True
        old, new = Socket([welcome, notification, reconnect]), Socket([welcome, notification, revoked])
        async def connect(url, **kwargs):
            if "reconnect" in url:
                assert not old.closed, "Old connection must remain open through new welcome"
                return new
            return old
        monkeypatch.setattr(twitch, "connect", connect)
        def handler(request):
            subscriptions.append(json.loads(request.content))
            return httpx.Response(202, json={"data": [{"id": "sub1"}]})
        connection = twitch.TwitchConnection("client", "secret", {"access_token": "test", "expires_in": 3600}, lambda *args: received.append(args), status)
        await connection.http.aclose()
        connection.http = httpx.AsyncClient(transport=httpx.MockTransport(handler))
        connection.user_id = "123"
        connection._validated = __import__('time').monotonic()
        with pytest.raises(twitch.TwitchFailure, match="revoked"):
            await asyncio.wait_for(connection.listen(), 2)
        assert len(received) == 1 and received[0][2] == "!wall"
        assert len(subscriptions) == 1, "Handoff inherits subscriptions instead of creating duplicates"
        assert subscriptions[0]["condition"] == {"broadcaster_user_id": "123", "user_id": "123"}
        assert old.closed and new.closed
        await connection.close()
    asyncio.run(scenario())
