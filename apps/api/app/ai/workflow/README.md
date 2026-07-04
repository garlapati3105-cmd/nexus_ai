# Agent Collaboration & Multi-Agent Orchestration

This module coordinates active collaboration between business agents (Sales, Inventory, Finance, Regional) using the AI Operating Kernel to parse customer purchase events.

## Collaborative Ordering Sequence

```mermaid
sequenceDiagram
    participant C as Customer
    participant WC as WorkflowCoordinator
    participant EB as InMemoryMessageBus
    participant S as SalesAIAgent
    participant I as InventoryAIAgent
    participant F as FinanceAIAgent
    participant R as RegionalAI (Composer)

    C->>WC: Submit Order Request
    activate WC
    WC->>WC: Initialize WorkflowContext & SharedState

    WC->>S: execute(Sales Request)
    activate S
    S-->>WC: SalesAIResponse (validation_status)
    deactivate S

    WC->>I: execute(Inventory Survey)
    activate I
    I-->>WC: InventoryAIResponse (checked=True)
    deactivate I

    alt validation_status is REDIRECT_TRANSFER
        WC->>F: execute(Finance Review)
        activate F
        F-->>WC: FinanceAIResponse (cost_comparison)
        deactivate F
        
        WC->>WC: Populate TransferState logs (needed=True)
    end

    WC->>R: DecisionComposer::compose(Sales, Inventory, Finance)
    activate R
    R->>R: Merge responses & evaluate explainability evidence
    R-->>WC: overall composite recommendation
    deactivate R

    WC->>EB: broadcast_context_update(Context)
    WC-->>C: Complete WorkflowContext (Execution Details)
    deactivate WC
```

## State & Metrics Captured
- **`SharedBusinessState`**: Enforces strict fields bounding Order, Inventory, Transfer, Approval, Invoice, and Notifications.
- **`CollaborationMetrics`**: Logs workflow duration, individual agent processing latencies, and total message counts.
