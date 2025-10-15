-- Laser OS Tier 1 - Seed Data
-- Initial data for the laser cutting business automation system

-- ============================================================================
-- Schema Version
-- ============================================================================

INSERT INTO schema_version (version) VALUES ('v1');

-- ============================================================================
-- Settings
-- ============================================================================

INSERT INTO settings (key, value, description) VALUES
    ('company_name', 'Laser OS', 'Company name for branding'),
    ('operating_hours', 'Mon-Thu 07:00-16:00, Fri 07:00-14:30', 'Operating hours'),
    ('default_sla_days', '3', 'Default SLA in days'),
    ('low_stock_threshold', '3', 'Low stock alert threshold'),
    ('max_thickness_ms', '16', 'Maximum thickness for mild steel (mm)'),
    ('max_thickness_ss', '12', 'Maximum thickness for stainless steel (mm)'),
    ('max_thickness_alu', '10', 'Maximum thickness for aluminum (mm)'),
    ('sheet_size_steel', '1225x2450', 'Standard steel sheet size (mm)'),
    ('sheet_size_acrylic', '1220x2440', 'Standard acrylic sheet size (mm)'),
    ('max_nest_quantity', '20', 'Maximum units per part per nest');

-- ============================================================================
-- Materials
-- ============================================================================

-- Mild Steel (MS)
INSERT INTO materials (material_type, thickness, sheet_size, quantity, cost_per_unit, unit) VALUES
    ('MS', 1.0, '1225x2450', 15, 800.00, 'sheets'),
    ('MS', 1.5, '1225x2450', 12, 1000.00, 'sheets'),
    ('MS', 2.0, '1225x2450', 10, 1200.00, 'sheets'),
    ('MS', 3.0, '1225x2450', 10, 1800.00, 'sheets'),
    ('MS', 4.0, '1225x2450', 8, 2400.00, 'sheets'),
    ('MS', 5.0, '1225x2450', 6, 3000.00, 'sheets'),
    ('MS', 6.0, '1225x2450', 8, 3600.00, 'sheets'),
    ('MS', 8.0, '1225x2450', 5, 4800.00, 'sheets'),
    ('MS', 10.0, '1225x2450', 4, 6000.00, 'sheets'),
    ('MS', 12.0, '1225x2450', 3, 7200.00, 'sheets');

-- Stainless Steel (SS)
INSERT INTO materials (material_type, thickness, sheet_size, quantity, cost_per_unit, unit) VALUES
    ('SS', 1.0, '1225x2450', 8, 2500.00, 'sheets'),
    ('SS', 1.5, '1225x2450', 6, 3200.00, 'sheets'),
    ('SS', 2.0, '1225x2450', 5, 4000.00, 'sheets'),
    ('SS', 3.0, '1225x2450', 5, 6000.00, 'sheets'),
    ('SS', 4.0, '1225x2450', 3, 8000.00, 'sheets'),
    ('SS', 5.0, '1225x2450', 2, 10000.00, 'sheets'),
    ('SS', 6.0, '1225x2450', 2, 12000.00, 'sheets');

-- Galvanized (GALV)
INSERT INTO materials (material_type, thickness, sheet_size, quantity, cost_per_unit, unit) VALUES
    ('GALV', 1.0, '1225x2450', 10, 1000.00, 'sheets'),
    ('GALV', 1.5, '1225x2450', 8, 1300.00, 'sheets'),
    ('GALV', 2.0, '1225x2450', 6, 1600.00, 'sheets'),
    ('GALV', 3.0, '1225x2450', 4, 2400.00, 'sheets');

-- Aluminum (ALU)
INSERT INTO materials (material_type, thickness, sheet_size, quantity, cost_per_unit, unit) VALUES
    ('ALU', 1.0, '1225x2450', 6, 1500.00, 'sheets'),
    ('ALU', 2.0, '1225x2450', 5, 2500.00, 'sheets'),
    ('ALU', 3.0, '1225x2450', 4, 3500.00, 'sheets'),
    ('ALU', 5.0, '1225x2450', 3, 5500.00, 'sheets');

-- Acrylic
INSERT INTO materials (material_type, thickness, sheet_size, quantity, cost_per_unit, unit) VALUES
    ('ACRYLIC', 3.0, '1220x2440', 12, 800.00, 'sheets'),
    ('ACRYLIC', 5.0, '1220x2440', 10, 1200.00, 'sheets'),
    ('ACRYLIC', 6.0, '1220x2440', 8, 1400.00, 'sheets'),
    ('ACRYLIC', 8.0, '1220x2440', 6, 1800.00, 'sheets'),
    ('ACRYLIC', 10.0, '1220x2440', 4, 2200.00, 'sheets');

