-- Rollback Script for Phase 10 Part 1 Migration
-- Date: 2025-10-16
-- Description: Rollback material_thickness column addition
--
-- WARNING: This will remove the material_thickness column and all data in it!

-- ============================================================================
-- ROLLBACK INSTRUCTIONS
-- ============================================================================
-- SQLite does not support DROP COLUMN directly in older versions.
-- We need to recreate the table without the column.

-- Step 1: Create a backup table with the old schema
CREATE TABLE projects_backup AS SELECT
    id,
    project_code,
    client_id,
    name,
    description,
    status,
    quote_date,
    approval_date,
    due_date,
    completion_date,
    quoted_price,
    final_price,
    notes,
    created_at,
    updated_at,
    -- Phase 9 fields
    material_type,
    material_quantity_sheets,
    parts_quantity,
    estimated_cut_time,
    number_of_bins,
    drawing_creation_time,
    scheduled_cut_date
FROM projects;

-- Step 2: Drop the original table
DROP TABLE projects;

-- Step 3: Rename backup to original
ALTER TABLE projects_backup RENAME TO projects;

-- Step 4: Recreate indexes
CREATE INDEX IF NOT EXISTS idx_projects_client_id ON projects(client_id);
CREATE INDEX IF NOT EXISTS idx_projects_status ON projects(status);
CREATE INDEX IF NOT EXISTS idx_projects_project_code ON projects(project_code);
CREATE INDEX IF NOT EXISTS idx_projects_material_type ON projects(material_type);

-- ============================================================================
-- VERIFICATION
-- ============================================================================
-- Verify the column was removed:
-- SELECT sql FROM sqlite_master WHERE type='table' AND name='projects';

-- ============================================================================
-- NOTES
-- ============================================================================
-- 1. All data in material_thickness column will be lost
-- 2. Foreign key constraints will be preserved
-- 3. Make sure to restore from backup if needed:
--    cp data/laser_os_backup_v10_phase1.db data/laser_os.db

