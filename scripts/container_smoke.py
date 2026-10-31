"""Exercise the real packaged HTTP application before a Compose restart."""
from http.cookiejar import CookieJar
import json
from urllib.request import HTTPCookieProcessor, Request, build_opener

origin = "http://127.0.0.1:8000"
client = build_opener(HTTPCookieProcessor(CookieJar()))


def post(path: str, body: dict) -> dict:
    request = Request(origin + path, data=json.dumps(body).encode(), headers={"Content-Type": "application/json", "Origin": origin})
    with client.open(request, timeout=5) as response:
        assert response.status == 200
        return json.load(response)


created = post("/api/sessions", {"seed": 7731})
key = created["id"]
assert post(f"/api/sessions/{key}/action", {"action": "start"})["phase"] == "running"
assert post(f"/api/sessions/{key}/action", {"action": "pause"})["phase"] == "paused"
with client.open(origin, timeout=5) as response:
    assert "CrowdForge" in response.read().decode()
print("Packaged frontend, authenticated actions, and paused-round checkpoint passed.")
