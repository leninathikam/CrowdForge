"""Measure real localhost POST-to-snapshot latency and reconnect synchronization."""
import asyncio
import json
from pathlib import Path
import statistics
import sys
import time

import httpx
from websockets.asyncio.client import connect


async def measure(base: str):
    origin = base.rstrip("/")
    async with httpx.AsyncClient(base_url=origin, headers={"Origin": origin}, timeout=10) as http:
        created = (await http.post("/api/sessions", json={})).json()
        key = created["id"]
        cookie = "; ".join(f"{k}={v}" for k, v in http.cookies.items())
        url = origin.replace("http", "ws", 1) + f"/api/sessions/{key}/ws"
        await http.post(f"/api/sessions/{key}/action", json={"action": "start"})
        timings = []
        async with connect(url, origin=origin, additional_headers={"Cookie": cookie}) as ws:
            await ws.recv()
            for i in range(30):
                await asyncio.sleep(.11)
                begin = time.perf_counter()
                response = await http.post(f"/api/sessions/{key}/action", json={"action": "simulate", "choice": "lava"})
                response.raise_for_status()
                while True:
                    state = json.loads(await asyncio.wait_for(ws.recv(), 2))
                    if state["vote"]["counts"]["lava"] == i + 1:
                        break
                timings.append((time.perf_counter() - begin) * 1000)
        begin = time.perf_counter()
        async with connect(url, origin=origin, additional_headers={"Cookie": cookie}) as ws:
            synced = json.loads(await ws.recv())
            reconnect_ms = (time.perf_counter() - begin) * 1000
        await http.post(f"/api/sessions/{key}/action", json={"action": "pause"})
    result = {"base": origin, "samples": len(timings), "post_to_snapshot_ms_median": round(statistics.median(timings), 2),
              "post_to_snapshot_ms_p95": round(sorted(timings)[int(len(timings) * .95)], 2),
              "reconnect_to_first_snapshot_ms": round(reconnect_ms, 2), "synchronized_votes": synced["vote"]["total"],
              "limits": "Loopback, synthetic votes, one observer; excludes Twitch delivery, DOM paint, public internet, OBS and multi-viewer load."}
    Path("artifacts/transport-results.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    asyncio.run(measure(sys.argv[1] if len(sys.argv) > 1 else "http://127.0.0.1:8000"))
