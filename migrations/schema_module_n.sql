-- Module N: File Ingest & Extract System
-- Database Schema Migration
-- Version: 1.0
-- Date: 2025-10-21

-- ============================================================================
-- Table 1: file_ingests
-- Tracks all uploaded files and their processing status
-- ============================================================================

CREATE TABLE IF NOT EXISTS file_ingests (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    
    -- Foreign Keys
    project_id INTEGER,
    client_id INTEGER,
    
    -- File Information
    original_filename VARCHAR(255) NOT NULL,
    stored_filename VARCHAR(255) NOT NULL,
    file_path VARCHAR(500) NOT NULL,
    file_size INTEGER,
    file_type VARCHAR(50) NOT NULL,  -- 'dxf', 'lbrn2', 'pdf', 'excel', 'image', 'text'
    mime_type VARCHAR(100),
    
    -- Processing Information
    status VARCHAR(20) NOT NULL DEFAULT 'pending',  -- 'pending', 'processing', 'completed', 'failed'
    processing_mode VARCHAR(20) DEFAULT 'AUTO',  -- 'AUTO', 'dxf', 'pdf', 'excel', etc.
    confidence_score DECIMAL(3,2),  -- 0.00 to 1.00
    
    -- Extracted Metadata (Quick Access)
    detected_type VARCHAR(50),
    client_code VARCHAR(50),
    project_code VARCHAR(100),
    part_name VARCHAR(200),
    material VARCHAR(100),
    thickness_mm DECIMAL(10,2),
    quantity INTEGER DEFAULT 1,
    version INTEGER DEFAULT 1,
    
    -- Error Handling
    error_message TEXT,
    retry_count INTEGER DEFAULT 0,
    
    -- Timestamps
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    processed_at DATETIME,
    
    -- Foreign Key Constraints
    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE SET NULL,
    FOREIGN KEY (client_id) REFERENCES clients(id) ON DELETE SET NULL
);

-- Indexes for file_ingests
CREATE INDEX IF NOT EXISTS idx_file_ingests_project_id ON file_ingests(project_id);
CREATE INDEX IF NOT EXISTS idx_file_ingests_client_id ON file_ingests(client_id);
CREATE INDEX IF NOT EXISTS idx_file_ingests_status ON file_ingests(status);
CREATE INDEX IF NOT EXISTS idx_file_ingests_file_type ON file_ingests(file_type);
CREATE INDEX IF NOT EXISTS idx_file_ingests_created_at ON file_ingests(created_at);
CREATE INDEX IF NOT EXISTS idx_file_ingests_client_code ON file_ingests(client_code);
CREATE INDEX IF NOT EXISTS idx_file_ingests_project_code ON file_ingests(project_code);

-- ============================================================================
-- Table 2: file_extractions
-- Stores raw extraction data in JSON format for flexibility
-- ============================================================================

CREATE TABLE IF NOT EXISTS file_extractions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    
    -- Foreign Key
    file_ingest_id INTEGER NOT NULL,
    
    -- Extraction Information
    extraction_type VARCHAR(50) NOT NULL,  -- 'dxf_metadata', 'pdf_text', 'excel_data', etc.
    extracted_data TEXT NOT NULL,  -- JSON format
    confidence_score DECIMAL(3,2),
    
    -- Parser Information
    parser_version VARCHAR(20),
    parser_name VARCHAR(50),
    
    -- Timestamps
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    
    -- Foreign Key Constraint
    FOREIGN KEY (file_ingest_id) REFERENCES file_ingests(id) ON DELETE CASCADE
);

-- Indexes for file_extractions
CREATE INDEX IF NOT EXISTS idx_file_extractions_file_ingest_id ON file_extractions(file_ingest_id);
CREATE INDEX IF NOT EXISTS idx_file_extractions_extraction_type ON file_extractions(extraction_type);

-- ============================================================================
-- Table 3: file_metadata
-- Normalized key-value pairs for fast querying
-- ============================================================================

CREATE TABLE IF NOT EXISTS file_metadata (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    
    -- Foreign Key
    file_ingest_id INTEGER NOT NULL,
    
    -- Metadata
    key VARCHAR(100) NOT NULL,
    value TEXT,
    data_type VARCHAR(20) DEFAULT 'string',  -- 'string', 'number', 'boolean', 'date', 'json'
    
    -- Source Information
    source VARCHAR(50),  -- 'filename', 'dxf_parser', 'pdf_parser', 'user_override', etc.
    
    -- Timestamps
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    
    -- Foreign Key Constraint
    FOREIGN KEY (file_ingest_id) REFERENCES file_ingests(id) ON DELETE CASCADE
);

-- Indexes for file_metadata
CREATE INDEX IF NOT EXISTS idx_file_metadata_file_ingest_id ON file_metadata(file_ingest_id);
CREATE INDEX IF NOT EXISTS idx_file_metadata_key ON file_metadata(key);
CREATE INDEX IF NOT EXISTS idx_file_metadata_key_value ON file_metadata(key, value);

-- ============================================================================
-- Triggers for updated_at timestamp
-- ============================================================================

CREATE TRIGGER IF NOT EXISTS update_file_ingests_timestamp 
AFTER UPDATE ON file_ingests
FOR EACH ROW
BEGIN
    UPDATE file_ingests SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
END;

-- ============================================================================
-- Sample Data (Optional - for testing)
-- ============================================================================

-- Uncomment to insert sample data for testing
/*
INSERT INTO file_ingests (
    original_filename, stored_filename, file_path, file_size, file_type,
    status, detected_type, client_code, project_code, part_name,
    material, thickness_mm, quantity, confidence_score
) VALUES (
    'bracket.dxf',
    'CL0001-JB-2025-10-CL0001-001-Bracket-MS-5mm-x10-v1.dxf',
    'clients/CL0001/projects/JB-2025-10-CL0001-001/inputs/CL0001-JB-2025-10-CL0001-001-Bracket-MS-5mm-x10-v1.dxf',
    45678,
    'dxf',
    'completed',
    'dxf',
    'CL0001',
    'JB-2025-10-CL0001-001',
    'Bracket',
    'Mild Steel',
    5.0,
    10,
    0.95
);
*/

-- ============================================================================
-- Migration Complete
-- ============================================================================

-- Verify tables were created
SELECT 'Module N tables created successfully:' AS message;
SELECT name FROM sqlite_master WHERE type='table' AND name LIKE 'file_%' ORDER BY name;

