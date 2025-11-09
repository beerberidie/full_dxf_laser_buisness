-- ============================================================================
-- Phase 10: Operator-User Link Migration
-- ============================================================================
-- This migration adds user_id foreign key to operators table to link
-- operators with user accounts for authentication and tracking.
--
-- Date: 2025-10-21
-- Phase: 10 - Automation Enhancements
-- ============================================================================

-- Add user_id column to operators table
ALTER TABLE operators ADD COLUMN user_id INTEGER;

-- Create foreign key constraint (SQLite doesn't support ADD CONSTRAINT, so we note it here)
-- The foreign key is defined in the model: db.ForeignKey('users.id')

-- Create index for performance
CREATE INDEX IF NOT EXISTS idx_operators_user_id ON operators(user_id);

-- ============================================================================
-- Notes:
-- ============================================================================
-- 1. user_id is nullable to allow operators without user accounts
-- 2. Existing operators will have user_id = NULL
-- 3. New operators can be linked to user accounts during creation
-- 4. One user can have one operator profile (one-to-one relationship)
-- 5. Deleting a user does not delete the operator (nullable foreign key)
-- ============================================================================

