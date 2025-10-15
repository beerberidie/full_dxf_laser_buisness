-- Laser OS Tier 1 - Database Schema v1
-- SQLite database schema for the laser cutting business automation system

-- Enable foreign keys
PRAGMA foreign_keys = ON;

-- ============================================================================
-- Schema Version Tracking
-- ============================================================================

CREATE TABLE IF NOT EXISTS schema_version (
    version TEXT PRIMARY KEY,
    applied_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================================
-- Clients
-- ============================================================================

CREATE TABLE IF NOT EXISTS clients (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    client_code TEXT UNIQUE NOT NULL,
    name TEXT NOT NULL,
    contact_person TEXT,
    email TEXT,
    phone TEXT,
    address TEXT,
    notes TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL
);

CREATE INDEX idx_clients_code ON clients(client_code);
CREATE INDEX idx_clients_name ON clients(name);

-- ============================================================================
-- Projects
-- ============================================================================

CREATE TABLE IF NOT EXISTS projects (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_code TEXT UNIQUE NOT NULL,
    client_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    status TEXT DEFAULT 'CREATED' NOT NULL,
    due_date DATE,
    sla_days INTEGER DEFAULT 3,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
    FOREIGN KEY (client_id) REFERENCES clients(id) ON DELETE CASCADE
);

CREATE INDEX idx_projects_code ON projects(project_code);
CREATE INDEX idx_projects_client ON projects(client_id);
CREATE INDEX idx_projects_status ON projects(status);
CREATE INDEX idx_projects_due_date ON projects(due_date);

-- ============================================================================
-- Design Files
-- ============================================================================

CREATE TABLE IF NOT EXISTS design_files (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id INTEGER NOT NULL,
    filename TEXT NOT NULL,
    original_filename TEXT NOT NULL,
    file_path TEXT NOT NULL,
    file_size INTEGER,
    file_type TEXT,
    part_name TEXT,
    material TEXT,
    thickness REAL,
    quantity INTEGER,
    bounding_box_width REAL,
    bounding_box_height REAL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
);

CREATE INDEX idx_files_project ON design_files(project_id);
CREATE INDEX idx_files_material ON design_files(material);

-- ============================================================================
-- Quotes
-- ============================================================================

CREATE TABLE IF NOT EXISTS quotes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id INTEGER NOT NULL,
    quote_number TEXT UNIQUE NOT NULL,
    total_amount REAL NOT NULL,
    notes TEXT,
    pdf_path TEXT,
    sent_date DATE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
);

CREATE INDEX idx_quotes_project ON quotes(project_id);
CREATE INDEX idx_quotes_number ON quotes(quote_number);

-- ============================================================================
-- Approvals
-- ============================================================================

CREATE TABLE IF NOT EXISTS approvals (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id INTEGER NOT NULL,
    approval_type TEXT NOT NULL,
    approved BOOLEAN DEFAULT 0,
    approved_date DATE,
    notes TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
);

CREATE INDEX idx_approvals_project ON approvals(project_id);
CREATE INDEX idx_approvals_type ON approvals(approval_type);

-- ============================================================================
-- Invoices
-- ============================================================================

CREATE TABLE IF NOT EXISTS invoices (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id INTEGER NOT NULL,
    invoice_number TEXT UNIQUE NOT NULL,
    amount REAL NOT NULL,
    paid BOOLEAN DEFAULT 0,
    paid_date DATE,
    pdf_path TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
);

CREATE INDEX idx_invoices_project ON invoices(project_id);
CREATE INDEX idx_invoices_number ON invoices(invoice_number);
CREATE INDEX idx_invoices_paid ON invoices(paid);

-- ============================================================================
-- Schedule Queue
-- ============================================================================

CREATE TABLE IF NOT EXISTS schedule_queue (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id INTEGER NOT NULL,
    position INTEGER NOT NULL,
    priority TEXT DEFAULT 'NORMAL',
    notes TEXT,
    added_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
);

CREATE INDEX idx_queue_position ON schedule_queue(position);
CREATE INDEX idx_queue_project ON schedule_queue(project_id);

-- ============================================================================
-- Laser Runs
-- ============================================================================

CREATE TABLE IF NOT EXISTS laser_runs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id INTEGER NOT NULL,
    start_time DATETIME,
    end_time DATETIME,
    duration_minutes INTEGER,
    material_used TEXT,
    gas_used TEXT,
    operator TEXT,
    notes TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
);

CREATE INDEX idx_runs_project ON laser_runs(project_id);
CREATE INDEX idx_runs_start_time ON laser_runs(start_time);

-- ============================================================================
-- Materials
-- ============================================================================

CREATE TABLE IF NOT EXISTS materials (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    material_type TEXT NOT NULL,
    thickness REAL NOT NULL,
    sheet_size TEXT,
    quantity INTEGER DEFAULT 0,
    cost_per_unit REAL,
    unit TEXT DEFAULT 'sheets',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL
);

CREATE INDEX idx_materials_type ON materials(material_type);
CREATE INDEX idx_materials_thickness ON materials(thickness);

-- ============================================================================
-- Inventory Events
-- ============================================================================

CREATE TABLE IF NOT EXISTS inventory_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    material_id INTEGER NOT NULL,
    event_type TEXT NOT NULL,
    quantity_change INTEGER NOT NULL,
    notes TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
    FOREIGN KEY (material_id) REFERENCES materials(id) ON DELETE CASCADE
);

CREATE INDEX idx_inventory_material ON inventory_events(material_id);
CREATE INDEX idx_inventory_type ON inventory_events(event_type);

-- ============================================================================
-- Activity Log
-- ============================================================================

CREATE TABLE IF NOT EXISTS activity_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    entity_type TEXT NOT NULL,
    entity_id INTEGER NOT NULL,
    action TEXT NOT NULL,
    user TEXT DEFAULT 'admin',
    details TEXT,
    ip_address TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL
);

CREATE INDEX idx_activity_entity ON activity_log(entity_type, entity_id);
CREATE INDEX idx_activity_user ON activity_log(user);
CREATE INDEX idx_activity_created ON activity_log(created_at);

-- ============================================================================
-- Settings
-- ============================================================================

CREATE TABLE IF NOT EXISTS settings (
    key TEXT PRIMARY KEY,
    value TEXT,
    description TEXT,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

