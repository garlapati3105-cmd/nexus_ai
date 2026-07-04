# Nexus AI - User Experience (UX) Documentation

| Metadata | Details |
| :--- | :--- |
| **Document Purpose** | Comprehensive UX strategy for Nexus AI Frontend |
| **Document Owner** | UX Architect |
| **Status** | Approved |
| **Version** | 1.0.0 |
| **Date** | 2026-07-03 |

---

## 1. Information Architecture
The Nexus AI platform is structured hierarchically based on user role (CEO vs. Branch Manager). Navigation prioritizes actionable intelligence over raw data tables. 
*   **Global Level:** Network Overview, Global Inventory, Aggregated Finance.
*   **Local Level:** Branch POS, Local Roster, Pending Approvals, Local Inventory Alerts.
*   **AI Layer (Universal):** Omni-present floating chat/command interface (Ctrl+K mapping) for global NLP queries.

## 2. Navigation Flow
*   **Authentication:** `Login -> Role Parsing -> Routing (CEO Dashboard OR Branch Dashboard)`
*   **Primary Sidebar:** Dashboard | Inventory | Approvals | Finance | Settings.
*   **Action Injection:** Any table view allows clicking a specific SKU/Row to open a slide-out modal (shadcn/ui sheet) detailing predictive AI analytics mapped to that specific resource.

## 3. User Journey
**Scenario: Branch Manager handling an AI-recommended stock transfer.**
1.  Manager logs in, views "Pending Actions" widget.
2.  Widget displays: *"AI Warning: Amoxicillin deficit predicted in 48 hrs. Transfer 50 units from Branch #4?"*
3.  Manager clicks the alert; a modal displays the explicit reasoning (historical sales vector graph + current local stock vs Branch #4 surplus).
4.  Manager clicks "Approve Transfer". Modal closes. Widget updates. 

## 4. Screen List
*   `Auth Login/Reset`
*   `Global CEO Dashboard`
*   `Local Branch Dashboard`
*   `Inventory Matrix (Global/Local variants)`
*   `Pending Approvals Center`
*   `Analytics & Margin Report`
*   `NLP AI Workcenter (Full screen chat agent)`

## 5. Role Flow
*   **CEO Role:** Accesses all branch permutations. Has ability to "impersonate" a branch view without logging out.
*   **Branch Manager Role:** Tightly restricted RLS access. Cannot toggle branches. Cannot view global margin data unless explicitly shared via Regional AI.

## 6. Dashboard Flow
Dashboards are widget-centric. Core widgets display Top KPIs (Sales today, Expiries pending month-end). Secondary widgets represent the AI message bus (Agent Notifications).

## 7. Branch Flow
At the branch level, speed is critical. The "Point of Sale" flow is integrated natively into the Inventory module, allowing pharmacists to quickly decrement stock while conversing with patients.

## 8. AI Workflow
The AI is not merely a chatbox. It operates proactively.
*   **Reactive:** User types "Why are sales down in Branch 3?" -> AI queries system -> Returns chart.
*   **Proactive:** Agent automatically inserts a notification card into the UI feed demanding attention for a cross-branch dispute.

## 9. Wireframe Descriptions
*   **Layout Structure:** Standard 250px left-rail navigation. Persistent top-bar (Search, Notifications, Profile). Main content area rendering interactive Next.js server components.
*   **Approval Cards:** Clean, white-space heavy cards with clear green/red (Approve/Deny) actions.

## 10. Component Layout
Utilizing `shadcn/ui` extensively to maintain a highly professional, enterprise-SaaS monochrome aesthetic (accessible high-contrast text on neutral backgrounds).

## 11. UX Principles
*   **Clarity Over Density:** Do not overwhelm the user with raw SQL tables. Visualize data, providing the raw table via a toggle only if necessary.
*   **Actionable Primacy:** If the AI surfaces data, it must surface the corresponding action (e.g., "Out of stock" -> "Request Indent Now" button).

## 12. Accessibility
*   **WCAG AA Compliance:** strict adherence to contrast ratios (crucial in brightly lit clinical environments).
*   **Keyboard Navigation:** Full Tabbing support for POS terminals where mouse usage is slow.

## 13. Responsive Behaviour
Optimized heavily for Desktop/Tablet displays (standard Pharmacy POS systems). Mobile forms provided purely for CEO metric viewing; complex inventory restructuring disabled on mobile breakpoints to prevent accidental taps.

## 14. Interaction Design
*   **Micro-interactions:** Framer Motion utilized for subtle layout shifts when AI loads dynamic charts to prevent sudden content jumps.
*   **Feedback:** Toast notifications strictly required for all database mutations (e.g., "Transfer Approved. Syncing...").

## 15. Error States
*   Meaningful error mapping. Instead of `Error 500`, display *"Nexus Orchestrator was unable to reach the Inventory AI. Retrying connection..."*

## 16. Loading States
*   Skeleton loaders replicating the exact dimensions of the target component (no generic spinners on primary dashboards).
*   AI reasoning streams (e.g., "Agent is querying regional branches...", "Agent is calculating transit time...") displayed while awaiting LLM resolution.

## 17. Empty States
*   Never display a blank page. E.g., `No Approvals Pending` should render an illustration and text: *"All network logistics are harmonized. The AI has nothing requiring your attention."*
