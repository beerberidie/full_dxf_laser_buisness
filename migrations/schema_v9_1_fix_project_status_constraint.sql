-- ============================================================================
-- Laser OS - Phase 9.1: Fix Project Status CHECK Constraint
-- ============================================================================
-- Version: 9.1
-- Description: Updates the projects table CHECK constraint to include new Phase 9 status values
-- Dependencies: Requires schema v9.0 (Phase 9 migration)
-- Issue: The Phase 9 migration added new status constants to the model but didn't update the database CHECK constraint
-- ============================================================================

-- SQLite doesn't support ALTER TABLE to modify CHECK constraints
-- We need to recreate the table with the updated constraint

-- ============================================================================
-- STEP 1: Create new projects table with updated CHECK constraint
-- ============================================================================

CREATE TABLE IF NOT EXISTS projects_new (
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
    
    -- Updated CHECK constraint with new Phase 9 status values
    CHECK (status IN (
        'Request',                          -- New Phase 9 status
        'Quote & Approval',                 -- New Phase 9 status
        'Approved (POP Received)',          -- New Phase 9 status
        'Queued (Scheduled for Cutting)',   -- New Phase 9 status
        'In Progress',
        'Completed',
        'Cancelled',
        'Quote',                            -- Legacy status (backward compatibility)
        'Approved'                          -- Legacy status (backward compatibility)
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
-- STEP 3: Drop old table and rename new table
-- ============================================================================

DROP TABLE projects;
ALTER TABLE projects_new RENAME TO projects;

-- ============================================================================
-- STEP 4: Recreate all indexes
-- ============================================================================

CREATE INDEX IF NOT EXISTS idx_projects_client_id ON projects(client_id);
CREATE INDEX IF NOT EXISTS idx_projects_status ON projects(status);
CREATE INDEX IF NOT EXISTS idx_projects_project_code ON projects(project_code);
CREATE INDEX IF NOT EXISTS idx_projects_due_date ON projects(due_date);
CREATE INDEX IF NOT EXISTS idx_projects_created_at ON projects(created_at);
CREATE INDEX IF NOT EXISTS idx_projects_material_type ON projects(material_type);
CREATE INDEX IF NOT EXISTS idx_projects_pop_received ON projects(pop_received);
CREATE INDEX IF NOT EXISTS idx_projects_scheduled_cut_date ON projects(scheduled_cut_date);
CREATE INDEX IF NOT EXISTS idx_projects_pop_deadline ON projects(pop_deadline);

-- ============================================================================
-- STEP 5: Update schema version
-- ============================================================================

UPDATE settings SET value = '9.1', updated_at = CURRENT_TIMESTAMP 
WHERE key = 'schema_version';

-- ============================================================================
-- STEP 6: Log migration in activity log
-- ============================================================================

INSERT INTO activity_log (entity_type, entity_id, action, details, created_at)
VALUES ('SYSTEM', 0, 'MIGRATION', 'Applied schema v9.1: Fixed project status CHECK constraint to include new Phase 9 statuses', CURRENT_TIMESTAMP);

-- ============================================================================
-- End of Migration v9.1
-- ============================================================================
-- Summary of changes:
-- 1. Recreated projects table with updated CHECK constraint
-- 2. New valid statuses: 'Request', 'Quote & Approval', 'Approved (POP Received)', 'Queued (Scheduled for Cutting)'
-- 3. Preserved legacy statuses: 'Quote', 'Approved', 'In Progress', 'Completed', 'Cancelled'
-- 4. All existing data preserved
-- 5. All indexes recreated
-- ============================================================================

