-- Phase 6: Inventory Management Schema
-- Version: 6.0
-- Date: 2025-10-07

-- Create inventory_items table
CREATE TABLE IF NOT EXISTS inventory_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    item_code VARCHAR(50) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    category VARCHAR(50) NOT NULL,
    material_type VARCHAR(100),
    thickness DECIMAL(10, 3),
    unit VARCHAR(20) NOT NULL,
    quantity_on_hand DECIMAL(10, 3) NOT NULL DEFAULT 0,
    reorder_level DECIMAL(10, 3) DEFAULT 0,
    reorder_quantity DECIMAL(10, 3),
    unit_cost DECIMAL(10, 2),
    supplier_name VARCHAR(255),
    supplier_contact VARCHAR(255),
    location VARCHAR(100),
    notes TEXT,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Create inventory_transactions table
CREATE TABLE IF NOT EXISTS inventory_transactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    inventory_item_id INTEGER NOT NULL,
    transaction_type VARCHAR(50) NOT NULL,
    quantity DECIMAL(10, 3) NOT NULL,
    unit_cost DECIMAL(10, 2),
    reference_type VARCHAR(50),
    reference_id INTEGER,
    transaction_date DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    performed_by VARCHAR(100),
    notes TEXT,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (inventory_item_id) REFERENCES inventory_items(id) ON DELETE CASCADE
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_inventory_items_item_code ON inventory_items(item_code);
CREATE INDEX IF NOT EXISTS idx_inventory_items_category ON inventory_items(category);
CREATE INDEX IF NOT EXISTS idx_inventory_items_material_type ON inventory_items(material_type);
CREATE INDEX IF NOT EXISTS idx_inventory_items_created_at ON inventory_items(created_at);

CREATE INDEX IF NOT EXISTS idx_inventory_transactions_item_id ON inventory_transactions(inventory_item_id);
CREATE INDEX IF NOT EXISTS idx_inventory_transactions_type ON inventory_transactions(transaction_type);
CREATE INDEX IF NOT EXISTS idx_inventory_transactions_date ON inventory_transactions(transaction_date);
CREATE INDEX IF NOT EXISTS idx_inventory_transactions_reference ON inventory_transactions(reference_type, reference_id);

-- Update schema version
UPDATE settings SET value = '6.0' WHERE key = 'schema_version';

-- Insert inventory management settings
INSERT OR IGNORE INTO settings (key, value, description) VALUES
    ('inventory_categories', 'Sheet Metal,Gas,Consumables,Tools,Other', 'Available inventory categories'),
    ('inventory_units', 'sheets,kg,liters,pieces,meters', 'Available inventory units'),
    ('low_stock_alert_enabled', 'true', 'Enable low stock alerts'),
    ('auto_deduct_inventory', 'false', 'Automatically deduct inventory on laser runs');

