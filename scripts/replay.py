"""Verify a downloaded replay against its recorded final-state digest."""
import json
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from apps.server.engine import replay_round

if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("Usage: python scripts/replay.py path/to/replay.json")
    record = json.loads(Path(sys.argv[1]).read_text())
    game = replay_round(record)
    if game.digest() != record["digest"]:
        raise SystemExit("Replay mismatch: state did not reproduce.")
    print(f"Verified seed {game.seed}: {game.phase}, {game.elapsed}s, digest {game.digest()}")
