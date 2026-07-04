-- Row-Level Security (RLS) Policies Migration for Nexus AI
-- Date: 2026-07-03
-- Author: Principal Database Architect

-- ====================================================
-- RLS HELPER FUNCTIONS (Supabase Integration)
-- ====================================================

-- Function to extract authenticated user UUID safely from JWT or session context
CREATE OR REPLACE FUNCTION public.get_auth_user_id()
RETURNS UUID AS $$
BEGIN
    RETURN COALESCE(
        NULLIF(current_setting('request.jwt.claims', true)::jsonb->>'sub', ''),
        auth.uid()::text
    )::uuid;
EXCEPTION
    WHEN OTHERS THEN
        RETURN auth.uid();
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Function to cache or fetch the current authenticated user's branch_id
CREATE OR REPLACE FUNCTION public.get_auth_user_branch_id()
RETURNS UUID AS $$
DECLARE
    v_branch_id UUID;
BEGIN
    SELECT branch_id INTO v_branch_id 
    FROM public.users 
    WHERE id = public.get_auth_user_id();
    RETURN v_branch_id;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Function to check if the current user has a specific role name
CREATE OR REPLACE FUNCTION public.user_has_role(p_role_name TEXT)
RETURNS BOOLEAN AS $$
DECLARE
    v_has_role BOOLEAN;
BEGIN
    SELECT EXISTS (
        SELECT 1 
        FROM public.user_roles ur
        JOIN public.roles r ON ur.role_id = r.id
        WHERE ur.user_id = public.get_auth_user_id() 
          AND r.name = p_role_name
    ) INTO v_has_role;
    RETURN v_has_role;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Function to check broad administrative or executive authority (CEO or ADMIN)
CREATE OR REPLACE FUNCTION public.is_executive_or_admin()
RETURNS BOOLEAN AS $$
BEGIN
    RETURN (
        public.user_has_role('CEO') OR 
        public.user_has_role('ADMIN')
    );
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;


-- ====================================================
-- ENABLE ROW LEVEL SECURITY ACROSS TABLES
-- ====================================================

ALTER TABLE organizations ENABLE ROW LEVEL SECURITY;
ALTER TABLE branches ENABLE ROW LEVEL SECURITY;
ALTER TABLE branch_settings ENABLE ROW LEVEL SECURITY;
ALTER TABLE roles ENABLE ROW LEVEL SECURITY;
ALTER TABLE permissions ENABLE ROW LEVEL SECURITY;
ALTER TABLE role_permissions ENABLE ROW LEVEL SECURITY;
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_roles ENABLE ROW LEVEL SECURITY;
ALTER TABLE employees ENABLE ROW LEVEL SECURITY;
ALTER TABLE employee_profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE employee_shifts ENABLE ROW LEVEL SECURITY;
ALTER TABLE medicine_categories ENABLE ROW LEVEL SECURITY;
ALTER TABLE manufacturers ENABLE ROW LEVEL SECURITY;
ALTER TABLE medicines ENABLE ROW LEVEL SECURITY;
ALTER TABLE medicine_batches ENABLE ROW LEVEL SECURITY;
ALTER TABLE medicine_prices ENABLE ROW LEVEL SECURITY;
ALTER TABLE medicine_images ENABLE ROW LEVEL SECURITY;
ALTER TABLE inventory ENABLE ROW LEVEL SECURITY;
ALTER TABLE inventory_transactions ENABLE ROW LEVEL SECURITY;
ALTER TABLE inventory_adjustments ENABLE ROW LEVEL SECURITY;
ALTER TABLE inventory_adjustment_items ENABLE ROW LEVEL SECURITY;
ALTER TABLE stock_movements ENABLE ROW LEVEL SECURITY;
ALTER TABLE stock_transfers ENABLE ROW LEVEL SECURITY;
ALTER TABLE transfer_items ENABLE ROW LEVEL SECURITY;
ALTER TABLE expiry_tracking ENABLE ROW LEVEL SECURITY;
ALTER TABLE suppliers ENABLE ROW LEVEL SECURITY;
ALTER TABLE supplier_contacts ENABLE ROW LEVEL SECURITY;
ALTER TABLE purchase_orders ENABLE ROW LEVEL SECURITY;
ALTER TABLE purchase_order_items ENABLE ROW LEVEL SECURITY;
ALTER TABLE goods_receipts ENABLE ROW LEVEL SECURITY;
ALTER TABLE goods_receipt_items ENABLE ROW LEVEL SECURITY;
ALTER TABLE customers ENABLE ROW LEVEL SECURITY;
ALTER TABLE customer_profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE customer_prescriptions ENABLE ROW LEVEL SECURITY;
ALTER TABLE prescription_items ENABLE ROW LEVEL SECURITY;
ALTER TABLE orders ENABLE ROW LEVEL SECURITY;
ALTER TABLE order_items ENABLE ROW LEVEL SECURITY;
ALTER TABLE payments ENABLE ROW LEVEL SECURITY;
ALTER TABLE invoices ENABLE ROW LEVEL SECURITY;
ALTER TABLE invoice_items ENABLE ROW LEVEL SECURITY;
ALTER TABLE expenses ENABLE ROW LEVEL SECURITY;
ALTER TABLE revenues ENABLE ROW LEVEL SECURITY;
ALTER TABLE financial_reports ENABLE ROW LEVEL SECURITY;
ALTER TABLE daily_branch_metrics ENABLE ROW LEVEL SECURITY;
ALTER TABLE monthly_branch_metrics ENABLE ROW LEVEL SECURITY;
ALTER TABLE network_metrics ENABLE ROW LEVEL SECURITY;
ALTER TABLE notifications ENABLE ROW LEVEL SECURITY;
ALTER TABLE notification_preferences ENABLE ROW LEVEL SECURITY;
ALTER TABLE knowledge_documents ENABLE ROW LEVEL SECURITY;
ALTER TABLE document_chunks ENABLE ROW LEVEL SECURITY;
ALTER TABLE embeddings ENABLE ROW LEVEL SECURITY;
ALTER TABLE knowledge_tags ENABLE ROW LEVEL SECURITY;
ALTER TABLE ai_agents ENABLE ROW LEVEL SECURITY;
ALTER TABLE ai_workflows ENABLE ROW LEVEL SECURITY;
ALTER TABLE ai_tasks ENABLE ROW LEVEL SECURITY;
ALTER TABLE ai_memory ENABLE ROW LEVEL SECURITY;
ALTER TABLE ai_reasoning ENABLE ROW LEVEL SECURITY;
ALTER TABLE ai_decisions ENABLE ROW LEVEL SECURITY;
ALTER TABLE ai_recommendations ENABLE ROW LEVEL SECURITY;
ALTER TABLE ai_conversations ENABLE ROW LEVEL SECURITY;
ALTER TABLE ai_messages ENABLE ROW LEVEL SECURITY;
ALTER TABLE ai_logs ENABLE ROW LEVEL SECURITY;
ALTER TABLE approvals ENABLE ROW LEVEL SECURITY;
ALTER TABLE approval_steps ENABLE ROW LEVEL SECURITY;
ALTER TABLE approval_history ENABLE ROW LEVEL SECURITY;
ALTER TABLE audit_logs ENABLE ROW LEVEL SECURITY;
ALTER TABLE activity_logs ENABLE ROW LEVEL SECURITY;
ALTER TABLE system_events ENABLE ROW LEVEL SECURITY;


-- ====================================================
-- RLS ACCESS CONTROL POLICIES
-- ====================================================

-- 1. Organizations table
CREATE POLICY select_orgs ON organizations
    FOR SELECT USING (TRUE); -- Everyone can view the organizations structure

CREATE POLICY modify_orgs ON organizations
    FOR ALL USING (public.user_has_role('ADMIN')); -- Only ADMIN can edit org profiles

-- 2. Branches table
CREATE POLICY select_branches ON branches
    FOR SELECT USING (TRUE); -- Branches are readable across networks for routing

CREATE POLICY modify_branches ON branches
    FOR ALL USING (public.user_has_role('ADMIN'));

-- 3. Users profile table
CREATE POLICY select_user_profile ON users
    FOR SELECT USING (
        public.get_auth_user_id() = id OR 
        public.is_executive_or_admin()
    );

CREATE POLICY update_user_profile ON users
    FOR UPDATE USING (
        public.get_auth_user_id() = id OR 
        public.user_has_role('ADMIN')
    );

-- 4. Inventory table
-- Executive: Read/write all
-- Manager/Pharmacist/Inventory/Finance/Auditor: Read local branch stock
-- Stock updates handled via cashiers or transfers
CREATE POLICY select_inventory ON inventory
    FOR SELECT USING (
        public.is_executive_or_admin() OR 
        public.user_has_role('FINANCE') OR
        public.get_auth_user_branch_id() = branch_id
    );

CREATE POLICY modify_inventory ON inventory
    FOR ALL USING (
        public.is_executive_or_admin() OR 
        (
            (public.user_has_role('BRANCH_MANAGER') OR public.user_has_role('INVENTORY')) AND
            public.get_auth_user_branch_id() = branch_id
        )
    );

-- 5. Inventory Transactions table
CREATE POLICY select_inventory_tx ON inventory_transactions
    FOR SELECT USING (
        public.is_executive_or_admin() OR 
        public.user_has_role('FINANCE') OR
        public.get_auth_user_branch_id() = branch_id
    );

-- 6. Stock Transfers
CREATE POLICY select_transfers ON stock_transfers
    FOR SELECT USING (
        public.is_executive_or_admin() OR
        public.get_auth_user_branch_id() = from_branch_id OR
        public.get_auth_user_branch_id() = to_branch_id
    );

CREATE POLICY create_transfers ON stock_transfers
    FOR INSERT WITH CHECK (
        public.is_executive_or_admin() OR
        public.get_auth_user_branch_id() = from_branch_id
    );

CREATE POLICY update_transfers ON stock_transfers
    FOR UPDATE USING (
        public.is_executive_or_admin() OR
        public.get_auth_user_branch_id() = from_branch_id OR
        public.get_auth_user_branch_id() = to_branch_id
    );

-- 7. Orders & POS Checkout
CREATE POLICY select_orders ON orders
    FOR SELECT USING (
        public.is_executive_or_admin() OR 
        public.user_has_role('FINANCE') OR
        public.get_auth_user_branch_id() = branch_id
    );

CREATE POLICY create_orders ON orders
    FOR INSERT WITH CHECK (
        public.get_auth_user_branch_id() = branch_id OR
        public.is_executive_or_admin()
    );

-- 8. Order Items
CREATE POLICY select_order_items ON order_items
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM orders
            WHERE orders.id = order_items.order_id
              AND (
                  public.is_executive_or_admin() OR 
                  public.user_has_role('FINANCE') OR 
                  orders.branch_id = public.get_auth_user_branch_id()
              )
        )
    );

-- 9. Invoices
CREATE POLICY select_invoices ON invoices
    FOR SELECT USING (
        public.is_executive_or_admin() OR 
        public.user_has_role('FINANCE') OR
        public.get_auth_user_branch_id() = branch_id
    );

-- 10. Financial Ledgers (Expenses, Revenues)
CREATE POLICY select_financials ON expenses
    FOR SELECT USING (
        public.is_executive_or_admin() OR 
        public.user_has_role('FINANCE') OR
        public.get_auth_user_branch_id() = branch_id
    );

CREATE POLICY select_revenues ON revenues
    FOR SELECT USING (
        public.is_executive_or_admin() OR 
        public.user_has_role('FINANCE') OR
        public.get_auth_user_branch_id() = branch_id
    );

-- 11. AI System Configurations, Recommendations & Telemetry
CREATE POLICY select_ai_recs ON ai_recommendations
    FOR SELECT USING (
        public.is_executive_or_admin() OR
        public.get_auth_user_branch_id() = branch_id
    );

CREATE POLICY modify_ai_recs ON ai_recommendations
    FOR UPDATE USING (
        public.is_executive_or_admin() OR
        (public.user_has_role('BRANCH_MANAGER') AND public.get_auth_user_branch_id() = branch_id)
    );

CREATE POLICY select_ai_telemetry ON ai_tasks
    FOR SELECT USING (TRUE); -- AI states are readable for dashboards

-- 12. Knowledge Center (RAG Document Embeddings)
CREATE POLICY select_knowledge ON knowledge_documents
    FOR SELECT USING (TRUE); -- Shared catalog reading enabled for RAG

-- 13. System Audit logs
CREATE POLICY select_audit ON audit_logs
    FOR SELECT USING (
        public.is_executive_or_admin()
    );
