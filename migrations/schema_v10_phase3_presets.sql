-- ============================================================================
-- LASER OS - PHASE 3 DATABASE MIGRATION
-- Version: 10 Phase 3
-- Description: Create machine_settings_presets and operators tables
-- Date: 2025-10-16
-- ============================================================================

-- ============================================================================
-- BACKUP INSTRUCTIONS
-- ============================================================================
-- Before running this migration, create a backup:
-- 
-- Windows PowerShell:
--   Copy-Item data\laser_os.db data\backups\laser_os_backup_v10_phase3_$(Get-Date -Format 'yyyyMMdd_HHmmss').db
--
-- Linux/Mac:
--   cp data/laser_os.db data/backups/laser_os_backup_v10_phase3_$(date +%Y%m%d_%H%M%S).db
-- ============================================================================

-- ============================================================================
-- 1. CREATE OPERATORS TABLE
-- ============================================================================

CREATE TABLE IF NOT EXISTS operators (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    
    -- Basic Information
    name VARCHAR(100) NOT NULL UNIQUE,
    email VARCHAR(100),
    phone VARCHAR(50),
    
    -- Status
    is_active BOOLEAN DEFAULT 1 NOT NULL,
    
    -- Metadata
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    
    -- Constraints
    CHECK(is_active IN (0, 1))
);

-- Indexes for operators table
CREATE INDEX IF NOT EXISTS idx_operators_name ON operators(name);
CREATE INDEX IF NOT EXISTS idx_operators_active ON operators(is_active);

-- ============================================================================
-- 2. CREATE MACHINE SETTINGS PRESETS TABLE
-- ============================================================================

CREATE TABLE IF NOT EXISTS machine_settings_presets (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    
    -- Identification
    preset_name VARCHAR(200) NOT NULL,
    material_type VARCHAR(100) NOT NULL,
    thickness NUMERIC(10, 3) NOT NULL,
    
    -- Description
    description TEXT,
    
    -- Cutting Parameters
    nozzle VARCHAR(50),                    -- e.g., "1.5mm Single", "2.0mm Double"
    cut_speed NUMERIC(10, 2),              -- mm/min
    nozzle_height NUMERIC(10, 3),          -- mm
    
    -- Gas Settings
    gas_type VARCHAR(50),                  -- e.g., "Oxygen", "Nitrogen", "Air"
    gas_pressure NUMERIC(10, 2),           -- bar
    
    -- Power Settings
    peak_power NUMERIC(10, 2),             -- Watts or %
    actual_power NUMERIC(10, 2),           -- Watts or %
    duty_cycle NUMERIC(5, 2),              -- %
    pulse_frequency NUMERIC(10, 2),        -- Hz
    
    -- Beam Settings
    beam_width NUMERIC(10, 3),             -- mm
    focus_position NUMERIC(10, 3),         -- mm (focal offset)
    
    -- Timing Settings
    laser_on_delay NUMERIC(10, 3),         -- milliseconds
    laser_off_delay NUMERIC(10, 3),        -- milliseconds
    
    -- Additional Settings
    pierce_time NUMERIC(10, 3),            -- seconds
    pierce_power NUMERIC(10, 2),           -- Watts or %
    corner_power NUMERIC(10, 2),           -- Watts or %
    
    -- Status and Metadata
    is_active BOOLEAN DEFAULT 1 NOT NULL,
    notes TEXT,
    created_by VARCHAR(100),
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    
    -- Constraints
    CHECK(is_active IN (0, 1)),
    UNIQUE(preset_name)
);

-- Indexes for machine_settings_presets table
CREATE INDEX IF NOT EXISTS idx_presets_material_type ON machine_settings_presets(material_type);
CREATE INDEX IF NOT EXISTS idx_presets_thickness ON machine_settings_presets(thickness);
CREATE INDEX IF NOT EXISTS idx_presets_active ON machine_settings_presets(is_active);
CREATE INDEX IF NOT EXISTS idx_presets_material_thickness ON machine_settings_presets(material_type, thickness);
CREATE INDEX IF NOT EXISTS idx_presets_name ON machine_settings_presets(preset_name);

-- ============================================================================
-- 3. ADD PRESET REFERENCE TO LASER_RUNS TABLE
-- ============================================================================

-- Add preset_id column to laser_runs table
-- Note: SQLite doesn't support adding foreign keys to existing tables,
-- so we'll add the column without the constraint and handle it in the application

ALTER TABLE laser_runs ADD COLUMN preset_id INTEGER;

-- Create index for preset_id
CREATE INDEX IF NOT EXISTS idx_laser_runs_preset_id ON laser_runs(preset_id);

-- ============================================================================
-- 4. SEED INITIAL DATA
-- ============================================================================

-- Insert default "System" operator
INSERT INTO operators (name, email, is_active, created_at, updated_at)
VALUES ('System', NULL, 1, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP);

-- Insert sample operators
INSERT INTO operators (name, email, is_active, created_at, updated_at)
VALUES 
    ('Operator 1', NULL, 1, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
    ('Operator 2', NULL, 1, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP);

-- Insert sample machine settings presets for common materials
-- These are example values - adjust based on your actual machine specifications

-- Mild Steel Presets
INSERT INTO machine_settings_presets (
    preset_name, material_type, thickness, description,
    nozzle, cut_speed, nozzle_height,
    gas_type, gas_pressure,
    peak_power, actual_power, duty_cycle, pulse_frequency,
    beam_width, focus_position,
    laser_on_delay, laser_off_delay,
    pierce_time, pierce_power, corner_power,
    is_active, created_by, created_at, updated_at
) VALUES
    ('Mild Steel 1mm - Standard', 'Mild Steel', 1.0, 'Standard cutting parameters for 1mm mild steel',
     '1.5mm Single', 3000.00, 1.000,
     'Oxygen', 0.80,
     2000.00, 1800.00, 80.00, 5000.00,
     0.200, 0.000,
     0.100, 0.100,
     0.500, 2200.00, 1600.00,
     1, 'System', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
     
    ('Mild Steel 2mm - Standard', 'Mild Steel', 2.0, 'Standard cutting parameters for 2mm mild steel',
     '1.5mm Single', 2500.00, 1.000,
     'Oxygen', 1.00,
     2200.00, 2000.00, 85.00, 4500.00,
     0.200, 0.000,
     0.100, 0.100,
     0.800, 2400.00, 1800.00,
     1, 'System', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
     
    ('Mild Steel 3mm - Standard', 'Mild Steel', 3.0, 'Standard cutting parameters for 3mm mild steel',
     '2.0mm Single', 2000.00, 1.200,
     'Oxygen', 1.20,
     2400.00, 2200.00, 90.00, 4000.00,
     0.250, 0.000,
     0.150, 0.150,
     1.200, 2600.00, 2000.00,
     1, 'System', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP);

-- Stainless Steel Presets
INSERT INTO machine_settings_presets (
    preset_name, material_type, thickness, description,
    nozzle, cut_speed, nozzle_height,
    gas_type, gas_pressure,
    peak_power, actual_power, duty_cycle, pulse_frequency,
    beam_width, focus_position,
    laser_on_delay, laser_off_delay,
    pierce_time, pierce_power, corner_power,
    is_active, created_by, created_at, updated_at
) VALUES
    ('Stainless Steel 1mm - Standard', 'Stainless Steel', 1.0, 'Standard cutting parameters for 1mm stainless steel',
     '1.5mm Single', 2800.00, 1.000,
     'Nitrogen', 12.00,
     2000.00, 1800.00, 80.00, 5000.00,
     0.200, 0.000,
     0.100, 0.100,
     0.600, 2200.00, 1600.00,
     1, 'System', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
     
    ('Stainless Steel 2mm - Standard', 'Stainless Steel', 2.0, 'Standard cutting parameters for 2mm stainless steel',
     '1.5mm Single', 2200.00, 1.000,
     'Nitrogen', 14.00,
     2200.00, 2000.00, 85.00, 4500.00,
     0.200, 0.000,
     0.100, 0.100,
     1.000, 2400.00, 1800.00,
     1, 'System', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP);

-- Aluminum Presets
INSERT INTO machine_settings_presets (
    preset_name, material_type, thickness, description,
    nozzle, cut_speed, nozzle_height,
    gas_type, gas_pressure,
    peak_power, actual_power, duty_cycle, pulse_frequency,
    beam_width, focus_position,
    laser_on_delay, laser_off_delay,
    pierce_time, pierce_power, corner_power,
    is_active, created_by, created_at, updated_at
) VALUES
    ('Aluminum 1mm - Standard', 'Aluminum', 1.0, 'Standard cutting parameters for 1mm aluminum',
     '1.5mm Single', 2500.00, 1.000,
     'Nitrogen', 10.00,
     2200.00, 2000.00, 85.00, 5000.00,
     0.200, 0.000,
     0.100, 0.100,
     0.700, 2400.00, 1800.00,
     1, 'System', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
     
    ('Aluminum 2mm - Standard', 'Aluminum', 2.0, 'Standard cutting parameters for 2mm aluminum',
     '2.0mm Single', 2000.00, 1.200,
     'Nitrogen', 12.00,
     2400.00, 2200.00, 90.00, 4500.00,
     0.250, 0.000,
     0.150, 0.150,
     1.200, 2600.00, 2000.00,
     1, 'System', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP);

-- ============================================================================
-- MIGRATION COMPLETE
-- ============================================================================
-- Tables created:
--   - operators (with 3 initial operators)
--   - machine_settings_presets (with 8 sample presets)
-- 
-- Tables modified:
--   - laser_runs (added preset_id column)
--
-- To verify the migration:
--   SELECT COUNT(*) FROM operators;
--   SELECT COUNT(*) FROM machine_settings_presets;
--   PRAGMA table_info(laser_runs);
-- ============================================================================

