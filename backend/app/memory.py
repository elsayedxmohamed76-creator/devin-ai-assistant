"""Dual Memory System — The AI's brain.

ShortTermMemory: Sliding window of recent interactions (context).
LongTermMemory: SQLite-backed persistent storage for rules, vocabulary, facts, and tools.
The LTM never forgets — data persists across app restarts.
"""

from __future__ import annotations

import json
import os
import sqlite3
import time
from collections import deque
from pathlib import Path
from typing import Any, Optional


# ---------------------------------------------------------------------------
# Short-Term Memory (STM) — volatile context window
# ---------------------------------------------------------------------------

class ShortTermMemory:
    """Sliding window buffer of recent interactions."""

    def __init__(self, max_size: int = 20) -> None:
        self.max_size = max_size
        self._buffer: deque[dict[str, Any]] = deque(maxlen=max_size)

    def add(self, role: str, content: str, metadata: dict[str, Any] | None = None) -> None:
        entry = {
            "role": role,
            "content": content,
            "timestamp": time.time(),
            "metadata": metadata or {},
        }
        self._buffer.append(entry)

    def get_context(self, last_n: int | None = None) -> list[dict[str, Any]]:
        """Get the last N interactions as context."""
        items = list(self._buffer)
        if last_n is not None:
            items = items[-last_n:]
        return items

    def get_context_string(self, last_n: int = 5) -> str:
        """Get a string representation of recent context for state matching."""
        items = self.get_context(last_n)
        parts = [f"{item['role']}:{item['content'][:50]}" for item in items]
        return " | ".join(parts)

    def clear(self) -> None:
        self._buffer.clear()

    @property
    def size(self) -> int:
        return len(self._buffer)


# ---------------------------------------------------------------------------
# Long-Term Memory (LTM) — persistent SQLite storage
# ---------------------------------------------------------------------------

_DEFAULT_DB_DIR = Path(__file__).parent.parent / "data"


class LongTermMemory:
    """SQLite-backed persistent memory — the AI's permanent brain.

    Tables:
        rules       — consolidated symbolic rules (pattern → action)
        vocabulary  — known words/concepts and their meanings
        facts       — learned facts and knowledge
        tools       — tool definitions the AI has learned or created
        q_table     — persistent Q-values for state-action pairs
    """

    def __init__(self, db_path: str | Path | None = None) -> None:
        if db_path is None:
            _DEFAULT_DB_DIR.mkdir(parents=True, exist_ok=True)
            db_path = _DEFAULT_DB_DIR / "brain.db"
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._conn: sqlite3.Connection | None = None
        self._init_db()

    def _get_conn(self) -> sqlite3.Connection:
        if self._conn is None:
            self._conn = sqlite3.connect(str(self.db_path), check_same_thread=False)
            self._conn.row_factory = sqlite3.Row
            self._conn.execute("PRAGMA journal_mode=WAL")
            self._conn.execute("PRAGMA foreign_keys=ON")
        return self._conn

    def _init_db(self) -> None:
        conn = self._get_conn()
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS rules (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                pattern TEXT NOT NULL UNIQUE,
                action TEXT NOT NULL,
                confidence REAL DEFAULT 1.0,
                times_used INTEGER DEFAULT 0,
                created_at REAL NOT NULL,
                updated_at REAL NOT NULL
            );

            CREATE TABLE IF NOT EXISTS vocabulary (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                word TEXT NOT NULL UNIQUE,
                meaning TEXT DEFAULT '',
                context TEXT DEFAULT '',
                times_seen INTEGER DEFAULT 1,
                first_seen REAL NOT NULL,
                last_seen REAL NOT NULL
            );

            CREATE TABLE IF NOT EXISTS facts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                subject TEXT NOT NULL,
                predicate TEXT NOT NULL,
                object TEXT NOT NULL,
                source TEXT DEFAULT 'user',
                confidence REAL DEFAULT 1.0,
                created_at REAL NOT NULL,
                UNIQUE(subject, predicate, object)
            );

            CREATE TABLE IF NOT EXISTS tools (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                description TEXT DEFAULT '',
                code TEXT DEFAULT '',
                parameters TEXT DEFAULT '{}',
                created_by TEXT DEFAULT 'system',
                created_at REAL NOT NULL
            );

            CREATE TABLE IF NOT EXISTS q_table (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                state TEXT NOT NULL,
                action TEXT NOT NULL,
                q_value REAL DEFAULT 0.0,
                visits INTEGER DEFAULT 0,
                updated_at REAL NOT NULL,
                UNIQUE(state, action)
            );

            CREATE TABLE IF NOT EXISTS interactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_input TEXT NOT NULL,
                agent_response TEXT NOT NULL,
                reward INTEGER DEFAULT 0,
                tools_used TEXT DEFAULT '[]',
                timestamp REAL NOT NULL
            );
        """)
        conn.commit()

    # ---- Rules ----

    def add_rule(self, pattern: str, action: str, confidence: float = 1.0) -> None:
        now = time.time()
        conn = self._get_conn()
        conn.execute(
            """INSERT INTO rules (pattern, action, confidence, created_at, updated_at)
               VALUES (?, ?, ?, ?, ?)
               ON CONFLICT(pattern) DO UPDATE SET
                 action=excluded.action, confidence=excluded.confidence, updated_at=?""",
            (pattern, action, confidence, now, now, now),
        )
        conn.commit()

    def get_rule(self, pattern: str) -> Optional[dict[str, Any]]:
        conn = self._get_conn()
        row = conn.execute("SELECT * FROM rules WHERE pattern = ?", (pattern,)).fetchone()
        if row:
            conn.execute(
                "UPDATE rules SET times_used = times_used + 1, updated_at = ? WHERE pattern = ?",
                (time.time(), pattern),
            )
            conn.commit()
            return dict(row)
        return None

    def get_all_rules(self) -> list[dict[str, Any]]:
        conn = self._get_conn()
        rows = conn.execute("SELECT * FROM rules ORDER BY times_used DESC").fetchall()
        return [dict(r) for r in rows]

    # ---- Vocabulary ----

    def learn_word(self, word: str, meaning: str = "", context: str = "") -> None:
        now = time.time()
        conn = self._get_conn()
        conn.execute(
            """INSERT INTO vocabulary (word, meaning, context, first_seen, last_seen)
               VALUES (?, ?, ?, ?, ?)
               ON CONFLICT(word) DO UPDATE SET
                 meaning = CASE WHEN excluded.meaning != '' THEN excluded.meaning ELSE vocabulary.meaning END,
                 context = CASE WHEN excluded.context != '' THEN excluded.context ELSE vocabulary.context END,
                 times_seen = vocabulary.times_seen + 1,
                 last_seen = ?""",
            (word, meaning, context, now, now, now),
        )
        conn.commit()

    def knows_word(self, word: str) -> bool:
        conn = self._get_conn()
        row = conn.execute("SELECT 1 FROM vocabulary WHERE word = ?", (word,)).fetchone()
        return row is not None

    def get_vocabulary(self) -> list[dict[str, Any]]:
        conn = self._get_conn()
        rows = conn.execute("SELECT * FROM vocabulary ORDER BY times_seen DESC").fetchall()
        return [dict(r) for r in rows]

    @property
    def vocabulary_size(self) -> int:
        conn = self._get_conn()
        row = conn.execute("SELECT COUNT(*) as cnt FROM vocabulary").fetchone()
        return row["cnt"] if row else 0

    # ---- Facts ----

    def add_fact(self, subject: str, predicate: str, obj: str, source: str = "user") -> None:
        now = time.time()
        conn = self._get_conn()
        conn.execute(
            """INSERT OR IGNORE INTO facts (subject, predicate, object, source, created_at)
               VALUES (?, ?, ?, ?, ?)""",
            (subject, predicate, obj, source, now),
        )
        conn.commit()

    def search_facts(self, query: str) -> list[dict[str, Any]]:
        conn = self._get_conn()
        rows = conn.execute(
            "SELECT * FROM facts WHERE subject LIKE ? OR object LIKE ?",
            (f"%{query}%", f"%{query}%"),
        ).fetchall()
        return [dict(r) for r in rows]

    # ---- Q-Table ----

    def get_q_value(self, state: str, action: str) -> float:
        conn = self._get_conn()
        row = conn.execute(
            "SELECT q_value FROM q_table WHERE state = ? AND action = ?",
            (state, action),
        ).fetchone()
        return row["q_value"] if row else 0.0

    def set_q_value(self, state: str, action: str, value: float) -> None:
        now = time.time()
        conn = self._get_conn()
        conn.execute(
            """INSERT INTO q_table (state, action, q_value, visits, updated_at)
               VALUES (?, ?, ?, 1, ?)
               ON CONFLICT(state, action) DO UPDATE SET
                 q_value = ?, visits = q_table.visits + 1, updated_at = ?""",
            (state, action, value, now, value, now),
        )
        conn.commit()

    def get_q_actions(self, state: str) -> list[dict[str, Any]]:
        conn = self._get_conn()
        rows = conn.execute(
            "SELECT action, q_value, visits FROM q_table WHERE state = ? ORDER BY q_value DESC",
            (state,),
        ).fetchall()
        return [dict(r) for r in rows]

    # ---- Interactions log ----

    def log_interaction(self, user_input: str, agent_response: str, reward: int = 0,
                        tools_used: list[str] | None = None) -> None:
        conn = self._get_conn()
        conn.execute(
            "INSERT INTO interactions (user_input, agent_response, reward, tools_used, timestamp) VALUES (?, ?, ?, ?, ?)",
            (user_input, agent_response, reward, json.dumps(tools_used or []), time.time()),
        )
        conn.commit()

    def update_last_reward(self, reward: int) -> None:
        """Update the reward for the most recent interaction."""
        conn = self._get_conn()
        conn.execute(
            "UPDATE interactions SET reward = ? WHERE id = (SELECT MAX(id) FROM interactions)",
            (reward,),
        )
        conn.commit()

    # ---- Stats ----

    def get_stats(self) -> dict[str, Any]:
        conn = self._get_conn()
        rules_count = conn.execute("SELECT COUNT(*) FROM rules").fetchone()[0]
        vocab_count = conn.execute("SELECT COUNT(*) FROM vocabulary").fetchone()[0]
        facts_count = conn.execute("SELECT COUNT(*) FROM facts").fetchone()[0]
        interactions_count = conn.execute("SELECT COUNT(*) FROM interactions").fetchone()[0]
        q_entries = conn.execute("SELECT COUNT(*) FROM q_table").fetchone()[0]
        avg_reward = conn.execute("SELECT AVG(reward) FROM interactions WHERE reward != 0").fetchone()[0]
        return {
            "rules_learned": rules_count,
            "vocabulary_size": vocab_count,
            "facts_known": facts_count,
            "total_interactions": interactions_count,
            "q_table_entries": q_entries,
            "average_reward": round(avg_reward, 3) if avg_reward else 0.0,
            "db_path": str(self.db_path),
        }

    def close(self) -> None:
        if self._conn:
            self._conn.close()
            self._conn = None
