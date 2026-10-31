"""Start the local production build without shell-evaluating .env contents."""
import argparse
import os
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def load_environment(path: Path):
    if not path.exists():
        return
    for number, line in enumerate(path.read_text(encoding="utf-8-sig").splitlines(), 1):
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        key, separator, value = line.partition("=")
        if not separator or not re.fullmatch(r"[A-Z][A-Z0-9_]*", key.strip()):
            raise ValueError(f"Invalid environment assignment on line {number}. Use KEY=value.")
        value = value.strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
            value = value[1:-1]
        os.environ.setdefault(key.strip(), value)


if __name__ == "__main__":
    args = argparse.ArgumentParser(description="Serve CrowdForge")
    args.add_argument("--port", type=int, default=8000)
    args.add_argument("--host", default="127.0.0.1")
    options = args.parse_args()
    load_environment(ROOT / ".env")
    os.environ.setdefault("PUBLIC_URL", f"http://127.0.0.1:{options.port}")
    import uvicorn
    uvicorn.run("apps.server.main:app", host=options.host, port=options.port, access_log=False, ws_max_size=4096, timeout_graceful_shutdown=10)
