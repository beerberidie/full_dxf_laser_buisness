-- ============================================================================
-- LASER OS - PHASE 3 ROLLBACK SCRIPT
-- Version: 10 Phase 3
-- Description: Rollback machine_settings_presets and operators tables
-- Date: 2025-10-16
-- ============================================================================

-- ============================================================================
-- WARNING
-- ============================================================================
-- This script will:
-- 1. Drop the machine_settings_presets table (all presets will be lost)
-- 2. Drop the operators table (all operators will be lost)
-- 3. Remove the preset_id column from laser_runs table
--
-- IMPORTANT: SQLite does not support DROP COLUMN directly.
-- To remove the preset_id column, we need to recreate the laser_runs table.
-- This is a complex operation and should only be done if absolutely necessary.
--
-- For now, we'll just drop the new tables and leave the preset_id column
-- (it won't cause any issues if it's not used).
-- ============================================================================

-- ============================================================================
-- BACKUP INSTRUCTIONS
-- ============================================================================
-- Before running this rollback, create a backup:
-- 
-- Windows PowerShell:
--   Copy-Item data\laser_os.db data\backups\laser_os_backup_before_rollback_$(Get-Date -Format 'yyyyMMdd_HHmmss').db
--
-- Linux/Mac:
--   cp data/laser_os.db data/backups/laser_os_backup_before_rollback_$(date +%Y%m%d_%H%M%S).db
-- ============================================================================

-- ============================================================================
-- 1. DROP INDEXES
-- ============================================================================

-- Drop machine_settings_presets indexes
DROP INDEX IF EXISTS idx_presets_material_type;
DROP INDEX IF EXISTS idx_presets_thickness;
DROP INDEX IF EXISTS idx_presets_active;
DROP INDEX IF EXISTS idx_presets_material_thickness;
DROP INDEX IF EXISTS idx_presets_name;

-- Drop operators indexes
DROP INDEX IF EXISTS idx_operators_name;
DROP INDEX IF EXISTS idx_operators_active;

-- Drop laser_runs preset_id index
DROP INDEX IF EXISTS idx_laser_runs_preset_id;

-- ============================================================================
-- 2. DROP TABLES
-- ============================================================================

-- Drop machine_settings_presets table
DROP TABLE IF EXISTS machine_settings_presets;

-- Drop operators table
DROP TABLE IF EXISTS operators;

-- ============================================================================
-- 3. REMOVE PRESET_ID COLUMN FROM LASER_RUNS
-- ============================================================================

-- Note: SQLite doesn't support DROP COLUMN directly.
-- The preset_id column will remain in the laser_runs table but won't be used.
-- If you need to completely remove it, you would need to:
--   1. Create a new laser_runs table without the preset_id column
--   2. Copy all data from the old table to the new table
--   3. Drop the old table
--   4. Rename the new table
--
-- This is complex and risky, so we're leaving the column in place.
-- It will simply be NULL for all rows and won't affect functionality.

-- ============================================================================
-- ROLLBACK COMPLETE
-- ============================================================================
-- Tables dropped:
--   - machine_settings_presets
--   - operators
-- 
-- Note: The preset_id column remains in laser_runs table but is unused.
--
-- To verify the rollback:
--   SELECT name FROM sqlite_master WHERE type='table' AND name IN ('operators', 'machine_settings_presets');
--   -- Should return no rows
-- ============================================================================

