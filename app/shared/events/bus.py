from __future__ import annotations

import asyncio
from collections import defaultdict
from inspect import isawaitable
from typing import Any, Callable

from app.shared.events.base import DomainEvent


EventHandler = Callable[[DomainEvent], Any]


class EventBus:
    def __init__(self) -> None:
        self._handlers: dict[type[DomainEvent], list[EventHandler]] = defaultdict(list)

    def subscribe(self, event_type: type[DomainEvent]):
        def decorator(handler: EventHandler) -> EventHandler:
            handlers = self._handlers[event_type]
            if handler not in handlers:
                handlers.append(handler)
            return handler

        return decorator

    def unsubscribe(self, event_type: type[DomainEvent], handler: EventHandler) -> None:
        handlers = self._handlers.get(event_type)
        if not handlers:
            return
        if handler in handlers:
            handlers.remove(handler)
        if not handlers:
            self._handlers.pop(event_type, None)

    async def publish(self, event: DomainEvent) -> None:
        handlers = self._handlers_for(event)
        if not handlers:
            return
        await asyncio.gather(*(self._invoke(handler, event) for handler in handlers))

    async def _invoke(self, handler: EventHandler, event: DomainEvent) -> Any:
        result = handler(event)
        if isawaitable(result):
            return await result
        return result

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


bus = EventBus()


__all__ = ["bus"]