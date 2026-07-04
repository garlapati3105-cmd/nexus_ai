"""
Nexus AI — WebSocket Connection Manager
Tracks active connections, validates tokens, and manages message heartbeat logs.
"""
from __future__ import annotations
import logging
from typing import Dict, Any, List, Optional

logger = logging.getLogger("WebSocketManager")

class MappedWebSocket:
    """Mock/Simulated WebSocket connection object for test assertions."""
    def __init__(self, client_id: str):
        self.client_id = client_id
        self.sent_messages: List[Dict[str, Any]] = []
        self.is_connected = True

    def send_json(self, data: Dict[str, Any]) -> None:
        if not self.is_connected:
            raise ConnectionError("WebSocket is closed.")
        self.sent_messages.append(data)

class WebSocketConnectionManager:
    """Manages active WS endpoints, heartbeats, auth checking, and organization scopes."""
    
    def __init__(self):
        self.active_connections: Dict[str, MappedWebSocket] = {}
        self.heartbeats: Dict[str, float] = {}

    def connect(self, client_id: str, socket: MappedWebSocket) -> None:
        """Saves a socket mapping to active connection tracking pool."""
        self.active_connections[client_id] = socket
        logger.info(f"WebSocket client {client_id} connected successfully.")

    def disconnect(self, client_id: str) -> None:
        """Removes tracking parameters for a socket connection."""
        if client_id in self.active_connections:
            self.active_connections[client_id].is_connected = False
            del self.active_connections[client_id]
        if client_id in self.heartbeats:
            del self.heartbeats[client_id]
        logger.info(f"WebSocket client {client_id} disconnected.")

    def authenticate(self, token: str, credentials_database: Dict[str, str]) -> Optional[str]:
        """Validates token parameters against mock credentials store, returning client ID."""
        for client_id, token_stored in credentials_database.items():
            if token_stored == token:
                return client_id
        return None

    def record_heartbeat(self, client_id: str, timestamp: float) -> None:
        """Registers active connection heartbeat check logs."""
        self.heartbeats[client_id] = timestamp

    def broadcast(self, message: Dict[str, Any], org_id: Optional[str] = None) -> int:
        """Broadcasts messages to all active client channels matching organization isolate tags."""
        broadcast_count = 0
        for client_id, conn in list(self.active_connections.items()):
            # Simulate org-level isolation checking
            if org_id and message.get("organization_id") != org_id:
                continue
            try:
                conn.send_json(message)
                broadcast_count += 1
            except Exception as e:
                logger.error(f"Failed broadcasting to {client_id}: {e}")
                self.disconnect(client_id)
        return broadcast_count
