"""Single-writer round state machine. All time is supplied by the server tick."""
import hashlib
import json
import uuid
import time

from .voting import VoteWindow
from .world import HEIGHT, WIDTH, LAVA, WALL, Mutation, generate, path, select_target, validate

ROUND_SECONDS = 100.0
VOTE_SECONDS = 15.0


class Game:
    def __init__(self, seed: int = 1847, allow_changes: bool = True, round_id: str | None = None, rules: int = 2):
        self.rules = rules
        self.round_id = round_id or uuid.uuid4().hex
        self.seed = seed
        self.allow_changes = allow_changes
        self.grid = generate(seed)
        self.player = (2, HEIGHT - 3)
        self.exit = (WIDTH - 3, 2)
        self.health = 100.0
        self.elapsed = 0.0
        self.phase = "ready"
        self.version = 0
        self.window: VoteWindow | None = None
        self.events: list[dict] = []
        self.audit: list[dict] = []
        self.commands: list[dict] = []
        self.move_ready = 0.0
        self.total_votes = 0
        self.accepted = 0
        self.rejected = 0
        self.chaos = 0
        self.frozen = False
        self.validation_ms: list[float] = []
        self.vote_receipts = {"accepted": 0, "ignored": 0}
        self.note("system", "Arena forged. Find the cyan portal. Chat reshapes your route.")

    def note(self, kind: str, text: str):
        self.events.append({"id": len(self.events) + 1, "time": round(self.elapsed, 2), "kind": kind, "text": text})

    def control(self, action: str, record: bool = True):
        if record:
            self.commands.append({"op": "control", "action": action})
        if action == "start" and self.phase == "ready":
            self.phase = "running"
            self.window = VoteWindow(1, 0, VOTE_SECONDS, self.allow_changes)
            self.note("system", "Round started. One streamer. An unpredictable world.")
        elif action == "pause" and self.phase == "running":
            self.phase = "paused"
        elif action == "resume" and self.phase == "paused":
            self.phase = "running"
        elif action == "freeze" and self.phase in ("running", "paused"):
            self.frozen = not self.frozen
            if self.window:
                self.window = VoteWindow(self.window.number + 1, self.elapsed, self.elapsed + VOTE_SECONDS, self.allow_changes)
            self.note("system", "Audience mutations frozen." if self.frozen else "Audience mutations resumed. A fresh vote window is open.")
        elif action == "rescue" and self.phase in ("running", "paused"):
            # Streamer emergency action is visible and auditable, never counted as an audience vote.
            self.grid[self.player[1]][self.player[0]] = 0
            self.health = min(100, self.health + 25)
            self.note("rescue", "Streamer used emergency rescue: +25 health, current tile made safe.")
        else:
            return False
        self.version += 1
        return True

    def move(self, dx: int, dy: int, record: bool = True) -> bool:
        if record:
            self.commands.append({"op": "move", "dx": dx, "dy": dy})
        if self.phase != "running" or abs(dx) + abs(dy) != 1 or self.elapsed < self.move_ready:
            return False
        x, y = self.player[0] + dx, self.player[1] + dy
        if not (0 <= x < WIDTH and 0 <= y < HEIGHT) or self.grid[y][x] == WALL:
            return False
        self.player = (x, y)
        self.move_ready = self.elapsed + .125
        self.version += 1
        if self.player == self.exit:
            self.phase = "won"
            self.note("win", "Portal reached. You escaped the crowd!")
        return True

    def mutate(self, proposal: Mutation, source: int, record: bool = True) -> dict:
        if record:
            self.commands.append({"op": "mutation", "proposal": proposal.model_dump(), "source": source})
        started = time.perf_counter_ns()
        result = validate(self.grid, self.player, self.exit, proposal,
                          ROUND_SECONDS - self.elapsed if self.rules >= 2 else None, self.rules)
        self.validation_ms = (self.validation_ms + [(time.perf_counter_ns() - started) / 1e6])[-200:]
        before = self.version
        route_before = len(path(self.grid, self.player, self.exit))
        original_tiles = [(x, y, self.grid[y][x]) for x, y in proposal.targets] if result.accepted else []
        if result.accepted:
            self.grid = result.grid
            self.version += 1
            self.accepted += 1
            # An intentionally simple game score, not a scientific causal metric.
            self.chaos += len(set(proposal.targets)) * 10 + max(0, len(path(self.grid, self.player, self.exit)) - route_before) * 2
        else:
            self.rejected += 1
        event = {"id": f"{self.round_id}:{len(self.audit) + 1}", "window": source, "kind": proposal.kind,
                 "targets": proposal.targets, "accepted": result.accepted, "reason": result.reason,
                 "previous_version": before, "resulting_version": self.version, "timestamp": round(self.elapsed, 3),
                 "protocol": ["PROPOSED", "VALIDATING", "ACCEPTED", "APPLIED"] if result.accepted else ["PROPOSED", "VALIDATING", "REJECTED"]}
        if self.rules >= 2:
            event["metrics"] = result.metrics
            event["changes"] = [{"x": x, "y": y, "before": old, "after": self.grid[y][x]}
                                for x, y, old in original_tiles] if result.accepted else []
        self.audit.append(event)
        self.note(proposal.kind if result.accepted else "rejected", f"{proposal.kind.title()} {'applied' if result.accepted else 'blocked'}. {result.reason}")
        return event

    def cast(self, user: str, message: str, text: str, sent: float | None = None) -> bool:
        if self.phase != "running" or self.frozen or not self.window:
            self.vote_receipts["ignored"] += 1
            return False
        sent = self.elapsed if sent is None else sent
        accepted = self.window.cast(user, message, text, sent, self.elapsed)
        self.vote_receipts["accepted" if accepted else "ignored"] += 1
        return accepted

    def restart_vote(self, record: bool = True):
        """Mode changes are replay inputs, including windows opened during pause."""
        if record:
            self.commands.append({"op": "restart_vote"})
        if self.window:
            self.window = VoteWindow(self.window.number + 1, self.elapsed, self.elapsed + VOTE_SECONDS, self.allow_changes)
        self.version += 1

    def tick(self, dt: float, record: bool = True):
        if self.phase != "running":
            return
        if record:
            self.commands.append({"op": "tick", "dt": dt, "winner": self.window.winner() if self.window else None,
                                  "votes": len(self.window.votes) if self.window else 0})
        self.elapsed = round(min(ROUND_SECONDS, self.elapsed + dt), 5)
        if self.grid[self.player[1]][self.player[0]] == LAVA:
            previous = self.health
            self.health = max(0, self.health - 22 * dt)
            if int(previous / 10) != int(self.health / 10):
                self.note("damage", f"Lava damage. Health {int(self.health)}%.")
        if self.health <= 0 or self.elapsed >= ROUND_SECONDS:
            self.phase = "lost"
            self.note("loss", "The world won. Forge another escape.")
        elif self.window and self.elapsed >= self.window.closes:
            self.close_vote()
        self.version += 1

    def close_vote(self, winner_override: str | None = None, count_override: int | None = None):
        if not self.window:
            return
        count = len(self.window.votes) if count_override is None else count_override
        self.total_votes += count
        winner = self.window.winner() if winner_override is None else winner_override
        if winner and not self.frozen:
            proposal = select_target(self.grid, self.player, self.exit, winner, self.seed + self.window.number * 7919,
                                     ROUND_SECONDS - self.elapsed if self.rules >= 2 else None, self.rules)
            self.mutate(proposal, self.window.number, record=False)
        elif not self.frozen:
            self.note("system", "No votes this window. The world holds steady.")
        self.window = VoteWindow(self.window.number + 1, self.elapsed, self.elapsed + VOTE_SECONDS, self.allow_changes)

    def state(self) -> dict:
        counts = self.window.counts() if self.window else {"lava": 0, "wall": 0, "bridge": 0}
        return {"schema": 1, "round_id": self.round_id, "version": self.version, "seed": self.seed, "grid": self.grid, "player": self.player,
                "exit": self.exit, "health": round(self.health, 1), "elapsed": self.elapsed,
                "remaining": round(max(0, ROUND_SECONDS - self.elapsed), 1), "phase": self.phase,
                "vote": {"number": self.window.number if self.window else 1, "counts": counts,
                         "remaining": round(max(0, self.window.closes - self.elapsed), 1) if self.window else VOTE_SECONDS,
                         "closes_at_round_seconds": self.window.closes if self.window else VOTE_SECONDS,
                         "total": sum(counts.values()), "allow_changes": self.allow_changes},
                "events": self.events[-20:], "audit": self.audit[-20:], "frozen": self.frozen,
                "stats": {"accepted": self.accepted, "rejected": self.rejected, "votes": self.total_votes + sum(counts.values()), "chaos": self.chaos}}

    def digest(self) -> str:
        payload = {key: self.state()[key] for key in ("grid", "player", "health", "elapsed", "phase", "stats")}
        if self.rules >= 2:
            payload.update(version=self.version, frozen=self.frozen, move_ready=self.move_ready,
                           window={"number": self.window.number, "opened": self.window.opened, "closes": self.window.closes,
                                   "counts": self.window.counts()} if self.window else None, audit=self.audit)
        return hashlib.sha256(json.dumps(payload, sort_keys=True).encode()).hexdigest()

    def replay(self) -> dict:
        return {"schema": 1, "rules": self.rules, "seed": self.seed, "round_id": self.round_id, "allow_changes": self.allow_changes, "commands": self.commands,
                "audit": self.audit, "final_vote_counts": self.window.counts() if self.window else {}, "digest": self.digest()}


def replay_round(record: dict) -> Game:
    game = Game(record["seed"], record["allow_changes"], record.get("round_id"), record.get("rules", 1))
    for command in record["commands"]:
        op = command["op"]
        if op == "control":
            game.control(command["action"], record=False)
        elif op == "move":
            game.move(command["dx"], command["dy"], record=False)
        elif op == "mutation":
            game.mutate(Mutation.model_validate(command["proposal"]), command["source"], record=False)
        elif op == "restart_vote":
            game.restart_vote(record=False)
        elif op == "tick":
            # Recorded aggregate decisions avoid retaining Twitch identities in replays.
            if game.window:
                game.window.votes = {f"replay-{i}": command["winner"] for i in range(command["votes"])} if command["winner"] else {}
            game.tick(command["dt"], record=False)
    if game.window:
        game.window.votes = {f"final-{kind}-{i}": kind for kind, count in record.get("final_vote_counts", {}).items() for i in range(count)}
    return game
