from __future__ import annotations

from typing import Protocol

from ren.memory.models import Memory, MemoryQuery


class MemoryStore(Protocol):
    async def remember(self, memory: Memory) -> str:
        """Store a memory and return its ID."""
        ...

    async def retrieve(
        self,
        query: MemoryQuery,
    ) -> list[Memory]:
        """Retrieve memories relevant to a query."""
        ...

    async def get(self, memory_id: str) -> Memory | None:
        """Retrieve a specific memory by ID."""
        ...

    async def forget(self, memory_id: str) -> bool:
        """Remove a memory and report whether it existed."""
        ...
