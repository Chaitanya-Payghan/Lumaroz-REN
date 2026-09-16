from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import pytest

from ren.core.context import ContextEngine
from ren.core.contracts import ContextSnapshot, Request


@dataclass
class FakeContextProvider:
    name: str
    facts: dict[str, Any]

    async def collect(
        self,
        request: Request,
        context: ContextSnapshot,
    ) -> dict[str, Any]:
        return self.facts


def create_context(request: Request) -> ContextSnapshot:
    return ContextSnapshot(
        request_id=request.request_id,
        session_id="test-session",
    )


@pytest.mark.asyncio
async def test_context_engine_builds_context() -> None:
    request = Request(text="Hello REN")

    provider = FakeContextProvider(
        name="test",
        facts={"active_app": "VS Code"},
    )

    engine = ContextEngine([provider])

    context = await engine.build(
        request,
        create_context(request),
    )

    assert context.request_id == request.request_id
    assert context.session_id == "test-session"
    assert context.facts["active_app"] == "VS Code"


@pytest.mark.asyncio
async def test_multiple_providers_are_combined() -> None:
    request = Request(text="Context test")

    engine = ContextEngine(
        [
            FakeContextProvider(
                name="system",
                facts={"os": "Windows"},
            ),
            FakeContextProvider(
                name="time",
                facts={"hour": 13},
            ),
        ]
    )

    context = await engine.build(
        request,
        create_context(request),
    )

    assert context.facts["os"] == "Windows"
    assert context.facts["hour"] == 13


@pytest.mark.asyncio
async def test_provider_can_enrich_existing_facts() -> None:
    request = Request(text="Existing context")

    base_context = ContextSnapshot(
        request_id=request.request_id,
        session_id="test-session",
        facts={"os": "Windows"},
    )

    engine = ContextEngine(
        [
            FakeContextProvider(
                name="system",
                facts={
                    "battery": 82,
                    "active_app": "VS Code",
                },
            )
        ]
    )

    context = await engine.build(
        request,
        base_context,
    )

    assert context.facts["os"] == "Windows"
    assert context.facts["battery"] == 82
    assert context.facts["active_app"] == "VS Code"


def test_provider_names_are_exposed() -> None:
    engine = ContextEngine(
        [
            FakeContextProvider(name="system", facts={}),
            FakeContextProvider(name="memory", facts={}),
        ]
    )

    assert engine.providers() == ("system", "memory")


def test_provider_can_be_registered() -> None:
    engine = ContextEngine()

    engine.register(
        FakeContextProvider(
            name="system",
            facts={},
        )
    )

    assert engine.providers() == ("system",)
