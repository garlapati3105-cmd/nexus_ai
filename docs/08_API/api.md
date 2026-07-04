# Nexus AI - REST API Documentation

| Metadata | Details |
| :--- | :--- |
| **Document Purpose** | API Interface definitions targeting FastAPI backend |
| **API Base URL** | `https://api.nexuscare.example.com/api/v1` |
| **Documentation Format** | Swagger/OpenAPI compliant specifications |
| **Date** | 2026-07-03 |

---
## Global Authorization
Almost all endpoints require a Bearer token derived from Supabase GoTrue Auth.
**Header:** `Authorization: Bearer <JWT>`

---

## 1. Authentication APIs

### `POST /auth/login` (Standard proxy for Supabase)
Bypassed if utilizing Supabase JS SDK on frontend. 
*   **Request:** `{ "email": "str", "password": "str" }`
*   **Response (200):** `{ "access_token": "jwt", "user": { "role": "CEO", "branch_id": null } }`
*   **Error Codes:** `401 Unauthorized` (Invalid credentials)

---

## 2. Branch APIs

### `GET /branches`
Returns a list of branches based on authorization. CEO sees all; managers see their single branch.
*   **Response (200):** `[ { "id": "uuid", "name": "Banjara Hills", "is_hq": false } ]`

---

## 3. Inventory APIs

### `GET /inventory/{branch_id}`
Retrieves localized stock for a branch.
*   **Validation:** Pydantic validates `branch_id` as UUID. FastAPI middleware validates token `branch_id` matches parameter (unless CEO).
*   **Response (200):** 
```json
{
  "total_items": 1400,
  "data": [
     { "medicine_name": "Paracetamol", "quantity": 50, "expiry": "2027-01-01" }
  ]
}
```

### `POST /inventory/transfer`
Initiates a multi-branch transfer request (usually triggered by Regional AI).
*   **Request:** 
```json
{
  "from_branch": "uuid",
  "to_branch": "uuid",
  "medicine_id": "uuid",
  "qty": 100
}
```
*   **Response (201):** `{ "status": "PENDING_APPROVAL", "transfer_id": "uuid" }`
*   **Error Codes:** `400 Bad Request` (Insufficient Stock in origin branch).

---

## 4. Medicine APIs

### `GET /medicines/search`
*   **Methodology:** Queries ChromaDB vector database, not pure Postgres.
*   **URL Prefix:** `?q=painkiller for kid`
*   **Response (200):** Array of SKUs semantically matched to the NLP query.

---

## 5. Orders APIs

### `POST /orders`
Records a finalized POS checkout. Atomically triggers inventory reduction.
*   **Request:** `{ "branch_id": "uuid", "items": [{"medicine_id":"uuid", "qty":2}] }`
*   **Validation:** Fails if `qty` pushed would result in negative stock.
*   **Response (201):** `{ "order_id": "uuid", "status": "COMPLETED" }`

---

## 6. Finance APIs

### `GET /finance/metrics`
*   **URL Prefix:** `?branch_id=uuid&range=30d`
*   **Security:** Only accessible to CEO or specific Branch Manager.
*   **Response (200):** `{ "revenue": 14050.00, "cogs": 9000.00, "margin": 0.35 }`

---

## 7. Analytics APIs

### `GET /analytics/dashboard`
Consolidated view requiring complex JOINS. Used to render initial visual widget loading.

---

## 8. AI APIs (The LangGraph Interface)

### `POST /ai/ask`
The universal entry point for human-to-AI interaction.
*   **Request:** `{ "query": "Why is branch 4 low on stock?", "context_branch": "uuid" }`
*   **Execution:** FastAPI routes this query to LangGraph. Graph determines it needs Inventory data, pings Supabase, returns to Gemini, yields result to API.
*   **Response (200):** 
```json
{
  "agent_id": "AI Regional Manager",
  "reply": "Branch 4 experienced an unseasonal spike in antibiotic requests. I can initiate a transfer from Branch 2 if you approve.",
  "suggested_actions": [
     { "type": "CREATE_TRANSFER", "payload": {...} }
  ]
}
```
*   **Error Codes:** `504 Gateway Timeout` (LLM processing exceeded SLA limits).

### `POST /ai/resolve-transfer`
The human-trigger edge endpoint satisfying the LangGraph halted state. 
*   **Request:** `{ "transfer_id": "uuid", "human_approval": true, "jwt_signature": "string" }`
*   **Response (200):** `{ "graph_state": "resumed", "db_status": "transferred" }`

---

## 9. Knowledge Base APIs

### `POST /kb/sync`
Triggers an automated synchronization where newly added Postgres medicines are converted into Embeddings and stored in ChromaDB. 
*   **Security:** Server-to-Server communication only. Requires Admin API key, not a user JWT.

---

## 10. Notifications APIs

### `GET /notifications`
*   **Methodology:** Returns SSE Event streams or standard JSON for pending Approval actions.
*   **Response (200):** `[ { "id": "uuid", "type": "APPROVAL_REQUIRED", "message": "Approve Transfer..." } ]`

### `PUT /notifications/{id}/read`
Marks a specific AI notification as acknowledged by the human reader.
