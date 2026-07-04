# Sales AI Agent

The `SalesAIAgent` evaluates incoming customer checkout orders, enforces prescription checking logic, resolves pricing structures, and performs generic medicine substitutions.

It interfaces with the environment strictly via standard tools, following the clean architecture guidelines of the `BaseAgent` framework.

## Architecture

```mermaid
sequenceDiagram
    participant K as AI Kernel
    participant S as SalesAIAgent
    participant T as ToolExecutor

    K->>S: execute(AgentRequest)
    activate S
    S->>S: Verify authorization
    S->>S: Load conversation hooks
    
    S->>T: check_local_inventory(medicine_id)
    T-->>S: stock quantity
    
    rect rgb(240, 240, 240)
        note right of S: Check: Requires prescription?
        S->>T: retrieve_medicine_information(medicine_id)
        T-->>S: requires_prescription, generic_name
        
        alt requires_prescription is true AND has_prescription is false
            S->>S: validation_status = REJECTED_PRESCRIPTION
            S->>S: Recommend generic OTC alternative
        else
            alt stock_limit > 0
                S->>S: validation_status = APPROVED
            else
                S->>T: check_network_inventory(medicine_id)
                T-->>S: branch stock list
                alt network branches exist
                    S->>S: validation_status = REDIRECT_TRANSFER
                else
                    S->>S: validation_status = BACKORDER
                end
            end
        end
    end
    
    S-->>K: return SalesAIResponse
    deactivate S
```

## Configured Rules
1. **Prescription Security Gate**: Automatically stops pharmacy orders referencing scheduled medicines if the validation context has `allows_unrestricted` flag or prescription parameters set to false. Recommends over-the-counter equivalents.
2. **Dynamic Stock Balancing**: Redirects order workflows into Transfer proposals if local stock runs out but network locations possess inventory.
3. **Backorder Resolution**: Triggers supplier replenishment events when network-wide depletion is verified.
