"""
Multi-turn session state per PP-195.

Each session_id maps to a list of turns:
  {role: "user" | "assistant", text: str, intent: str, source: str, timestamp: float, audit_root: str}

In-memory store with FIFO eviction once SESSIONS_MAX is reached. Production: persist via
substrate bitemporal layer per cycle 145.
"""
from __future__ import annotations
import time
from dataclasses import asdict, dataclass, field
from threading import Lock
from typing import Optional


SESSIONS_MAX = 1000               # keep recent sessions in memory
SESSION_MAX_TURNS = 50            # cap per session to bound memory
SESSION_TTL_S = 3600 * 24         # auto-drop sessions older than 24 hr


@dataclass
class Turn:
    role: str                # "user" or "assistant"
    text: str
    intent: Optional[str] = None
    source: Optional[str] = None         # "substrate-direct" / "substrate+template" / "llm-mediated"
    audit_root: Optional[str] = None
    timestamp: float = field(default_factory=time.time)


@dataclass
class Session:
    session_id: str
    turns: list = field(default_factory=list)
    created_at: float = field(default_factory=time.time)
    last_seen: float = field(default_factory=time.time)

    def add_turn(self, turn: Turn) -> None:
        self.turns.append(turn)
        if len(self.turns) > SESSION_MAX_TURNS:
            # Keep first 2 + most recent (SESSION_MAX_TURNS - 2) to preserve early context
            self.turns = self.turns[:2] + self.turns[-(SESSION_MAX_TURNS - 2):]
        self.last_seen = time.time()

    def recent_turns(self, k: int = 6) -> list:
        return self.turns[-k:]

    def last_user(self) -> Optional[Turn]:
        for t in reversed(self.turns):
            if t.role == "user":
                return t
        return None

    def last_assistant(self) -> Optional[Turn]:
        for t in reversed(self.turns):
            if t.role == "assistant":
                return t
        return None

    def to_dict(self) -> dict:
        return {
            "session_id": self.session_id,
            "created_at": self.created_at,
            "last_seen": self.last_seen,
            "turn_count": len(self.turns),
            "turns": [asdict(t) for t in self.turns],
        }


_sessions: dict = {}
_lock = Lock()


def get_or_create_session(session_id: str) -> Session:
    with _lock:
        s = _sessions.get(session_id)
        if s is None:
            # FIFO eviction
            if len(_sessions) >= SESSIONS_MAX:
                oldest_id = min(_sessions, key=lambda k: _sessions[k].last_seen)
                _sessions.pop(oldest_id, None)
            s = Session(session_id=session_id)
            _sessions[session_id] = s
        # TTL drop
        if time.time() - s.last_seen > SESSION_TTL_S:
            s = Session(session_id=session_id)
            _sessions[session_id] = s
        return s


def get_session(session_id: str) -> Optional[Session]:
    with _lock:
        s = _sessions.get(session_id)
        if s and (time.time() - s.last_seen > SESSION_TTL_S):
            _sessions.pop(session_id, None)
            return None
        return s


def list_sessions() -> list[dict]:
    with _lock:
        return [
            {
                "session_id": s.session_id,
                "turn_count": len(s.turns),
                "last_seen_age_s": time.time() - s.last_seen,
            }
            for s in _sessions.values()
        ]


def _self_test():
    s = get_or_create_session("test_sess_1")
    assert len(s.turns) == 0
    s.add_turn(Turn(role="user", text="hi"))
    s.add_turn(Turn(role="assistant", text="Hello!", intent="greeting", source="substrate-direct"))
    s.add_turn(Turn(role="user", text="who founded Anthropic"))
    s.add_turn(Turn(role="assistant", text="Anthropic was founded in 2021", intent="factual", source="substrate+template"))

    same = get_session("test_sess_1")
    assert same is not None
    assert len(same.turns) == 4
    assert same.last_user().text == "who founded Anthropic"
    assert same.last_assistant().text == "Anthropic was founded in 2021"

    # Cap test
    for i in range(100):
        s.add_turn(Turn(role="user", text=f"msg {i}"))
    assert len(s.turns) == SESSION_MAX_TURNS

    # Recent turns
    recent = s.recent_turns(3)
    assert len(recent) == 3

    print(f"[converse.state] self-test PASS ({len(_sessions)} session(s); max_turns={SESSION_MAX_TURNS})")


if __name__ == "__main__":
    _self_test()
