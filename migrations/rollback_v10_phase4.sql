-- ============================================================================
-- Rollback Phase 10 Part 4: Remove operator_id from laser_runs
-- ============================================================================
-- This script rolls back the Phase 4 migration by removing the operator_id
-- column and its index from the laser_runs table.
-- ============================================================================

-- Drop index
DROP INDEX IF EXISTS idx_laser_runs_operator_id;

-- ============================================================================
-- SQLite Limitation: Cannot drop columns
-- ============================================================================
-- SQLite does not support dropping columns directly.
-- The operator_id column will remain in the table but will not be used.
--
-- To fully remove the column, you would need to:
-- 1. Create a new table without the operator_id column
-- 2. Copy all data from the old table to the new table
-- 3. Drop the old table
-- 4. Rename the new table
--
-- This is not recommended unless absolutely necessary.
-- ============================================================================

-- Alternative: Restore from backup
-- Copy-Item data/backups/laser_os_backup_v10_phase4_YYYYMMDD_HHMMSS.db data/laser_os.db -Force
-- ============================================================================

