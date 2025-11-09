-- Module N: Rollback Script
-- Removes all Module N tables and indexes
-- Version: 1.0
-- Date: 2025-10-21

-- WARNING: This will delete all Module N data!
-- Make sure to backup your database before running this script.

-- ============================================================================
-- Drop Triggers
-- ============================================================================

DROP TRIGGER IF EXISTS update_file_ingests_timestamp;

-- ============================================================================
-- Drop Indexes
-- ============================================================================

-- file_ingests indexes
DROP INDEX IF EXISTS idx_file_ingests_project_id;
DROP INDEX IF EXISTS idx_file_ingests_client_id;
DROP INDEX IF EXISTS idx_file_ingests_status;
DROP INDEX IF EXISTS idx_file_ingests_file_type;
DROP INDEX IF EXISTS idx_file_ingests_created_at;
DROP INDEX IF EXISTS idx_file_ingests_client_code;
DROP INDEX IF EXISTS idx_file_ingests_project_code;

-- file_extractions indexes
DROP INDEX IF EXISTS idx_file_extractions_file_ingest_id;
DROP INDEX IF EXISTS idx_file_extractions_extraction_type;

-- file_metadata indexes
DROP INDEX IF EXISTS idx_file_metadata_file_ingest_id;
DROP INDEX IF EXISTS idx_file_metadata_key;
DROP INDEX IF EXISTS idx_file_metadata_key_value;

-- ============================================================================
-- Drop Tables (in reverse order due to foreign keys)
-- ============================================================================

DROP TABLE IF EXISTS file_metadata;
DROP TABLE IF EXISTS file_extractions;
DROP TABLE IF EXISTS file_ingests;

-- ============================================================================
-- Verification
-- ============================================================================

SELECT 'Module N tables removed successfully' AS message;
SELECT name FROM sqlite_master WHERE type='table' AND name LIKE 'file_%' ORDER BY name;

