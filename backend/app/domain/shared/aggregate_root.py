from __future__ import annotations

from app.domain.shared.domain_event import DomainEvent


class AggregateRoot:
    def __init__(self) -> None:
        self._domain_events: list[DomainEvent] = []

    def _record_event(self, event: DomainEvent) -> None:
        self._domain_events.append(event)

    def collect_events(self) -> list[DomainEvent]:
        events = list(self._domain_events)
        self._domain_events.clear()
        return events

    @property
    def domain_events(self) -> list[DomainEvent]:
        return list(self._domain_events)
