-- Phase 5: Schedule Queue & Laser Runs Management Schema
-- Version: 5.0
-- Date: 2025-10-07

-- Create queue_items table
CREATE TABLE IF NOT EXISTS queue_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id INTEGER NOT NULL,
    queue_position INTEGER NOT NULL,
    status VARCHAR(50) NOT NULL DEFAULT 'Queued',
    priority VARCHAR(20) DEFAULT 'Normal',
    scheduled_date DATE,
    estimated_cut_time INTEGER,
    notes TEXT,
    added_by VARCHAR(100),
    added_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    started_at DATETIME,
    completed_at DATETIME,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
);

-- Create laser_runs table
CREATE TABLE IF NOT EXISTS laser_runs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id INTEGER NOT NULL,
    queue_item_id INTEGER,
    run_date DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    operator VARCHAR(100),
    cut_time_minutes INTEGER,
    material_type VARCHAR(100),
    material_thickness DECIMAL(10, 3),
    sheet_count INTEGER DEFAULT 1,
    parts_produced INTEGER,
    machine_settings TEXT,
    notes TEXT,
    status VARCHAR(50) DEFAULT 'Completed',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE,
    FOREIGN KEY (queue_item_id) REFERENCES queue_items(id) ON DELETE SET NULL
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_queue_items_project_id ON queue_items(project_id);
CREATE INDEX IF NOT EXISTS idx_queue_items_status ON queue_items(status);
CREATE INDEX IF NOT EXISTS idx_queue_items_queue_position ON queue_items(queue_position);
CREATE INDEX IF NOT EXISTS idx_queue_items_scheduled_date ON queue_items(scheduled_date);
CREATE INDEX IF NOT EXISTS idx_queue_items_added_at ON queue_items(added_at);

CREATE INDEX IF NOT EXISTS idx_laser_runs_project_id ON laser_runs(project_id);
CREATE INDEX IF NOT EXISTS idx_laser_runs_queue_item_id ON laser_runs(queue_item_id);
CREATE INDEX IF NOT EXISTS idx_laser_runs_run_date ON laser_runs(run_date);
CREATE INDEX IF NOT EXISTS idx_laser_runs_operator ON laser_runs(operator);
CREATE INDEX IF NOT EXISTS idx_laser_runs_created_at ON laser_runs(created_at);

-- Update schema version
UPDATE settings SET value = '5.0' WHERE key = 'schema_version';

-- Insert queue management settings
INSERT OR IGNORE INTO settings (key, value, description) VALUES
    ('queue_auto_position', 'true', 'Automatically assign queue positions'),
    ('default_priority', 'Normal', 'Default priority for new queue items'),
    ('queue_statuses', 'Queued,In Progress,Completed,Cancelled', 'Available queue statuses'),
    ('priority_levels', 'Low,Normal,High,Urgent', 'Available priority levels');

