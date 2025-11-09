-- Migration: Add product_files table for product file uploads
-- Date: 2025-10-16
-- Description: Creates product_files table to store DXF and LightBurn files for products

-- Create product_files table
CREATE TABLE IF NOT EXISTS product_files (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    product_id INTEGER NOT NULL,
    original_filename VARCHAR(255) NOT NULL,
    stored_filename VARCHAR(255) NOT NULL,
    file_path VARCHAR(500) NOT NULL,
    file_size INTEGER NOT NULL,  -- in bytes
    file_type VARCHAR(50) DEFAULT 'dxf',  -- 'dxf' or 'lbrn2'
    upload_date DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    uploaded_by VARCHAR(100),
    notes TEXT,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE
);

-- Create indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_product_files_product_id ON product_files(product_id);
CREATE INDEX IF NOT EXISTS idx_product_files_upload_date ON product_files(upload_date);
CREATE INDEX IF NOT EXISTS idx_product_files_created_at ON product_files(created_at);

-- Verify table creation
SELECT 'product_files table created successfully' AS status;

