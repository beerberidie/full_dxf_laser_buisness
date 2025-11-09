-- Phase 10 Migration: Simple Changes (Part 1)
-- Date: 2025-10-16
-- Description: Add material_thickness column to projects table
--
-- This migration adds support for:
-- 1. Material thickness field in projects
--
-- Note: Label changes (Number of Bins → Number of Bends) are template-only
-- and do not require database changes.

-- ============================================================================
-- BACKUP INSTRUCTIONS
-- ============================================================================
-- Before running this migration, create a backup:
--   cp data/laser_os.db data/laser_os_backup_v10_phase1.db
--
-- To rollback, use the rollback script:
--   migrations/rollback_v10_phase1.sql

-- ============================================================================
-- SCHEMA CHANGES
-- ============================================================================

-- Add material_thickness column to projects table
ALTER TABLE projects ADD COLUMN material_thickness NUMERIC(10, 3);

-- ============================================================================
-- DATA MIGRATION
-- ============================================================================
-- No data migration needed for this phase

-- ============================================================================
-- VERIFICATION
-- ============================================================================
-- Verify the column was added:
-- SELECT sql FROM sqlite_master WHERE type='table' AND name='projects';

-- ============================================================================
-- NOTES
-- ============================================================================
-- 1. The material_thickness column is nullable to support existing projects
-- 2. The column uses NUMERIC(10, 3) to store values like 3.000 mm
-- 3. No index is created as this field is not used for filtering/sorting
-- 4. The database column name 'number_of_bins' remains unchanged
--    Only the display label changes to "Number of Bends"

