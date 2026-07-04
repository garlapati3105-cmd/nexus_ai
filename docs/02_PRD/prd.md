# Nexus AI - Product Requirements Document (PRD)

| Metadata | Details |
| :--- | :--- |
| **Document Purpose** | Product Requirements for MVP Engineering |
| **Document Owner** | Chief Product Officer |
| **Status** | Approved for Implementation |
| **Version** | 1.0.0 |
| **Date** | 2026-07-03 |

---

## 1. Executive Summary
Nexus AI is a multi-agent AI Operating System designed to automate backend logistics and operations for multi-branch pharmacy chains. By deploying an autonomous Digital Workforce modeled on a human corporate hierarchy, the system handles complex workflows (inventory rebalancing, POS intelligence, operational analytics) while ensuring absolute human governance via one-click approval mechanisms. 

## 2. Objectives
*   Build a deployable, scalable SaaS MVP modeling a 10-branch localized Indian pharmacy ("NexusCare Pharmacy").
*   Implement secure, deterministic, auditable multi-agent workflows using LangGraph and FastAPI.
*   Establish a seamless, zero-friction approval loop for human authorities.

## 3. Business Goals
*   **Reduce Dead Stock:** Lower percentage of expired drugs by 25% through inter-branch AI negotiations.
*   **Optimize Headcount:** Enable the 10 branches to operate backend logistics without a dedicated central inventory administration team.
*   **Prove ROI:** Justify enterprise pricing by demonstrating direct cost savings derived from AI operational management.

## 4. User Goals
*   **CEO:** Gain macro visibility into all 10 branches, requiring zero granular data mining to grasp performance metrics.
*   **Branch Manager:** Alleviate the burden of daily indenting and administrative reconciliations, focusing instead on branch expansion and clinician support.

## 5. Success Metrics
*   **Agent Latency SLA:** < 2.5 seconds per workflow step execution natively within the LLM inference loop.
*   **Actionable Accuracy:** 95%+ of AI recommended critical systemic changes (e.g., purchasing, transfers) approved by a human without modification.
*   **Task Resolution Time:** Cross-branch transfers executed natively in under 3 minutes (compared to a typical 2+ hour manual negotiation).

## 6. Personas
*   **Human CEO (Business Owner):** Strategy, Macro-Analytics, Regional Dispute Override.
*   **Human Branch Manager:** Branch-level Operations, Local Approvals (Indents/Discounts), Local Performance.
*   **Human Pharmacist / Clerk:** Frontline POS execution, Prescription reading (assisted by Sales AI), customer fulfillment.

## 7. User Stories
*   As a *Branch Manager*, I want to *receive an AI alert predicting a deficit of Amoxicillin before it occurs*, so that *I can approve an automatic transfer from the nearest branch equipped with a surplus*.
*   As a *CEO*, I want to *ask the dashboard natural language questions regarding financial performance*, so that *I don't have to wait for an accountant to run SQL reports*.
*   As a *Pharmacist*, I want the *Sales AI to instantly query global stock*, so that *I can accurately guide a patient to a neighboring branch if we are out of stock.*

## 8. Use Cases
**Use Case 1: Inter-Branch Stock Resourcing**
*(Triggered by Inventory AI predicting a critical low).* 
Inventory AI alerts Branch AI. Branch AI flags Regional AI. Regional AI finds nearest surplus. Generates digital Transfer Order. Pings both Human Branch Managers for a 1-click Approval. Updates Supabase.

**Use Case 2: NLP Analytics Dashboarding**
CEO inputs "Which branch had the highest pharmaceutical margin decay last week?" Regional AI queries Finance AI. Finance AI pulls from Supabase. Result output as natural language explanation + dynamically generated UI chart (Framer Motion).

## 9. Functional Requirements
*   **FR-01:** System must maintain a real-time, ACID-compliant ledger of inventory strictly synchronized across 10 branches using Supabase.
*   **FR-02:** Human approval gates must halt LangGraph workflows; state must be preserved until authorization is granted or denied via JWT-authenticated API endpoints.
*   **FR-03:** AI nodes (Agents) must communicate via standardized JSON schemas to prevent hallucinated API arguments.
*   **FR-04:** Search functions must utilize ChromaDB vectorization allowing NLP mapping of generic drug names to proprietary SKU variants flawlessly.

## 10. Non Functional Requirements
*   **NFR-01 (Availability):** Core Supabase/FastAPI infrastructure must observe 99.9% uptime.
*   **NFR-02 (Security):** Row Level Security (RLS) ensuring Branch Managers cannot arbitrarily query database rows tied to unassigned branches.
*   **NFR-03 (Performance):** Frontend Next.js client must hit >90% Lighthouse scores across all metrics utilizing Edge Caching.

## 11. Feature List
*   Hierarchical User Dashboard (CEO vs. Branch Manager Views)
*   Role-Based Authorization (Supabase Auth)
*   Multi-Agent Conversational UI (LangChain integration)
*   Pending Actions Queue (Human-in-the-loop validation center)
*   Predictive Inventory Matrix (AI recommendations)

## 12. MVP Scope
*   10 simulated branches bounded geographically within Hyderabad.
*   10,000 localized Pharmaceutical SKUs.
*   Core Agent active layer: Sales AI, Inventory AI, AI Branch Manager, AI Regional Manager.
*   Full Read/Write via Next.js to FastAPI to Supabase PostgreSQL.

## 13. Future Scope
*   Full integration with national pharmaceutical distributor B2B APIs for autonomous purchase order formulation.
*   AI HR module determining shift capacities utilizing predictive foot-traffic modeling.
*   WhatsApp Business API integration for patient prescription refills.

## 14. Acceptance Criteria
*   When a user clicks "Approve Transfer", the LangGraph state machine unlocks, mutates specific inventory integers in Supabase correctly, and generates a corresponding ledger event logging the human approver ID.
*   The Sales AI successfully parses a complex NLP query ("I need the generic equivalent of paracetamol syrup for a 5yo") and maps it accurately to localized database SKUs via ChromaDB.

## 15. Assumptions
*   All branches have consistent, uninterrupted internet connectivity.
*   Medical regulatory compliance allows for cloud-hosted AI inferences assuming strict PII (Personally Identifiable Information) removal prior to prompt execution.
*   Gemini 2.5 Flash context window limits are not exceeded by single workflow schemas.

## 16. Constraints
*   Hardware limitation: Cannot rely on heavy client-side processing; inference orchestration occurs exclusively on the FastAPI/Render tier.
*   Zero proprietary pharmacy transactional data is utilized during basic LLM model fine-tuning; only RAG workflows dictate data visibility.

## 17. Dependencies
*   Supabase (Database, Auth, Edge Functions)
*   Google Cloud (Gemini 2.5 Flash API uptime)
*   Render (FastAPI Application hosting)
*   Vercel (Next.js Application hosting)

## 18. Glossary
*   **RAG (Retrieval-Augmented Generation):** Process optimizing LLM output using an authoritative domain-specific knowledge base (our proprietary pharmacy SKU datasets).
*   **LangGraph:** A library for building stateful, multi-actor applications with LLMs; used to choreograph our Agent hierarchy.
*   **Indent:** An internal supply chain request generated by a branch to acquire stock.
