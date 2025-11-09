-- Laser OS - Sage Integration Rollback Script
-- Version: Sage Integration v1.0
-- Description: Removes all Sage integration tables

-- Enable foreign keys
PRAGMA foreign_keys = ON;

-- Drop tables in reverse order (respecting foreign key constraints)
DROP TABLE IF EXISTS sage_audit_logs;
DROP TABLE IF EXISTS sage_sync_cursors;
DROP TABLE IF EXISTS sage_businesses;
DROP TABLE IF EXISTS sage_connections;

-- Remove schema version entry
DELETE FROM schema_version WHERE version = 'sage_integration_v1.0';

-- Verify rollback
SELECT 'Sage Integration Schema v1.0 rolled back successfully' AS status;

