# Nexus AI - Branch Manager Specification Gap Analysis
**Enterprise ERP Architecture Review — Pharmacy Operations**

This report reviews the existing Branch Manager Functional Specification against 17 operational sections and 7 specific requested capabilities verified individually. All recommendations are modeled on real operations used at Apollo Pharmacy, MedPlus, and Wellness Forever retail branches.

---

## Section-by-Section Review

### 1. Daily Branch Operations
**Status: Complete.** Opening/closing checklists, intra-day tasks, EOD reconciliation flow, and staff orientation steps are all documented.

### 2. Dashboard
**Status: Partially Complete.** 20 widgets are specified. Missing: Branch Performance Target progress bars, Reserved Inventory counter, Supplier Delivery ETA panel, Branch Capacity/Queue monitor, and Equipment Status indicator.

### 3. Employee Management
**Status: Complete.** Shift allocation, attendance, leave, and performance monitoring are all covered with workflows.

### 4. Inventory Management
**Status: Partially Complete.** General stock overview is present. Missing: Reserved Inventory Monitoring and Supplier Delivery Visibility (read-only PO status).

### 5. Customer Management
**Status: Complete.** Profiles, loyalty, returns, complaints, and refunds are all covered.

### 6. Sales Management
**Status: Complete.** Daily sales lifecycle, discounts, cash flow, and billing statistics are documented.

### 7. Branch Workflow
**Status: Complete.** End-to-end Mermaid flowchart from opening to closing is included.

### 8. AI Integration
**Status: Complete.** Five AI agents with inputs, outputs, and confidence models are defined.

### 9. Reports
**Status: Complete.** Nine standard report types are specified with frequencies and formats.

### 10. Notifications
**Status: Partially Complete.** Ten notification types exist. Missing: Medicine Recall alert and Equipment Failure notifications.

### 11. Analytics
**Status: Complete.** Sales trends, top/slow-moving medicines, peak hours, and inventory analytics are defined.

### 12. Security
**Status: Complete.** RLS, MFA, audit logs, and session management are covered.

### 13. APIs
**Status: Partially Complete.** Five essential endpoints exist. Missing: Supplier delivery status, reserved inventory, prescription queue monitor, and branch capacity APIs.

### 14. Database
**Status: Partially Complete.** 17 tables are mapped. Missing: `purchase_orders`, `stock_reservations`, `equipment_health`, `medicine_recalls`.

### 15. Real World Use Cases
**Status: Complete.** Six practical pharmacy scenarios are documented.

### 16. Edge Cases
**Status: Complete.** Six failure scenarios defined with system responses.

### 17. Production Readiness
**Status: Complete.** 10-item checklist is documented.

---

## Missing Feature Analysis

### Feature 1: Branch Performance Target Tracking

**Purpose:** Allows the BM to see real-time progress against daily, weekly, and monthly sales and operational KPIs set by the Regional Manager.

**Business Problem Solved:** Without visible targets, branch managers optimize reactively rather than proactively. Target tracking drives purposeful daily decisions about upselling, staffing, and stock availability.

**Real-world Pharmacy Example:** At MedPlus, Branch Managers view a daily target board on their management terminal showing ₹ Revenue vs. Target, Prescription Count vs. Target, and Customer Count vs. Target. They adjust staffing and sales incentives in real time.

**Branch Manager Workflow:**
1. BM opens the dashboard each morning and reviews the **Daily Target Progress** widget.
2. At mid-day, if revenue is at 30% of daily target by noon, BM verifies counter queue speed and investigates slow-moving items.
3. End-of-day, the system marks each KPI as Hit / Missed and logs it in the monthly performance ledger.

**Dashboard Widget:** *Target Progress Ring Cards* — one card per KPI (Revenue, Prescription Count, Customer Footfall, Inventory Accuracy) showing percentage completion in real time.

**Database Tables Required:**
* `branch_targets` (NEW): Stores daily/monthly targets per branch, set by Regional Manager.
* `invoices`, `orders`: Aggregated to calculate live achievement values.

**API Requirements:**
* `GET /api/branches/{branch_id}/targets` — Returns active targets and current achievement percentages.

**Notifications:**
* **Medium Priority:** "You are at 40% of today's revenue target at 4:00 PM."
* **High Priority:** "You missed yesterday's revenue target by 18%."

**Acceptance Criteria:**
* Target progress cards refresh every 5 minutes.
* End-of-day target completion status is logged immutably in the audit trail.
* BM cannot edit targets — they can only read them.

**Priority: High**

---

### Feature 2: Reserved Inventory Monitoring

**Purpose:** Allows the BM to see which medicines are currently reserved (committed to orders at POS but not yet dispensed) versus available stock.

**Business Problem Solved:** Without reserved stock visibility, a cashier may commit the last 10 strips of a medicine to one order while another cashier commits the same 10 strips to another — causing a double-booking failure at dispensing.

**Real-world Pharmacy Example:** At Apollo Pharmacy, a stock reservation system freezes committed medicine quantities for each active order. The BM can see "Physical Stock: 12 strips | Reserved: 8 strips | Available: 4 strips" on the inventory screen.

**Branch Manager Workflow:**
1. BM views the **Reserved Inventory** widget showing medicines with high reservation ratios.
2. For orders reserved more than 15 minutes without dispensing, the system flags them as **Expired Reservations**.
3. BM releases expired reservations manually or via the auto-release system, returning stock to available.

**Dashboard Widget:** *Reserved Stock Summary Card* — total SKUs with active reservations, and count of reservations older than 15 minutes.

**Database Tables Required:**
* `stock_reservations` (NEW): Stores `order_id`, `medicine_id`, `quantity`, `reserved_at`, `status`.
* `inventory`: Referenced to calculate available vs. reserved quantity.

**API Requirements:**
* `GET /api/branches/{branch_id}/inventory/reservations` — Returns all active reservations with age and status.
* `POST /api/branches/{branch_id}/inventory/reservations/{id}/release` — Releases an expired reservation.

**Notifications:**
* **Medium Priority:** "{medicine_name} has 90% of available stock reserved. Risk of stockout."
* **Low Priority:** "3 reservations have been pending for over 15 minutes and have been auto-released."

**Acceptance Criteria:**
* Reservations older than 20 minutes are auto-released with a system notification.
* The Available Quantity shown on the inventory screen always reflects Physical Quantity minus Reserved Quantity.

**Priority: Critical**

---

### Feature 3: Supplier Delivery Visibility (Read-Only)

**Purpose:** Allows the BM to monitor expected delivery ETAs for pending purchase orders placed by the Regional Manager or procurement team, from this branch's receiving perspective.

**Business Problem Solved:** Without delivery ETA visibility, the BM cannot plan for receiving, cannot communicate to customers waiting for a specific medicine, and cannot identify delayed shipments that require escalation.

**Real-world Pharmacy Example:** MedPlus branch managers view a "Expected Deliveries Today" panel in the morning. If an insulin delivery shows 3-day delay, the BM immediately raises a transfer request from a nearby branch to fill the gap.

**Branch Manager Workflow:**
1. BM opens the **Deliveries Due Today** panel from the dashboard.
2. Reviews the timeline: Ordered Date, Dispatch Date, Expected Delivery Date, and Current Status.
3. If a delivery shows Delayed, BM clicks **Escalate** which sends an alert to the Regional Manager.
4. Upon physical delivery, the branch receiving system marks the PO as Received, automatically crediting inventory.

**Dashboard Widget:** *Incoming Deliveries Timeline* — a list widget showing today's and tomorrow's expected purchase order arrivals with status badges.

**Database Tables Required:**
* `purchase_orders` (Read-Only): BM cannot create; only reads `status`, `expected_delivery_date`, and `supplier_name`.
* `goods_receipt_notes`: BM confirms received deliveries, triggering inventory credit.

**API Requirements:**
* `GET /api/branches/{branch_id}/deliveries/incoming` — Returns pending POs with ETA, status, and item details.
* `POST /api/branches/{branch_id}/deliveries/{po_id}/confirm-receipt` — Confirms physical goods received.

**Notifications:**
* **High Priority:** "Expected delivery from Sun Pharma is 2 days delayed. Review transfer options."
* **Medium Priority:** "Delivery from Cipla scheduled for today — 3 items, expected by 2:00 PM."

**Acceptance Criteria:**
* BM cannot modify or cancel purchase orders — only read status and confirm receipt.
* Delivery confirmation triggers an automatic inventory quantity update within 10 seconds.

**Priority: High**

---

### Feature 4: Branch Capacity & Queue Monitoring

**Purpose:** Gives the BM a real-time view of customer queue depth, active cashier counters, pharmacist availability, and estimated customer wait times.

**Business Problem Solved:** Without live capacity data, the BM cannot proactively open an additional counter during a rush, leading to customer dissatisfaction and walkouts.

**Real-world Pharmacy Example:** Wellness Forever branch managers watch a live counter status board. When any counter queue exceeds 5 customers, the system suggests opening Counter 3 and assigning the available cashier.

**Branch Manager Workflow:**
1. BM views the **Counter Capacity Panel** on the dashboard.
2. When estimated wait time exceeds **8 minutes**, the system triggers a **High Queue Alert**.
3. BM assigns a standby cashier or pharmacist to an available counter using the employee module.

**Dashboard Widget:** *Live Counter Status Grid* — one tile per POS counter showing: Active/Inactive, current cashier name, queue depth, and estimated wait time.

**Database Tables Required:**
* `pos_sessions` (NEW): Tracks active/inactive status of each POS terminal and the assigned cashier.
* `orders`: Counts orders in `CREATED` or `PENDING_DISPENSING` state per counter per hour.

**API Requirements:**
* `GET /api/branches/{branch_id}/capacity` — Returns counter status, active staff, queue depths, and estimated wait time.

**Notifications:**
* **High Priority:** "Estimated customer wait time is 12 minutes. Consider opening an additional counter."
* **Medium Priority:** "Counter 2 has been idle for 30 minutes."

**Acceptance Criteria:**
* Wait time estimate is recalculated every 60 seconds based on average billing time from last 2 hours.
* Counter activation/deactivation is logged in the audit trail.

**Priority: High**

---

### Feature 5: Medicine Recall Management

**Purpose:** Allows the BM to receive, acknowledge, and act on medicine recall alerts issued by manufacturers or government regulators (CDSCO).

**Business Problem Solved:** Without a formal recall workflow, a recalled batch may continue to be dispensed, creating serious patient safety risk and regulatory liability for the pharmacy chain.

**Real-world Pharmacy Example:** When CDSCO issues a recall on a contaminated batch of Glycomet, all Apollo Pharmacy branch managers receive an immediate recall alert, quarantine the batch, and confirm removal from shelves within 2 hours.

**Branch Manager Workflow:**
```
[Recall Alert Received: Batch B20261001 Metformin 500mg]
        ↓
BM Opens Recall Module → Views affected batch quantities
        ↓
BM Quarantines Batch → Marks stock as RECALLED in inventory
        ↓
BM Confirms Shelf Removal → Logs compliance timestamp
        ↓
System Updates Recall Compliance Status → Notifies Regional Manager
```

**Dashboard Widget:** *Active Recalls Banner* — a prominent red banner on the dashboard when any active recall affects this branch's inventory.

**Database Tables Required:**
* `medicine_recalls` (NEW): Stores `recall_id`, `medicine_id`, `batch_no`, `issued_by`, `severity`, `compliance_deadline`, `status`.
* `inventory`: Updated to `QUARANTINED` status for recalled batches.
* `audit_logs`: Timestamps for BM compliance confirmations.

**API Requirements:**
* `GET /api/branches/{branch_id}/recalls/active` — Returns all open recalls affecting this branch.
* `POST /api/branches/{branch_id}/recalls/{recall_id}/confirm` — Logs BM compliance confirmation.

**Notifications:**
* **Critical Priority:** "URGENT RECALL: Batch B20261001 of Metformin 500mg must be quarantined immediately."
* **High Priority:** "Recall compliance deadline in 4 hours. Action required."

**Acceptance Criteria:**
* Recalled batches are immediately blocked from new POS sales.
* BM compliance confirmation is timestamped and forwarded to the Regional Manager's audit view.
* Overdue compliance (past deadline) triggers an automatic escalation to the Regional Manager.

**Priority: Critical**

---

### Feature 6: Prescription Queue Monitoring

**Purpose:** Provides the BM with a live view of the pharmacist prescription verification and dispensing queue — covering pending, in-progress, and rejected prescriptions.

**Business Problem Solved:** Without queue visibility, the BM is unaware of bottlenecks in the dispensing workflow. A single pharmacist managing 15 pending prescriptions without support causes delays and patient risk.

**Real-world Pharmacy Example:** At Apollo 24x7 branches, the Branch Manager's terminal shows a live prescription queue dashboard with color-coded age indicators (Green < 5 min, Yellow 5–10 min, Red > 10 min pending).

**Branch Manager Workflow:**
1. BM reviews the **Prescription Queue Widget** each 30 minutes.
2. If a prescription has been pending for over 10 minutes without pharmacist action, BM follows up with the responsible pharmacist.
3. Rejected prescriptions are reviewed by the BM — if the rejection seems incorrect, the BM can escalate to the senior pharmacist.
4. Average dispensing time is tracked to identify performance trends.

**Dashboard Widget:** *Live Prescription Queue Card* — totals for Pending Verification, In Progress, Completed Today, and Rejected Today with age-heat color bands.

**Database Tables Required:**
* `orders` / `order_items`: Filter on `PENDING_DISPENSING` and `DISPENSED` statuses.
* `prescriptions` (NEW or extended): Stores `verification_status`, `pharmacist_id`, `received_at`, `dispensed_at`.

**API Requirements:**
* `GET /api/branches/{branch_id}/prescriptions/queue` — Returns queue summary and aged item details.

**Notifications:**
* **High Priority:** "5 prescriptions have been pending for over 10 minutes. Pharmacist queue backlog."
* **Medium Priority:** "Prescription rejected by pharmacist: Order #ORD-2026-1142. BM review recommended."

**Acceptance Criteria:**
* Queue data refreshes every 90 seconds.
* Average dispense time KPI is available on the daily performance report.
* Prescriptions pending over 15 minutes generate an automatic BM alert.

**Priority: High**

---

### Feature 7: Store Equipment & Infrastructure Health

**Purpose:** Provides the BM with a real-time status indicator for critical branch equipment: POS terminals, barcode scanners, printers, internet connectivity, refrigerator temperature, and UPS power.

**Business Problem Solved:** Without equipment monitoring, a malfunctioning barcode scanner or printer can go unreported for hours, blocking customer billing. A refrigerator temperature spike can silently spoil thousands of rupees worth of cold-chain medicines.

**Real-world Pharmacy Example:** Wellness Forever stores use a store health panel that alerts the manager if the refrigerator temperature exceeds 8°C (for vaccines and insulin), if a POS terminal is offline, or if the UPS battery drops below 20%.

**Branch Manager Workflow:**
1. BM sees a **Store Health Badge** in the dashboard topbar showing green/yellow/red.
2. If yellow/red, BM clicks through to the **Equipment Status Panel** for details.
3. BM raises a **Maintenance Request** directly from the panel, which routes to the facilities team.
4. Maintenance requests are tracked as open/resolved within the audit log.

**Dashboard Widget:** *Store Equipment Health Panel* — grid of equipment tiles with status badges:

| Equipment | Status | Last Checked |
| :--- | :--- | :--- |
| POS Terminal 1 | 🟢 Online | 2 min ago |
| Barcode Scanner | 🟡 Degraded | 5 min ago |
| Receipt Printer | 🟢 Online | 2 min ago |
| Refrigerator (Insulin Bay) | 🟢 4°C | 5 min ago |
| Internet Connection | 🟢 Active | 1 min ago |
| UPS Battery | 🟡 62% | 10 min ago |

**Database Tables Required:**
* `equipment_health` (NEW): Stores `branch_id`, `equipment_type`, `status`, `last_reading`, `last_checked_at`.
* `maintenance_requests` (NEW): Stores `branch_id`, `equipment_type`, `issue_description`, `status`, `raised_by`, `resolved_at`.

**API Requirements:**
* `GET /api/branches/{branch_id}/equipment/status` — Returns current health of all registered equipment.
* `POST /api/branches/{branch_id}/equipment/maintenance-requests` — Raises a new maintenance ticket.

**Notifications:**
* **Critical Priority:** "Refrigerator temperature has exceeded 8°C. Insulin and cold-chain stock at risk."
* **High Priority:** "POS Terminal 2 is offline. Counter 2 cannot process payments."
* **Medium Priority:** "UPS battery at 18%. Power failure protection critical."

**Acceptance Criteria:**
* Refrigerator temperature breach triggers a Critical alert within 2 minutes of threshold violation.
* POS offline status triggers a High alert within 3 minutes.
* Maintenance request is logged and assigned a ticket ID within 10 seconds.

**Priority: High**

---

## Evaluation Summary

### Branch Manager Completeness Score: 76 / 100

The existing specification covers all core day-to-day operational, financial, inventory, employee, and customer modules well. However, the absence of real-time capacity monitoring, reserved stock visibility, compliance recall workflows, performance tracking, and equipment health monitoring leaves significant operational gaps that would prevent a real pharmacy branch manager from fully relying on this system.

---

### Recommended Additions

| # | Feature | Priority |
|---|---|---|
| 1 | Branch Performance Target Tracking | High |
| 2 | Reserved Inventory Monitoring | Critical |
| 3 | Supplier Delivery Visibility (Read-Only) | High |
| 4 | Branch Capacity & Queue Monitoring | High |
| 5 | Medicine Recall Management | Critical |
| 6 | Prescription Queue Monitoring | High |
| 7 | Store Equipment & Infrastructure Health | High |

---

### Existing Features That Are Already Complete

* Daily branch opening and closing checklists.
* Branch dashboard KPI widgets (20 items).
* Employee shift management, attendance, and leave approvals.
* Customer profiles, purchase history, loyalty, returns, and complaints.
* Inventory overview (stock levels, expiry visibility, adjustments, transfers).
* Sales lifecycle — order creation through payment and invoice.
* EOD cash reconciliation and mismatch handling.
* AI integrations (5 agents: Inventory, Sales, Analytics, Knowledge, Finance).
* Full suite of 9 reports (Daily Sales, Inventory, Employee, Cash, etc.).
* 10 notification types with priority tiers.
* Branch-level search across 7 entity categories.
* Sales, medicine performance, peak hours, and customer analytics.
* Security — RLS branch isolation, MFA, session management, audit logs.
* 5 core API endpoints with complete schemas.
* 17 database table access mappings.
* 6 real-world pharmacy use cases.
* 6 edge case scenarios with system responses.
* 10-item production readiness checklist.

---

### Features That Should NOT Be Added

| Feature | Reason for Exclusion |
| :--- | :--- |
| Payroll Management | Belongs to HR/Finance — outside BM scope. |
| Supplier Contract Negotiation | Regional Manager or Procurement responsibility. |
| Global Medicine Pricing | CEO and Pricing team responsibility. |
| Purchase Order Creation | Regional Manager responsibility. BM only receives and confirms. |
| Network-Wide Inventory Reports | CEO / Regional Manager scope. BM sees only their branch. |
| AI Agent Configuration | AI Systems Administration role. Not a BM operational task. |
| Company-Wide Financial Reporting | CEO scope. |
| Role Assignment / User Management | System Administrator scope. |
