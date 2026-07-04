# Nexus AI
**The AI Operating System for Multi-Branch Pharmacy Chains**

## 1. Document Information
| Attribute | Detail |
| :--- | :--- |
| **Document Purpose** | Project README & High-Level Architecture Overview |
| **Project Type** | Enterprise SaaS, AI Multi-Agent Platform, Healthcare Retail |
| **Target MVP Scope** | NexusCare Pharmacy (Simulated) - 10 Branches in Hyderabad |
| **Version** | 1.0.0 |
| **Last Updated** | 2026-07-03 |

## 2. Table of Contents
1. [Document Information](#1-document-information)
2. [Executive Summary](#2-executive-summary)
3. [Organization & Multi-Agent Structure](#3-organization--multi-agent-structure)
4. [AI Philosophy & Guiding Principles](#4-ai-philosophy--guiding-principles)
5. [Primary MVP Workflow](#5-primary-mvp-workflow)
6. [Technology Stack](#6-technology-stack)

## 3. Executive Summary
Nexus AI is an enterprise-grade AI Operating System designed specifically for modern pharmacy chains. Moving beyond traditional ERP systems, Nexus AI deploys a sophisticated, collaborative AI Digital Workforce across multiple pharmacy branches. The system is designed to automate repetitive operations while presenting explainable recommendations to human stakeholders for strategic decision-making. 

## 4. Organization & Multi-Agent Structure
The system models a hierarchical corporate structure utilizing specialized AI agents overseen by human leadership:

*   **Human CEO (Business Owner)** - Ultimate strategic decision maker.
    *   **AI Regional Manager** - Oversees regional multi-branch operations and handles cross-branch coordination.
        *   **10 AI Branch Managers** - Manage individual branch operations.
            *   **Sales AI**: Handles customer interactions and point-of-sale intelligence.
            *   **Inventory AI**: Predicts stock requirements and manages supply chain at the branch level.
            *   **Finance AI**: Analyzes margins, revenue, and local expenses.
            *   **HR AI**: Manages staff scheduling and basic hr operational tasks.

## 5. AI Philosophy & Guiding Principles
Nexus AI operations are governed by strict ethical and operational tenets:
*   **Empowerment, Not Replacement**: AI assists humans; it does NOT replace humans.
*   **Strategic Supremacy**: Humans make strategic decisions.
*   **Operational Automation**: AI automates repetitive operations.
*   **Absolute Transparency**: Every AI recommendation must be inherently explainable.
*   **Human-in-the-Loop Safeguards**: Every critical workflow requires explicit human approval.

## 6. Primary MVP Workflow
The core operational loop for a customer order flows through the agent hierarchy:

1.  **Customer Order Initiated**
2.  **Sales AI**: Processes initial request.
3.  **Inventory AI**: Confirms stock availability and allocates items.
4.  **Branch AI Manager**: Validates branch-level compliance and rules.
5.  **Regional AI Manager**: Triggered *only* if cross-branch coordination (e.g., stock transfer) is required.
6.  **Finance AI**: Calculates pricing, discounts, and tax requirements.
7.  **Human Approval**: Requested *only* for flagged exceptions or high-risk transactions.
8.  **Invoice Generated**: Finalized financial document created.
9.  **Inventory Updated**: Final deduction executed.
10. **Analytics Updated**: Real-time dashboards refresh.

## 7. Technology Stack
The platform is built on modern, scalable, enterprise-grade cloud technologies.

### Frontend
*   **Framework**: Next.js (React)
*   **Language**: TypeScript
*   **Styling**: TailwindCSS
*   **Component Library**: shadcn/ui
*   **Animation**: Framer Motion

### Backend & AI Infrastructure
*   **API Framework**: FastAPI
*   **AI Engine**: Gemini 2.5 Flash
*   **Agent Orchestration**: LangGraph & LangChain

### Data & Persistence
*   **Relational Database**: Supabase PostgreSQL
*   **Vector Database**: ChromaDB
*   **Authentication**: Supabase Auth

### Deployment Infrastructure
*   **Frontend**: Vercel
*   **Backend**: Render
