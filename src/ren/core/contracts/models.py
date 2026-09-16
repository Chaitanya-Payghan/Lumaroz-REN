from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import IntEnum
from typing import Any
from uuid import uuid4


class RiskLevel(IntEnum):
    """REN action risk levels."""

    OBSERVATION = 0
    SAFE = 1
    MODIFYING = 2
    SENSITIVE = 3
    CRITICAL = 4


@dataclass(frozen=True, slots=True)
class Request:
    """A request received by REN."""

    text: str
    source: str = "unknown"
    request_id: str = field(default_factory=lambda: str(uuid4()))
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class ContextSnapshot:
    """Context available while processing a request."""

    request_id: str
    session_id: str
    facts: dict[str, Any] = field(default_factory=dict)
    memory_refs: tuple[str, ...] = ()
    capabilities: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class Action:
    """A concrete operation REN intends to execute."""

    tool_name: str
    arguments: dict[str, Any] = field(default_factory=dict)
    action_id: str = field(default_factory=lambda: str(uuid4()))
    risk_level: RiskLevel = RiskLevel.SAFE


@dataclass(frozen=True, slots=True)
class Plan:
    """An executable plan produced for a request."""

    request_id: str
    steps: tuple[Action, ...] = ()
    explanation: str = ""


@dataclass(frozen=True, slots=True)
class PolicyDecision:
    """Decision made by REN's policy engine."""

    allowed: bool
    requires_confirmation: bool = False
    reason: str = ""


@dataclass(frozen=True, slots=True)
class PermissionDecision:
    """Decision made by REN's permission engine."""

    allowed: bool
    reason: str = ""


@dataclass(frozen=True, slots=True)
class ActionResult:
    """Result returned after an action is processed."""

    action_id: str
    success: bool
    output: Any = None
    error: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)
