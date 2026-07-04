# Nexus AI - High Level Design (HLD)

| Metadata | Details |
| :--- | :--- |
| **Document Purpose** | High Level Architecture & System Design |
| **Document Owner** | Principal Software Architect |
| **Status** | Approved |
| **Version** | 1.0.0 |
| **Date** | 2026-07-03 |

---

## 1. Architecture Overview
Nexus AI utilizes a decoupled, modern cloud-native architecture. The system bifurcates presentation and heavy computational orchestration. The Next.js frontend handles secure presentation and human oversight, while a FastAPI backend serves as the deterministic gateway to the LangGraph autonomous AI network and the Supabase persistence layer.

## 2. System Components
*   **Next.js Client (Web):** Server-Side Rendered UI, Edge Caching, Client-side state.
*   **FastAPI Orchestrator (Backend):** Pydantic validation, Business Logic router, LangGraph executor.
*   **LangGraph/Gemini Engine:** Stateful LLM inference pipelines handling complex natural language workflows.
*   **Supabase PostgreSQL:** The absolute source of truth for all transactional ledgers and RBAC.
*   **ChromaDB:** Vector index utilized for semantic similarity matching (mapping patient NLP queries to exact database SKUs).

## 3. Module Communication
*   **Client -> API:** REST / JWT attached via HTTPS.
*   **API -> Database:** PostgREST / Supabase Python SDK strictly.
*   **API -> LLM Engine:** LangChain SDK invoking the Google Gemini endpoint natively over gRPC/REST.

## 4. Deployment Architecture
*   **Frontend Tier:** Deployed globally to the Edge via Vercel for minimized UI latency.
*   **Backend Tier:** Containerized Python FastAPI application hosted on Render (or similar PaaS) scaling linearly.
*   **Database Tier:** Supabase Managed Cloud Postgres.

## 5. Authentication Flow
1. User requests login via Next.js client.
2. Supabase GoTrue Auth processes credential payload.
3. Supabase returns JWT encapsulating user ID and Branch ID.
4. Client passes JWT in `Authorization` header to FastAPI.
5. FastAPI decodes JWT, verifies integrity, and utilizes the embedded claims to enforce logic paths.

## 6. AI Architecture
Utilizing a multi-node Graph network (LangGraph). 
Instead of a linear chain, nodes are categorized by departmental function (`FinanceNode`, `InventoryNode`, `RegionalRouterNode`). The `RegionalRouterNode` acts as a triage engine, directing specific NLP queries down to the correct specialized LangChain prompt sequence, yielding highly predictable JSON output.

## 7. Database Architecture
Relational standard. Core normalized tables:
*   `core.branches`
*   `core.users` (mapped to branch)
*   `inventory.skus` (Master catalogue)
*   `inventory.stock_ledger` (Append-only immutable transaction log acting as the absolute source of truth for current stock).

## 8. Frontend Architecture
React (Next.js App Router). Utilizing React Server Components (RSC) to securely fetch preliminary non-interactive data server-side, reducing client payload. Client components used exclusively for highly interactive slices (Charts, AI Chat inputs).

## 9. Backend Architecture
Python FastAPI. Built strongly on Pydantic schemas. Every endpoint has an explicit Request model and Response model, ensuring that if the LLM engine generates a malformed response, it is caught as a 500 error *before* it reaches the Next.js client or mutates the database.

## 10. Security
*   **Transport Layer:** TLS 1.3 enforced globally.
*   **Data Tier:** Supabase Row Level Security (RLS) is paramount. `auth.uid()` checks ensure cross-branch data bleeding is impossible at a database level regardless of API flaws.
*   **LLM Tier:** PII removal middleware strips patient data logically before vectorizing or inferring against third-party AI APIs.

## 11. Scalability
*   **Horizontal scaling:** The FastAPI backend is completely stateless (LangGraph states are cached via Redis or persisted to Postgres temporarily), allowing infinite horizontal pod scaling based on inbound traffic volume.
*   **Database connection limits:** PgBouncer utilized in front of Supabase to pool connections effectively preventing exhaustion during high-volume API requests across the 10 branches.

## 12. Technology Decisions
| Component | Decision | Rationale |
| :--- | :--- | :--- |
| Core API | **FastAPI** | Native Pydantic integration, asynchronous core, dominant ML/AI ecosystem support in Python. |
| AI Pipeline | **LangGraph** | Enables cyclical, multi-actor conversations (unlike linear LangChain expressions) which is required for negotiating stock transfers. |
| DB Engine | **Supabase Postgres** | Built-in Auth, RLS, and instant API generation minimizes DevOps bootstrapping time drastically. |

## 13. Architecture Diagrams
*(Visualized placeholder)*
`[Client (Next.js/Vercel)]` <--(HTTPS/JWT)--> `[FastAPI (Render)]`
`[FastAPI (Render)]` <--(HTTP API)--> `[Gemini LLM / LangGraph]`
`[FastAPI (Render)]` <--(PostgREST)--> `[Supabase PostgreSQL]`

## 14. Data Flow
**Action: Approval of automated stock transfer.**
1. `Client` sends `POST /api/action/approve {action_id, branch_jwt}`.
2. `FastAPI` validates Branch JWT matches the target `action_id` owner.
3. `FastAPI` invokes Supabase RPC function `exec_stock_transfer`.
4. Supabase atomically decrements Branch A ledger and increments Branch B ledger.
5. Supabase returns success block.
6. `FastAPI` resumes suspended LangGraph state, informing AI the transfer succeeded.
7. AI formulates natural language confirmation.
8. `FastAPI` returns 200 OK + Confirmation string to Client.

## 15. Sequence Diagrams
*(To be expanded in detailed tooling utilizing Mermaid.js natively within repository readmes or execution spaces.)*
