from __future__ import annotations

from datetime import UTC

from ren.memory import Memory, MemoryType


def test_memory_has_defaults() -> None:
    memory = Memory(content="REN is being built.")

    assert memory.content == "REN is being built."
    assert memory.memory_type == MemoryType.NOTE
    assert memory.importance == 0.5
    assert memory.memory_id
    assert memory.created_at.tzinfo == UTC
    assert memory.updated_at.tzinfo == UTC


def test_memory_type_values() -> None:
    assert MemoryType.FACT.value == "fact"
    assert MemoryType.PREFERENCE.value == "preference"
    assert MemoryType.PROJECT.value == "project"
    assert MemoryType.PERSON.value == "person"
    assert MemoryType.GOAL.value == "goal"
    assert MemoryType.INSTRUCTION.value == "instruction"
    assert MemoryType.CONVERSATION.value == "conversation"
    assert MemoryType.NOTE.value == "note"


def test_memory_accepts_metadata() -> None:
    memory = Memory(
        content="Lumaroz project decision",
        memory_type=MemoryType.PROJECT,
        importance=0.9,
        metadata={
            "project": "REN",
            "source": "conversation",
        },
    )

    assert memory.metadata["project"] == "REN"
    assert memory.metadata["source"] == "conversation"
    assert memory.importance == 0.9


def test_memory_ids_are_unique() -> None:
    first = Memory(content="First")
    second = Memory(content="Second")

    assert first.memory_id != second.memory_id
