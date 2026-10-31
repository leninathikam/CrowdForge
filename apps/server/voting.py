"""Bounded, timestamp-aware voting. Transport retries never count twice."""
from collections import OrderedDict
from dataclasses import dataclass, field
import re

from .world import KINDS


def parse_vote(text: str) -> str | None:
    command = text.strip().lower()
    if command in ("!lava", "!wall", "!bridge"):
        return command[1:]
    match = re.fullmatch(r"!vote\s+([123])", command)
    return KINDS[int(match[1]) - 1] if match else None


@dataclass
class VoteWindow:
    number: int
    opened: float
    closes: float
    allow_changes: bool = True
    votes: dict[str, str] = field(default_factory=dict)
    last_vote: dict[str, float] = field(default_factory=dict)
    last_sent: dict[str, float] = field(default_factory=dict)
    seen: OrderedDict[str, None] = field(default_factory=OrderedDict)
    cooldown: float = 1.0
    capacity: int = 20000
    received: int = 0
    limited: int = 0

    def cast(self, user: str, message: str, text: str, sent: float, now: float) -> bool:
        kind = parse_vote(text)
        if kind is None or not user or not message or message in self.seen:
            return False
        if not self.opened <= sent < self.closes or not self.opened <= now < self.closes:
            return False
        # At capacity fail closed, preserving deduplication for the whole window.
        if len(self.seen) >= self.capacity or len(self.votes) >= self.capacity:
            self.limited += 1
            return False
        self.seen[message] = None
        self.received += 1
        if now - self.last_vote.get(user, -1000) < self.cooldown:
            return False
        if user in self.votes and not self.allow_changes:
            return False
        if sent < self.last_sent.get(user, -1000):
            return False
        self.last_vote[user] = now
        self.last_sent[user] = sent
        self.votes[user] = kind
        return True

    def counts(self) -> dict[str, int]:
        counts = dict.fromkeys(KINDS, 0)
        for choice in self.votes.values():
            counts[choice] += 1
        return counts

    def winner(self) -> str | None:
        counts = self.counts()
        # Ties rotate by window number; no votes means no mutation.
        order = KINDS[(self.number - 1) % 3:] + KINDS[:(self.number - 1) % 3]
        return max(order, key=lambda key: counts[key]) if self.votes else None
