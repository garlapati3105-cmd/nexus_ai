# Nexus AI - Low Level Design (LLD)

| Metadata | Details |
| :--- | :--- |
| **Document Purpose** | Low Level Coding Standards and structural design |
| **Document Owner** | Principal Software Architect |
| **Status** | Approved |
| **Version** | 1.0.0 |
| **Date** | 2026-07-03 |

---

## 1. Folder Structure (Monorepo)
Nexus AI implements a turbo/npm workspaces styling to isolate domains predictably.

```text
/nexus_ai
├── apps/
│   ├── api/                 # FastAPI Service
│   └── web/                 # Next.js Application
├── packages/
│   ├── database/            # Supabase migrations, typescript types
│   ├── ai-core/             # Shared LangChain prompts & static logic
│   └── ui/                  # Shared shadcn/ui components
├── docs/                    # Architecture Documentation
└── package.json             # Root workspace mapping
```

## 2. File Structure (FastAPI app/api)
```text
/api
├── main.py                  # App entry point, CORS configuration
├── routers/                 # API endpoint handlers
│   ├── v1/
│   │   ├── users.py
│   │   ├── inventory.py
│   │   └── agents.py
├── schemas/                 # Pydantic models (Request/Response)
├── core/                    # Security, Settings, Config loading
├── services/                # Business logic mapping routers to DB/AI
└── ai_graph/                # LangGraph node definitions & state
```

## 3. Components (Frontend Next.js)
UI components are strictly segregated into:
*   **Atoms:** Buttons, Inputs, Cards (Extracted from UI package).
*   **Molecules:** Search bars, Notification Banners.
*   **Organisms:** `PendingApprovalsList`, `AgentChatInterface`.
*   **Templates:** Dashboard Layout wrappers.

## 4. Services (Backend)
The `/services` directory isolates logic from FastAPI Router endpoints. 
A router endpoint simply receives the request, passes arguments to essentially `InventoryService.execute_transfer(args)`, and handles the HTTP return wrapper. This ensures code is highly testable independently of API state.

## 5. Controllers
(Mapped to `routers/` in FastAPI). Defines routes, attaches dependency injections (`Depends(get_current_user)`), and explicitly defines Response Models for auto-generating pristine OpenAPI/Swagger documentation.

## 6. Repositories
Data access is fully encapsulated. The FastAPI backend does not write raw SQL execution strings in logic layers. It invokes Supabase client functions wrapper classes (e.g., `DatabaseService.get_stock_levels()`) acting as the ORM/Repository layer interface. 

## 7. Hooks (Frontend)
Custom React Hooks abstract data fetching complexity.
*   `useAuth()` - Contextual JWT management.
*   `useAgentStream()` - WebSockets/SSE hook managing the live typing animation stream from LangGraph via FastAPI.

## 8. Utilities
*   **Date Mapping:** Centralized datetime handlers (strict ISO-8601 formatting required).
*   **Retry Mechanisms:** Backend exponential backoff algorithms for LLM endpoint rate-limiting handling.

## 9. Configuration
*   Application configuration managed via `.env` files parsed robustly via `pydantic-settings`. 
*   Variables injected gracefully; application fails to boot instantly if a required env parameter (e.g., `GEMINI_API_KEY`) is missing.

## 10. Middleware
*   **FastAPI Auth Middleware:** Validates Supabase JWT headers prior to router resolution.
*   **Next.js Edge Middleware:** Blocks unauthorized routes at the CDN edge before rendering computing begins, redirecting unauthenticated users to `/login`.

## 11. Business Logic
Core transactional integrity resides in the SQL Database.
*   Business Logic enforces that "An indent cannot be created for a Schedule H drug without a licensed pharmacist override." 
*   This rule exists in FastAPI `services/` and is secondarily reinforced by PostgreSQL constraints/triggers.

## 12. Class Design (AI Graph)
Agent nodes are formulated as classes to track execution history natively.
*   `class State(TypedDict):` - The literal memory of the multi-agent execution loop.
*   `class NodeInventory:` - Possesses `invoke()` method responsible for reading state, querying vector DB, and mapping LLM prompt.

## 13. Sequence Flow (Edge Case Logging)
Whenever the LLM returns unstructured output despite strict system prompts, the fallback sequence engages:
1. `ValidationError` raised by Pydantic.
2. LangGraph error state triggers.
3. System injects "Correction Prompt" automatically feeding the error back to the LLM.
4. (After 3 retries) Circuit breaks, user receives friendly error UI stating AI is overloaded.

## 14. Coding Standards
*   **Formatting:** `Black` (Python) and `Prettier` (Typescript) enforced strictly via pre-commit hooks.
*   **Typing:** Absolute adherence to `mypy` strict configurations. No `Any` types permitted in FastAPI data mapping layers.
*   **State:** Absolute avoidance of global mutability. Functional programming paradigms favored heavily within services architecture.
