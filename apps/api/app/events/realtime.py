"""
Nexus AI — Realtime Supabase Channels
Implements database change broadcast pipelines and update channels.
"""
from __future__ import annotations
from typing import Any, Dict, List, Optional
from app.events.models import BaseEvent
from app.events.websocket import WebSocketConnectionManager

class RealtimeChannel:
    """Manages real-time db change notifications, metrics, and network configurations."""
    
    def __init__(self, channel_name: str, ws_manager: WebSocketConnectionManager):
        self.channel_name = channel_name
        self.ws_manager = ws_manager
        self.subscribed_clients: List[str] = []

    def subscribe_client(self, client_id: str) -> None:
        """Saves client ID to active subscription track."""
        if client_id not in self.subscribed_clients:
            self.subscribed_clients.append(client_id)

    def unsubscribe_client(self, client_id: str) -> None:
        """Removes client ID from active subscription track."""
        if client_id in self.subscribed_clients:
            self.subscribed_clients.remove(client_id)

    def broadcast_db_change(self, table: str, record_id: str, action: str, data: Dict[str, Any]) -> int:
        """Forces a realtime DB change notification to all active subscribers of this channel."""
        payload = {
            "channel": self.channel_name,
            "type": "database_change",
            "table": table,
            "record_id": record_id,
            "action": action, # "INSERT" | "UPDATE" | "DELETE"
            "data": data
        }
        
        broadcast_count = 0
        for client_id in self.subscribed_clients:
            conn = self.ws_manager.active_connections.get(client_id)
            if conn:
                try:
                    conn.send_json(payload)
                    broadcast_count += 1
                except Exception:
                    pass
        return broadcast_count

    def broadcast_realtime_metrics(self, resource_metrics: Dict[str, Any]) -> int:
        """Forces system resource telemetry metrics updates to active subscribers."""
        payload = {
            "channel": self.channel_name,
            "type": "dashboard_metrics",
            "metrics": resource_metrics
        }
        
        broadcast_count = 0
        for client_id in self.subscribed_clients:
            conn = self.ws_manager.active_connections.get(client_id)
            if conn:
                try:
                    conn.send_json(payload)
                    broadcast_count += 1
                except Exception:
                    pass
        return broadcast_count
