"""
Nexus AI — Inbound Event Handlers
Maps published business events to live websocket broadcasts and metric logs.
"""
from __future__ import annotations
import logging
from typing import Dict, Any, List
from app.events.models import BaseEvent, OrderCreated, LowStockDetected, NotificationCreated
from app.events.websocket import WebSocketConnectionManager

logger = logging.getLogger("EventHandlers")

class BusinessEventHandler:
    """Invokes downstream actions when specific business events propagate on the bus."""
    
    def __init__(self, ws_manager: WebSocketConnectionManager):
        self.ws_manager = ws_manager
        self.received_events: List[BaseEvent] = []
        self.dashboard_metrics: Dict[str, Any] = {
            "total_revenue": 0.0,
            "total_orders": 0,
            "net_savs": 0.0,
            "low_stock_alerts_count": 0
        }

    def handle_order_created(self, event: BaseEvent) -> None:
        """Processes order registrations, updating real-time KPI metrics."""
        self.received_events.append(event)
        self.dashboard_metrics["total_orders"] += 1
        
        amount = event.payload.get("amount", 0.0)
        self.dashboard_metrics["total_revenue"] += amount
        
        logger.info(f"Handler: Recorded OrderCreated. New order count: {self.dashboard_metrics['total_orders']}")
        
        # Broadcast metric changes over WS connection pool
        self.ws_manager.broadcast({
            "event_type": "DashboardMetricsUpdated",
            "organization_id": event.organization_id,
            "payload": self.dashboard_metrics
        })

    def handle_low_stock_detected(self, event: BaseEvent) -> None:
        """Triggers alerts when inventory thresholds are breached."""
        self.received_events.append(event)
        self.dashboard_metrics["low_stock_alerts_count"] += 1
        
        logger.warning(f"Handler: Low stock detected on medicine {event.payload.get('medicine_id')}")
        
        # Broadcast notification payload
        self.ws_manager.broadcast({
            "event_type": "NotificationCreated",
            "organization_id": event.organization_id,
            "payload": {
                "message": f"Low Stock Warning: Medicine {event.payload.get('medicine_id')} below limit.",
                "branch_id": event.branch_id
            }
        })
