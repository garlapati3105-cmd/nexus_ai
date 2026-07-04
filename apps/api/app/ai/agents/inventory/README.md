# Inventory AI Agent

The `InventoryAIAgent` acts as the primary telemetry mapping intelligence layer for stock optimization. It collaborates closely with `BranchAI` and `RegionalAI` boundaries, specifically monitoring reorder algorithms, supply chain thresholds, turnover velocity, and network-wide dead-stock isolations.

## Architecture & Integration

This Agent acts deterministically under the `BaseAgent` abstraction bounds, utilizing only registered inventory tool capabilities.

```mermaid
sequenceDiagram
    participant K as AI Kernel
    participant I as InventoryAIAgent
    participant T as ToolExecutor
    
    K->>I: execute(AgentRequest)
    activate I
    I->>I: Verify permissions (Inventory bounds)
    I->>I: select_tools()
    note right of I: Pulls network bounds, expiry lists.
    
    I->>T: Dispatch tools
    activate T
    T-->>I: Returns Overstock/Shortage mappings
    deactivate T
    
    I->>I: generate_response()
    note right of I: Executes Rules:<br/>1. Expiry -> Transfer to High Demand<br/>2. Network Stockout -> Supplier Reorder<br/>3. Surplus -> Rebalance
    I-->>K: Returns InventoryAIResponse
    deactivate I
```

## Business Rules Tracked
- Dead Stock Identification
- Automated Branch-to-Branch Stock Transfers (preferring Network balancing over direct supplier injection)
- Expiry Hazard Ratios
- Turnover KPI Tracking
