"""Round evidence only. OAuth tokens and chat identities are never persisted."""
import json
import sqlite3
from pathlib import Path


class RoundStore:
    def __init__(self, location: str):
        Path(location).parent.mkdir(parents=True, exist_ok=True)
        self.connection = sqlite3.connect(location)
        self.connection.execute("CREATE TABLE IF NOT EXISTS rounds (id TEXT PRIMARY KEY, seed INTEGER, outcome TEXT, replay TEXT)")

    def save(self, key: str, game, provenance: dict | None = None):
        record = {**game.replay(), "provenance": provenance or {}}
        self.connection.execute("INSERT OR REPLACE INTO rounds VALUES (?, ?, ?, ?)", (key, game.seed, game.phase, json.dumps(record)))
        self.connection.commit()

    def close(self):
        self.connection.close()
