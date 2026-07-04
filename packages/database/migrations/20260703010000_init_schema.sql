-- Init Schema Migration for Nexus AI
-- Date: 2026-07-03
-- Author: Principal Database Architect

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Enable pgvector extension for AI embeddings
CREATE EXTENSION IF NOT EXISTS vector;

-- Create custom common statuses and enums
CREATE TYPE operational_status AS ENUM ('active', 'inactive', 'suspended', 'terminated');
CREATE TYPE transfer_status AS ENUM ('draft', 'pending_approval', 'approved', 'rejected', 'in_transit', 'received', 'cancelled');
CREATE TYPE order_status AS ENUM ('pending', 'completed', 'cancelled', 'refunded');
CREATE TYPE payment_status AS ENUM ('unpaid', 'partially_paid', 'paid', 'refunded', 'failed');
CREATE TYPE transaction_type AS ENUM ('stock_in', 'stock_out', 'transfer_in', 'transfer_out', 'adjustment_add', 'adjustment_sub', 'sale', 'sale_return', 'purchase', 'purchase_return', 'expiry_discard');
CREATE TYPE agent_state AS ENUM ('idle', 'analyzing', 'executing', 'awaiting_approval', 'offline', 'error');
CREATE TYPE approval_status AS ENUM ('pending', 'approved', 'rejected', 'escalated');
CREATE TYPE audit_severity AS ENUM ('info', 'low', 'medium', 'high', 'critical');

-- ====================================================
-- MODULE 1: Organization & Branches
-- ====================================================

-- Organizations Table (Multi-tenant structure support)
CREATE TABLE organizations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    legal_name VARCHAR(255),
    registration_no VARCHAR(100),
    tax_identifier VARCHAR(100),
    website VARCHAR(255),
    logo_url VARCHAR(512),
    status operational_status DEFAULT 'active' NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL,
    deleted_at TIMESTAMP WITH TIME ZONE
);

COMMENT ON TABLE organizations IS 'Top-level enterprise tenant representing the chain operator.';

-- Branches Table
CREATE TABLE branches (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    organization_id UUID NOT NULL REFERENCES organizations(id) ON DELETE RESTRICT,
    name VARCHAR(255) NOT NULL,
    code VARCHAR(50) UNIQUE NOT NULL,
    address TEXT NOT NULL,
    city VARCHAR(100) NOT NULL,
    state VARCHAR(100) NOT NULL,
    postal_code VARCHAR(20) NOT NULL,
    phone VARCHAR(50),
    email VARCHAR(255),
    is_hq BOOLEAN DEFAULT FALSE NOT NULL,
    status operational_status DEFAULT 'active' NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL,
    deleted_at TIMESTAMP WITH TIME ZONE
);

COMMENT ON TABLE branches IS 'Individual pharmacy retail branches under the parent organization.';

-- Branch Settings Table
CREATE TABLE branch_settings (
    branch_id UUID PRIMARY KEY REFERENCES branches(id) ON DELETE CASCADE,
    inventory_control_mode VARCHAR(50) DEFAULT 'FEFO' NOT NULL CHECK (inventory_control_mode IN ('FEFO', 'FIFO', 'LIFO')),
    auto_transfer_enabled BOOLEAN DEFAULT TRUE NOT NULL,
    pricing_override_allowed BOOLEAN DEFAULT FALSE NOT NULL,
    timezone VARCHAR(100) DEFAULT 'Asia/Kolkata' NOT NULL,
    currency VARCHAR(10) DEFAULT 'INR' NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);

COMMENT ON TABLE branch_settings IS 'Configuration controls specific to each branch execution node.';

-- ====================================================
-- MODULE 2: Authentication
-- ====================================================

-- Roles Table
CREATE TABLE roles (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(100) UNIQUE NOT NULL,
    description TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);

-- Permissions Table
CREATE TABLE permissions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    code VARCHAR(100) UNIQUE NOT NULL,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    category VARCHAR(50) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);

-- RolePermissions Table
CREATE TABLE role_permissions (
    role_id UUID NOT NULL REFERENCES roles(id) ON DELETE CASCADE,
    permission_id UUID NOT NULL REFERENCES permissions(id) ON DELETE CASCADE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL,
    PRIMARY KEY (role_id, permission_id)
);

-- Users Profile Table (Tied to Supabase auth.users)
CREATE TABLE users (
    id UUID PRIMARY KEY, -- Links 1:1, populated from auth.users UUIDs
    email VARCHAR(255) UNIQUE NOT NULL,
    phone VARCHAR(50),
    branch_id UUID REFERENCES branches(id) ON DELETE SET NULL, -- Null means Global/CEO/Regional scope
    status operational_status DEFAULT 'active' NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL,
    deleted_at TIMESTAMP WITH TIME ZONE
);

COMMENT ON TABLE users IS 'User profiles extending authentication records with tenant scope linkages.';

-- User Roles Table (Many-to-Many mapping for users and roles)
CREATE TABLE user_roles (
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    role_id UUID NOT NULL REFERENCES roles(id) ON DELETE CASCADE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL,
    PRIMARY KEY (user_id, role_id)
);

-- ====================================================
-- MODULE 3: Employees
-- ====================================================

-- Employees Table
CREATE TABLE employees (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID UNIQUE REFERENCES users(id) ON DELETE SET NULL,
    branch_id UUID NOT NULL REFERENCES branches(id) ON DELETE RESTRICT,
    employee_id VARCHAR(50) UNIQUE NOT NULL, -- Format EMP-XXXXXX
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    status operational_status DEFAULT 'active' NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL,
    deleted_at TIMESTAMP WITH TIME ZONE
);

-- Employee Profiles Table
CREATE TABLE employee_profiles (
    employee_id UUID PRIMARY KEY REFERENCES employees(id) ON DELETE CASCADE,
    gender VARCHAR(20),
    date_of_birth DATE,
    address TEXT,
    city VARCHAR(100),
    state VARCHAR(100),
    postal_code VARCHAR(20),
    emergency_contact_name VARCHAR(150),
    emergency_contact_phone VARCHAR(50),
    license_no VARCHAR(100), -- For registered pharmacists
    hire_date DATE NOT NULL,
    resignation_date DATE
);

-- Employee Shifts Table
CREATE TABLE employee_shifts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    employee_id UUID NOT NULL REFERENCES employees(id) ON DELETE CASCADE,
    day_of_week INT NOT NULL CHECK (day_of_week BETWEEN 0 AND 6), -- 0=Sunday, 6=Saturday
    start_time TIME NOT NULL,
    end_time TIME NOT NULL,
    is_active BOOLEAN DEFAULT TRUE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);

-- ====================================================
-- MODULE 4: Medicines
-- ====================================================

-- Medicine Categories Table
CREATE TABLE medicine_categories (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(100) UNIQUE NOT NULL,
    description TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);

-- Manufacturers Table
CREATE TABLE manufacturers (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) UNIQUE NOT NULL,
    code VARCHAR(50) UNIQUE,
    contact_email VARCHAR(255),
    contact_phone VARCHAR(50),
    address TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);

-- Medicines Table (SKU Master Database)
CREATE TABLE medicines (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    category_id UUID REFERENCES medicine_categories(id) ON DELETE SET NULL,
    manufacturer_id UUID REFERENCES manufacturers(id) ON DELETE RESTRICT,
    sku VARCHAR(100) UNIQUE NOT NULL, -- Stock Keeping Unit code
    substance_name VARCHAR(255) NOT NULL, -- Generic chemical formula name (e.g. Paracetamol)
    brand_name VARCHAR(255) NOT NULL, -- Commercial name (e.g. Crocin)
    dosage_form VARCHAR(100) NOT NULL, -- Tablet, Syrup, Injection, Capsule
    strength VARCHAR(50) NOT NULL, -- e.g. 500mg, 10ml, 50mcg
    hsn_code VARCHAR(20), -- Tax classification code
    requires_prescription BOOLEAN DEFAULT FALSE NOT NULL,
    is_narcotic BOOLEAN DEFAULT FALSE NOT NULL,
    requires_cold_chain BOOLEAN DEFAULT FALSE NOT NULL,
    status operational_status DEFAULT 'active' NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL,
    deleted_at TIMESTAMP WITH TIME ZONE
);

-- Medicine Batches Table
CREATE TABLE medicine_batches (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    medicine_id UUID NOT NULL REFERENCES medicines(id) ON DELETE CASCADE,
    batch_number VARCHAR(100) NOT NULL,
    manufacturing_date DATE,
    expiry_date DATE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL,
    UNIQUE (medicine_id, batch_number)
);

-- Medicine Prices Table (Maintains price history and regional overrides)
CREATE TABLE medicine_prices (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    medicine_id UUID NOT NULL REFERENCES medicines(id) ON DELETE CASCADE,
    branch_id UUID REFERENCES branches(id) ON DELETE CASCADE, -- NULL means global standard price
    mrp NUMERIC(12, 2) NOT NULL CHECK (mrp >= 0), -- Maximum Retail Price
    purchase_price NUMERIC(12, 2) NOT NULL CHECK (purchase_price >= 0),
    discount_percentage NUMERIC(5, 2) DEFAULT 0.00 NOT NULL CHECK (discount_percentage BETWEEN 0 AND 100),
    is_active BOOLEAN DEFAULT TRUE NOT NULL,
    effective_from TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL,
    effective_to TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);

-- Medicine Images Table
CREATE TABLE medicine_images (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    medicine_id UUID NOT NULL REFERENCES medicines(id) ON DELETE CASCADE,
    image_url VARCHAR(512) NOT NULL,
    is_primary BOOLEAN DEFAULT FALSE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);

-- ====================================================
-- MODULE 5: Inventory
-- ====================================================

-- Inventory Table (Tracks stock on a per-batch, per-branch level)
CREATE TABLE inventory (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    branch_id UUID NOT NULL REFERENCES branches(id) ON DELETE RESTRICT,
    medicine_id UUID NOT NULL REFERENCES medicines(id) ON DELETE RESTRICT,
    batch_id UUID NOT NULL REFERENCES medicine_batches(id) ON DELETE RESTRICT,
    quantity INT DEFAULT 0 NOT NULL CHECK (quantity >= 0),
    reorder_level INT DEFAULT 10 NOT NULL CHECK (reorder_level >= 0),
    max_level INT CHECK (max_level >= reorder_level),
    last_stock_take TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL,
    UNIQUE (branch_id, batch_id)
);

-- Inventory Transactions Table (Double Entry Ledger of Stock Changes)
CREATE TABLE inventory_transactions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    branch_id UUID NOT NULL REFERENCES branches(id) ON DELETE RESTRICT,
    medicine_id UUID NOT NULL REFERENCES medicines(id) ON DELETE RESTRICT,
    batch_id UUID NOT NULL REFERENCES medicine_batches(id) ON DELETE RESTRICT,
    inventory_id UUID REFERENCES inventory(id) ON DELETE SET NULL,
    type transaction_type NOT NULL,
    qty_changed INT NOT NULL, -- Positive for increase, negative for decrease
    reference_id UUID, -- Links to orders, transfers, receipts, or adjustments tables
    notes TEXT,
    created_by UUID REFERENCES users(id) ON DELETE SET NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);

-- Inventory Adjustments Table
CREATE TABLE inventory_adjustments (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    branch_id UUID NOT NULL REFERENCES branches(id) ON DELETE RESTRICT,
    reason TEXT NOT NULL,
    status approval_status DEFAULT 'pending' NOT NULL,
    approved_by UUID REFERENCES users(id) ON DELETE SET NULL,
    approved_at TIMESTAMP WITH TIME ZONE,
    created_by UUID NOT NULL REFERENCES users(id) ON DELETE RESTRICT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);

-- Inventory Adjustment Items Table (Details of Adjustments)
CREATE TABLE inventory_adjustment_items (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    adjustment_id UUID NOT NULL REFERENCES inventory_adjustments(id) ON DELETE CASCADE,
    inventory_id UUID NOT NULL REFERENCES inventory(id) ON DELETE RESTRICT,
    batch_id UUID NOT NULL REFERENCES medicine_batches(id) ON DELETE RESTRICT,
    system_qty INT NOT NULL,
    actual_qty INT NOT NULL CHECK (actual_qty >= 0),
    difference_qty INT NOT NULL CHECK (difference_qty = actual_qty - system_qty)
);

-- Stock Movements Table (Higher-level logistical summary mapping)
CREATE TABLE stock_movements (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    branch_id UUID NOT NULL REFERENCES branches(id) ON DELETE RESTRICT,
    direction VARCHAR(10) NOT NULL CHECK (direction IN ('IN', 'OUT')),
    transaction_date DATE DEFAULT CURRENT_DATE NOT NULL,
    total_items INT DEFAULT 0 NOT NULL CHECK (total_items >= 0),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);

-- Stock Transfers Table (Inter-branch Movements)
CREATE TABLE stock_transfers (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    from_branch_id UUID NOT NULL REFERENCES branches(id) ON DELETE RESTRICT,
    to_branch_id UUID NOT NULL REFERENCES branches(id) ON DELETE RESTRICT,
    status transfer_status DEFAULT 'draft' NOT NULL,
    estimated_arrival TIMESTAMP WITH TIME ZONE,
    actual_arrival TIMESTAMP WITH TIME ZONE,
    courier_details TEXT,
    tracking_no VARCHAR(100),
    freight_charges NUMERIC(10, 2) DEFAULT 0.00 CHECK (freight_charges >= 0),
    rejection_reason TEXT,
    created_by UUID REFERENCES users(id) ON DELETE SET NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL,
    CONSTRAINT chk_different_branches CHECK (from_branch_id <> to_branch_id)
);

-- Transfer Items Table (Line items of stock transfers)
CREATE TABLE transfer_items (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    transfer_id UUID NOT NULL REFERENCES stock_transfers(id) ON DELETE CASCADE,
    medicine_id UUID NOT NULL REFERENCES medicines(id) ON DELETE RESTRICT,
    batch_id UUID NOT NULL REFERENCES medicine_batches(id) ON DELETE RESTRICT,
    qty_requested INT NOT NULL CHECK (qty_requested > 0),
    qty_shipped INT CHECK (qty_shipped >= 0),
    qty_received INT CHECK (qty_received >= 0),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);

-- Expiry Tracking Table (Fitted specifically for FEFO agent triggers)
CREATE TABLE expiry_tracking (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    inventory_id UUID NOT NULL REFERENCES inventory(id) ON DELETE CASCADE,
    batch_id UUID NOT NULL REFERENCES medicine_batches(id) ON DELETE RESTRICT,
    days_to_expiry INT NOT NULL,
    risk_level VARCHAR(20) NOT NULL CHECK (risk_level IN ('safe', 'low', 'medium', 'high', 'critical')),
    action_taken TEXT,
    notified_to_agent BOOLEAN DEFAULT FALSE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);

-- ====================================================
-- MODULE 6: Suppliers
-- ====================================================

-- Suppliers Table
CREATE TABLE suppliers (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    code VARCHAR(50) UNIQUE NOT NULL,
    tax_no VARCHAR(100),
    credit_period_days INT DEFAULT 30 CHECK (credit_period_days >= 0),
    balance_payable NUMERIC(15, 2) DEFAULT 0.00 NOT NULL,
    status operational_status DEFAULT 'active' NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL,
    deleted_at TIMESTAMP WITH TIME ZONE
);

-- Supplier Contacts Table
CREATE TABLE supplier_contacts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    supplier_id UUID NOT NULL REFERENCES suppliers(id) ON DELETE CASCADE,
    contact_name VARCHAR(150) NOT NULL,
    contact_phone VARCHAR(50),
    contact_email VARCHAR(255),
    designation VARCHAR(100),
    is_primary BOOLEAN DEFAULT TRUE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);

-- Purchase Orders Table
CREATE TABLE purchase_orders (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    supplier_id UUID NOT NULL REFERENCES suppliers(id) ON DELETE RESTRICT,
    branch_id UUID NOT NULL REFERENCES branches(id) ON DELETE RESTRICT,
    po_number VARCHAR(100) UNIQUE NOT NULL,
    total_amount NUMERIC(15, 2) DEFAULT 0.00 NOT NULL CHECK (total_amount >= 0),
    status VARCHAR(50) DEFAULT 'draft' NOT NULL CHECK (status IN ('draft', 'sent', 'partially_received', 'received', 'cancelled')),
    delivery_date DATE,
    created_by UUID REFERENCES users(id) ON DELETE SET NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);

-- Purchase Order Items Table
CREATE TABLE purchase_order_items (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    po_id UUID NOT NULL REFERENCES purchase_orders(id) ON DELETE CASCADE,
    medicine_id UUID NOT NULL REFERENCES medicines(id) ON DELETE RESTRICT,
    quantity INT NOT NULL CHECK (quantity > 0),
    unit_cost NUMERIC(12, 2) NOT NULL CHECK (unit_cost >= 0),
    discount_percentage NUMERIC(5, 2) DEFAULT 0.00 CHECK (discount_percentage BETWEEN 0 AND 100),
    net_cost NUMERIC(12, 2) NOT NULL CHECK (net_cost >= 0)
);

-- Goods Receipts Table
CREATE TABLE goods_receipts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    po_id UUID REFERENCES purchase_orders(id) ON DELETE SET NULL,
    supplier_id UUID NOT NULL REFERENCES suppliers(id) ON DELETE RESTRICT,
    branch_id UUID NOT NULL REFERENCES branches(id) ON DELETE RESTRICT,
    receipt_no VARCHAR(100) UNIQUE NOT NULL,
    received_date TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL,
    invoice_no VARCHAR(100),
    invoice_amount NUMERIC(15, 2),
    created_by UUID REFERENCES users(id) ON DELETE SET NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);

-- Goods Receipt Items Table (Inventory batch items populated during receipt)
CREATE TABLE goods_receipt_items (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    receipt_id UUID NOT NULL REFERENCES goods_receipts(id) ON DELETE CASCADE,
    medicine_id UUID NOT NULL REFERENCES medicines(id) ON DELETE RESTRICT,
    batch_id UUID NOT NULL REFERENCES medicine_batches(id) ON DELETE RESTRICT,
    qty_received INT NOT NULL CHECK (qty_received > 0),
    qty_rejected INT DEFAULT 0 CHECK (qty_rejected >= 0),
    unit_cost NUMERIC(12, 2) NOT NULL CHECK (unit_cost >= 0),
    expiry_date DATE NOT NULL
);

-- ====================================================
-- MODULE 7: Customers
-- ====================================================

-- Customers Table
CREATE TABLE customers (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    phone VARCHAR(50) UNIQUE,
    email VARCHAR(255),
    loyalty_points INT DEFAULT 0 NOT NULL CHECK (loyalty_points >= 0),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL,
    deleted_at TIMESTAMP WITH TIME ZONE
);

-- Customer Profiles Table (Additional demographical data)
CREATE TABLE customer_profiles (
    customer_id UUID PRIMARY KEY REFERENCES customers(id) ON DELETE CASCADE,
    gender VARCHAR(20),
    date_of_birth DATE,
    address TEXT,
    allergies TEXT,
    medical_history TEXT,
    notes TEXT
);

-- Customer Prescriptions Table
CREATE TABLE customer_prescriptions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    customer_id UUID NOT NULL REFERENCES customers(id) ON DELETE CASCADE,
    doctor_name VARCHAR(150),
    clinic_details TEXT,
    prescription_date DATE NOT NULL,
    digital_copy_url VARCHAR(512),
    extracted_text TEXT, -- Parsed details through AI OCR
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);

-- Prescription Items Table (Granular items extracted to parse match SKUs)
CREATE TABLE prescription_items (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    prescription_id UUID NOT NULL REFERENCES customer_prescriptions(id) ON DELETE CASCADE,
    medicine_id UUID REFERENCES medicines(id) ON DELETE SET NULL,
    raw_medicine_name VARCHAR(255) NOT NULL, -- Text read by OCR
    dosage VARCHAR(100), -- E.g., 1-0-1
    duration VARCHAR(50), -- E.g., 5 days
    qty_prescribed INT CHECK (qty_prescribed > 0)
);

-- ====================================================
-- MODULE 8: Orders & Checkouts
-- ====================================================

-- Orders Table
CREATE TABLE orders (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    branch_id UUID NOT NULL REFERENCES branches(id) ON DELETE RESTRICT,
    customer_id UUID REFERENCES customers(id) ON DELETE SET NULL,
    cashier_id UUID REFERENCES users(id) ON DELETE SET NULL, -- Employee POS user
    order_no VARCHAR(100) UNIQUE NOT NULL, -- Order sequence number
    subtotal NUMERIC(12, 2) NOT NULL CHECK (subtotal >= 0),
    tax_amount NUMERIC(12, 2) DEFAULT 0.00 NOT NULL CHECK (tax_amount >= 0),
    discount_amount NUMERIC(12, 2) DEFAULT 0.00 NOT NULL CHECK (discount_amount >= 0),
    total_amount NUMERIC(12, 2) NOT NULL CHECK (total_amount >= 0),
    status order_status DEFAULT 'pending' NOT NULL,
    prescription_id UUID REFERENCES customer_prescriptions(id) ON DELETE SET NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);

-- Order Items Table
CREATE TABLE order_items (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    order_id UUID NOT NULL REFERENCES orders(id) ON DELETE CASCADE,
    medicine_id UUID NOT NULL REFERENCES medicines(id) ON DELETE RESTRICT,
    batch_id UUID NOT NULL REFERENCES medicine_batches(id) ON DELETE RESTRICT,
    quantity INT NOT NULL CHECK (quantity > 0),
    unit_price NUMERIC(12, 2) NOT NULL CHECK (unit_price >= 0),
    discount_percentage NUMERIC(5, 2) DEFAULT 0.00 CHECK (discount_percentage BETWEEN 0 AND 100),
    tax_percentage NUMERIC(5, 2) DEFAULT 12.00 CHECK (tax_percentage >= 0),
    net_price NUMERIC(12, 2) NOT NULL CHECK (net_price >= 0)
);

-- Payment Methods Table
CREATE TABLE payment_methods (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(50) UNIQUE NOT NULL, -- e.g. Cash, Card, UPI, Wallet
    is_active BOOLEAN DEFAULT TRUE NOT NULL
);

-- Payments Table
CREATE TABLE payments (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    order_id UUID NOT NULL REFERENCES orders(id) ON DELETE CASCADE,
    payment_method_id UUID NOT NULL REFERENCES payment_methods(id) ON DELETE RESTRICT,
    amount NUMERIC(12, 2) NOT NULL CHECK (amount > 0),
    transaction_no VARCHAR(100),
    status payment_status DEFAULT 'unpaid' NOT NULL,
    paid_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL,
    notes TEXT
);

-- Invoices Table (Fiscal Legal Document)
CREATE TABLE invoices (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    order_id UUID UNIQUE NOT NULL REFERENCES orders(id) ON DELETE CASCADE,
    branch_id UUID NOT NULL REFERENCES branches(id) ON DELETE RESTRICT,
    invoice_no VARCHAR(100) UNIQUE NOT NULL,
    issue_date TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL,
    due_date DATE,
    total_tax NUMERIC(12, 2) NOT NULL,
    total_amount NUMERIC(12, 2) NOT NULL,
    status payment_status DEFAULT 'unpaid' NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);

-- Invoice Items Table
CREATE TABLE invoice_items (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    invoice_id UUID NOT NULL REFERENCES invoices(id) ON DELETE CASCADE,
    order_item_id UUID NOT NULL REFERENCES order_items(id) ON DELETE RESTRICT,
    item_description VARCHAR(255) NOT NULL,
    qty INT NOT NULL CHECK (qty > 0),
    unit_rate NUMERIC(12, 2) NOT NULL,
    tax_amount NUMERIC(12, 2) NOT NULL,
    net_amount NUMERIC(12, 2) NOT NULL
);

-- ====================================================
-- MODULE 9: Finance
-- ====================================================

-- Expense Categories Table
CREATE TABLE expense_categories (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(155) UNIQUE NOT NULL,
    description TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);

-- Expenses Table
CREATE TABLE expenses (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    branch_id UUID REFERENCES branches(id) ON DELETE SET NULL, -- Null represents network-wide/corporate cost
    category_id UUID NOT NULL REFERENCES expense_categories(id) ON DELETE RESTRICT,
    amount NUMERIC(15, 2) NOT NULL CHECK (amount > 0),
    expense_date DATE DEFAULT CURRENT_DATE NOT NULL,
    payment_reference VARCHAR(155),
    notes TEXT,
    created_by UUID REFERENCES users(id) ON DELETE SET NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);

-- Revenues Table (Aggregated daily from checkout audits for rapid reading)
CREATE TABLE revenues (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    branch_id UUID NOT NULL REFERENCES branches(id) ON DELETE CASCADE,
    amount NUMERIC(15, 2) NOT NULL CHECK (amount >= 0),
    sales_count INT DEFAULT 0 NOT NULL CHECK (sales_count >= 0),
    revenue_date DATE DEFAULT CURRENT_DATE NOT NULL,
    is_audited BOOLEAN DEFAULT FALSE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL,
    UNIQUE (branch_id, revenue_date)
);

-- Financial Reports Table
CREATE TABLE financial_reports (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    organization_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    type VARCHAR(50) NOT NULL CHECK (type IN ('profit_loss', 'balance_sheet', 'tax_report', 'margin_leakage')),
    period_start DATE NOT NULL,
    period_end DATE NOT NULL,
    metrics JSONB NOT NULL,
    digital_copy_url VARCHAR(512),
    created_by UUID REFERENCES users(id) ON DELETE SET NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);

-- ====================================================
-- MODULE 10: Analytics
-- ====================================================

-- Daily Branch Metrics Table
CREATE TABLE daily_branch_metrics (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    branch_id UUID NOT NULL REFERENCES branches(id) ON DELETE CASCADE,
    date DATE DEFAULT CURRENT_DATE NOT NULL,
    total_sales NUMERIC(15, 2) DEFAULT 0.00 NOT NULL CHECK (total_sales >= 0),
    total_transactions INT DEFAULT 0 NOT NULL CHECK (total_transactions >= 0),
    items_sold INT DEFAULT 0 NOT NULL CHECK (items_sold >= 0),
    average_order_value NUMERIC(12, 2) DEFAULT 0.00 NOT NULL,
    stockouts_count INT DEFAULT 0 NOT NULL CHECK (stockouts_count >= 0),
    expiries_detected INT DEFAULT 0 NOT NULL CHECK (expiries_detected >= 0),
    ai_decisions_executed INT DEFAULT 0 NOT NULL CHECK (ai_decisions_executed >= 0),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL,
    UNIQUE (branch_id, date)
);

-- Monthly Branch Metrics Table
CREATE TABLE monthly_branch_metrics (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    branch_id UUID NOT NULL REFERENCES branches(id) ON DELETE CASCADE,
    month_start DATE NOT NULL, -- First day of the month
    total_sales NUMERIC(15, 2) DEFAULT 0.00 NOT NULL CHECK (total_sales >= 0),
    total_transactions INT DEFAULT 0 NOT NULL CHECK (total_transactions >= 0),
    items_sold INT DEFAULT 0 NOT NULL CHECK (items_sold >= 0),
    average_order_value NUMERIC(12, 2) DEFAULT 0.00 NOT NULL,
    stockouts_count INT DEFAULT 0 NOT NULL CHECK (stockouts_count >= 0),
    expiries_detected INT DEFAULT 0 NOT NULL CHECK (expiries_detected >= 0),
    ai_decisions_count INT DEFAULT 0 NOT NULL CHECK (ai_decisions_count >= 0),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL,
    UNIQUE (branch_id, month_start)
);

-- Network Metrics Table
CREATE TABLE network_metrics (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    organization_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    date DATE DEFAULT CURRENT_DATE NOT NULL,
    network_sales NUMERIC(15, 2) DEFAULT 0.00 NOT NULL CHECK (network_sales >= 0),
    network_transactions INT DEFAULT 0 NOT NULL CHECK (network_transactions >= 0),
    network_health_score NUMERIC(5, 2) DEFAULT 100.00 NOT NULL CHECK (network_health_score BETWEEN 0 AND 100),
    total_active_agents INT DEFAULT 0 NOT NULL CHECK (total_active_agents >= 0),
    total_transfers_saved_costs NUMERIC(12, 2) DEFAULT 0.00 NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL,
    UNIQUE (organization_id, date)
);

-- ====================================================
-- MODULE 11: Notifications
-- ====================================================

-- Notifications Table
CREATE TABLE notifications (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE, -- Link to user profile
    branch_id UUID REFERENCES branches(id) ON DELETE CASCADE, -- Optional broad branch alerts
    title VARCHAR(255) NOT NULL,
    message TEXT NOT NULL,
    type VARCHAR(50) DEFAULT 'system' NOT NULL CHECK (type IN ('system', 'critical_alert', 'warning', 'ai_trace')),
    severity audit_severity DEFAULT 'info' NOT NULL,
    is_read BOOLEAN DEFAULT FALSE NOT NULL,
    action_url VARCHAR(512),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);

-- Notification Preferences Table
CREATE TABLE notification_preferences (
    user_id UUID PRIMARY KEY REFERENCES users(id) ON DELETE CASCADE,
    email_alerts_enabled BOOLEAN DEFAULT TRUE NOT NULL,
    sys_alerts_enabled BOOLEAN DEFAULT TRUE NOT NULL,
    sms_alerts_enabled BOOLEAN DEFAULT FALSE NOT NULL,
    ai_recommendation_notify BOOLEAN DEFAULT TRUE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);

-- ====================================================
-- MODULE 12: Knowledge Center (RAG Vectors)
-- ====================================================

-- Knowledge Documents Table
CREATE TABLE knowledge_documents (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    title VARCHAR(255) NOT NULL,
    file_name VARCHAR(255) NOT NULL,
    file_size INT NOT NULL CHECK (file_size > 0),
    mime_type VARCHAR(100) NOT NULL,
    storage_path VARCHAR(512) NOT NULL,
    chunk_count INT DEFAULT 0 NOT NULL,
    uploaded_by UUID REFERENCES users(id) ON DELETE SET NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);

-- Document Chunks Table
CREATE TABLE document_chunks (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    document_id UUID NOT NULL REFERENCES knowledge_documents(id) ON DELETE CASCADE,
    chunk_index INT NOT NULL,
    content TEXT NOT NULL,
    metadata JSONB DEFAULT '{}'::jsonb NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);

-- Embeddings Vector Table (ChromaDB replacement in Postgres)
CREATE TABLE embeddings (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    chunk_id UUID UNIQUE NOT NULL REFERENCES document_chunks(id) ON DELETE CASCADE,
    embedding VECTOR(1536) NOT NULL, -- Compatible with OpenAI text-embedding-3
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);

-- Knowledge Tags Table
CREATE TABLE knowledge_tags (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    document_id UUID NOT NULL REFERENCES knowledge_documents(id) ON DELETE CASCADE,
    tag VARCHAR(50) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL,
    UNIQUE (document_id, tag)
);

-- ====================================================
-- MODULE 13: AI SYSTEM (LangGraph Execution)
-- ====================================================

-- AI Agents Table
CREATE TABLE ai_agents (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(100) UNIQUE NOT NULL, -- Regional Manager, Inventory Agent, etc.
    role VARCHAR(150) NOT NULL,
    model_provider VARCHAR(50) DEFAULT 'openai' NOT NULL,
    model_name VARCHAR(100) DEFAULT 'gpt-4o' NOT NULL,
    system_instructions TEXT NOT NULL,
    state agent_state DEFAULT 'idle' NOT NULL,
    version VARCHAR(20) DEFAULT '1.0.0' NOT NULL,
    latency_ms INT DEFAULT 0 CHECK (latency_ms >= 0),
    active_memory_kb INT DEFAULT 0,
    flows_executed INT DEFAULT 0 NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);

-- AI Workflows Table (LangGraph structures)
CREATE TABLE ai_workflows (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(150) NOT NULL,
    description TEXT,
    state_schema JSONB NOT NULL, -- Current active dynamic schema variables
    is_active BOOLEAN DEFAULT TRUE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);

-- AI Tasks Table (Actions queued & executed by agents)
CREATE TABLE ai_tasks (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    agent_id UUID NOT NULL REFERENCES ai_agents(id) ON DELETE CASCADE,
    workflow_id UUID REFERENCES ai_workflows(id) ON DELETE SET NULL,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    status VARCHAR(50) DEFAULT 'pending' NOT NULL CHECK (status IN ('pending', 'running', 'completed', 'failed', 'cancelled')),
    attempts INT DEFAULT 0 NOT NULL,
    error_message TEXT,
    started_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);

-- AI Memory Table (Persistent chat context / RAG storage)
CREATE TABLE ai_memory (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    session_id VARCHAR(100) NOT NULL, -- Session boundaries
    agent_id UUID NOT NULL REFERENCES ai_agents(id) ON DELETE CASCADE,
    key VARCHAR(255) NOT NULL,
    value JSONB NOT NULL,
    expires_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);

-- AI Reasoning Trace Table
CREATE TABLE ai_reasoning (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    task_id UUID REFERENCES ai_tasks(id) ON DELETE CASCADE,
    step_name VARCHAR(150) NOT NULL,
    chain_of_thought TEXT[] NOT NULL, -- Graph node reasoning sequence arrays
    raw_prompt TEXT,
    raw_completion TEXT,
    tokens_used INT DEFAULT 0 CHECK (tokens_used >= 0),
    cost_usd NUMERIC(10, 5) DEFAULT 0.00000,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);

-- AI Decisions Table
CREATE TABLE ai_decisions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    agent_id UUID NOT NULL REFERENCES ai_agents(id) ON DELETE RESTRICT,
    decision_type VARCHAR(100) NOT NULL, -- e.g. stock_reorder, pricing_alert
    context JSONB NOT NULL, -- Supporting JSON factors
    actions_delegated JSONB NOT NULL, -- Target endpoints / state parameters
    status VARCHAR(50) DEFAULT 'unexecuted' CHECK (status IN ('unexecuted', 'executed', 'failed')),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);

-- AI Recommendations Table
CREATE TABLE ai_recommendations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    agent_id UUID NOT NULL REFERENCES ai_agents(id) ON DELETE RESTRICT,
    branch_id UUID REFERENCES branches(id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    details TEXT NOT NULL,
    estimated_savings NUMERIC(12, 2),
    confidence NUMERIC(5, 2) CHECK (confidence BETWEEN 0 AND 100),
    is_applied BOOLEAN DEFAULT FALSE NOT NULL,
    dismissed BOOLEAN DEFAULT FALSE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);

-- AI Conversations Table
CREATE TABLE ai_conversations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    session_id VARCHAR(100) UNIQUE NOT NULL,
    user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    branch_id UUID REFERENCES branches(id) ON DELETE SET NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);

-- AI Messages Table (Detail logs inside conversations)
CREATE TABLE ai_messages (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    conversation_id UUID NOT NULL REFERENCES ai_conversations(id) ON DELETE CASCADE,
    sender VARCHAR(20) NOT NULL CHECK (sender IN ('user', 'assistant', 'system')),
    content TEXT NOT NULL,
    reasoning_trace TEXT, -- Optional inner detail
    tokens INT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);

-- AI System Logs Table (Internal low level trace)
CREATE TABLE ai_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    agent_id UUID REFERENCES ai_agents(id) ON DELETE RESTRICT,
    session_id VARCHAR(100),
    log_level VARCHAR(20) DEFAULT 'info' CHECK (log_level IN ('info', 'debug', 'warning', 'error')),
    message TEXT NOT NULL,
    stack_trace TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);

-- ====================================================
-- MODULE 14: Approval Workflows
-- ====================================================

-- Approvals Table
CREATE TABLE approvals (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    organization_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    branch_id UUID REFERENCES branches(id) ON DELETE CASCADE,
    document_type VARCHAR(100) NOT NULL, -- e.g. stock_transfer, purchase_order, price_override
    document_reference_id UUID NOT NULL, -- Links to stock_transfers(id), purchase_orders(id), etc.
    title VARCHAR(255) NOT NULL,
    description TEXT,
    current_step INT DEFAULT 1 NOT NULL,
    total_steps INT NOT NULL CHECK (total_steps >= current_step),
    status approval_status DEFAULT 'pending' NOT NULL,
    rework_required BOOLEAN DEFAULT FALSE NOT NULL,
    created_by UUID REFERENCES users(id) ON DELETE SET NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);

-- Approval Steps Table
CREATE TABLE approval_steps (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    approval_id UUID NOT NULL REFERENCES approvals(id) ON DELETE CASCADE,
    step_number INT NOT NULL CHECK (step_number > 0),
    approver_role_id UUID REFERENCES roles(id) ON DELETE RESTRICT, -- Target authorization role
    approver_user_id UUID REFERENCES users(id) ON DELETE RESTRICT, -- Optional specified human
    status approval_status DEFAULT 'pending' NOT NULL,
    completed_at TIMESTAMP WITH TIME ZONE,
    comments TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL,
    UNIQUE (approval_id, step_number)
);

-- Approval History Table
CREATE TABLE approval_history (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    approval_id UUID NOT NULL REFERENCES approvals(id) ON DELETE CASCADE,
    step_number INT NOT NULL,
    action_taken VARCHAR(50) NOT NULL CHECK (action_taken IN ('submitted', 'approved', 'rejected', 'escalated', 'rework_requested')),
    actor_id UUID NOT NULL REFERENCES users(id) ON DELETE RESTRICT,
    comments TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);

-- ====================================================
-- MODULE 15: Auditing
-- ====================================================

-- Audit Logs Table
CREATE TABLE audit_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    action VARCHAR(100) NOT NULL,
    table_name VARCHAR(100) NOT NULL,
    record_id UUID NOT NULL,
    old_values JSONB,
    new_values JSONB,
    ip_address VARCHAR(45),
    user_agent VARCHAR(255),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);

-- Activity Logs Table (Higher-level human actions inside the app interface)
CREATE TABLE activity_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    branch_id UUID REFERENCES branches(id) ON DELETE SET NULL,
    activity_type VARCHAR(100) NOT NULL,
    description TEXT NOT NULL,
    metadata JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);

-- System Events Table (Automatic infrastructure telemetry)
CREATE TABLE system_events (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    event_name VARCHAR(150) NOT NULL,
    source VARCHAR(100) NOT NULL, -- e.g. API Gateway, Database trigger, Job Scheduler
    severity audit_severity DEFAULT 'info' NOT NULL,
    payload JSONB,
    resolved BOOLEAN DEFAULT FALSE NOT NULL,
    resolved_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);

-- ====================================================
-- INDEX OPTIMIZATIONS (Primary Core B-Trees & GINs)
-- ====================================================

-- Core and Authentication module indexes
CREATE INDEX idx_users_branch ON users(branch_id);
CREATE INDEX idx_user_roles_composite ON user_roles(user_id, role_id);

-- Employee module indexes
CREATE INDEX idx_employees_branch ON employees(branch_id);
CREATE INDEX idx_employee_shifts_day ON employee_shifts(employee_id, day_of_week);

-- Medicine tracking optimized indexes
CREATE INDEX idx_medicines_category ON medicines(category_id);
CREATE INDEX idx_medicine_batches_expiry ON medicine_batches(expiry_date);
CREATE INDEX idx_medicine_prices_composite ON medicine_prices(medicine_id, branch_id, is_active);
CREATE INDEX idx_medicines_search_composite ON medicines(brand_name, substance_name, sku);

-- High speed inventory lookup indexes
CREATE INDEX idx_inventory_lookup ON inventory(branch_id, medicine_id);
CREATE INDEX idx_inventory_transactions_batch ON inventory_transactions(batch_id, type);
CREATE INDEX idx_stock_transfers_branches ON stock_transfers(from_branch_id, to_branch_id, status);
CREATE INDEX idx_expiry_risk ON expiry_tracking(risk_level, notified_to_agent);

-- Order POS checking performance indexes
CREATE INDEX idx_orders_checkout ON orders(branch_id, status, created_at DESC);
CREATE INDEX idx_order_items_order ON order_items(order_id);
CREATE INDEX idx_invoices_order ON invoices(order_id);

-- Analytics & Notification indexes
CREATE INDEX idx_daily_branch_metrics_lookup ON daily_branch_metrics(branch_id, date DESC);
CREATE INDEX idx_notifications_user_unread ON notifications(user_id, is_read) WHERE is_read = FALSE;

-- AI telemetry and search indexes
CREATE INDEX idx_ai_tasks_status ON ai_tasks(agent_id, status);
CREATE INDEX idx_embeddings_chunk ON embeddings(chunk_id);
CREATE INDEX idx_doc_chunks_document ON document_chunks(document_id);

-- Vector Similarity GIN / HNSW index for ChromaDB style database searches
-- Using HNSW index for fast dot product / cosine similarity queries on OpenAI dimensions
CREATE INDEX idx_embeddings_vector ON embeddings USING hnsw (embedding vector_cosine_ops);
