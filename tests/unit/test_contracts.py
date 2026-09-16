from ren.core.contracts import (
    Action,
    ActionResult,
    ContextSnapshot,
    PermissionDecision,
    Plan,
    PolicyDecision,
    Request,
    RiskLevel,
)


def test_request_has_id_and_timestamp() -> None:
    request = Request(text="Hello REN")

    assert request.request_id
    assert request.created_at.tzinfo is not None


def test_action_defaults_to_safe_risk() -> None:
    action = Action(tool_name="test.tool")

    assert action.risk_level == RiskLevel.SAFE


def test_plan_contains_actions() -> None:
    action = Action(tool_name="test.tool")
    plan = Plan(request_id="request-1", steps=(action,))

    assert len(plan.steps) == 1
    assert plan.steps[0] == action


def test_policy_and_permission_are_separate() -> None:
    policy = PolicyDecision(
        allowed=True,
        requires_confirmation=True,
        reason="Critical action requires confirmation.",
    )

    permission = PermissionDecision(
        allowed=True,
        reason="User authorized the action.",
    )

    assert policy.allowed
    assert policy.requires_confirmation
    assert permission.allowed


def test_action_result_represents_success() -> None:
    result = ActionResult(
        action_id="action-1",
        success=True,
        output="completed",
    )

    assert result.success
    assert result.output == "completed"


def test_context_snapshot() -> None:
    context = ContextSnapshot(
        request_id="request-1",
        session_id="session-1",
        capabilities=("browser", "filesystem"),
    )

    assert context.request_id == "request-1"
    assert "browser" in context.capabilities
