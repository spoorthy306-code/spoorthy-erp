-- Spoorthy Quantum OS Database Seed Data
-- This file is loaded during database initialization

-- Insert GST rates
INSERT INTO gst_rates (hsn_code, description, cgst_rate, sgst_rate, igst_rate, cess_rate) VALUES
('996511', 'Financial leasing services', 9.00, 9.00, 18.00, 0.00),
('997212', 'Renting of residential dwellings', 9.00, 9.00, 18.00, 0.00),
('998311', 'IT consulting services', 9.00, 9.00, 18.00, 0.00),
('998313', 'Data processing services', 9.00, 9.00, 18.00, 0.00),
('998399', 'Other professional services', 9.00, 9.00, 18.00, 0.00);

-- Insert currencies
INSERT INTO currencies (code, name, symbol, decimal_places, is_base_currency) VALUES
('INR', 'Indian Rupee', '₹', 2, true),
('USD', 'US Dollar', '$', 2, false),
('EUR', 'Euro', '€', 2, false),
('GBP', 'British Pound', '£', 2, false);

-- Insert exchange rates (sample data)
INSERT INTO exchange_rates (from_currency, to_currency, rate, effective_date) VALUES
('USD', 'INR', 83.50, CURRENT_DATE),
('EUR', 'INR', 90.25, CURRENT_DATE),
('GBP', 'INR', 105.75, CURRENT_DATE);

-- Insert chart of accounts
INSERT INTO chart_of_accounts (account_code, account_name, account_type, category, subcategory, is_active) VALUES
-- Assets
('1001001', 'Cash in Hand', 'asset', 'current_asset', 'cash_and_bank', true),
('1001002', 'Bank Account - HDFC', 'asset', 'current_asset', 'cash_and_bank', true),
('1001003', 'Bank Account - SBI', 'asset', 'current_asset', 'cash_and_bank', true),
('1002001', 'Accounts Receivable', 'asset', 'current_asset', 'receivables', true),
('1003001', 'Inventory - Raw Materials', 'asset', 'current_asset', 'inventory', true),
('1003002', 'Inventory - Work in Progress', 'asset', 'current_asset', 'inventory', true),
('1003003', 'Inventory - Finished Goods', 'asset', 'current_asset', 'inventory', true),
('1004001', 'Prepaid Expenses', 'asset', 'current_asset', 'prepaid', true),
('2001001', 'Buildings', 'asset', 'fixed_asset', 'property', true),
('2001002', 'Computers & Software', 'asset', 'fixed_asset', 'equipment', true),
('2001003', 'Furniture & Fixtures', 'asset', 'fixed_asset', 'equipment', true),
('2001004', 'Vehicles', 'asset', 'fixed_asset', 'equipment', true),

-- Liabilities
('3001001', 'Accounts Payable', 'liability', 'current_liability', 'payables', true),
('3002001', 'GST Payable', 'liability', 'current_liability', 'taxes', true),
('3002002', 'TDS Payable', 'liability', 'current_liability', 'taxes', true),
('3003001', 'Short-term Loans', 'liability', 'current_liability', 'loans', true),
('4001001', 'Long-term Loans', 'liability', 'non_current_liability', 'loans', true),

-- Equity
('5001001', 'Share Capital', 'equity', 'equity', 'capital', true),
('5001002', 'Retained Earnings', 'equity', 'equity', 'reserves', true),

-- Income
('6001001', 'Sales Revenue', 'income', 'operating_income', 'sales', true),
('6001002', 'Service Revenue', 'income', 'operating_income', 'services', true),
('6002001', 'Interest Income', 'income', 'other_income', 'interest', true),
('6002002', 'Other Income', 'income', 'other_income', 'misc', true),

-- Expenses
('7001001', 'Cost of Goods Sold', 'expense', 'cost_of_sales', 'direct_costs', true),
('7002001', 'Salaries & Wages', 'expense', 'operating_expense', 'personnel', true),
('7002002', 'Rent Expense', 'expense', 'operating_expense', 'overhead', true),
('7002003', 'Utilities', 'expense', 'operating_expense', 'overhead', true),
('7002004', 'Professional Fees', 'expense', 'operating_expense', 'professional', true),
('7003001', 'Depreciation Expense', 'expense', 'non_operating_expense', 'depreciation', true),
('7003002', 'Interest Expense', 'expense', 'non_operating_expense', 'interest', true),
('7003003', 'GST Expense', 'expense', 'non_operating_expense', 'taxes', true);

-- Insert entities (sample companies)
INSERT INTO entities (entity_name, gstin, pan, address, city, state, pincode, phone, email, business_type, incorporation_date, status) VALUES
('Spoorthy Technologies Pvt Ltd', '27AABCS1234C1Z1', 'AABCS1234C', '123 Business District', 'Mumbai', 'Maharashtra', '400001', '+91-22-1234-5678', 'accounts@spoorthy.com', 'Private Limited Company', '2020-04-01', 'active'),
('Spoorthy Solutions LLP', '27AABCS5678D2Y2', 'AABCS5678D', '456 Tech Park', 'Pune', 'Maharashtra', '411001', '+91-20-2345-6789', 'finance@spoorthy-solutions.com', 'Limited Liability Partnership', '2021-07-15', 'active'),
('Quantum Innovations India Pvt Ltd', '27AABCS9012E3X3', 'AABCS9012E', '789 Innovation Hub', 'Bangalore', 'Karnataka', '560001', '+91-80-3456-7890', 'admin@quantum-india.com', 'Private Limited Company', '2022-01-10', 'active');

-- Insert sample journal entries for April 2024
INSERT INTO journal_entries (entry_date, reference_number, description, entry_type, period, created_by) VALUES
('2024-04-01', 'JE-2024-0001', 'Opening cash balance', 'manual', '2024-04', 'system'),
('2024-04-01', 'JE-2024-0002', 'Share capital contribution', 'manual', '2024-04', 'system'),
('2024-04-05', 'JE-2024-0003', 'Office rent payment', 'manual', '2024-04', 'system'),
('2024-04-10', 'JE-2024-0004', 'Software license purchase', 'manual', '2024-04', 'system'),
('2024-04-15', 'JE-2024-0005', 'Client payment received', 'manual', '2024-04', 'system'),
('2024-04-20', 'JE-2024-0006', 'Salary payments', 'manual', '2024-04', 'system'),
('2024-04-25', 'JE-2024-0007', 'GST payment', 'manual', '2024-04', 'system'),
('2024-04-30', 'JE-2024-0008', 'Monthly depreciation', 'auto', '2024-04', 'system');

-- Insert journal entry lines
INSERT INTO journal_entry_lines (journal_entry_id, account_code, debit_amount, credit_amount, description, entity_id) VALUES
-- Opening cash balance
(1, '1001001', 500000.00, 0.00, 'Opening cash balance', 1),
(1, '5001001', 0.00, 500000.00, 'Opening cash balance', 1),

-- Share capital
(2, '1001001', 2000000.00, 0.00, 'Share capital contribution', 1),
(2, '5001001', 0.00, 2000000.00, 'Share capital contribution', 1),

-- Office rent
(3, '7002002', 50000.00, 0.00, 'Monthly office rent', 1),
(3, '1001002', 0.00, 50000.00, 'Monthly office rent', 1),

-- Software license
(4, '2001002', 250000.00, 0.00, 'Software license purchase', 1),
(4, '1001002', 0.00, 250000.00, 'Software license purchase', 1),

-- Client payment
(5, '1001002', 750000.00, 0.00, 'Client project payment', 1),
(5, '6001001', 0.00, 750000.00, 'Client project payment', 1),

-- Salaries
(6, '7002001', 300000.00, 0.00, 'Monthly salaries', 1),
(6, '1001002', 0.00, 300000.00, 'Monthly salaries', 1),

-- GST payment
(7, '3002001', 45000.00, 0.00, 'GST payment', 1),
(7, '1001002', 0.00, 45000.00, 'GST payment', 1),

-- Depreciation
(8, '7003001', 12500.00, 0.00, 'Monthly depreciation', 1),
(8, '2001002', 0.00, 12500.00, 'Monthly depreciation', 1);

-- Insert fixed assets
INSERT INTO fixed_assets (asset_code, asset_name, asset_category, purchase_date, purchase_cost, accumulated_depreciation, useful_life_years, depreciation_method, location, entity_id) VALUES
('COMP-001', 'Dell Laptop', 'Computer Equipment', '2023-01-15', 85000.00, 17000.00, 5, 'straight_line', 'Mumbai Office', 1),
('COMP-002', 'HP Desktop', 'Computer Equipment', '2023-03-20', 65000.00, 13000.00, 5, 'straight_line', 'Mumbai Office', 1),
('VEH-001', 'Toyota Innova', 'Vehicles', '2022-06-10', 1500000.00, 300000.00, 8, 'straight_line', 'Mumbai Office', 1),
('FURN-001', 'Office Furniture Set', 'Furniture', '2023-08-05', 200000.00, 40000.00, 10, 'straight_line', 'Mumbai Office', 1);

-- Insert inventory items
INSERT INTO inventory_items (item_code, item_name, item_category, unit_of_measure, current_stock, reorder_point, unit_cost, selling_price, hsn_code, gst_rate, entity_id) VALUES
('RAW-001', 'Steel Sheets', 'Raw Materials', 'Kg', 500.00, 100.00, 150.00, 180.00, '7208', 18.00, 1),
('RAW-002', 'Aluminum Rods', 'Raw Materials', 'Kg', 300.00, 75.00, 200.00, 240.00, '7604', 18.00, 1),
('FG-001', 'Finished Component A', 'Finished Goods', 'Piece', 150.00, 25.00, 500.00, 650.00, '8473', 18.00, 1),
('FG-002', 'Finished Component B', 'Finished Goods', 'Piece', 200.00, 30.00, 750.00, 950.00, '8473', 18.00, 1);

-- Insert customers
INSERT INTO customers (customer_code, customer_name, gstin, pan, address, city, state, pincode, phone, email, credit_limit, payment_terms, entity_id) VALUES
('CUST-001', 'TechCorp India Pvt Ltd', '27AAACT1234F1Z1', 'AAACT1234F', '123 Tech Street', 'Mumbai', 'Maharashtra', '400002', '+91-22-9876-5432', 'billing@techcorp.com', 1000000.00, 'Net 30', 1),
('CUST-002', 'Global Solutions Ltd', '27AAAAG5678G2Y2', 'AAAAG5678G', '456 Business Ave', 'Delhi', 'Delhi', '110001', '+91-11-8765-4321', 'accounts@globalsolutions.com', 500000.00, 'Net 15', 1),
('CUST-003', 'Innovate Systems', '27AAAAI9012H3X3', 'AAAAI9012H', '789 Innovation Rd', 'Bangalore', 'Karnataka', '560002', '+91-80-7654-3210', 'finance@innovatesystems.com', 750000.00, 'Net 30', 1);

-- Insert vendors
INSERT INTO vendors (vendor_code, vendor_name, gstin, pan, address, city, state, pincode, phone, email, payment_terms, entity_id) VALUES
('VEND-001', 'Office Supplies Co', '27AAAAS1234J1Z1', 'AAAAS1234J', '321 Supply Lane', 'Mumbai', 'Maharashtra', '400003', '+91-22-6543-2109', 'sales@officesupplies.com', 'Net 30', 1),
('VEND-002', 'Tech Hardware Ltd', '27AAAAT5678K2Y2', 'AAAAT5678K', '654 Hardware St', 'Pune', 'Maharashtra', '411002', '+91-20-5432-1098', 'orders@techhardware.com', 'Net 15', 1),
('VEND-003', 'Software Solutions Inc', '27AAAAU9012L3X3', 'AAAAU9012L', '987 Software Blvd', 'Hyderabad', 'Telangana', '500001', '+91-40-4321-0987', 'support@softwaresolutions.com', 'Net 30', 1);

-- Insert sample invoices
INSERT INTO invoices (invoice_number, invoice_date, due_date, customer_id, entity_id, total_amount, tax_amount, discount_amount, status, invoice_type) VALUES
('INV-2024-0001', '2024-04-01', '2024-05-01', 1, 1, 118000.00, 18000.00, 0.00, 'paid', 'sales'),
('INV-2024-0002', '2024-04-10', '2024-05-10', 2, 1, 236000.00, 36000.00, 0.00, 'sent', 'sales'),
('INV-2024-0003', '2024-04-15', '2024-05-15', 3, 1, 177000.00, 27000.00, 0.00, 'overdue', 'sales');

-- Insert invoice lines
INSERT INTO invoice_lines (invoice_id, item_code, description, quantity, unit_price, discount_percent, gst_rate, line_total) VALUES
(1, 'FG-001', 'Finished Component A', 100.00, 650.00, 0.00, 18.00, 65000.00),
(1, 'FG-002', 'Finished Component B', 50.00, 950.00, 0.00, 18.00, 47500.00),
(1, null, 'Installation Services', 1.00, 5000.00, 0.00, 18.00, 5000.00),
(2, 'FG-001', 'Finished Component A', 200.00, 650.00, 5.00, 18.00, 123500.00),
(2, 'FG-002', 'Finished Component B', 100.00, 950.00, 5.00, 18.00, 90250.00),
(3, 'FG-001', 'Finished Component A', 150.00, 650.00, 0.00, 18.00, 97500.00),
(3, null, 'Consulting Services', 1.00, 75000.00, 0.00, 18.00, 75000.00);

-- Insert GST returns (sample data)
INSERT INTO gst_returns (return_type, period, entity_id, status, total_taxable_value, total_igst, total_cgst, total_sgst, total_cess, filing_date) VALUES
('GSTR-1', '032024', 1, 'filed', 531000.00, 0.00, 47790.00, 47790.00, 0.00, '2024-04-20'),
('GSTR-3B', '032024', 1, 'filed', 531000.00, 0.00, 47790.00, 47790.00, 0.00, '2024-04-25');

-- Insert GST return details
INSERT INTO gst_return_details (gst_return_id, hsn_code, description, uqc, total_quantity, taxable_value, igst_rate, igst_amount, cgst_rate, cgst_amount, sgst_rate, sgst_amount, cess_rate, cess_amount) VALUES
(1, '8473', 'Finished Components', 'PCS', 450.00, 393000.00, 0.00, 0.00, 9.00, 35370.00, 9.00, 35370.00, 0.00, 0.00),
(1, '998311', 'IT Consulting Services', 'OTH', 2.00, 125000.00, 0.00, 0.00, 9.00, 11250.00, 9.00, 11250.00, 0.00, 0.00),
(1, '998399', 'Installation Services', 'OTH', 1.00, 13000.00, 0.00, 0.00, 9.00, 1170.00, 9.00, 1170.00, 0.00, 0.00);

-- Insert quantum jobs (sample completed jobs)
INSERT INTO quantum_jobs (job_type, status, input_data, result_data, execution_time_seconds, speedup_factor, created_at, completed_at) VALUES
('reconciliation', 'completed', '{"transactions": 150, "tolerance": 0.01}', '{"matched": 142, "unmatched": 8, "accuracy": 94.67}', 1.25, 2.3, '2024-04-01 10:00:00', '2024-04-01 10:00:01'),
('forecasting', 'completed', '{"periods": 12, "data_points": 24}', '{"forecast_accuracy": 92.5, "confidence": 0.95}', 3.75, 3.8, '2024-04-05 14:30:00', '2024-04-05 14:30:04'),
('risk_analysis', 'completed', '{"assets": 25, "simulations": 10000}', '{"var_95": -12.5, "expected_return": 8.75}', 8.50, 15.2, '2024-04-10 16:45:00', '2024-04-10 16:45:09');

-- Insert users (sample users with hashed passwords)
-- Passwords are hashed versions of 'password123'
INSERT INTO users (username, email, full_name, password_hash, role, is_active, entity_id, created_at) VALUES
('admin', 'admin@spoorthy.com', 'System Administrator', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LeCt1uAjhZzX8IwCe', 'admin', true, 1, CURRENT_TIMESTAMP),
('accountant', 'accountant@spoorthy.com', 'Senior Accountant', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LeCt1uAjhZzX8IwCe', 'accountant', true, 1, CURRENT_TIMESTAMP),
('auditor', 'auditor@spoorthy.com', 'External Auditor', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LeCt1uAjhZzX8IwCe', 'auditor', true, 1, CURRENT_TIMESTAMP);

-- Insert API keys (sample keys for external integrations)
INSERT INTO api_keys (key_name, key_value, permissions, expires_at, created_by, entity_id) VALUES
('gstn_integration', 'gstn_key_123456789', '["gst:read", "gst:write"]', '2025-03-31 23:59:59', 'admin', 1),
('rbi_fx_rates', 'rbi_key_987654321', '["fx:read"]', '2025-03-31 23:59:59', 'admin', 1),
('quantum_engine', 'quantum_key_abcdef123', '["quantum:execute"]', '2025-03-31 23:59:59', 'admin', 1);

-- Insert audit log (sample entries)
INSERT INTO audit_log (user_id, action, resource_type, resource_id, old_values, new_values, ip_address, user_agent, timestamp) VALUES
(1, 'CREATE', 'journal_entry', '1', null, '{"amount": 500000, "description": "Opening cash balance"}', '127.0.0.1', 'System/1.0', '2024-04-01 09:00:00'),
(1, 'CREATE', 'invoice', '1', null, '{"customer": "TechCorp India", "amount": 118000}', '127.0.0.1', 'System/1.0', '2024-04-01 10:30:00'),
(2, 'UPDATE', 'customer', '1', '{"credit_limit": 500000}', '{"credit_limit": 1000000}', '192.168.1.100', 'Mozilla/5.0', '2024-04-05 14:20:00');

-- Insert compliance checks (sample results)
INSERT INTO compliance_checks (check_type, entity_id, period, status, check_date, details, remediation_required) VALUES
('gst_filing', 1, '032024', 'passed', '2024-04-25', '{"gstr1_filed": true, "gstr3b_filed": true, "due_date": "2024-04-20"}', false),
('tds_deduction', 1, '032024', 'passed', '2024-04-30', '{"tds_deducted": 15000, "tds_deposited": 15000}', false),
('audit_trail', 1, '032024', 'passed', '2024-04-30', '{"entries_audited": 8, "modifications_logged": 8}', false);