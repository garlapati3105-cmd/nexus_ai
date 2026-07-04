# Finance AI Agent

The `FinanceAIAgent` manages financial performance tracking, profit margin safety gates, invoice generation hooks, and procurement decision trees.

It evaluates whether to trigger local inter-branch stock transfers or request external supplier purchases.

## Architecture

```mermaid
sequenceDiagram
    participant K as AI Kernel
    participant F as FinanceAIAgent
    participant T as ToolExecutor

    K->>F: execute(AgentRequest)
    activate F
    
    F->>T: get_dashboard_kpis()
    T-->>F: daily/weekly/monthly revenue and expenses
    
    F->>T: retrieve_medicine_information(medicine_id)
    T-->>F: supplier_price, local_cost
    
    F->>T: calculate_transfer_cost(medicine_id)
    T-->>F: transfer_freight
    
    rect rgb(245, 245, 245)
        note right of F: Decision Logic:<br/>Compare Transfer vs Supplier Cost
        F->>F: supplier_total = qty * supplier_price
        F->>F: transfer_total = (qty * local_cost) + freight
        alt transfer_total < supplier_total
            F->>F: cheapest_option = TRANSFER
        else
            F->>F: cheapest_option = SUPPLIER
        end
    end
    
    F-->>K: return FinanceAIResponse
    deactivate F
```

## Business Rules & Savings Logic
1. **Procurement Comparison**: Calculates standard total purchase costs against network transfer costs (local item cost + freight charges). Recommends the action yielding the highest net savings path.
2. **Branch Profitability Scoring**: Analyzes expenses (salaries, utilities, waste) against daily revenue snapshots to compute margins.
3. **Billing and Audits**: Prepares structured invoice and savings details for dashboard display or API reporting.
