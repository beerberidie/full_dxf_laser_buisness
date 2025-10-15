-- ============================================================================
-- Laser OS Tier 1 - Phase 2: Projects Table Migration
-- ============================================================================
-- Version: 2.0
-- Description: Adds projects table for job/project management
-- Dependencies: Requires clients table from Phase 1
-- ============================================================================

-- Projects/Jobs Table
CREATE TABLE IF NOT EXISTS projects (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_code VARCHAR(30) UNIQUE NOT NULL,
    client_id INTEGER NOT NULL,
    name VARCHAR(200) NOT NULL,
    description TEXT,
    status VARCHAR(20) NOT NULL DEFAULT 'Quote',
    
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
    
    -- Foreign Keys
    FOREIGN KEY (client_id) REFERENCES clients(id) ON DELETE CASCADE,
    
    -- Indexes
    CHECK (status IN ('Quote', 'Approved', 'In Progress', 'Completed', 'Cancelled'))
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_projects_client_id ON projects(client_id);
CREATE INDEX IF NOT EXISTS idx_projects_status ON projects(status);
CREATE INDEX IF NOT EXISTS idx_projects_project_code ON projects(project_code);
CREATE INDEX IF NOT EXISTS idx_projects_due_date ON projects(due_date);
CREATE INDEX IF NOT EXISTS idx_projects_created_at ON projects(created_at);

-- Update schema version
UPDATE settings SET value = '2.0', updated_at = CURRENT_TIMESTAMP 
WHERE key = 'schema_version';

-- ============================================================================
-- End of Migration
-- ============================================================================

