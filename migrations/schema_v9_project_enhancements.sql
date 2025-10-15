-- ============================================================================
-- Laser OS - Phase 9: Project Enhancements & Communications Module
-- ============================================================================
-- Version: 9.0
-- Description: Adds enhanced project tracking, POP management, and communications
-- Dependencies: Requires all previous migrations (v1-v8)
-- ============================================================================

-- ============================================================================
-- PART 1: PROJECT TABLE ENHANCEMENTS
-- ============================================================================

-- Add new columns to projects table for enhanced tracking
ALTER TABLE projects ADD COLUMN material_type VARCHAR(100);
ALTER TABLE projects ADD COLUMN material_quantity_sheets INTEGER;
ALTER TABLE projects ADD COLUMN parts_quantity INTEGER;
ALTER TABLE projects ADD COLUMN estimated_cut_time INTEGER; -- in minutes
ALTER TABLE projects ADD COLUMN number_of_bins INTEGER;
ALTER TABLE projects ADD COLUMN drawing_creation_time INTEGER; -- in minutes

-- Add POP (Proof of Payment) tracking columns
ALTER TABLE projects ADD COLUMN pop_received BOOLEAN DEFAULT 0;
ALTER TABLE projects ADD COLUMN pop_received_date DATE;
ALTER TABLE projects ADD COLUMN pop_deadline DATE; -- Auto-calculated: POP date + 3 days

-- Add client notification tracking
ALTER TABLE projects ADD COLUMN client_notified BOOLEAN DEFAULT 0;
ALTER TABLE projects ADD COLUMN client_notified_date DATETIME;

-- Add delivery confirmation tracking
ALTER TABLE projects ADD COLUMN delivery_confirmed BOOLEAN DEFAULT 0;
ALTER TABLE projects ADD COLUMN delivery_confirmed_date DATE;

-- Add scheduling column
ALTER TABLE projects ADD COLUMN scheduled_cut_date DATE;

-- Create indexes for new columns (performance optimization)
CREATE INDEX IF NOT EXISTS idx_projects_material_type ON projects(material_type);
CREATE INDEX IF NOT EXISTS idx_projects_pop_received ON projects(pop_received);
CREATE INDEX IF NOT EXISTS idx_projects_scheduled_cut_date ON projects(scheduled_cut_date);
CREATE INDEX IF NOT EXISTS idx_projects_pop_deadline ON projects(pop_deadline);

-- ============================================================================
-- PART 2: PROJECT DOCUMENTS TABLE (NEW)
-- ============================================================================
-- Separate table for project documents (Quote, Invoice, POP, Delivery Note)
-- This keeps design_files table focused on DXF files only

CREATE TABLE IF NOT EXISTS project_documents (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id INTEGER NOT NULL,
    document_type VARCHAR(50) NOT NULL, -- 'Quote', 'Invoice', 'Proof of Payment', 'Delivery Note'
    original_filename VARCHAR(255) NOT NULL,
    stored_filename VARCHAR(255) NOT NULL,
    file_path VARCHAR(500) NOT NULL,
    file_size INTEGER NOT NULL,
    upload_date DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    uploaded_by VARCHAR(100),
    
    -- Future: Quote parsing capabilities
    is_parsed BOOLEAN DEFAULT 0,
    parsed_data TEXT, -- JSON format for extracted data
    
    notes TEXT,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    
    -- Foreign Keys
    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE,
    
    -- Constraints
    CHECK (document_type IN ('Quote', 'Invoice', 'Proof of Payment', 'Delivery Note'))
);

-- Indexes for project_documents
CREATE INDEX IF NOT EXISTS idx_project_documents_project_id ON project_documents(project_id);
CREATE INDEX IF NOT EXISTS idx_project_documents_document_type ON project_documents(document_type);
CREATE INDEX IF NOT EXISTS idx_project_documents_upload_date ON project_documents(upload_date);

-- ============================================================================
-- PART 3: COMMUNICATIONS TABLE (NEW)
-- ============================================================================
-- Unified communication hub for Email, WhatsApp, and Notifications

CREATE TABLE IF NOT EXISTS communications (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    
    -- Communication metadata
    comm_type VARCHAR(20) NOT NULL, -- 'Email', 'WhatsApp', 'Notification'
    direction VARCHAR(10) NOT NULL, -- 'Inbound', 'Outbound'
    
    -- Linking to clients and projects
    client_id INTEGER,
    project_id INTEGER,
    
    -- Message content
    subject VARCHAR(500),
    body TEXT,
    from_address VARCHAR(255), -- Email or phone number
    to_address VARCHAR(255), -- Email or phone number
    
    -- Status tracking
    status VARCHAR(50) DEFAULT 'Pending', -- 'Pending', 'Sent', 'Delivered', 'Failed', 'Read'
    sent_at DATETIME,
    received_at DATETIME,
    read_at DATETIME,
    
    -- Attachments and linking
    has_attachments BOOLEAN DEFAULT 0,
    is_linked BOOLEAN DEFAULT 0, -- Whether successfully linked to client/project

    -- Additional metadata (JSON format)
    comm_metadata TEXT, -- For storing additional data like message IDs, thread IDs, etc.
    
    -- Timestamps
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    
    -- Foreign Keys
    FOREIGN KEY (client_id) REFERENCES clients(id) ON DELETE SET NULL,
    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE SET NULL,
    
    -- Constraints
    CHECK (comm_type IN ('Email', 'WhatsApp', 'Notification')),
    CHECK (direction IN ('Inbound', 'Outbound')),
    CHECK (status IN ('Pending', 'Sent', 'Delivered', 'Failed', 'Read'))
);

-- Indexes for communications
CREATE INDEX IF NOT EXISTS idx_communications_client_id ON communications(client_id);
CREATE INDEX IF NOT EXISTS idx_communications_project_id ON communications(project_id);
CREATE INDEX IF NOT EXISTS idx_communications_comm_type ON communications(comm_type);
CREATE INDEX IF NOT EXISTS idx_communications_is_linked ON communications(is_linked);
CREATE INDEX IF NOT EXISTS idx_communications_created_at ON communications(created_at);
CREATE INDEX IF NOT EXISTS idx_communications_status ON communications(status);

-- ============================================================================
-- PART 4: COMMUNICATION ATTACHMENTS TABLE (NEW)
-- ============================================================================
-- Attachments for communications (emails, etc.)

CREATE TABLE IF NOT EXISTS communication_attachments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    communication_id INTEGER NOT NULL,
    original_filename VARCHAR(255) NOT NULL,
    stored_filename VARCHAR(255) NOT NULL,
    file_path VARCHAR(500) NOT NULL,
    file_size INTEGER NOT NULL,
    file_type VARCHAR(50),
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    
    -- Foreign Keys
    FOREIGN KEY (communication_id) REFERENCES communications(id) ON DELETE CASCADE
);

-- Indexes for communication_attachments
CREATE INDEX IF NOT EXISTS idx_comm_attachments_communication_id ON communication_attachments(communication_id);

-- ============================================================================
-- PART 5: DATA MIGRATION FOR EXISTING PROJECTS
-- ============================================================================
-- Update existing projects to have default values for new fields

-- Set default values for boolean fields (already have DEFAULT 0 in ALTER TABLE)
UPDATE projects SET pop_received = 0 WHERE pop_received IS NULL;
UPDATE projects SET client_notified = 0 WHERE client_notified IS NULL;
UPDATE projects SET delivery_confirmed = 0 WHERE delivery_confirmed IS NULL;

-- ============================================================================
-- PART 6: UPDATE SCHEMA VERSION
-- ============================================================================

UPDATE settings SET value = '9.0', updated_at = CURRENT_TIMESTAMP 
WHERE key = 'schema_version';

-- ============================================================================
-- PART 7: ACTIVITY LOG ENTRIES FOR MIGRATION
-- ============================================================================

INSERT INTO activity_log (entity_type, entity_id, action, details, created_at)
VALUES ('SYSTEM', 0, 'MIGRATION', 'Applied schema v9.0: Project enhancements and communications module', CURRENT_TIMESTAMP);

-- ============================================================================
-- End of Migration v9.0
-- ============================================================================
-- Summary of changes:
-- 1. Added 13 new columns to projects table for enhanced tracking
-- 2. Created project_documents table for Quote/Invoice/POP/Delivery Note files
-- 3. Created communications table for unified communication hub
-- 4. Created communication_attachments table for email attachments
-- 5. Added appropriate indexes for performance
-- 6. Migrated existing data with safe defaults
-- ============================================================================

