-- Phase 8: Quotes & Invoices Schema
-- Version: 8.0
-- Date: 2025-10-07

-- Disable foreign key constraints temporarily
PRAGMA foreign_keys = OFF;

-- Drop existing tables if they exist
DROP TABLE IF EXISTS invoice_items;
DROP TABLE IF EXISTS invoices;
DROP TABLE IF EXISTS quote_items;
DROP TABLE IF EXISTS quotes;

-- Create quotes table
CREATE TABLE IF NOT EXISTS quotes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    quote_number VARCHAR(50) UNIQUE NOT NULL,
    project_id INTEGER,
    client_id INTEGER NOT NULL,
    quote_date DATE NOT NULL,
    valid_until DATE,
    status VARCHAR(50) NOT NULL DEFAULT 'Draft',
    subtotal DECIMAL(10, 2) NOT NULL DEFAULT 0,
    tax_rate DECIMAL(5, 2) DEFAULT 0,
    tax_amount DECIMAL(10, 2) DEFAULT 0,
    total_amount DECIMAL(10, 2) NOT NULL DEFAULT 0,
    notes TEXT,
    terms TEXT,
    created_by VARCHAR(100),
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Create quote_items table
CREATE TABLE IF NOT EXISTS quote_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    quote_id INTEGER NOT NULL,
    item_number INTEGER NOT NULL,
    description TEXT NOT NULL,
    quantity DECIMAL(10, 3) NOT NULL DEFAULT 1,
    unit_price DECIMAL(10, 2) NOT NULL,
    line_total DECIMAL(10, 2) NOT NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Create invoices table
CREATE TABLE IF NOT EXISTS invoices (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    invoice_number VARCHAR(50) UNIQUE NOT NULL,
    project_id INTEGER,
    client_id INTEGER NOT NULL,
    quote_id INTEGER,
    invoice_date DATE NOT NULL,
    due_date DATE,
    status VARCHAR(50) NOT NULL DEFAULT 'Draft',
    subtotal DECIMAL(10, 2) NOT NULL DEFAULT 0,
    tax_rate DECIMAL(5, 2) DEFAULT 0,
    tax_amount DECIMAL(10, 2) DEFAULT 0,
    total_amount DECIMAL(10, 2) NOT NULL DEFAULT 0,
    amount_paid DECIMAL(10, 2) DEFAULT 0,
    payment_terms VARCHAR(100),
    notes TEXT,
    created_by VARCHAR(100),
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Create invoice_items table
CREATE TABLE IF NOT EXISTS invoice_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    invoice_id INTEGER NOT NULL,
    item_number INTEGER NOT NULL,
    description TEXT NOT NULL,
    quantity DECIMAL(10, 3) NOT NULL DEFAULT 1,
    unit_price DECIMAL(10, 2) NOT NULL,
    line_total DECIMAL(10, 2) NOT NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_quotes_quote_number ON quotes(quote_number);
CREATE INDEX IF NOT EXISTS idx_quotes_client_id ON quotes(client_id);
CREATE INDEX IF NOT EXISTS idx_quotes_project_id ON quotes(project_id);
CREATE INDEX IF NOT EXISTS idx_quotes_status ON quotes(status);
CREATE INDEX IF NOT EXISTS idx_quotes_quote_date ON quotes(quote_date);

CREATE INDEX IF NOT EXISTS idx_quote_items_quote_id ON quote_items(quote_id);

CREATE INDEX IF NOT EXISTS idx_invoices_invoice_number ON invoices(invoice_number);
CREATE INDEX IF NOT EXISTS idx_invoices_client_id ON invoices(client_id);
CREATE INDEX IF NOT EXISTS idx_invoices_project_id ON invoices(project_id);
CREATE INDEX IF NOT EXISTS idx_invoices_status ON invoices(status);
CREATE INDEX IF NOT EXISTS idx_invoices_invoice_date ON invoices(invoice_date);
CREATE INDEX IF NOT EXISTS idx_invoices_due_date ON invoices(due_date);

CREATE INDEX IF NOT EXISTS idx_invoice_items_invoice_id ON invoice_items(invoice_id);

-- Update schema version
-- UPDATE settings SET value = '8.0' WHERE key = 'schema_version';

-- Insert quote and invoice settings
-- INSERT OR IGNORE INTO settings (key, value, description) VALUES ('quote_number_prefix', 'QT', 'Prefix for quote numbers');
-- INSERT OR IGNORE INTO settings (key, value, description) VALUES ('invoice_number_prefix', 'INV', 'Prefix for invoice numbers');
-- INSERT OR IGNORE INTO settings (key, value, description) VALUES ('default_tax_rate', '15.0', 'Default tax rate percentage');
-- INSERT OR IGNORE INTO settings (key, value, description) VALUES ('default_payment_terms', 'Net 30', 'Default payment terms');
-- INSERT OR IGNORE INTO settings (key, value, description) VALUES ('quote_validity_days', '30', 'Default quote validity period in days');

-- Re-enable foreign key constraints
PRAGMA foreign_keys = ON;

