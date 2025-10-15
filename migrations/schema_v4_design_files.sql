-- Phase 4: DXF File Management Schema
-- Version: 4.0
-- Date: 2025-10-06

-- Create design_files table
CREATE TABLE IF NOT EXISTS design_files (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id INTEGER NOT NULL,
    original_filename VARCHAR(255) NOT NULL,
    stored_filename VARCHAR(255) NOT NULL,
    file_path VARCHAR(500) NOT NULL,
    file_size INTEGER NOT NULL,
    file_type VARCHAR(50) DEFAULT 'dxf',
    upload_date DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    uploaded_by VARCHAR(100),
    notes TEXT,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_design_files_project_id ON design_files(project_id);
CREATE INDEX IF NOT EXISTS idx_design_files_upload_date ON design_files(upload_date);
CREATE INDEX IF NOT EXISTS idx_design_files_file_type ON design_files(file_type);
CREATE INDEX IF NOT EXISTS idx_design_files_created_at ON design_files(created_at);

-- Update schema version
UPDATE settings SET value = '4.0' WHERE key = 'schema_version';

-- Insert file management settings
INSERT OR IGNORE INTO settings (key, value, description) VALUES
    ('max_file_size_mb', '50', 'Maximum file upload size in megabytes'),
    ('allowed_file_types', '.dxf,.DXF', 'Allowed file extensions for upload'),
    ('file_storage_path', 'data/files/projects', 'Base path for file storage');

