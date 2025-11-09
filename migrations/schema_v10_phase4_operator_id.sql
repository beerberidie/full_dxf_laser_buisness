-- ============================================================================
-- Phase 10 Part 4: Add operator_id to laser_runs table
-- ============================================================================
-- This migration adds the operator_id foreign key column to laser_runs
-- to support the new Operator model relationship.
--
-- The legacy 'operator' text field is kept for backward compatibility.
-- ============================================================================

-- Add operator_id column to laser_runs table
ALTER TABLE laser_runs ADD COLUMN operator_id INTEGER;

-- Create index on operator_id for performance
CREATE INDEX IF NOT EXISTS idx_laser_runs_operator_id ON laser_runs(operator_id);

-- ============================================================================
-- Migration Complete
-- ============================================================================
-- New column added:
--   - laser_runs.operator_id (INTEGER, nullable, indexed)
--
-- Note: The legacy 'operator' text field remains unchanged for backward compatibility.
-- ============================================================================

