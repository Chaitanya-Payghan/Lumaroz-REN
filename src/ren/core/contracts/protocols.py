from __future__ import annotations

from collections.abc import Mapping
from typing import Any, Protocol

from ren.core.contracts.models import (
    Action,
    ActionResult,
    ContextSnapshot,
    PermissionDecision,
    Plan,
    PolicyDecision,
    Request,
)


class Reasoner(Protocol):
    """Produces reasoning or decision support for a request."""

    async def reason(
        self,
        request: Request,
        context: ContextSnapshot,
    ) -> str: ...


class Planner(Protocol):
    """Converts a request and context into an executable plan."""

    async def create_plan(
        self,
        request: Request,
        context: ContextSnapshot,
    ) -> Plan: ...


class PolicyEngine(Protocol):
    """Determines whether a proposed action is permitted by policy."""

    async def evaluate(
        self,
        action: Action,
        context: ContextSnapshot,
    ) -> PolicyDecision: ...


class PermissionEngine(Protocol):
    """Determines whether REN is authorized to perform an action."""

    async def authorize(
        self,
        action: Action,
        context: ContextSnapshot,
    ) -> PermissionDecision: ...


class Tool(Protocol):
    """Contract implemented by every REN executable tool."""

    name: str
    description: str

    async def execute(
        self,
        action: Action,
    ) -> ActionResult: ...


class ToolRegistry(Protocol):
    """Registry responsible for discovering and resolving tools."""

    def register(self, tool: Tool) -> None: ...

    def get(self, name: str) -> Tool | None: ...

    def list_tools(self) -> tuple[str, ...]: ...


class MemoryStore(Protocol):
    """Contract for REN memory implementations."""

    async def remember(
        self,
        content: Any,
        metadata: dict[str, Any] | None = None,
    ) -> str: ...

    async def retrieve(
        self,
        query: str,
        limit: int = 10,
    ) -> list[Any]: ...


class ContextProvider(Protocol):
    """Provides contextual information to REN."""

    name: str

    async def collect(
        self,
        request: Request,
        context: ContextSnapshot,
    ) -> Mapping[str, Any]: ...
