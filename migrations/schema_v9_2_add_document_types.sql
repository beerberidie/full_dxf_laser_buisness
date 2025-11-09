-- ============================================================================
-- LASER OS - SCHEMA v9.2 MIGRATION
-- Version: 9.2
-- Description: Add 'Other' and 'Image' document types to project_documents table
-- Date: 2025-10-23
-- ============================================================================
-- This migration updates the CHECK constraint on project_documents.document_type
-- to include two new document types: 'Other' and 'Image'
--
-- IMPORTANT: SQLite does not support ALTER TABLE to modify CHECK constraints.
-- We must recreate the table with the new constraint.
-- ============================================================================

PRAGMA foreign_keys = OFF;

-- ============================================================================
-- STEP 1: Create backup of project_documents table
-- ============================================================================

CREATE TABLE IF NOT EXISTS project_documents_backup (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id INTEGER NOT NULL,
    document_type VARCHAR(50) NOT NULL,
    original_filename VARCHAR(255) NOT NULL,
    stored_filename VARCHAR(255) NOT NULL,
    file_path VARCHAR(500) NOT NULL,
    file_size INTEGER NOT NULL,
    upload_date DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    uploaded_by VARCHAR(100),
    is_parsed BOOLEAN DEFAULT 0,
    parsed_data TEXT,
    notes TEXT,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Copy all existing data to backup
INSERT INTO project_documents_backup 
SELECT * FROM project_documents;

-- ============================================================================
-- STEP 2: Drop the old table and its indexes
-- ============================================================================

DROP INDEX IF EXISTS idx_project_documents_project_id;
DROP INDEX IF EXISTS idx_project_documents_document_type;
DROP INDEX IF EXISTS idx_project_documents_upload_date;
DROP TABLE IF EXISTS project_documents;

-- ============================================================================
-- STEP 3: Create new table with updated CHECK constraint
-- ============================================================================

CREATE TABLE project_documents (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id INTEGER NOT NULL,
    document_type VARCHAR(50) NOT NULL, -- 'Quote', 'Invoice', 'Proof of Payment', 'Delivery Note', 'Other', 'Image'
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
    
    -- Constraints - UPDATED to include 'Other' and 'Image'
    CHECK (document_type IN ('Quote', 'Invoice', 'Proof of Payment', 'Delivery Note', 'Other', 'Image'))
);

-- ============================================================================
-- STEP 4: Restore data from backup
-- ============================================================================

INSERT INTO project_documents 
SELECT * FROM project_documents_backup;

-- ============================================================================
-- STEP 5: Recreate indexes
-- ============================================================================

CREATE INDEX idx_project_documents_project_id ON project_documents(project_id);
CREATE INDEX idx_project_documents_document_type ON project_documents(document_type);
CREATE INDEX idx_project_documents_upload_date ON project_documents(upload_date);

-- ============================================================================
-- STEP 6: Drop backup table
-- ============================================================================

DROP TABLE project_documents_backup;

-- ============================================================================
-- STEP 7: Re-enable foreign keys
-- ============================================================================

PRAGMA foreign_keys = ON;

-- ============================================================================
-- STEP 8: Update schema version
-- ============================================================================

UPDATE settings SET value = '9.2', updated_at = CURRENT_TIMESTAMP 
WHERE key = 'schema_version';

-- ============================================================================
-- STEP 9: Log migration in activity log
-- ============================================================================

INSERT INTO activity_log (entity_type, entity_id, action, details, created_at)
VALUES ('SYSTEM', 0, 'MIGRATION', 'Applied schema v9.2: Added Other and Image document types to project_documents CHECK constraint', CURRENT_TIMESTAMP);

-- ============================================================================
-- STEP 10: Verification
-- ============================================================================

-- Verify table structure
SELECT 'Migration v9.2 completed successfully' AS status;
SELECT COUNT(*) AS total_documents FROM project_documents;

-- ============================================================================
-- End of Migration
-- ============================================================================

