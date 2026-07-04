# LangGraph Multi-Agent Orchestration

The `app/ai/langgraph` module replaces hardcoded pipeline executions with a flexible, stateful `StateGraph`.

## Graph Topology

The orchestration sequence supports conditional redirects:

```mermaid
graph TD
    START --> Sales[Sales AI validation]
    Sales --> Inventory[Inventory stock evaluation]
    
    Inventory -->|Stock Available YES| YES[Finance AI metrics check]
    YES --> Invoice[Generate Invoice]
    Invoice --> END
    
    Inventory -->|Stock Available NO| NO[Regional AI Routing]
    NO --> FinanceLocal[Finance Transfer cost calculation]
    FinanceLocal --> Approval[Approval gate verification]
    Approval --> InvoiceTransfer[Generate invoice for transfer]
    InvoiceTransfer --> END
```

## Configured State
- **`GraphWorkflowState`**: Structured as a TypedDict containing localized keys mirroring existing schemas, trace trackers, latency tracking dicts, and intermediate output stores.
- **Checkpointers**: Uses standard `MemorySaver` in-memory checkpoints to enable thread resolution, state recovery, and tracing details.
