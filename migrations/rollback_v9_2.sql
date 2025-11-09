-- ============================================================================
-- LASER OS - ROLLBACK SCRIPT FOR v9.2
-- Version: Rollback v9.2 to v9.1
-- Description: Revert project_documents table to original CHECK constraint
-- Date: 2025-10-23
-- ============================================================================
-- This script reverts the v9.2 migration by restoring the original CHECK
-- constraint that only allows: 'Quote', 'Invoice', 'Proof of Payment', 'Delivery Note'
--
-- WARNING: This will fail if any documents with type 'Other' or 'Image' exist!
-- You must delete or update those documents first.
-- ============================================================================

PRAGMA foreign_keys = OFF;

-- ============================================================================
-- STEP 1: Check for documents with new types
-- ============================================================================

-- This will show any documents that would be lost
SELECT 'Documents with new types that will be affected:' AS warning;
SELECT id, project_id, document_type, original_filename 
FROM project_documents 
WHERE document_type IN ('Other', 'Image');

-- ============================================================================
-- STEP 2: Create backup of project_documents table
-- ============================================================================

CREATE TABLE IF NOT EXISTS project_documents_rollback_backup (
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
INSERT INTO project_documents_rollback_backup 
SELECT * FROM project_documents;

-- ============================================================================
-- STEP 3: Drop the current table and its indexes
-- ============================================================================

DROP INDEX IF EXISTS idx_project_documents_project_id;
DROP INDEX IF EXISTS idx_project_documents_document_type;
DROP INDEX IF EXISTS idx_project_documents_upload_date;
DROP TABLE IF EXISTS project_documents;

-- ============================================================================
-- STEP 4: Create table with original CHECK constraint
-- ============================================================================

CREATE TABLE project_documents (
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
    
    -- Constraints - ORIGINAL (without 'Other' and 'Image')
    CHECK (document_type IN ('Quote', 'Invoice', 'Proof of Payment', 'Delivery Note'))
);

-- ============================================================================
-- STEP 5: Restore data from backup (excluding new document types)
-- ============================================================================

-- Only restore documents with original types
INSERT INTO project_documents 
SELECT * FROM project_documents_rollback_backup
WHERE document_type IN ('Quote', 'Invoice', 'Proof of Payment', 'Delivery Note');

-- ============================================================================
-- STEP 6: Recreate indexes
-- ============================================================================

CREATE INDEX idx_project_documents_project_id ON project_documents(project_id);
CREATE INDEX idx_project_documents_document_type ON project_documents(document_type);
CREATE INDEX idx_project_documents_upload_date ON project_documents(upload_date);

-- ============================================================================
-- STEP 7: Keep backup table for safety
-- ============================================================================

-- DO NOT drop the backup table - keep it for manual recovery if needed
SELECT 'Backup table project_documents_rollback_backup has been preserved' AS notice;

-- ============================================================================
-- STEP 8: Re-enable foreign keys
-- ============================================================================

PRAGMA foreign_keys = ON;

-- ============================================================================
-- STEP 9: Update schema version
-- ============================================================================

UPDATE settings SET value = '9.1', updated_at = CURRENT_TIMESTAMP 
WHERE key = 'schema_version';

-- ============================================================================
-- STEP 10: Log rollback in activity log
-- ============================================================================

INSERT INTO activity_log (entity_type, entity_id, action, details, created_at)
VALUES ('SYSTEM', 0, 'ROLLBACK', 'Rolled back schema from v9.2 to v9.1: Removed Other and Image document types', CURRENT_TIMESTAMP);

-- ============================================================================
-- STEP 11: Verification
-- ============================================================================

SELECT 'Rollback to v9.1 completed' AS status;
SELECT COUNT(*) AS documents_restored FROM project_documents;
SELECT COUNT(*) AS documents_in_backup FROM project_documents_rollback_backup;

-- ============================================================================
-- End of Rollback
-- ============================================================================

