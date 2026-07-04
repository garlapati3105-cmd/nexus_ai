# Branch AI Agent

The `BranchAIAgent` handles operations scoped exclusively to a single pharmacy location. It sits beneath the `RegionalAIAgent` and orchestrates data provided strictly from that branch.

It extends the safe `BaseAgent` boundaries.

## Architecture

```mermaid
sequenceDiagram
    participant H as CEO/Manager
    participant B as BranchAIAgent
    participant T as ToolExecutor
    participant DB as Business Data

    H->>B: execute(AgentRequest)
    activate B
    B->>B: Validate Permission (Local bounds)
    B->>B: Load Memory
    B->>B: select_tools()
    
    B->>T: execute checks
    activate T
    T->>DB: query low stock/KPIs
    DB-->>T: returns
    T-->>B: tool_results
    deactivate T
    
    B->>B: generate_response()
    note right of B: Evaluates low stock.<br/>Triggers local recommendations<br/>or escalates to Regional.
    B-->>H: AgentResponse(BranchAIResponse)
    deactivate B
```

## Responsibilities
- Track expiry mappings locally.
- Recommend local reorder schedules vs transfer requests.
- Track metrics (Order efficiency, staff productivity).
- Issue immediate escalations to Regional bounds for network shortages.
