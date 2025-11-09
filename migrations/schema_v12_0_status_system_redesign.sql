-- ============================================================================
-- Laser OS - Version 12.0: Status System Redesign
-- ============================================================================
-- Version: 12.0
-- Date: 2025-10-23
-- Description: Comprehensive status system redesign with automation, timers, and notifications
-- Dependencies: Requires schema v11 (indexes)
-- ============================================================================
-- 
-- CHANGES:
-- 1. Add 7 new fields for status automation and tracking
-- 2. Update status CHECK constraint (remove legacy statuses)
-- 3. Create 3 new indexes for performance
-- 4. Migrate legacy status values to new equivalents
-- 
-- NEW FEATURES:
-- - 30-day quote expiry timer with auto-cancellation
-- - 25-day quote reminder system
-- - On-hold capability (independent flag)
-- - Reinstate workflow for cancelled projects
-- - Enhanced cancellation tracking
-- 
-- ============================================================================

-- ============================================================================
-- STEP 1: Create new projects table with all enhancements
-- ============================================================================

CREATE TABLE IF NOT EXISTS projects_new (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_code VARCHAR(30) UNIQUE NOT NULL,
    client_id INTEGER NOT NULL,
    name VARCHAR(200) NOT NULL,
    description TEXT,
    status VARCHAR(50) NOT NULL DEFAULT 'Request',
    
    -- Timeline
    quote_date DATE,
    approval_date DATE,
    due_date DATE,
    completion_date DATE,
    
    -- Pricing
    quoted_price DECIMAL(10, 2),
    final_price DECIMAL(10, 2),
    
    -- Additional info
    notes TEXT,
    
    -- Metadata
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    
    -- Phase 9 enhancements
    material_type VARCHAR(100),
    material_quantity_sheets INTEGER,
    parts_quantity INTEGER,
    estimated_cut_time INTEGER,
    number_of_bins INTEGER,
    drawing_creation_time INTEGER,
    
    -- Phase 10 enhancement
    material_thickness DECIMAL(10, 2),
    
    -- POP tracking
    pop_received BOOLEAN DEFAULT 0,
    pop_received_date DATE,
    pop_deadline DATE,
    
    -- Client notification tracking
    client_notified BOOLEAN DEFAULT 0,
    client_notified_date DATETIME,
    
    -- Delivery confirmation tracking
    delivery_confirmed BOOLEAN DEFAULT 0,
    delivery_confirmed_date DATE,
    
    -- Scheduling
    scheduled_cut_date DATE,
    
    -- ========================================================================
    -- V12.0: NEW FIELDS - Status System Redesign
    -- ========================================================================
    
    -- On Hold Management (independent flag - can be set on any status)
    on_hold BOOLEAN DEFAULT 0,
    on_hold_reason TEXT,
    on_hold_date DATE,
    
    -- Quote Expiry Timer (30-day auto-cancel)
    quote_expiry_date DATE,
    quote_reminder_sent BOOLEAN DEFAULT 0,
    
    -- Cancellation Management
    cancellation_reason TEXT,
    can_reinstate BOOLEAN DEFAULT 0,
    
    -- Foreign Keys
    FOREIGN KEY (client_id) REFERENCES clients(id) ON DELETE CASCADE,
    
    -- ========================================================================
    -- V12.0: UPDATED CHECK CONSTRAINT - Remove legacy statuses
    -- ========================================================================
    CHECK (status IN (
        'Request',
        'Quote & Approval',
        'Approved (POP Received)',
        'Queued (Scheduled for Cutting)',
        'In Progress',
        'Completed',
        'Cancelled'
    ))
);

-- ============================================================================
-- STEP 2: Copy all data from old table to new table
-- ============================================================================

INSERT INTO projects_new (
    id, project_code, client_id, name, description, status,
    quote_date, approval_date, due_date, completion_date,
    quoted_price, final_price, notes,
    created_at, updated_at,
    material_type, material_quantity_sheets, parts_quantity,
    estimated_cut_time, number_of_bins, drawing_creation_time,
    material_thickness,
    pop_received, pop_received_date, pop_deadline,
    client_notified, client_notified_date,
    delivery_confirmed, delivery_confirmed_date,
    scheduled_cut_date,
    -- V12.0: New fields (will be NULL/default for existing records)
    on_hold, on_hold_reason, on_hold_date,
    quote_expiry_date, quote_reminder_sent,
    cancellation_reason, can_reinstate
)
SELECT 
    id, project_code, client_id, name, description,
    -- V12.0: Migrate legacy statuses to new equivalents
    CASE 
        WHEN status = 'Quote' THEN 'Quote & Approval'
        WHEN status = 'Approved' THEN 'Approved (POP Received)'
        ELSE status
    END as status,
    quote_date, approval_date, due_date, completion_date,
    quoted_price, final_price, notes,
    created_at, updated_at,
    material_type, material_quantity_sheets, parts_quantity,
    estimated_cut_time, number_of_bins, drawing_creation_time,
    material_thickness,
    pop_received, pop_received_date, pop_deadline,
    client_notified, client_notified_date,
    delivery_confirmed, delivery_confirmed_date,
    scheduled_cut_date,
    -- V12.0: Initialize new fields with defaults
    0 as on_hold,                    -- Not on hold by default
    NULL as on_hold_reason,
    NULL as on_hold_date,
    -- Calculate quote_expiry_date for existing projects in "Quote & Approval"
    CASE 
        WHEN (status = 'Quote & Approval' OR status = 'Quote') AND quote_date IS NOT NULL 
        THEN DATE(quote_date, '+30 days')
        ELSE NULL
    END as quote_expiry_date,
    0 as quote_reminder_sent,        -- Reminder not sent yet
    NULL as cancellation_reason,
    -- Mark existing cancelled projects as can_reinstate
    CASE 
        WHEN status = 'Cancelled' THEN 1
        ELSE 0
    END as can_reinstate
FROM projects;

-- ============================================================================
-- STEP 3: Drop old table and rename new table
-- ============================================================================

DROP TABLE projects;
ALTER TABLE projects_new RENAME TO projects;

-- ============================================================================
-- STEP 4: Recreate all indexes
-- ============================================================================

-- Original indexes
CREATE INDEX IF NOT EXISTS idx_projects_client_id ON projects(client_id);
CREATE INDEX IF NOT EXISTS idx_projects_status ON projects(status);
CREATE INDEX IF NOT EXISTS idx_projects_due_date ON projects(due_date);
CREATE INDEX IF NOT EXISTS idx_projects_material_type ON projects(material_type);
CREATE INDEX IF NOT EXISTS idx_projects_pop_received ON projects(pop_received);
CREATE INDEX IF NOT EXISTS idx_projects_pop_deadline ON projects(pop_deadline);
CREATE INDEX IF NOT EXISTS idx_projects_scheduled_cut_date ON projects(scheduled_cut_date);

-- V12.0: New indexes for status system redesign
CREATE INDEX IF NOT EXISTS idx_projects_on_hold ON projects(on_hold);
CREATE INDEX IF NOT EXISTS idx_projects_quote_expiry_date ON projects(quote_expiry_date);
CREATE INDEX IF NOT EXISTS idx_projects_can_reinstate ON projects(can_reinstate);

-- ============================================================================
-- STEP 5: Verification queries
-- ============================================================================

-- Count projects by status (should show no legacy statuses)
-- SELECT status, COUNT(*) as count FROM projects GROUP BY status ORDER BY count DESC;

-- Count projects on hold
-- SELECT COUNT(*) as on_hold_count FROM projects WHERE on_hold = 1;

-- Count projects with quote expiry dates
-- SELECT COUNT(*) as with_expiry FROM projects WHERE quote_expiry_date IS NOT NULL;

-- Count projects that can be reinstated
-- SELECT COUNT(*) as can_reinstate_count FROM projects WHERE can_reinstate = 1;

-- Show projects with upcoming quote expiry (next 7 days)
-- SELECT project_code, name, quote_date, quote_expiry_date, 
--        JULIANDAY(quote_expiry_date) - JULIANDAY('now') as days_until_expiry
-- FROM projects 
-- WHERE quote_expiry_date IS NOT NULL 
--   AND quote_expiry_date >= DATE('now')
--   AND quote_expiry_date <= DATE('now', '+7 days')
-- ORDER BY quote_expiry_date;

-- ============================================================================
-- MIGRATION COMPLETE
-- ============================================================================
-- 
-- SUMMARY:
-- ✅ Added 7 new fields for status automation
-- ✅ Updated CHECK constraint (removed legacy statuses)
-- ✅ Created 3 new indexes for performance
-- ✅ Migrated legacy "Quote" → "Quote & Approval"
-- ✅ Migrated legacy "Approved" → "Approved (POP Received)"
-- ✅ Set quote_expiry_date for existing projects in "Quote & Approval"
-- ✅ Marked existing cancelled projects as can_reinstate
-- 
-- NEXT STEPS:
-- 1. Update Project model in app/models/business.py
-- 2. Create status_automation.py service
-- 3. Implement background scheduler
-- 4. Update routes and templates
-- 5. Create notification system
-- 6. Run tests
-- 
-- ============================================================================
