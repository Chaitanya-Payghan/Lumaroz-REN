from __future__ import annotations

from ren.core.contracts import (
    ActionResult,
    ContextSnapshot,
    PermissionEngine,
    Planner,
    PolicyEngine,
    Reasoner,
    Request,
    ToolRegistry,
)


class Orchestrator:
    """Coordinates REN's request-processing pipeline."""

    def __init__(
        self,
        reasoner: Reasoner,
        planner: Planner,
        policy_engine: PolicyEngine,
        permission_engine: PermissionEngine,
        tool_registry: ToolRegistry,
    ) -> None:
        self._reasoner = reasoner
        self._planner = planner
        self._policy_engine = policy_engine
        self._permission_engine = permission_engine
        self._tool_registry = tool_registry

    async def process(
        self,
        request: Request,
        context: ContextSnapshot,
    ) -> tuple[ActionResult, ...]:
        """Process a request through planning, policy, permission, and execution."""

        await self._reasoner.reason(request, context)

        plan = await self._planner.create_plan(request, context)

        results: list[ActionResult] = []

        for action in plan.steps:
            policy = await self._policy_engine.evaluate(action, context)

            if not policy.allowed:
                results.append(
                    ActionResult(
                        action_id=action.action_id,
                        success=False,
                        error=f"Policy denied action: {policy.reason}",
                    )
                )
                continue

            permission = await self._permission_engine.authorize(action, context)

            if not permission.allowed:
                results.append(
                    ActionResult(
                        action_id=action.action_id,
                        success=False,
                        error=f"Permission denied action: {permission.reason}",
                    )
                )
                continue

            tool = self._tool_registry.get(action.tool_name)

            if tool is None:
                results.append(
                    ActionResult(
                        action_id=action.action_id,
                        success=False,
                        error=f"Tool not found: {action.tool_name}",
                    )
                )
                continue

            result = await tool.execute(action)
            results.append(result)

        return tuple(results)
