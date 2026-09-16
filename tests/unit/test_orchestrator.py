from __future__ import annotations

from dataclasses import dataclass

import pytest

from ren.core.contracts import (
    Action,
    ActionResult,
    ContextSnapshot,
    PermissionDecision,
    Plan,
    PolicyDecision,
    Request,
    RiskLevel,
    Tool,
)
from ren.core.runtime import Orchestrator


@dataclass
class FakeReasoner:
    calls: int = 0

    async def reason(
        self,
        request: Request,
        context: ContextSnapshot,
    ) -> str:
        self.calls += 1
        return "reasoned"


@dataclass
class FakePlanner:
    action: Action
    calls: int = 0

    async def create_plan(
        self,
        request: Request,
        context: ContextSnapshot,
    ) -> Plan:
        self.calls += 1
        return Plan(
            request_id=request.request_id,
            steps=(self.action,),
        )


@dataclass
class FakePolicyEngine:
    allowed: bool = True

    async def evaluate(
        self,
        action: Action,
        context: ContextSnapshot,
    ) -> PolicyDecision:
        return PolicyDecision(
            allowed=self.allowed,
            reason="test policy",
        )


@dataclass
class FakePermissionEngine:
    allowed: bool = True

    async def authorize(
        self,
        action: Action,
        context: ContextSnapshot,
    ) -> PermissionDecision:
        return PermissionDecision(
            allowed=self.allowed,
            reason="test permission",
        )


class FakeTool:
    name = "test.tool"
    description = "Test tool"

    def __init__(self) -> None:
        self.calls = 0

    async def execute(self, action: Action) -> ActionResult:
        self.calls += 1
        return ActionResult(
            action_id=action.action_id,
            success=True,
            output="executed",
        )


class FakeToolRegistry:
    def __init__(self, tool: Tool | None = None) -> None:
        self.tool = tool

    def register(self, tool: Tool) -> None:
        self.tool = tool

    def get(self, name: str) -> Tool | None:
        if self.tool is not None and self.tool.name == name:
            return self.tool
        return None

    def list_tools(self) -> tuple[str, ...]:
        if self.tool is None:
            return ()
        return (self.tool.name,)


def create_context(request: Request) -> ContextSnapshot:
    return ContextSnapshot(
        request_id=request.request_id,
        session_id="test-session",
    )


@pytest.mark.asyncio
async def test_orchestrator_executes_allowed_action() -> None:
    request = Request(text="Test REN")
    action = Action(
        tool_name="test.tool",
        risk_level=RiskLevel.SAFE,
    )

    reasoner = FakeReasoner()
    planner = FakePlanner(action)
    policy = FakePolicyEngine()
    permission = FakePermissionEngine()
    tool = FakeTool()
    registry = FakeToolRegistry(tool)

    orchestrator = Orchestrator(
        reasoner,
        planner,
        policy,
        permission,
        registry,
    )

    results = await orchestrator.process(
        request,
        create_context(request),
    )

    assert len(results) == 1
    assert results[0].success
    assert results[0].output == "executed"
    assert reasoner.calls == 1
    assert planner.calls == 1
    assert tool.calls == 1


@pytest.mark.asyncio
async def test_policy_denial_prevents_execution() -> None:
    request = Request(text="Test policy")
    action = Action(tool_name="test.tool")

    tool = FakeTool()

    orchestrator = Orchestrator(
        FakeReasoner(),
        FakePlanner(action),
        FakePolicyEngine(allowed=False),
        FakePermissionEngine(),
        FakeToolRegistry(tool),
    )

    results = await orchestrator.process(
        request,
        create_context(request),
    )

    assert len(results) == 1
    assert not results[0].success
    assert "Policy denied" in (results[0].error or "")
    assert tool.calls == 0


@pytest.mark.asyncio
async def test_permission_denial_prevents_execution() -> None:
    request = Request(text="Test permission")
    action = Action(tool_name="test.tool")

    tool = FakeTool()

    orchestrator = Orchestrator(
        FakeReasoner(),
        FakePlanner(action),
        FakePolicyEngine(),
        FakePermissionEngine(allowed=False),
        FakeToolRegistry(tool),
    )

    results = await orchestrator.process(
        request,
        create_context(request),
    )

    assert len(results) == 1
    assert not results[0].success
    assert "Permission denied" in (results[0].error or "")
    assert tool.calls == 0


@pytest.mark.asyncio
async def test_missing_tool_prevents_execution() -> None:
    request = Request(text="Test missing tool")
    action = Action(tool_name="missing.tool")

    orchestrator = Orchestrator(
        FakeReasoner(),
        FakePlanner(action),
        FakePolicyEngine(),
        FakePermissionEngine(),
        FakeToolRegistry(),
    )

    results = await orchestrator.process(
        request,
        create_context(request),
    )

    assert len(results) == 1
    assert not results[0].success
    assert "Tool not found" in (results[0].error or "")
