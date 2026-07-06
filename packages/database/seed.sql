-- Seeding script for Nexus AI - Hyderabad Pharmacy Network Dataset
-- Date: 2026-07-03
-- Author: Principal Database Architect

-- Clean slate inserts
TRUNCATE organizations, branches, roles, permissions, role_permissions, users, user_roles, employees, medicine_categories, manufacturers, medicines, suppliers, payment_methods RESTART IDENTITY CASCADE;

-- ====================================================
-- SEED DATA PHASE 1: Baseline Entities
-- ====================================================

-- 1. Insert Enterprise Organization
INSERT INTO organizations (id, name, legal_name, registration_no, tax_identifier, website, status)
VALUES (
    '88888888-8888-4888-a888-888888888888',
    'NexusCare Pharmacy',
    'NexusCare Retail Labs PVT LTD',
    'U52310TG2026PTC184920',
    '36AABCN4910C1Z8',
    'https://www.nexuscare.com',
    'active'
);

-- 2. Insert 10 Hyderabad Branches (with Region support)
INSERT INTO branches (id, organization_id, name, code, region, address, city, state, postal_code, phone, email, is_hq, status)
VALUES
    ('b1111111-1111-4111-9111-111111111111', '88888888-8888-4888-a888-888888888888', 'NexusCare Banjara Hills', 'NEX-HYD-001', 'Central Hyderabad', 'Road No. 2, Banjara Hills', 'Hyderabad', 'Telangana', '500034', '+914023401122', 'banjara@nexuscare.com', TRUE, 'active'),
    ('b2222222-2222-4222-9222-222222222222', '88888888-8888-4888-a888-888888888888', 'NexusCare Jubilee Hills', 'NEX-HYD-002', 'Central Hyderabad', 'Road No. 36, Jubilee Hills', 'Hyderabad', 'Telangana', '500033', '+914023502233', 'jubilee@nexuscare.com', FALSE, 'active'),
    ('b3333333-3333-4333-9333-333333333333', '88888888-8888-4888-a888-888888888888', 'NexusCare Madhapur', 'NEX-HYD-003', 'West Hyderabad', 'Hitec City Road, Madhapur', 'Hyderabad', 'Telangana', '500081', '+914023603344', 'madhapur@nexuscare.com', FALSE, 'active'),
    ('b4444444-4444-4444-9444-444444444444', '88888888-8888-4888-a888-888888888888', 'NexusCare Gachibowli', 'NEX-HYD-004', 'West Hyderabad', 'DLF Cybercity Road, Gachibowli', 'Hyderabad', 'Telangana', '500032', '+914023704455', 'gachibowli@nexuscare.com', FALSE, 'active'),
    ('b5555555-5555-4555-9555-555555555555', '88888888-8888-4888-a888-888888888888', 'NexusCare Begumpet', 'NEX-HYD-005', 'North Hyderabad', 'SP Road, Begumpet', 'Hyderabad', 'Telangana', '500016', '+914023805566', 'begumpet@nexuscare.com', FALSE, 'active'),
    ('b6666666-6666-4666-9666-666666666666', '88888888-8888-4888-a888-888888888888', 'NexusCare Secunderabad', 'NEX-HYD-006', 'North Hyderabad', 'MG Road, Secunderabad', 'Hyderabad', 'Telangana', '500003', '+914023906677', 'secunderabad@nexuscare.com', FALSE, 'active'),
    ('b7777777-7777-4777-9777-777777777777', '88888888-8888-4888-a888-888888888888', 'NexusCare Kukatpally', 'NEX-HYD-007', 'West Hyderabad', 'KPHB Colony Phase 3, Kukatpally', 'Hyderabad', 'Telangana', '500072', '+914024007788', 'kukatpally@nexuscare.com', FALSE, 'active'),
    ('b8888888-8888-4888-9888-888888888888', '88888888-8888-4888-a888-888888888888', 'NexusCare Dilsukhnagar', 'NEX-HYD-008', 'East Hyderabad', 'Main Road, Dilsukhnagar', 'Hyderabad', 'Telangana', '500060', '+914024108899', 'dilsukhnagar@nexuscare.com', FALSE, 'active'),
    ('b9999999-9999-4999-9999-999999999999', '88888888-8888-4888-a888-888888888888', 'NexusCare Himayatnagar', 'NEX-HYD-009', 'Central Hyderabad', 'Himayatnagar Main Road', 'Hyderabad', 'Telangana', '500029', '+914024209900', 'himayatnagar@nexuscare.com', FALSE, 'active'),
    ('baaaaaaa-aaaa-4aaa-9aaa-aaaaaaaaaaaa', '88888888-8888-4888-a888-888888888888', 'NexusCare Kondapur', 'NEX-HYD-010', 'West Hyderabad', 'Botanical Garden Road, Kondapur', 'Hyderabad', 'Telangana', '500084', '+914024301111', 'kondapur@nexuscare.com', FALSE, 'active');

-- 3. Insert Branch Settings
INSERT INTO branch_settings (branch_id, inventory_control_mode, auto_transfer_enabled, pricing_override_allowed)
SELECT id, 'FEFO', TRUE, FALSE FROM branches;

-- 4. Install Roles (Ensured valid HEX UUIDs - starting with 'd' instead of 'r')
INSERT INTO roles (id, name, description) VALUES
    ('d1111111-1111-4111-a111-111111111111', 'CEO', 'Global network chief executive with full read access.'),
    ('d2222222-2222-4222-a222-222222222222', 'ADMIN', 'Superuser administrative coordinator.'),
    ('d3333333-3333-4333-a333-333333333333', 'BRANCH_MANAGER', 'Local branch manager responsible for location inventory, sales, and employee approvals.'),
    ('d4444444-4444-4444-a444-444444444444', 'PHARMACIST', 'Local branch pharmacist handling prescription audits and order creation.'),
    ('d5555555-5555-4555-a555-555555555555', 'FINANCE', 'Corporate accountant handling ledger reviews.'),
    ('d6666666-6666-4666-a666-666666666666', 'INVENTORY', 'Regional inventory manager coordinating inter-branch transfers.'),
    ('d7777777-7777-4777-a777-777777777777', 'CASHIER', 'Local branch cashier handling billing and POS checkouts.');

-- 5. Install basic permissions catalog
INSERT INTO permissions (code, name, description, category) VALUES
    ('org:view', 'View organization data', 'View company general profile', 'org'),
    ('org:edit', 'Edit organization data', 'Modify business identifiers', 'org'),
    ('inventory:view', 'View Inventory', 'Read stock lists', 'inventory'),
    ('inventory:write', 'Modify Inventory', 'Manually adjust quantities', 'inventory'),
    ('orders:create', 'Create Orders', 'Execute POS transactions', 'orders'),
    ('orders:view', 'View Orders', 'Inspect sales receipt history', 'orders'),
    ('transfers:initiate', 'Initiate Stock Transfer', 'Request items from adjacent branches', 'logistics'),
    ('transfers:approve', 'Approve Stock Transfer', 'Authorize inter-branch transfers', 'logistics');

-- Map permissions to CEO & Admin
INSERT INTO role_permissions (role_id, permission_id)
SELECT 'd1111111-1111-4111-a111-111111111111', id FROM permissions;

INSERT INTO role_permissions (role_id, permission_id)
SELECT 'd2222222-2222-4222-a222-222222222222', id FROM permissions;

-- Map basic permissions to Pharmacist
INSERT INTO role_permissions (role_id, permission_id)
SELECT 'd4444444-4444-4444-a444-444444444444', id FROM permissions WHERE code IN ('inventory:view', 'orders:create', 'orders:view');

-- Map basic permissions to Cashier
INSERT INTO role_permissions (role_id, permission_id)
SELECT 'd7777777-7777-4777-a777-777777777777', id FROM permissions WHERE code IN ('inventory:view', 'orders:create', 'orders:view');

-- 6. Insert Baseline Payment Methods
INSERT INTO payment_methods (id, name, is_active) VALUES
    (uuid_generate_v4(), 'Cash', TRUE),
    (uuid_generate_v4(), 'Credit Card', TRUE),
    (uuid_generate_v4(), 'UPI (GPay / PhonePe)', TRUE),
    (uuid_generate_v4(), 'Net Banking', TRUE);


-- ====================================================
-- SEED DATA PHASE 2: Procedural System Generation
-- ====================================================

-- DO block to seed 200 Employees, 500 Medicines, 100 Suppliers, 1000 Customers, 2000 Orders
DO $$
DECLARE
    -- Core arrays for synthetic generation
    first_names text[] := ARRAY['Anil', 'Sanjay', 'Rahul', 'Sunita', 'Pooja', 'Ramesh', 'Harish', 'Preethi', 'Kiran', 'Deepak', 'Vikram', 'Divya', 'Ganesh', 'Kavitha', 'Vijay', 'Jyothi', 'Rajesh', 'Sravani', 'Prasad', 'Madhavi'];
    last_names text[] := ARRAY['Reddy', 'Rao', 'Sharma', 'Verma', 'Goud', 'Naidu', 'Kumar', 'Joshi', 'Chawla', 'Deshmukh', 'Patel', 'Nair', 'Shetty', 'Bhat', 'Gupta', 'Singh', 'Choudhary', 'Sen', 'Pillai', 'Som'];
    
    med_cat_names text[] := ARRAY['Antibiotics', 'Analgesics', 'Antidiabetics', 'Cardiovascular', 'Respiratory', 'Gastrointestinal', 'Vitamins', 'Dermatology', 'Psychotropic', 'Antihistamines'];
    chemical_formulas text[] := ARRAY['Amoxicillin', 'Paracetamol', 'Metformin', 'Atorvastatin', 'Montelukast', 'Pantoprazole', 'Vitamin D3', 'Clobetasol', 'Alprazolam', 'Cetirizine'];
    brand_suffixes text[] := ARRAY['-250', '-500', ' Forte', ' Active', ' Ultra', ' D', ' Max', '-OD', ' Plus', ' Kid'];
    
    supplier_prefixes text[] := ARRAY['Astra', 'Novis', 'MedPlus', 'Hyderabad Pharma', 'Apex', 'Cipla Dist', 'Hetero Retail', 'Gland Wholesalers', 'Dr. Reddys Auth', 'Sun Distrib'];
    supplier_suffixes text[] := ARRAY['Logistics', 'Wholesale', 'Distributors', 'Pharma Agency', 'Enterprises'];

    -- DB UUID references
    v_org_id UUID := '88888888-8888-4888-a888-888888888888';
    v_branch_ids UUID[] := ARRAY[
        'b1111111-1111-4111-9111-111111111111'::UUID,
        'b2222222-2222-4222-9222-222222222222'::UUID,
        'b3333333-3333-4333-9333-333333333333'::UUID,
        'b4444444-4444-4444-9444-444444444444'::UUID,
        'b5555555-5555-4555-9555-555555555555'::UUID,
        'b6666666-6666-4666-9666-666666666666'::UUID,
        'b7777777-7777-4777-9777-777777777777'::UUID,
        'b8888888-8888-4888-9888-888888888888'::UUID,
        'b9999999-9999-4999-9999-999999999999'::UUID,
        'baaaaaaa-aaaa-4aaa-9aaa-aaaaaaaaaaaa'::UUID
    ];

    -- Generated ID arrays
    v_user_ids UUID[];
    v_employee_ids UUID[];
    v_med_cat_ids UUID[];
    v_manufacturer_ids UUID[];
    v_medicine_ids UUID[];
    v_batch_ids UUID[];
    v_supplier_ids UUID[];
    v_customer_ids UUID[];
    v_order_ids UUID[];
    v_payment_method_ids UUID[];

    -- Iteration variables
    i INT;
    j INT;
    temp_idx INT;
    temp_uuid UUID;
    temp_batch_uuid UUID;
    temp_price_uuid UUID;
    temp_inv_uuid UUID;

    -- Names and details construction
    v_f_name VARCHAR(100);
    v_l_name VARCHAR(100);
    v_email VARCHAR(255);
    v_phone VARCHAR(50);
    v_item_count INT;
    v_subtotal NUMERIC(12,2);
    v_total NUMERIC(12,2);
BEGIN

    -- Get payment methods in array
    SELECT array_agg(id) INTO v_payment_method_ids FROM payment_methods;

    -- 1. Create Base CEO and ADMIN Users
    INSERT INTO users (id, email, phone, branch_id, status)
    VALUES 
        ('99999999-9999-4999-b999-999999999999', 'ceo@nexuscare.com', '+919999999999', NULL, 'active')
    ON CONFLICT (id) DO NOTHING;
    
    INSERT INTO user_roles (user_id, role_id)
    VALUES ('99999999-9999-4999-b999-999999999999', 'd1111111-1111-4111-a111-111111111111')
    ON CONFLICT DO NOTHING;

    -- 2. Generate 200 Employees (and users mapping)
    FOR i IN 1..200 LOOP
        v_f_name := first_names[mod(i, 20) + 1];
        v_l_name := last_names[mod(i + 3, 20) + 1];
        v_email := lower(v_f_name || '.' || v_l_name || i || '@nexuscare.net');
        v_phone := '+9198480' || lpad(i::text, 5, '0');
        temp_uuid := uuid_generate_v4();

        -- Create User Profile
        INSERT INTO users (id, email, phone, branch_id, status)
        VALUES (temp_uuid, v_email, v_phone, v_branch_ids[mod(i, 10) + 1], 'active');

        -- Assign Branch Manager to the first employee per branch, cashier for index 11-50, pharmacists to others
        IF (i <= 10) THEN
            INSERT INTO user_roles (user_id, role_id) VALUES (temp_uuid, 'd3333333-3333-4333-a333-333333333333');
        ELSIF (i >= 11 AND i <= 50) THEN
            INSERT INTO user_roles (user_id, role_id) VALUES (temp_uuid, 'd7777777-7777-4777-a777-777777777777');
        ELSE
            INSERT INTO user_roles (user_id, role_id) VALUES (temp_uuid, 'd4444444-4444-4444-a444-444444444444');
        END IF;

        -- Create Employee Record
        INSERT INTO employees (id, user_id, branch_id, employee_id, first_name, last_name, status)
        VALUES (
            temp_uuid,
            temp_uuid,
            v_branch_ids[mod(i, 10) + 1],
            'EMP-' || lpad(i::text, 6, '0'),
            v_f_name,
            v_l_name,
            'active'
        );

        -- Add Employee profile and shifts
        INSERT INTO employee_profiles (employee_id, gender, date_of_birth, address, city, state, postal_code, hire_date)
        VALUES (temp_uuid, CASE WHEN mod(i, 2) = 0 THEN 'Female' ELSE 'Male' END, '1990-01-01'::DATE + (mod(i, 5000) * interval '1 day'), 'Street ' || i, 'Hyderabad', 'Telangana', '500034', '2024-01-01'::DATE);

        INSERT INTO employee_shifts (employee_id, day_of_week, start_time, end_time)
        VALUES (temp_uuid, mod(i, 6), '09:00:00'::TIME, '17:00:00'::TIME);

        v_user_ids := array_append(v_user_ids, temp_uuid);
    END LOOP;

    -- 3. Install 10 Medicine Categories
    FOR i IN 1..10 LOOP
        temp_uuid := uuid_generate_v4();
        INSERT INTO medicine_categories(id, name, description)
        VALUES (temp_uuid, med_cat_names[i], 'All meds classifying as ' || med_cat_names[i]);
        v_med_cat_ids := array_append(v_med_cat_ids, temp_uuid);
    END LOOP;

    -- 4. Generate Manufacturers (100)
    FOR i IN 1..100 LOOP
        temp_uuid := uuid_generate_v4();
        INSERT INTO manufacturers (id, name, code)
        VALUES (temp_uuid, 'Hyderabad Pharma Labs Ltd ' || i, 'HPL-' || lpad(i::text, 4, '0'));
        v_manufacturer_ids := array_append(v_manufacturer_ids, temp_uuid);
    END LOOP;

    -- 5. Generate 500 Medicines
    FOR i IN 1..500 LOOP
        temp_uuid := uuid_generate_v4();
        INSERT INTO medicines (
            id, category_id, manufacturer_id, sku, substance_name, brand_name, dosage_form, strength, requires_prescription
        ) VALUES (
            temp_uuid,
            v_med_cat_ids[mod(i, 10) + 1],
            v_manufacturer_ids[mod(i, 100) + 1],
            'SKU-NEX-' || lpad(i::text, 6, '0'),
            chemical_formulas[mod(i, 10) + 1],
            chemical_formulas[mod(i, 10) + 1] || brand_suffixes[mod(i, 10) + 1],
            CASE WHEN mod(i, 3) = 0 THEN 'Syrup' WHEN mod(i, 3) = 1 THEN 'Capsule' ELSE 'Tablet' END,
            CASE WHEN mod(i, 2) = 0 THEN '500mg' ELSE '250mg' END,
            CASE WHEN mod(i, 4) = 0 THEN TRUE ELSE FALSE END
        );
        v_medicine_ids := array_append(v_medicine_ids, temp_uuid);

        -- Generate two batches of stock for each medicine
        FOR j IN 1..2 LOOP
            temp_batch_uuid := uuid_generate_v4();
            INSERT INTO medicine_batches (id, medicine_id, batch_number, manufacturing_date, expiry_date)
            VALUES (
                temp_batch_uuid,
                temp_uuid,
                'BAT-' || i || '-' || j,
                CURRENT_DATE - (80 * j),
                -- Generate a specific set of critical expiries (less than 30 days) to demonstrate the AI trigger capabilities
                CASE 
                    WHEN (mod(i, 20) = 0 AND j = 1) THEN CURRENT_DATE + 22 -- 22 days expiry risk (High Risk)
                    ELSE CURRENT_DATE + (180 * j)
                END
            );
            v_batch_ids := array_append(v_batch_ids, temp_batch_uuid);

            -- Global standard pricing matching batch
            INSERT INTO medicine_prices (medicine_id, branch_id, mrp, purchase_price, discount_percentage, is_active)
            VALUES (
                temp_uuid,
                NULL,
                150.00 + (mod(i, 10) * 10),
                90.00 + (mod(i, 10) * 8),
                5.00,
                TRUE
            );
        END LOOP;
    END LOOP;

    -- 6. Generate 100 Suppliers
    FOR i IN 1..100 LOOP
        temp_uuid := uuid_generate_v4();
        INSERT INTO suppliers(id, name, code, credit_period_days, status)
        VALUES (
            temp_uuid,
            supplier_prefixes[mod(i, 10) + 1] || ' ' || supplier_suffixes[mod(i + 2, 5) + 1] || ' #' || i,
            'SUP-' || lpad(i::text, 4, '0'),
            30,
            'active'
        );
        v_supplier_ids := array_append(v_supplier_ids, temp_uuid);
    END LOOP;

    -- 7. Populate Realistic Inventory stock levels across 10 branches
    -- For each branch, seed stock for 200 random medicines
    FOR i IN 1..10 LOOP
        FOR j IN 1..200 LOOP
            -- pick a unique index to avoid conflict
            temp_idx := mod((i * j), 500) + 1;
            temp_uuid := v_medicine_ids[temp_idx];
            
            -- Insert inventory
            INSERT INTO inventory (id, branch_id, medicine_id, batch_id, quantity, reorder_level, max_level)
            VALUES (
                uuid_generate_v4(),
                v_branch_ids[i],
                temp_uuid,
                v_batch_ids[((temp_idx - 1) * 2) + 1], -- Link to first batch
                CASE 
                    -- force a stockout risk on Branch 4 for Amoxicillin SKU to demonstrate UI
                    WHEN (i = 4 AND temp_idx = 1) THEN 0
                    ELSE 150 + mod(i * j, 100)
                END,
                15,
                300
            ) ON CONFLICT (branch_id, batch_id) DO NOTHING;
        END LOOP;
    END LOOP;

    -- 8. Generate 1000 Customers
    FOR i IN 1..1000 LOOP
        temp_uuid := uuid_generate_v4();
        INSERT INTO customers (id, first_name, last_name, phone, email, loyalty_points)
        VALUES (
            temp_uuid,
            first_names[mod(i, 20) + 1],
            last_names[mod(i + 2, 20) + 1],
            '+919866' || lpad(i::text, 6, '0'),
            lower(first_names[mod(i, 20) + 1] || '.' || last_names[mod(i + 2, 20) + 1] || i || '@gmail.com'),
            mod(i * 10, 500)
        );
        v_customer_ids := array_append(v_customer_ids, temp_uuid);

        -- 10% of customers have active prescriptions
        IF (mod(i, 10) = 0) THEN
            INSERT INTO customer_prescriptions (id, customer_id, doctor_name, prescription_date, extracted_text)
            VALUES (
                uuid_generate_v4(),
                temp_uuid,
                'Dr. K. Srinivas Rao MD',
                CURRENT_DATE - 5,
                'Extracted Rx: Paracetamol 500mg, taking thrice daily for 3 days. Signed KSR.'
            );
        END IF;
    END LOOP;

    -- 9. Generate 2000 POS Sales Orders spanning 30 days
    FOR i IN 1..2000 LOOP
        temp_uuid := uuid_generate_v4();
        temp_idx := mod(i, 10) + 1; -- Determines target branch
        v_subtotal := 250.00 + (mod(i, 20) * 15.00);
        v_total := v_subtotal + 25.00;

        INSERT INTO orders (
            id, branch_id, customer_id, cashier_id, order_no, subtotal, tax_amount, discount_amount, total_amount, status, created_at
        ) VALUES (
            temp_uuid,
            v_branch_ids[temp_idx],
            v_customer_ids[mod(i, 1000) + 1],
            v_user_ids[mod(i, 200) + 1],
            'ORD-' || lpad(i::text, 8, '0'),
            v_subtotal,
            25.00,
            0.00,
            v_total,
            'completed',
            CURRENT_TIMESTAMP - (mod(i, 30)::text || ' days')::interval
        );
        v_order_ids := array_append(v_order_ids, temp_uuid);

        -- Add single item order trace
        INSERT INTO order_items (
            order_id, medicine_id, batch_id, quantity, unit_price, discount_percentage, tax_percentage, net_price
        ) VALUES (
            temp_uuid,
            v_medicine_ids[mod(i, 500) + 1],
            v_batch_ids[(mod(i, 500) * 2) + 1],
            1 + mod(i, 3),
            v_total,
            0.00,
            12.00,
            v_total
        );

        -- Payments record matching
        INSERT INTO payments (order_id, payment_method_id, amount, status, notes)
        VALUES (
            temp_uuid,
            v_payment_method_ids[mod(i, 4) + 1],
            v_total,
            'paid',
            'POS payment auto success'
        );

        -- Invoice record matching
        INSERT INTO invoices (order_id, branch_id, invoice_no, issue_date, total_tax, total_amount, status)
        VALUES (
            temp_uuid,
            v_branch_ids[temp_idx],
            'INV-NEX-' || lpad(i::text, 8, '0'),
            CURRENT_TIMESTAMP - (mod(i, 30)::text || ' days')::interval,
            25.00,
            v_total,
            'paid'
        );
    END LOOP;
END;
$$ LANGUAGE plpgsql;


-- ====================================================
-- SEED DATA PHASE 3: AI Agents, Telemetry & Logs
-- ====================================================

-- 1. AI Agents Statuses Initialized
INSERT INTO ai_agents (name, role, model_provider, model_name, system_instructions, state, latency_ms, flows_executed)
VALUES
    ('Regional AI Manager', 'Macro-Orchestrator', 'openai', 'gpt-4o', 'You are the Regional Manager orchestrating supply chains across 10 stores.', 'idle', 145, 1284),
    ('Branch AI (Banjara)', 'Local Triage Optimizer', 'openai', 'gpt-4o', 'Manage stockouts and staffing inside Banjara Hills Branch.', 'analyzing', 280, 4829),
    ('Inventory AI', 'Supply Chain FEFO Executor', 'openai', 'gpt-4o-mini', 'Eradicate expiry values at risk.', 'idle', 92, 9204),
    ('Sales AI', 'POS Semantic Query Parser', 'openai', 'gpt-4o', 'Help pharmacists search medicine records semantically.', 'idle', 110, 3140),
    ('Finance AI', 'Margin Leakage Guardian', 'openai', 'gpt-4o-mini', 'Monitor branch pricing overrides and detect margin leakages.', 'idle', 85, 1140);

-- 2. Insert active RAG Knowledge Documentation placeholders
INSERT INTO knowledge_documents (title, file_name, file_size, mime_type, storage_path, chunk_count)
VALUES
    ('Hyderabad Drug Licensing Regulation 2026', 'hyd_drug_licensing_2026.pdf', 142055, 'application/pdf', '/documents/licensing.pdf', 32),
    ('FEFO Stock Movement Guidelines', 'fefo_guidelines.md', 12050, 'text/markdown', '/documents/fefo.md', 5),
    ('NexusCare Pricing Discretion Rules v4', 'pricing_policy_v4.pdf', 89204, 'application/pdf', '/documents/pricing.pdf', 12);

-- 3. Insert specific active AI Recommendations to demonstrate inter-branch routing
INSERT INTO ai_recommendations (agent_id, branch_id, title, details, estimated_savings, confidence, is_applied)
VALUES
    (
        (SELECT id FROM ai_agents WHERE name = 'Regional AI Manager'),
        'b4444444-4444-4444-9444-444444444444', -- Gachibowli Target
        'Transfer Amoxicillin 500mg from Banjara Hills', 
        'Amoxicillin is stocked out in Gachibowli, while Banjara Hills holds excess, slow-moving inventory (80 units) expiring in 22 days. Transfer avoids write-off and serves existing deficit.', 
        2400.00, 
        95.00, 
        FALSE
    ),
    (
        (SELECT id FROM ai_agents WHERE name = 'Finance AI'),
        'b2222222-2222-4222-9222-222222222222', -- Jubilee Hills
        'Correct pricing leak on cough syrup', 
        'Revert manual pharmacist discount running 18% below corporate floor price.', 
        8500.00, 
        99.00, 
        FALSE
    );

-- 4. Generating Active System Notification indicators
INSERT INTO notifications (title, message, type, severity, is_read)
VALUES
    ('Amoxicillin Deficit Critical', 'Branch 4 (Gachibowli) inventory level reached 0 units. Patients turning away.', 'critical_alert', 'high', FALSE),
    ('AI Transfer Recommendation negotiated', 'Regional AI recommends transferring 80 units of Amoxicillin from Branch 1 to Branch 4. Awaiting Approval.', 'ai_trace', 'info', FALSE),
    ('Jubilee Hills Margin Leakage warning', 'Jubilee Hills branch discounting product 18% below safe floor price limits.', 'warning', 'medium', FALSE);
