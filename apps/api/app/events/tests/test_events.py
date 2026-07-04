import unittest
from unittest.mock import MagicMock
import time

from app.events.models import BaseEvent, OrderCreated, LowStockDetected
from app.events.bus import SimpleEventBus
from app.events.websocket import WebSocketConnectionManager, MappedWebSocket
from app.events.realtime import RealtimeChannel
from app.events.handlers import BusinessEventHandler

class TestEnterpriseEvents(unittest.TestCase):
    
    def test_event_bus_retry_and_dlq(self):
        """Verify the event bus retries failing subscribers and forwards to DB Dead Letter Queue."""
        bus = SimpleEventBus(max_retries=2)
        
        # Mock failing subscriber
        failing_sub = MagicMock(side_effect=Exception("Database lock error"))
        bus.subscribe("OrderCreated", failing_sub)
        
        evt = OrderCreated(organization_id="org-123", payload={"order_id": "O-1"})
        
        # Publish
        bus.publish(evt)
        
        # Verify subscriber was tried twice before landing in DLQ
        self.assertEqual(failing_sub.call_count, 2)
        self.assertEqual(len(bus.dead_letter_queue), 1)
        self.assertEqual(bus.dead_letter_queue[0][0].event_id, evt.event_id)

    def test_websocket_broadcast_and_isolation(self):
        """Verify organization-based isolation filter on websocket broadcasts."""
        mgr = WebSocketConnectionManager()
        
        sock_1 = MappedWebSocket("client-1")
        sock_2 = MappedWebSocket("client-2")
        
        mgr.connect("client-1", sock_1)
        mgr.connect("client-2", sock_2)
        
        # Broadcast event specifying org isolation
        msg = {
            "organization_id": "org-aaa",
            "message": "Update code data"
        }
        
        mgr.broadcast(msg, org_id="org-aaa")
        
        # Verify both sockets connections received it (isolation holds true)
        self.assertEqual(len(sock_1.sent_messages), 1)
        self.assertEqual(len(sock_2.sent_messages), 1)
        
        # Send message with different org filter
        mgr.broadcast(msg, org_id="org-bbb")
        
        # Counts should remain at 1
        self.assertEqual(len(sock_1.sent_messages), 1)

    def test_realtime_db_changes_channels(self):
        """Verify that change signals propagate over realtime channels."""
        mgr = WebSocketConnectionManager()
        sock = MappedWebSocket("client-1")
        mgr.connect("client-1", sock)
        
        channel = RealtimeChannel("db-changes", mgr)
        channel.subscribe_client("client-1")
        
        channel.broadcast_db_change("orders", "O-123", "INSERT", {"amount": 25.00})
        
        self.assertEqual(len(sock.sent_messages), 1)
        self.assertEqual(sock.sent_messages[0]["table"], "orders")
        self.assertEqual(sock.sent_messages[0]["action"], "INSERT")

    def test_business_handlers_metrics(self):
        """Verify business event updates metrics correctly."""
        mgr = WebSocketConnectionManager()
        handler = BusinessEventHandler(mgr)
        
        # Register Event
        evt = OrderCreated(organization_id="org-123", payload={"amount": 150.00})
        handler.handle_order_created(evt)
        
        self.assertEqual(handler.dashboard_metrics["total_orders"], 1)
        self.assertEqual(handler.dashboard_metrics["total_revenue"], 150.0)

if __name__ == "__main__":
    unittest.main()
