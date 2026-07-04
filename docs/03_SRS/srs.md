# IEEE Software Requirements Specification (SRS)
## Nexus AI - Pharmacy Operating System

| Metadata | Details |
| :--- | :--- |
| **Document Purpose** | Software Requirements Specification (IEEE standard) |
| **Document Owner** | Principal Software Architect |
| **Status** | Approved |
| **Version** | 1.0.0 |
| **Date** | 2026-07-03 |

---

## 1. Introduction

### 1.1 Purpose
This document provides a comprehensive Software Requirements Specification (SRS) for the Nexus AI project. It delineates the behavioral and structural logic for creating a scalable, multi-agent artificial intelligence platform handling the operational backbone of localized pharmacy networks.

### 1.2 Scope
Nexus AI encompasses a multi-tier architectural system comprising a Next.js frontend, a FastAPI Python orchestration backend, robust Supabase Postgres data structures, and LangGraph-driven Gemini AI node workflows. The system replaces passive localized ERPs with an active digital workforce optimizing inter-branch data logistics, POS execution, and enterprise analytics, initially constrained to a 10-branch MVP.

### 1.3 Definitions
*   **State Machine:** The programmatic structure (via LangGraph) tracking multi-agent conversation history and halted approvals.
*   **Edge Determinism:** Absolute mathematical verification of transactional data taking place primarily at the Supabase/SQL boundary, abstracted from the LLM. 
*   **JWT:** JSON Web Token used securely across FastApi and Next.js for precise role validation.

---

## 2. Overall Description

### 2.1 System Features
The fundamental mechanism driving Nexus AI is a stateless API connected to a highly stateful Database and workflow engine. 
*   Inter-Agent Message Bus (LangChain).
*   LLM Schema Parsing and Validation Constraints (Pydantic / FastAPI).
*   Deterministic Database operations executing isolated SQL transactions.
*   Real-time Websocket/Edge subscriptions for human notification queues.

### 2.2 External Interfaces

**User Interfaces**
*   CEO Workspace (Macro-Dashboard, Financial Aggregation Views).
*   Branch Manager Workspace (Operational queues, Pending Approvals, POS Insights).

**Software Interfaces**
*   **Supabase PostgreSQL (Database/Auth):** Interface via Supabase Python/JS SDK; relies strictly on REST/PostgREST.
*   **Gemini 2.5 Flash API:** Interface via official Google Generative AI SDK, heavily structured forcing JSON outputs.
*   **ChromaDB API:** Connected via LangChain Vector Stores for document/SKU similarity search embeddings.

---

## 3. Performance Requirements
*   **Response Time:** 
    *   API Database Read/Writes: < 150ms.
    *   LLM Inference (Single prompt): < 2000ms.
    *   Complex LangGraph Negotiation (Multi-agent loop): < 2500ms up until human interaction gate.
*   **Throughput:** 
    *   System must comfortably manage 25 concurrent requests per second equating to ~85,000 daily transaction endpoints across 10 distinct branches.
*   **Vector Search Efficiency:**
    *   ChromaDB must perform Cosine Similarity comparisons against up to 10,000 localized pharmaceutical product embeddings in sub-100ms blocks.

---

## 4. Security Requirements
*   **Authentication:** Strictly enforced JWT protocols routed via Supabase Auth.
*   **Row-Level Security (RLS):** Every PostgreSQL table queried must validate the UUID of the executing function, restricting branch operators strictly to `branch_id = (SELECT branch_id FROM users WHERE id = auth.uid())`.
*   **PII Sanitization:** All patient data/names referenced during standard transactions must be stripped before being bundled as context to the Gemini LLM endpoint.
*   **Prompt Injection Modeling:** Input endpoints dealing directly with conversational agents must validate through a Pydantic guardrail identifying and aborting recognized malicious overrides (e.g. system prompt overrides).

---

## 5. Business Rules
*   **Rule A [Approval Gate]:** No inventory vector can be reduced or transferred cross-branch strictly via an LLM instruction. The LLM may only stage a `Transfer Request` payload forcing human UUID verification to officially mutate state.
*   **Rule B [Expiry Priority]:** Pharmaceutical inventory logic prioritizing FEFO (First Expired, First Out) is deterministic and executed entirely in SQL space; AI agents may not override mathematical fulfillment logic, they only invoke it.
*   **Rule C [Hierarchy Escalation]:** If an AI Branch Manager is unable to source an item logically, it must escalate exclusively to the AI Regional Manager node; it cannot negotiate directly with adjacent Branch Managers.

---

## 6. Constraints
*   **Hardware Architecture Integration:** Existing pharmacy POS hardware (barcode scanners) will communicate via the Next.js client layer translating raw input streams into standard UI field entries. No native Windows drivers built.
*   **Development Deadlines:** Built strictly against hackathon deadlines, thereby favoring rapid prototyping tools (Tailwind, shadcn/ui) over highly customized UX assets in the immediate iteration.

---

## 7. Quality Attributes
*   **Reliability:** Strict fallback routines in FastAPI handling intermittent API timeouts from external LLM providers gracefully without locking the LangGraph state.
*   **Maintainability:** Monorepo architecture enforcing segregated domains (`/apps/web`, `/packages/core`, `/apps/api`) preventing spaghetti dependencies.
*   **Usability:** Minimal cognitive friction. Any human-actionable item must be highlighted vividly in a unified "Pending Actions" inbox.

---

## 8. Acceptance Criteria
1.  **Architecture Initialization:** Next.js and FastAPI environments boot successfully, connect efficiently via CORS, and authenticate to a unified Supabase cloud project.
2.  **Workflow Verification:** The LangGraph execution correctly halts at an arbitrary `ActionRequired(human)` class object, waits indefinitely via thread tracking, and continues cleanly upon receiving external API verification.
3.  **Data Isolation Validation:** A unit test executing a query using a Branch Manager role successfully returns a 403 Forbidden payload when attempting to read cross-branch financial aggregates natively restricted to CEO RLS profiles.

---

## 9. Appendices
*   **Appendix A:** Next.js / React Router Implementation Guide (To be completed).
*   **Appendix B:** FastAPI Endpoints & Pydantic Definitions structure (To be completed).
*   **Appendix C:** Core Agent Prompts Master Log (To be completed).
