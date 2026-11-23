-- =============================================================================
-- SYSTEM ARCHITECTURE: ZNS / Defense Force Mess Hall Logistics Engine
-- DATABASE: military_food_db (REALISTIC SHELF-LIFE & HEADCOUNT LOGGING)
-- =============================================================================

DROP TABLE IF EXISTS demand_forecasts CASCADE;
DROP TABLE IF EXISTS inventory_batches CASCADE;
DROP TABLE IF EXISTS food_items CASCADE;
DROP TABLE IF EXISTS suppliers CASCADE;
DROP TABLE IF EXISTS operational_schedules CASCADE;

-- 1. Suppliers Table
CREATE TABLE suppliers (
    id SERIAL PRIMARY KEY,
    supplier_name VARCHAR(150) NOT NULL,
    contact_person VARCHAR(100),
    phone VARCHAR(30),
    category VARCHAR(50)
);

-- 2. Master Food Items & Nutritional Metadata
CREATE TABLE food_items (
    id SERIAL PRIMARY KEY,
    item_code VARCHAR(20) UNIQUE NOT NULL,
    item_name VARCHAR(100) NOT NULL,
    unit_of_measure VARCHAR(20) NOT NULL,
    category VARCHAR(50) NOT NULL, -- Fresh Produce, Perishable, Dry Rations, Bulk Rations
    min_safety_stock NUMERIC(10,2) DEFAULT 50.00,
    calories_per_unit NUMERIC(10,2) DEFAULT 0.00
);

-- 3. Inventory Batches with Explicit Purchase & Expiry Auditing
CREATE TABLE inventory_batches (
    id SERIAL PRIMARY KEY,
    food_item_id INT REFERENCES food_items(id) ON DELETE CASCADE,
    supplier_id INT REFERENCES suppliers(id) ON DELETE SET NULL,
    batch_number VARCHAR(50) NOT NULL,
    quantity_received NUMERIC(10,2) NOT NULL,
    current_quantity NUMERIC(10,2) NOT NULL,
    unit_cost NUMERIC(10,2) NOT NULL,
    date_purchased DATE NOT NULL,
    expiry_date DATE NOT NULL
);

-- 4. Operational Schedules & Personnel Headcount Logs
CREATE TABLE operational_schedules (
    id SERIAL PRIMARY KEY,
    log_date DATE UNIQUE NOT NULL,
    headcount INT NOT NULL,
    is_training_exercise INT DEFAULT 0,
    avg_temperature NUMERIC(4,1) DEFAULT 25.0,
    caloric_target_kcal INT DEFAULT 3000
);

-- 5. AI Machine Learning Demand Forecast Logs (Includes Headcount)
CREATE TABLE demand_forecasts (
    id SERIAL PRIMARY KEY,
    forecast_date DATE NOT NULL,
    food_item_id INT REFERENCES food_items(id) ON DELETE CASCADE,
    headcount INT NOT NULL DEFAULT 1000,
    predicted_demand_kg NUMERIC(10,2) NOT NULL,
    model_used VARCHAR(50) DEFAULT 'Ridge Regression',
    generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Master Commodity Seed Data
INSERT INTO food_items (item_code, item_name, unit_of_measure, category, min_safety_stock, calories_per_unit) VALUES
('RKN-001', 'Green Vegetables (Rape / Chinese / Spinach)', 'kg', 'Fresh Produce', 30.00, 250.00),
('RKN-002', 'Tomatoes (Fresh Harvest)', 'kg', 'Fresh Produce', 40.00, 180.00),
('RKN-003', 'Onions (Bulb)', 'kg', 'Fresh Produce', 50.00, 400.00),
('RKN-004', 'Garlic (Dry Bulb)', 'kg', 'Fresh Produce', 15.00, 1490.00),
('RKN-005', 'Fresh Fish (Refrigerated)', 'kg', 'Perishable', 60.00, 2060.00),
('RKN-006', 'Kapenta (Dry Rations)', 'kg', 'Semi-Perishable', 50.00, 3200.00),
('RKN-007', 'Beef Carcass (Cold Storage)', 'kg', 'Perishable', 100.00, 2500.00),
('RKN-008', 'Chicken / Pork (Cold Storage)', 'kg', 'Perishable', 80.00, 2390.00),
('RKN-009', 'Rice (White Grain)', 'kg', 'Bulk Rations', 200.00, 1300.00),
('RKN-010', 'Cooking Oil (Bulk Containers)', 'liters', 'Bulk Rations', 150.00, 8840.00),
('RKN-011', 'Breakfast Meal (Mealie Meal)', 'kg', 'Bulk Rations', 300.00, 3600.00);

-- Supplier Seed Data
INSERT INTO suppliers (supplier_name, contact_person, phone, category) VALUES
('ZNS Production Units (National Supply)', 'Major B. Phiri', '+260 977 123 456', 'Bulk Rations'),
('Lusaka Livestock & Meat Co-op', 'Capt. M. Tembo', '+260 966 987 654', 'Meat & Cold Storage'),
('Chongwe Green Farms & Produce', 'Lt. C. Banda', '+260 955 444 333', 'Fresh Produce');