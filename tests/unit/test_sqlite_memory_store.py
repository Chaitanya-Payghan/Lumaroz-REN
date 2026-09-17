from __future__ import annotations

from ren.memory import Memory, MemoryQuery, MemoryType
from ren.memory.storage import SQLiteMemoryStore


def create_store(tmp_path) -> SQLiteMemoryStore:
    return SQLiteMemoryStore(str(tmp_path / "memory.db"))


async def test_remember_and_get(tmp_path) -> None:
    store = create_store(tmp_path)

    memory = Memory(
        content="REN is a personal AI system.",
        memory_type=MemoryType.PROJECT,
    )

    memory_id = await store.remember(memory)

    assert memory_id == memory.memory_id

    retrieved = await store.get(memory_id)

    assert retrieved is not None
    assert retrieved.memory_id == memory.memory_id
    assert retrieved.content == memory.content
    assert retrieved.memory_type == MemoryType.PROJECT


async def test_memory_persists_across_store_instances(tmp_path) -> None:
    database_path = tmp_path / "memory.db"

    first_store = SQLiteMemoryStore(str(database_path))

    memory = Memory(
        content="Persistent REN memory.",
        memory_type=MemoryType.NOTE,
    )

    await first_store.remember(memory)

    second_store = SQLiteMemoryStore(str(database_path))

    retrieved = await second_store.get(memory.memory_id)

    assert retrieved is not None
    assert retrieved.content == "Persistent REN memory."


async def test_retrieve_finds_matching_memories(tmp_path) -> None:
    store = create_store(tmp_path)

    await store.remember(Memory(content="REN uses SQLite for local memory."))
    await store.remember(Memory(content="Lumaroz is building REN."))

    results = await store.retrieve(MemoryQuery(text="SQLite"))

    assert len(results) == 1
    assert results[0].content == "REN uses SQLite for local memory."


async def test_retrieve_respects_limit(tmp_path) -> None:
    store = create_store(tmp_path)

    for index in range(5):
        await store.remember(Memory(content=f"Memory item {index}"))

    results = await store.retrieve(
        MemoryQuery(
            text="Memory",
            limit=2,
        )
    )

    assert len(results) == 2


async def test_forget_removes_memory(tmp_path) -> None:
    store = create_store(tmp_path)

    memory = Memory(content="Temporary memory.")

    await store.remember(memory)

    assert await store.forget(memory.memory_id) is True
    assert await store.get(memory.memory_id) is None


async def test_forget_returns_false_for_missing_memory(tmp_path) -> None:
    store = create_store(tmp_path)

    assert await store.forget("does-not-exist") is False


async def test_retrieve_filters_by_memory_type(tmp_path) -> None:
    store = create_store(tmp_path)

    await store.remember(
        Memory(
            content="REN is a personal AI project.",
            memory_type=MemoryType.PROJECT,
        )
    )

    await store.remember(
        Memory(
            content="REN is a personal AI preference.",
            memory_type=MemoryType.PREFERENCE,
        )
    )

    results = await store.retrieve(
        MemoryQuery(
            text="REN",
            memory_type=MemoryType.PROJECT,
        )
    )

    assert len(results) == 1
    assert results[0].memory_type == MemoryType.PROJECT
