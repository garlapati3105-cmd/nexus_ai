# Enterprise Event & Realtime System

The `app/events/` module shifts Nexus AI into a reactive, event-driven architecture. 

It tracks and broadcasts database updates, inventory mutations, and decision updates instantly contextually.

## Realtime Message Loop

```mermaid
graph TD
    EventSender[Core Engine Workflow] -->|1. Emits payload| Bus[SimpleEventBus]
    Bus -->|2. Relays to subscribers| Handler[BusinessEventHandler]
    
    subgraph Event Broker Layer
        Bus -->|If fails 3 times| DLQ[(Dead Letter Queue)]
    end
    
    Handler -->|3. Updates metrics| WSManager[WebSocketConnectionManager]
    Handler -->|4. DB Change trigger| Realtime[RealtimeChannel]
    
    WSManager -->|5. Push payload| Clients[Connected UI Browsers]
    Realtime -->|6. Push update notifications| Clients
```

## Security Profiles
- **Organization Isolation**: Event broadcasts sanitize packages using `organization_id` matching rules.
- **WebSocket Auth**: Authenticators match credentials tokens to active subscriber tracks.
