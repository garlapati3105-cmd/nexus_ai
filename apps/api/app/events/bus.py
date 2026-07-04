"""
Nexus AI — Enterprise Event Bus
Brokers publish/subscribe operations, retries, and dead letter queue routing.
"""
from __future__ import annotations
import logging
from typing import Any, Callable, Dict, List, Set, Tuple
from app.events.models import BaseEvent

logger = logging.getLogger("EventBus")

class SimpleEventBus:
    """Manages publishers, subscriptions, retry schedules, and DLQ stores."""
    
    def __init__(self, max_retries: int = 3):
        self.max_retries = max_retries
        self._subscribers: Dict[str, Set[Callable[[BaseEvent], Any]]] = {}
        self.dead_letter_queue: List[Tuple[BaseEvent, Exception]] = []
        self.log_store: List[BaseEvent] = []

    def subscribe(self, event_type: str, callback: Callable[[BaseEvent], Any]) -> None:
        """Binds a subscriber callback to an event type."""
        if event_type not in self._subscribers:
            self._subscribers[event_type] = set()
        self._subscribers[event_type].add(callback)

    def unsubscribe(self, event_type: str, callback: Callable[[BaseEvent], Any]) -> None:
        """Removes a subscriber callback."""
        if event_type in self._subscribers:
            self._subscribers[event_type].discard(callback)

    def publish(self, event: BaseEvent) -> None:
        """Dispatches an event, logging transactions and triggering retries if callbacks fail."""
        self.log_store.append(event)
        subscribers = self._subscribers.get(event.event_type, set())
        
        # If wildcard or base event subscriptions exist
        base_subs = self._subscribers.get("*", set())
        all_subs = subscribers.union(base_subs)
        
        for subscriber in all_subs:
            self._dispatch_with_retry(subscriber, event)

    def _dispatch_with_retry(self, subscriber: Callable[[BaseEvent], Any], event: BaseEvent) -> None:
        """Tries execution up to max_retries before routing to DLQ."""
        retries = 0
        last_error = None
        while retries < self.max_retries:
            try:
                subscriber(event)
                return # Successful execution
            except Exception as e:
                retries += 1
                last_error = e
                logger.warning(f"Subscriber failed: {e}. Retrying {retries}/{self.max_retries}...")
                
        # If all retries exhausted, send to DLQ
        self.dead_letter_queue.append((event, last_error or Exception("Max retries exceeded")))
        logger.error(f"Event {event.event_id} of type {event.event_type} routed to DLQ. Error: {last_error}")
