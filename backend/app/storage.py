"""SQLite storage adapter for Codex Cortex memories."""

from __future__ import annotations

import json
import sqlite3
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

DB_PATH = Path(__file__).resolve().parents[1] / "cortex.db"


def _connect() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    with _connect() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS memories (
                id TEXT PRIMARY KEY,
                content TEXT NOT NULL,
                type TEXT NOT NULL,
                importance REAL NOT NULL,
                embedding TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )
        conn.commit()


def _row_to_memory(row: sqlite3.Row) -> dict:
    memory = dict(row)
    try:
        memory["embedding"] = json.loads(memory["embedding"])
    except (TypeError, json.JSONDecodeError):
        memory["embedding"] = []
    return memory


def insert_memory(memory_dict: dict) -> dict:
    init_db()
    memory_id = memory_dict.get("id") or str(uuid.uuid4())
    created_at = memory_dict.get("created_at") or datetime.now(timezone.utc).isoformat()
    embedding = memory_dict.get("embedding") or []
    record = {
        "id": memory_id,
        "content": memory_dict.get("content", "").strip(),
        "type": memory_dict.get("type", "general"),
        "importance": float(memory_dict.get("importance", 0.5)),
        "embedding": embedding,
        "created_at": created_at,
    }
    with _connect() as conn:
        conn.execute(
            """
            INSERT INTO memories (id, content, type, importance, embedding, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                record["id"],
                record["content"],
                record["type"],
                record["importance"],
                json.dumps(record["embedding"]),
                record["created_at"],
            ),
        )
        conn.commit()
    return record


def get_all_memories() -> list[dict]:
    init_db()
    with _connect() as conn:
        rows = conn.execute("SELECT * FROM memories ORDER BY created_at DESC").fetchall()
    return [_row_to_memory(row) for row in rows]


def get_memories_by_ids(ids: Iterable[str]) -> list[dict]:
    init_db()
    id_list = list(ids)
    if not id_list:
        return []
    placeholders = ",".join("?" for _ in id_list)
    with _connect() as conn:
        rows = conn.execute(f"SELECT * FROM memories WHERE id IN ({placeholders})", id_list).fetchall()
    by_id = {row["id"]: _row_to_memory(row) for row in rows}
    return [by_id[memory_id] for memory_id in id_list if memory_id in by_id]


def delete_memory(id: str) -> bool:
    init_db()
    with _connect() as conn:
        cursor = conn.execute("DELETE FROM memories WHERE id = ?", (id,))
        conn.commit()
        return cursor.rowcount > 0
