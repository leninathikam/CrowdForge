import asyncio
import json
import os
import sqlite3
import time

from fastapi.testclient import TestClient
import pytest

from apps.server import main

ORIGIN = {"Origin": "http://localhost:5173"}


@pytest.fixture
def client(tmp_path, monkeypatch):
    monkeypatch.setenv("DATABASE_PATH", str(tmp_path / "rounds.sqlite3"))
    main.oauth_states.clear()
    with TestClient(main.app, headers=ORIGIN) as client:
        yield client


def create(client):
    result = client.post("/api/sessions", json={})
    assert result.status_code == 200
    return result.json()


def test_full_websocket_vote_mutation_and_reconnect(client):
    data = create(client)
    key = data["id"]
    assert client.post(f"/api/sessions/{key}/action", json={"action": "start"}).status_code == 200
    session = main.sessions[key]
    assert session.game.cast("real-adapter-test", "msg1", "!wall")
    assert not session.game.cast("real-adapter-test", "msg1", "!wall")
    for _ in range(150):
        session.game.tick(.1)
    with client.websocket_connect(f"/api/sessions/{key}/ws") as ws:
        snapshot = ws.receive_json()
        assert snapshot["schema"] == 1 and snapshot["stats"]["accepted"] == 1
        version = snapshot["version"]
    with client.websocket_connect(f"/api/sessions/{key}/ws") as ws:
        assert ws.receive_json()["version"] >= version
    assert client.get(f"/api/sessions/{key}/replay").json()["audit"][0]["accepted"]


def test_origin_owner_and_overlay_permissions(client):
    data = create(client)
    key = data["id"]
    assert client.post("/api/sessions", json={}, headers={"Origin": "https://evil.example"}).status_code == 403
    client.cookies.clear()
    assert client.get(f"/api/sessions/{key}").status_code == 403
    assert client.post(f"/api/sessions/{key}/action", json={"action": "start"}).status_code == 403
    assert client.get(f"/api/sessions/{key}?token={data['overlay_token']}").status_code == 200
    with client.websocket_connect(f"/api/sessions/{key}/ws?token={data['overlay_token']}") as ws:
        assert ws.receive_json()["phase"] == "ready"
    assert client.get(f"/api/sessions/{key}/replay").status_code == 403


def test_configuration_and_bad_auth_state(client):
    data = create(client)
    assert client.get("/api/health").json()["status"] == "ok"
    assert client.get("/api/auth/callback?state=forged&code=forged").status_code == 400
    assert client.get("/auth/twitch/callback?state=forged&code=forged").status_code == 400
    assert client.get("/api/auth/start?session=" + data["id"]).status_code == 503
    assert client.post("/api/sessions", json={"seed": -1}).status_code == 422
    assert client.post("/api/sessions", json={"seed": 1, "extra": "no"}).status_code == 422


def test_simulation_is_blocked_in_live_mode_and_action_limits(client):
    data = create(client)
    session = main.sessions[data["id"]]
    session.mode = "live"
    response = client.post(f"/api/sessions/{data['id']}/action", json={"action": "simulate", "choice": "lava"})
    assert response.status_code == 409
    session.action_tokens = 0
    session.action_refill = time.monotonic()
    assert client.post(f"/api/sessions/{data['id']}/action", json={"action": "start"}).status_code == 429


def test_streamer_integrity_diagnostic_is_atomic_and_labeled(client):
    data = create(client)
    key = data["id"]
    game = main.sessions[key].game
    game.control("start")
    before = [row[:] for row in game.grid]
    result = client.post(f"/api/sessions/{key}/action", json={"action": "integrity_probe"})
    assert result.status_code == 200
    assert result.json()["stats"]["rejected"] == 1
    assert result.json()["stats"]["votes"] == 0
    assert game.grid == before
    assert "not an audience vote" in game.events[-2]["text"]


def test_pause_preserves_evidence_without_auth_tokens(client):
    data = create(client)
    key = data["id"]
    main.sessions[key].game.control("start")
    assert client.post(f"/api/sessions/{key}/action", json={"action": "pause"}).status_code == 200
    with sqlite3.connect(os.environ["DATABASE_PATH"]) as connection:
        record = json.loads(connection.execute("SELECT replay FROM rounds WHERE id=?", (key,)).fetchone()[0])
    assert record["provenance"]["mode"] == "simulation"
    assert record["commands"][-1] == {"op": "control", "action": "pause"}
    assert "access_token" not in record and "refresh_token" not in record


def test_single_use_oauth_state_bound_to_browser(client, monkeypatch):
    monkeypatch.setattr(main, "CLIENT_ID", "test-client")
    monkeypatch.setattr(main, "CLIENT_SECRET", "test-secret")
    data = create(client)
    response = client.get("/api/auth/start?session=" + data["id"], follow_redirects=False)
    assert response.status_code == 303
    state = client.cookies["cf_oauth"]
    assert "scope=user%3Aread%3Achat" in response.headers["location"]
    assert client.get(f"/api/auth/callback?state={state}&error=access_denied", follow_redirects=False).status_code == 303
    assert client.get(f"/api/auth/callback?state={state}&error=access_denied").status_code == 400
    assert main.sessions[data["id"]].twitch_status["state"] == "error"


def test_proof_is_owner_only_and_snapshot_order_survives_reset(client):
    data = create(client)
    key = data["id"]
    url = f"/api/sessions/{key}"
    client.post(url + "/action", json={"action": "start"})
    assert client.get(url + "/proof").status_code == 409
    client.post(url + "/action", json={"action": "disconnect"})
    paused = client.post(url + "/action", json={"action": "pause"}).json()
    proof = client.get(url + "/proof").json()
    assert proof["matches"] and proof["audit_matches"]
    reset = client.post(url + "/action", json={"action": "reset"}).json()
    assert reset["snapshot_sequence"] > paused["snapshot_sequence"]
    assert reset["round_id"] != paused["round_id"]
    assert reset["version"] == 0
    client.cookies.clear()
    assert client.get(url + "/proof?token=" + data["overlay_token"]).status_code == 403


def test_checkpoint_failure_is_visible_without_crashing_round(client, monkeypatch):
    data = create(client)
    session = main.sessions[data["id"]]
    def fail(*args, **kwargs):
        raise sqlite3.OperationalError("disk unavailable")
    monkeypatch.setattr(main.store, "save", fail)
    main.checkpoint(data["id"], session)
    assert "save failed" in session.snapshot()["diagnostics"]["persistence"]
    assert session.game.control("start")
    session.game.tick(.1)
    assert session.game.elapsed == .1
