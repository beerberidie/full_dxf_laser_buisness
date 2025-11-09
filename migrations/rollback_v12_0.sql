-- ============================================================================
-- Laser OS - Rollback Version 12.0: Status System Redesign
-- ============================================================================
-- Version: 12.0 Rollback
-- Date: 2025-10-23
-- Description: Rollback status system redesign to v11 schema
-- WARNING: This will remove all v12.0 enhancements
-- ============================================================================

-- ============================================================================
-- STEP 1: Create projects table with v11 schema (before v12.0 changes)
-- ============================================================================

CREATE TABLE IF NOT EXISTS projects_rollback (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_code VARCHAR(30) UNIQUE NOT NULL,
    client_id INTEGER NOT NULL,
    name VARCHAR(200) NOT NULL,
    description TEXT,
    status VARCHAR(50) NOT NULL DEFAULT 'Quote',
    
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
    
    -- Foreign Keys
    FOREIGN KEY (client_id) REFERENCES clients(id) ON DELETE CASCADE,
    
    -- V11 CHECK constraint (includes legacy statuses)
    CHECK (status IN (
        'Request',
        'Quote & Approval',
        'Approved (POP Received)',
        'Queued (Scheduled for Cutting)',
        'In Progress',
        'Completed',
        'Cancelled',
        'Quote',      -- Legacy
        'Approved'    -- Legacy
    ))
);

-- ============================================================================
-- STEP 2: Copy data back (excluding v12.0 fields)
-- ============================================================================

INSERT INTO projects_rollback (
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
    scheduled_cut_date
)
SELECT 
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
    scheduled_cut_date
FROM projects;

-- ============================================================================
-- STEP 3: Drop current table and rename rollback table
-- ============================================================================

DROP TABLE projects;
ALTER TABLE projects_rollback RENAME TO projects;

-- ============================================================================
-- STEP 4: Recreate v11 indexes (without v12.0 indexes)
-- ============================================================================

CREATE INDEX IF NOT EXISTS idx_projects_client_id ON projects(client_id);
CREATE INDEX IF NOT EXISTS idx_projects_status ON projects(status);
CREATE INDEX IF NOT EXISTS idx_projects_due_date ON projects(due_date);
CREATE INDEX IF NOT EXISTS idx_projects_material_type ON projects(material_type);
CREATE INDEX IF NOT EXISTS idx_projects_pop_received ON projects(pop_received);
CREATE INDEX IF NOT EXISTS idx_projects_pop_deadline ON projects(pop_deadline);
CREATE INDEX IF NOT EXISTS idx_projects_scheduled_cut_date ON projects(scheduled_cut_date);

-- ============================================================================
-- ROLLBACK COMPLETE
-- ============================================================================
-- 
-- SUMMARY:
-- ✅ Removed 7 v12.0 fields (on_hold, quote_expiry_date, etc.)
-- ✅ Restored v11 CHECK constraint (with legacy statuses)
-- ✅ Removed 3 v12.0 indexes
-- ✅ Preserved all project data
-- 
-- DATA LOSS WARNING:
-- ❌ Lost: on_hold flags and reasons
-- ❌ Lost: quote_expiry_date calculations
-- ❌ Lost: cancellation_reason text
-- ❌ Lost: can_reinstate flags
-- 
-- NEXT STEPS:
-- 1. Revert Project model changes in app/models/business.py
-- 2. Remove status_automation.py service
-- 3. Remove background scheduler
-- 4. Revert route changes
-- 5. Revert template changes
-- 
-- ============================================================================
