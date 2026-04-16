from __future__ import annotations

from collections import defaultdict
from inspect import isawaitable
from typing import Any, Callable


class DomainEvent:
    """Base class for all domain events."""

    __slots__ = ()


EventHandler = Callable[[DomainEvent], Any]


class EventBus:
    def __init__(self) -> None:
        self._handlers: dict[type[DomainEvent], list[EventHandler]] = defaultdict(list)

    def subscribe(self, event_type: type[DomainEvent], handler: EventHandler) -> None:
        handlers = self._handlers[event_type]
        if handler not in handlers:
            handlers.append(handler)

    def unsubscribe(self, event_type: type[DomainEvent], handler: EventHandler) -> None:
        handlers = self._handlers.get(event_type)
        if not handlers:
            return

        if handler in handlers:
            handlers.remove(handler)

        if not handlers:
            self._handlers.pop(event_type, None)

    def clear(self) -> None:
        self._handlers.clear()

    async def publish(self, event: DomainEvent) -> None:
        for handler in self._handlers_for(event):
            result = handler(event)
            if isawaitable(result):
                await result

    def _handlers_for(self, event: DomainEvent) -> list[EventHandler]:
        handlers: list[EventHandler] = []
        seen: set[EventHandler] = set()

        for event_type, registered_handlers in tuple(self._handlers.items()):
            if isinstance(event, event_type):
                for handler in registered_handlers:
                    if handler in seen:
                        continue
                    seen.add(handler)
                    handlers.append(handler)

        return handlers


event_bus = EventBus()


__all__ = ["DomainEvent", "EventBus", "event_bus"]
