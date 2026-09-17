from __future__ import annotations

import json
import sqlite3
from datetime import datetime

from ren.memory.models import Memory, MemoryQuery, MemoryType


class SQLiteMemoryStore:
    """SQLite-backed implementation of REN's MemoryStore protocol."""

    def __init__(self, database_path: str) -> None:
        self._database_path = database_path
        self._initialize()

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self._database_path)
        connection.row_factory = sqlite3.Row
        return connection

    def _initialize(self) -> None:
        with self._connect() as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS memories (
                    memory_id TEXT PRIMARY KEY,
                    content TEXT NOT NULL,
                    memory_type TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    importance REAL NOT NULL,
                    metadata TEXT NOT NULL
                )
                """
            )
            connection.commit()

    async def remember(self, memory: Memory) -> str:
        with self._connect() as connection:
            connection.execute(
                """
                INSERT INTO memories (
                    memory_id,
                    content,
                    memory_type,
                    created_at,
                    updated_at,
                    importance,
                    metadata
                )
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    memory.memory_id,
                    memory.content,
                    memory.memory_type.value,
                    memory.created_at.isoformat(),
                    memory.updated_at.isoformat(),
                    memory.importance,
                    json.dumps(memory.metadata),
                ),
            )
            connection.commit()

        return memory.memory_id

    async def retrieve(
        self,
        query: MemoryQuery,
    ) -> list[Memory]:
        sql = """
            SELECT *
            FROM memories
            WHERE content LIKE ?
        """

        parameters: list[object] = [f"%{query.text}%"]

        if query.memory_type is not None:
            sql += " AND memory_type = ?"
            parameters.append(query.memory_type.value)

        sql += " ORDER BY updated_at DESC LIMIT ?"
        parameters.append(query.limit)

        with self._connect() as connection:
            rows = connection.execute(
                sql,
                parameters,
            ).fetchall()

        return [self._row_to_memory(row) for row in rows]

    async def get(self, memory_id: str) -> Memory | None:
        with self._connect() as connection:
            row = connection.execute(
                """
                SELECT *
                FROM memories
                WHERE memory_id = ?
                """,
                (memory_id,),
            ).fetchone()

        if row is None:
            return None

        return self._row_to_memory(row)

    async def forget(self, memory_id: str) -> bool:
        with self._connect() as connection:
            cursor = connection.execute(
                """
                DELETE FROM memories
                WHERE memory_id = ?
                """,
                (memory_id,),
            )
            connection.commit()

        return cursor.rowcount > 0

    @staticmethod
    def _row_to_memory(row: sqlite3.Row) -> Memory:
        return Memory(
            memory_id=row["memory_id"],
            content=row["content"],
            memory_type=MemoryType(row["memory_type"]),
            created_at=datetime.fromisoformat(row["created_at"]),
            updated_at=datetime.fromisoformat(row["updated_at"]),
            importance=row["importance"],
            metadata=json.loads(row["metadata"]),
        )
