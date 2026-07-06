-- Views and Triggers Migration for Nexus AI
-- Date: 2026-07-03
-- Author: Principal Database Architect

-- ====================================================
-- HELPER FUNCTIONS & TRIGGERS FOR TIMESTAMPS
-- ====================================================

-- Function to update updated_at automatically
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = timezone('utc'::text, now());
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Apply to Organizations
CREATE TRIGGER tr_update_organizations_updated_at
    BEFORE UPDATE ON organizations
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Apply to Branches
CREATE TRIGGER tr_update_branches_updated_at
    BEFORE UPDATE ON branches
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Apply to Branch Settings
CREATE TRIGGER tr_update_branch_settings_updated_at
    BEFORE UPDATE ON branch_settings
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Apply to Roles
CREATE TRIGGER tr_update_roles_updated_at
    BEFORE UPDATE ON roles
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Apply to Permissions
CREATE TRIGGER tr_update_permissions_updated_at
    BEFORE UPDATE ON permissions
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Apply to Users
CREATE TRIGGER tr_update_users_updated_at
    BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Apply to Employees
CREATE TRIGGER tr_update_employees_updated_at
    BEFORE UPDATE ON employees
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Apply to Employee Shifts
CREATE TRIGGER tr_update_employee_shifts_updated_at
    BEFORE UPDATE ON employee_shifts
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Apply to Medicine Categories
CREATE TRIGGER tr_update_medicine_categories_updated_at
    BEFORE UPDATE ON medicine_categories
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Apply to Manufacturers
CREATE TRIGGER tr_update_manufacturers_updated_at
    BEFORE UPDATE ON manufacturers
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Apply to Medicines
CREATE TRIGGER tr_update_medicines_updated_at
    BEFORE UPDATE ON medicines
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Apply to Medicine Batches
CREATE TRIGGER tr_update_medicine_batches_updated_at
    BEFORE UPDATE ON medicine_batches
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Apply to Medicine Prices
CREATE TRIGGER tr_update_medicine_prices_updated_at
    BEFORE UPDATE ON medicine_prices
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Apply to Inventory
CREATE TRIGGER tr_update_inventory_updated_at
    BEFORE UPDATE ON inventory
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Apply to Inventory Adjustments
CREATE TRIGGER tr_update_inventory_adjustments_updated_at
    BEFORE UPDATE ON inventory_adjustments
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Apply to Expiry Tracking
CREATE TRIGGER tr_update_expiry_tracking_updated_at
    BEFORE UPDATE ON expiry_tracking
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Apply to Stock Transfers
CREATE TRIGGER tr_update_stock_transfers_updated_at
    BEFORE UPDATE ON stock_transfers
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Apply to Suppliers
CREATE TRIGGER tr_update_suppliers_updated_at
    BEFORE UPDATE ON suppliers
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Apply to Purchase Orders
CREATE TRIGGER tr_update_purchase_orders_updated_at
    BEFORE UPDATE ON purchase_orders
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Apply to Customers
CREATE TRIGGER tr_update_customers_updated_at
    BEFORE UPDATE ON customers
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Apply to Orders
CREATE TRIGGER tr_update_orders_updated_at
    BEFORE UPDATE ON orders
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Apply to AI Agents
CREATE TRIGGER tr_update_ai_agents_updated_at
    BEFORE UPDATE ON ai_agents
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Apply to AI Workflows
CREATE TRIGGER tr_update_ai_workflows_updated_at
    BEFORE UPDATE ON ai_workflows
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Apply to AI Memory
CREATE TRIGGER tr_update_ai_memory_updated_at
    BEFORE UPDATE ON ai_memory
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Apply to AI Recommendations
CREATE TRIGGER tr_update_ai_recommendations_updated_at
    BEFORE UPDATE ON ai_recommendations
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Apply to AI Conversations
CREATE TRIGGER tr_update_ai_conversations_updated_at
    BEFORE UPDATE ON ai_conversations
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Apply to Approvals
CREATE TRIGGER tr_update_approvals_updated_at
    BEFORE UPDATE ON approvals
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Apply to Approval Steps
CREATE TRIGGER tr_update_approval_steps_updated_at
    BEFORE UPDATE ON approval_steps
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Apply to Notification Preferences
CREATE TRIGGER tr_update_notification_preferences_updated_at
    BEFORE UPDATE ON notification_preferences
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Apply to Knowledge Documents
CREATE TRIGGER tr_update_knowledge_documents_updated_at
    BEFORE UPDATE ON knowledge_documents
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();


-- ====================================================
-- AUTOMATED LEDGER AND QUANTITY SYNC TRIGGERS
-- ====================================================

-- Function to sync inventory changes to transaction history log
CREATE OR REPLACE FUNCTION log_inventory_change()
RETURNS TRIGGER AS $$
DECLARE
    v_qty_diff INT;
    v_tx_type transaction_type;
    v_notes TEXT;
BEGIN
    IF (TG_OP = 'INSERT') THEN
        v_qty_diff := NEW.quantity;
        v_tx_type := 'stock_in';
        v_notes := 'Initial stock record created.';
    ELSIF (TG_OP = 'UPDATE') THEN
        v_qty_diff := NEW.quantity - OLD.quantity;
        IF v_qty_diff = 0 THEN
            RETURN NEW; -- No actual change in quantity
        END IF;

        IF v_qty_diff > 0 THEN
            v_tx_type := 'adjustment_add';
            v_notes := 'Stock increased (manual or trigger update)';
        ELSE
            v_tx_type := 'adjustment_sub';
            v_notes := 'Stock reduced (manual or trigger update)';
        END IF;
    END IF;

    -- Insert dynamic tracking row
    INSERT INTO inventory_transactions (
        branch_id,
        medicine_id,
        batch_id,
        inventory_id,
        type,
        qty_changed,
        notes,
        created_at
    ) VALUES (
        NEW.branch_id,
        NEW.medicine_id,
        NEW.batch_id,
        NEW.id,
        v_tx_type,
        v_qty_diff,
        v_notes,
        timezone('utc'::text, now())
    );

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER tr_log_inventory_flow
    AFTER INSERT OR UPDATE ON inventory
    FOR EACH ROW EXECUTE FUNCTION log_inventory_change();


-- ====================================================
-- AUTOMATIC EXPIRY ASSESSMENT E.G. RISK LABELLING
-- ====================================================

-- Trigger assessment on batch dates config
CREATE OR REPLACE FUNCTION assessment_expiry_risk()
RETURNS TRIGGER AS $$
DECLARE
    v_days INT;
    v_risk VARCHAR(20);
    v_inv_record RECORD;
BEGIN
    v_days := NEW.expiry_date - CURRENT_DATE;

    IF v_days > 180 THEN
        v_risk := 'safe';
    ELSIF v_days BETWEEN 91 AND 180 THEN
        v_risk := 'low';
    ELSIF v_days BETWEEN 31 AND 90 THEN
        v_risk := 'medium';
    ELSIF v_days BETWEEN 11 AND 30 THEN
        v_risk := 'high';
    ELSE
        v_risk := 'critical';
    END IF;

    -- Upsert tracking logic for active inventory stock referencing this batch
    FOR v_inv_record IN 
        SELECT id FROM inventory WHERE batch_id = NEW.id
    LOOP
        INSERT INTO expiry_tracking (
            inventory_id,
            batch_id,
            days_to_expiry,
            risk_level,
            created_at,
            updated_at
        ) VALUES (
            v_inv_record.id,
            NEW.id,
            v_days,
            v_risk,
            timezone('utc'::text, now()),
            timezone('utc'::text, now())
        ) ON CONFLICT (id) DO UPDATE SET -- fallback update details
            days_to_expiry = EXCLUDED.days_to_expiry,
            risk_level = EXCLUDED.risk_level,
            updated_at = timezone('utc'::text, now());
    END LOOP;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER tr_trigger_expiry_assessment
    AFTER INSERT OR UPDATE ON medicine_batches
    FOR EACH ROW EXECUTE FUNCTION assessment_expiry_risk();


-- ====================================================
-- ANALYTICAL PERFORMANCE VIEWS
-- ====================================================

-- View 1: Real-time Stock Deficiency/Reorder Alert System
CREATE OR REPLACE VIEW view_stockout_alerts AS
SELECT 
    i.id AS inventory_id,
    b.id AS branch_id,
    b.name AS branch_name,
    m.id AS medicine_id,
    m.brand_name,
    m.substance_name,
    m.sku,
    mb.batch_number,
    mb.expiry_date,
    i.quantity,
    i.reorder_level,
    (i.reorder_level - i.quantity) AS deficit,
    CASE 
        WHEN i.quantity = 0 THEN 'OUT_OF_STOCK'
        ELSE 'REORDER_CRITICAL'
    END AS status
FROM inventory i
JOIN branches b ON i.branch_id = b.id
JOIN medicines m ON i.medicine_id = m.id
JOIN medicine_batches mb ON i.batch_id = mb.id
WHERE i.quantity <= i.reorder_level AND b.deleted_at IS NULL;

-- View 2: Expiry Risk Trajectory Network-wide
CREATE OR REPLACE VIEW view_expiry_risk_summary AS
SELECT 
    et.id AS tracking_id,
    b.id AS branch_id,
    b.name AS branch_name,
    m.brand_name,
    m.substance_name,
    m.sku,
    mb.batch_number,
    mb.expiry_date,
    et.days_to_expiry,
    et.risk_level,
    i.quantity AS stock_qty,
    (i.quantity * COALESCE(mp.purchase_price, 0.00)) AS financial_risk_value
FROM expiry_tracking et
JOIN medicine_batches mb ON et.batch_id = mb.id
JOIN inventory i ON et.inventory_id = i.id
JOIN branches b ON i.branch_id = b.id
JOIN medicines m ON i.medicine_id = m.id
LEFT JOIN medicine_prices mp ON mp.id = (
    SELECT id FROM medicine_prices mp2 
    WHERE mp2.medicine_id = m.id AND mp2.is_active = TRUE 
      AND (mp2.branch_id = b.id OR mp2.branch_id IS NULL)
    ORDER BY (CASE WHEN mp2.branch_id = b.id THEN 1 ELSE 2 END) ASC
    LIMIT 1
)
WHERE et.risk_level IN ('medium', 'high', 'critical')
ORDER BY et.days_to_expiry ASC;

-- View 3: POS Financial Branch Margin Performance Comparison
CREATE OR REPLACE VIEW view_branch_margin_performance AS
WITH order_aggregates AS (
    SELECT 
        o.branch_id,
        COUNT(DISTINCT o.id) AS sales_count,
        COALESCE(SUM(o.total_amount), 0.00) AS total_revenue
    FROM orders o
    WHERE o.status = 'completed'
    GROUP BY o.branch_id
),
cost_aggregates AS (
    SELECT 
        o.branch_id,
        COALESCE(SUM(oi.quantity * (
            SELECT purchase_price FROM medicine_prices mp2
            WHERE mp2.medicine_id = oi.medicine_id AND mp2.is_active = TRUE
              AND (mp2.branch_id = o.branch_id OR mp2.branch_id IS NULL)
            ORDER BY (CASE WHEN mp2.branch_id = o.branch_id THEN 1 ELSE 2 END) ASC
            LIMIT 1
        )), 0.00) AS total_cost
    FROM orders o
    JOIN order_items oi ON oi.order_id = o.id
    WHERE o.status = 'completed'
    GROUP BY o.branch_id
)
SELECT 
    b.id AS branch_id,
    b.name AS branch_name,
    b.city AS branch_city,
    COALESCE(oa.sales_count, 0) AS sales_count,
    COALESCE(oa.total_revenue, 0.00) AS total_revenue,
    COALESCE(ca.total_cost, 0.00) AS total_cost,
    COALESCE(oa.total_revenue, 0.00) - COALESCE(ca.total_cost, 0.00) AS net_profit,
    CASE 
        WHEN COALESCE(oa.total_revenue, 0.00) = 0 THEN 0.00
        ELSE ROUND(((COALESCE(oa.total_revenue, 0.00) - COALESCE(ca.total_cost, 0.00)) / COALESCE(oa.total_revenue, 0.00)) * 100, 2)
    END AS profit_margin_percentage
FROM branches b
LEFT JOIN order_aggregates oa ON oa.branch_id = b.id
LEFT JOIN cost_aggregates ca ON ca.branch_id = b.id
WHERE b.deleted_at IS NULL;

-- View 4: LangGraph Agent Node Orchestration Telemetry
CREATE OR REPLACE VIEW view_ai_telemetry AS
SELECT 
    aa.id AS agent_id,
    aa.name AS agent_name,
    aa.role AS agent_role,
    aa.state AS current_state,
    aa.model_name,
    aa.latency_ms,
    aa.flows_executed,
    COALESCE(SUM(ar.tokens_used), 0) AS total_tokens_used,
    COALESCE(SUM(ar.cost_usd), 0.00000) AS total_cost_usd
FROM ai_agents aa
LEFT JOIN ai_tasks at ON at.agent_id = aa.id
LEFT JOIN ai_reasoning ar ON ar.task_id = at.id
GROUP BY aa.id, aa.name, aa.role, aa.state, aa.model_name, aa.latency_ms, aa.flows_executed;

-- Helper to sync auth.users with public.users on signup
CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO public.users (id, email, phone, branch_id, status)
    VALUES (new.id, new.email, new.phone, null, 'active');
    RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

CREATE OR REPLACE TRIGGER on_auth_user_created
    AFTER INSERT ON auth.users
    FOR EACH ROW EXECUTE FUNCTION public.handle_new_user();
