-- Phase 3: SKU/Product Management Schema
-- Version: 3.0
-- Date: 2025-10-06

-- Create products/SKUs table
CREATE TABLE IF NOT EXISTS products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    sku_code VARCHAR(30) UNIQUE NOT NULL,
    name VARCHAR(200) NOT NULL,
    description TEXT,
    material VARCHAR(100),
    thickness DECIMAL(10, 3),
    unit_price DECIMAL(10, 2),
    notes TEXT,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_products_sku_code ON products(sku_code);
CREATE INDEX IF NOT EXISTS idx_products_name ON products(name);
CREATE INDEX IF NOT EXISTS idx_products_material ON products(material);
CREATE INDEX IF NOT EXISTS idx_products_created_at ON products(created_at);

-- Create project_products junction table (many-to-many relationship)
CREATE TABLE IF NOT EXISTS project_products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id INTEGER NOT NULL,
    product_id INTEGER NOT NULL,
    quantity INTEGER NOT NULL DEFAULT 1,
    unit_price DECIMAL(10, 2),
    notes TEXT,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE,
    UNIQUE(project_id, product_id)
);

-- Create indexes for junction table
CREATE INDEX IF NOT EXISTS idx_project_products_project_id ON project_products(project_id);
CREATE INDEX IF NOT EXISTS idx_project_products_product_id ON project_products(product_id);

-- Update schema version
UPDATE settings SET value = '3.0' WHERE key = 'schema_version';

-- Insert default materials if not exists
INSERT OR IGNORE INTO settings (key, value, description) VALUES
    ('default_materials', 'Mild Steel,Stainless Steel,Aluminum,Brass,Copper,Acrylic,Wood,MDF', 'Default material options for products'),
    ('default_thicknesses', '0.5,0.8,1.0,1.2,1.5,2.0,3.0,4.0,5.0,6.0,8.0,10.0', 'Default thickness options (mm) for products');

