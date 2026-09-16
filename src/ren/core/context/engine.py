from __future__ import annotations

from collections.abc import Iterable

from ren.core.contracts import (
    ContextProvider,
    ContextSnapshot,
    Request,
)


class ContextEngine:
    """Collects contextual information from registered providers."""

    def __init__(
        self,
        providers: Iterable[ContextProvider] = (),
    ) -> None:
        self._providers: list[ContextProvider] = list(providers)

    def register(self, provider: ContextProvider) -> None:
        """Register a context provider."""

        self._providers.append(provider)

    def providers(self) -> tuple[str, ...]:
        """Return registered provider names."""

        return tuple(provider.name for provider in self._providers)

    async def build(
        self,
        request: Request,
        base_context: ContextSnapshot,
    ) -> ContextSnapshot:
        """Build an enriched context snapshot."""

        facts = dict(base_context.facts)

        for provider in self._providers:
            provided_facts = await provider.collect(
                request,
                base_context,
            )

            facts.update(provided_facts)

        return ContextSnapshot(
            request_id=base_context.request_id,
            session_id=base_context.session_id,
            facts=facts,
            memory_refs=base_context.memory_refs,
            capabilities=base_context.capabilities,
        )
