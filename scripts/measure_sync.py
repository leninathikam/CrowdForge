"""Real loopback fan-out, reset and reconnect checks; synthetic inputs, not Twitch load."""
import asyncio
from contextlib import AsyncExitStack
import json
from pathlib import Path
import statistics
import sys
import time

import httpx
from websockets.asyncio.client import connect


async def run(base):
    origin = base.rstrip("/")
    latencies, failures, checks = [], [], 0
    async with httpx.AsyncClient(base_url=origin, headers={"Origin": origin}, timeout=10) as http:
        result = await http.post("/api/sessions", json={})
        result.raise_for_status()
        created = result.json()
        key, token = created["id"], created["overlay_token"]
        url = origin.replace("http", "ws", 1) + f"/api/sessions/{key}/ws?token={token}"
        async def act(action, **extra):
            response = await http.post(f"/api/sessions/{key}/action", json={"action": action, **extra})
            response.raise_for_status()
            return response.json()
        async def until(ws, predicate):
            async with asyncio.timeout(5):
                while True:
                    state = json.loads(await ws.recv())
                    if predicate(state): return state
        async with AsyncExitStack() as stack:
            sockets = [await stack.enter_async_context(connect(url, origin=origin)) for _ in range(8)]
            for ws in sockets: await ws.recv()
            await act("start")
            for i in range(24):
                await asyncio.sleep(.11)
                start = time.perf_counter()
                issued = await act("simulate", choice="lava")
                target = issued["vote"]["total"]
                observed = await asyncio.gather(*(until(ws, lambda state: state["vote"]["total"] >= target) for ws in sockets))
                latencies.append((time.perf_counter() - start) * 1000)
                checks += len(observed)
                failures += ["vote fan-out mismatch" for state in observed if state["vote"]["total"] != target]
            paused = await act("pause")
            def same(state, expected):
                return all(state[field] == expected[field] for field in ("round_id", "version", "grid", "player", "phase", "vote", "stats", "audit"))
            paused_states = await asyncio.gather(*(until(ws, lambda state: state["phase"] == "paused") for ws in sockets))
            checks += len(paused_states)
            failures += ["paused snapshot mismatch" for state in paused_states if not same(state, paused)]
            reset = await act("reset")
            reset_states = await asyncio.gather(*(until(ws, lambda state: state["round_id"] == reset["round_id"]) for ws in sockets))
            checks += len(reset_states)
            failures += ["reset snapshot mismatch" for state in reset_states if not same(state, reset)]
        reconnect_start = time.perf_counter()
        async with connect(url, origin=origin) as ws:
            state = json.loads(await ws.recv())
            reconnect_ms = (time.perf_counter() - reconnect_start) * 1000
            checks += 1
            if not same(state, reset): failures.append("reconnect snapshot mismatch")
    result = {"observers": 8, "synthetic_votes": 24, "snapshot_checks": checks, "synchronization_failures": len(failures),
        "failure_details": failures, "post_to_all_observers_ms_median": round(statistics.median(latencies), 2),
        "post_to_all_observers_ms_p95": round(sorted(latencies)[int(len(latencies) * .95)], 2),
        "reconnect_ms": round(reconnect_ms, 2), "limits": "One localhost session, eight read-only sockets, 24 synthetic votes, pause/reset/reconnect. No Twitch delivery, public internet, browser rendering or long soak."}
    Path("artifacts/sync-results.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))
    assert not failures


if __name__ == "__main__":
    asyncio.run(run(sys.argv[1] if len(sys.argv) > 1 else "http://127.0.0.1:8000"))
