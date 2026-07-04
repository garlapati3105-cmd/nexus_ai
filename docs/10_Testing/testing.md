# Nexus AI - Testing Strategy

| Metadata | Details |
| :--- | :--- |
| **Document Purpose** | Comprehensive Test Matrix for SaaS Deployments |
| **Document Owner** | QA / Engineering Lead |
| **Status** | Approved |
| **Version** | 1.0.0 |
| **Date** | 2026-07-03 |

---

## 1. Overview
Given the combination of autonomous LangGraph AI processes and rigid pharmaceutical inventory constraints, the Nexus AI testing strategy operates on a "Trust, but Mathematically Verify" paradigm. While AI outputs are stochastic natively, our FastAPI wrappers ensuring database mutation are entirely deterministic unit-testable blocks.

## 2. Core Testing Methodologies

### 2.1 Unit Testing
*   **Backend (Python/PyTest):** Validates Pydantic schemas, isolated database execution (mocking Supabase API), and individual Agent Tool output wrappers (e.g., verifying `calculate_fefo_expiry()` yields the correct date integer).
*   **Frontend (Vitest / Jest):** Validates React Hook state transitions, complex routing dependencies, and standard UI rendering checks (ensuring Shadcn/ui mounts properly without hydration errors).

### 2.2 Integration Testing
Verities that FastApi controllers successfully handshake with both the actual Supabase Development branch and the active LangSmith/Gemini test environments without CORS failure or unhandled token death.

### 2.3 Workflow Testing
Crucially tests the LangGraph state machine logic sequence. 
*   *Test:* Inject a mock event triggering "Inventory Alert".
*   *Expectation:* The graph advances to `RegionalNode`, halts at `HumanGateNode`, waits indefinitely until unblocked by test script, and strictly proceeds to `SupabaseUpdateNode`. 

### 2.4 UI Testing
*   **Tool:** Playwright or Cypress.
*   Automated scripts simulating a human clerk authenticating, opening a Pending Action, viewing an AI summary, and clicking "Approve" (validating UI responsiveness and optimistic update logic).

### 2.5 API Testing
*   **Tool:** Postman / Insomnia (Exported collections).
*   Rigorous iteration over all endpoints defined in `08_API` validating HTTP 200/400 codes, checking explicitly that Malformed JWTs return immediate `401 Unauthorized` errors.

### 2.6 AI Prompt Testing (Evaluation)
*   **Tooling:** LangSmith / Ragas.
*   Since prompts drift in effectiveness, we maintain a test array of 100 historical queries comparing the LLM's new answers against baseline expectations. 
*   *Metric:* Cosine similarity of the AI's answer vector compared against the "perfectly crafted" human baseline answer vector must exceed 0.90.

### 2.7 Performance Testing
*   **Tooling:** k6 or Locust.
*   Simulating 1,000 localized POS requests per minute directly hitting the FastAPI gateway simulating peak operational hours across the network, enforcing our `< 2.5s` SLA.

### 2.8 Security Testing
*   **Focus:** Edge-case abuse testing against Supabase Row Level Security.
*   *Test:* Using a Branch Manager JWT (Branch ID 4) to manually POST a transfer request originating from Branch ID 7. 
*   *Expectation:* Immediate 403 Forbidden generated at the Postgres database tier, un-overrideable by the backend application layer.

### 2.9 Acceptance Testing
Conducted by designated QA pharmacists or stakeholder proxies in a UAT (User Acceptance Testing) sandbox environment mirroring the 10-branch MVP schema exactly.

### 2.10 Demo Testing (Hackathon MVP Focus)
A specialized dry-run script simulating the precise live-demo presentation flow end-to-end to ensure zero visual UI artifacting or unhandled API cold starts during investor/panel presentation screensharing.

---

## 3. Unified Test Matrix & Test Cases

| Test ID | Module | Scenario Classification | Execution Mechanism | Expected Result Target |
| :--- | :--- | :--- | :--- | :--- |
| **TC-01** | Database (RLS) | Attempt unauthorized cross-branch data read. | Integration (PyTest POST) | HTTP 403. DB rejects read attempt. |
| **TC-02** | AI / LangGraph | Simulate LLM Hallucinated Function Call missing required `quantity` parameter | Unit/Workflow Test | Pydantic traps error. Node initiates Retry mechanism successfully. |
| **TC-03** | Auth / Edge | Load `/dashboard` without valid token. | UI (Playwright) | Next.js Edge Middleware intercepts, zero visual render, immediate 302 redirect. |
| **TC-04** | Inventory (DB) | POS Checkout execution exceeding logical stock balance. | API | Constraint `quantity >= 0` halts transaction. Rollback initialized cleanly. |
| **TC-05** | UI (Framer) | Render Dynamic Margins Chart upon AI data load. | UI (Vitest) | Chart vectors populate smoothly without layout shifts violating CLS metrics. |
