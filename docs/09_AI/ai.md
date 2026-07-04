# Nexus AI - AI Architecture Specification

| Metadata | Details |
| :--- | :--- |
| **Document Purpose** | Specification for AI Nodes, Prompts, and LangGraph Logic |
| **Primary LLM Engine** | Gemini 2.5 Flash |
| **Orchestrator** | LangGraph / LangChain Core |
| **Version** | 1.0.0 |
| **Date** | 2026-07-03 |

---

## 1. Agent Hierarchical Structure

The Nexus AI network operates identically to a pharmaceutical corporate structure, modeled organically through connected LangGraph nodes.

### 1.1 Regional AI Manager
**Role:** The Macro-Orchestrator. Handles queries that require data aggregation across multiple branches.
**Capabilities:** Can invoke the `Initiate_Transfer` tool. Will negotiate directly with individual Branch AI Managers to locate excess stock before escalating a solution to the Human CEO.

### 1.2 Branch AI Manager
**Role:** The Local Triage Agent. Every branch has one isolated node instance initialized with its specific `branch_id`.
**Capabilities:** Triages incoming localized requests. Determines whether an inquiry should be forwarded to the localized Sales, Inventory, Finance, or HR AI nodes.

### 1.3 Sales AI
**Role:** Frontline Pharmacist Assistant.
**Primary Tool:** Semantic SKU Indexing (conversational identification of drugs via generic symptoms or proprietary names) via ChromaDB.

### 1.4 Inventory AI
**Role:** Supply Chain Predictor.
**Capabilities:** Executes daily scheduled vector searches identifying impending expiry (FEFO) vulnerabilities and predicting `stock_out` conditions based on historical sales velocity.

### 1.5 Finance AI
**Role:** Margin Guardian.
**Capabilities:** Reviews raw SQL arrays to flag anomalous transactional behavior (e.g., localized discounting occurring outside of established thresholds).

### 1.6 HR AI
**Role:** Resource Optimizer.
**Capabilities:** (Future Scope MVP) Connects predictive foot-traffic modeling to localized roster templates.

---

## 2. Execution & Cognitive Flow

### 2.1 Memory & Context Management
*   **Volatile Memory (LangGraph State):** A `TypedDict` retaining the direct sequence of events during a single workflow execution. This is suspended (persisted in Postgres via LangGraph Checkpointers) when halted for human validation.
*   **Long-Term Memory:** Relegated entirely to Supabase SQL. Agents do not infinitely remember past interactions; they query historical logs via API tools when needed (Retrieval-Augmented Generation context).

### 2.2 Prompt Strategy
System prompts enforce strict ReAct (Reasoning and Acting) methodologies.
**Standardized System Prompt Header (Example):**
> *You are the Nexus Regional AI Manager. You answer strictly in JSON conforming to the predefined schema. Never apologize. If you lack authority, you must escalate action to a Human by appending {"approval_required": true} into your response stream.*

### 2.3 LangGraph Architecture
The architecture is inherently non-linear.
*   **Nodes:** Represent the individual Agents (Sales, Inventory, etc.).
*   **Edges:** Determine the routing logically (e.g., if the user asks for a refund, the NLP intent classifier edge routes instantly from `SalesNode` -> `FinanceNode`).
*   **Halt Nodes:** Artificial workflow blockers waiting for an external `/api/resolve` trigger holding a valid JWT.

### 2.4 Tool Calling
Gemini 2.5 Flash native function-calling is enabled strictly for immutable external data gathering and staging immutable mutations.
*   `search_drug_catalog(query: str) -> dict`
*   `stage_inter_branch_transfer(from_id, to_id, qty) -> uuid` (Does not move stock, only stages the request).

### 2.5 Reasoning & Decision Making
Agents operate purely on heuristic probability mapped against strict SQL validations. An agent cannot "decide" to discount an item; it can "propose" the discount because the calculation aligns with profit margins retrieved from the `find_margin()` tool call.

### 2.6 Knowledge Base (ChromaDB)
The unstructured brain. Contains massive unstructured catalogs of pharmaceutical drug equivalents (Generics vs Branded), medical interaction definitions, and legacy SOP (Standard Operating Procedures) documents for pharmacy clerks.

### 2.7 Human Approval (The Imperative Loop)
No destructive state change is autonomous. The LangGraph executes up to the `ActionNode`. If the `ActionNode` requires mutation (SQL UPDATE/DELETE), it forces a `StateInterrupt`. The frontend reads this state, displays the "Approve/Deny" card to the human manager. Clicking "Approve" injects a continuation message back into the LangGraph state machine.

---

## 3. Resilience & Fault Tolerance

### 3.1 Fallback Strategy
If Gemini 2.5 Flash encounters a rate limit or a momentary hallucination (refusing to return proper JSON structure):
1. Pydantic parser catches the `ValidationError`.
2. LangGraph edge route falls back to a specialized `CorrectionNode`.
3. `CorrectionNode` injects the literal Python error back into the prompt: *"You failed to provide JSON. Here is the error: [x]. Try again adhering to structure."*
4. Max 3 Retries. If failed, falls back to standard HTTP 500 alerting the user.

### 3.2 Error Handling
Medical liability prevents automated guesswork during failure. If the KB search returns an ambiguity score lower than 85% for a medication equivalent query, the AI is hard-coded to return: *"Ambiguous query. Please consult the on-duty pharmacist directly."*
