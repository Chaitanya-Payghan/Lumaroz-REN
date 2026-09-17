from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import StrEnum
from typing import Any
from uuid import uuid4


class MemoryType(StrEnum):
    FACT = "fact"
    PREFERENCE = "preference"
    PROJECT = "project"
    PERSON = "person"
    GOAL = "goal"
    INSTRUCTION = "instruction"
    CONVERSATION = "conversation"
    NOTE = "note"


@dataclass(frozen=True, slots=True)
class Memory:
    content: str
    memory_type: MemoryType = MemoryType.NOTE
    memory_id: str = field(default_factory=lambda: str(uuid4()))
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    importance: float = 0.5
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class MemoryQuery:
    text: str
    memory_type: MemoryType | None = None
    limit: int = 10
