# Technical Specification: Machine Settings Preset System
**Date:** 2025-10-16  
**Version:** 1.0

---

## 1. Database Schema Design

### 1.1 Machine Settings Presets Table

```sql
CREATE TABLE machine_settings_presets (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    
    -- Identification
    preset_name VARCHAR(200) NOT NULL,
    material_type VARCHAR(100) NOT NULL,
    thickness DECIMAL(10, 3) NOT NULL,
    
    -- Cutting Parameters
    nozzle VARCHAR(50),                    -- e.g., "1.5mm Single", "2.0mm Double"
    cut_speed DECIMAL(10, 2),              -- mm/min
    nozzle_height DECIMAL(10, 3),          -- mm
    
    -- Gas Settings
    gas_type VARCHAR(50),                  -- e.g., "Oxygen", "Nitrogen", "Air"
    gas_pressure DECIMAL(10, 2),           -- bar
    
    -- Power Settings
    peak_power DECIMAL(10, 2),             -- Watts or %
    actual_power DECIMAL(10, 2),           -- Watts or %
    duty_cycle DECIMAL(5, 2),              -- %
    pulse_frequency DECIMAL(10, 2),        -- Hz
    
    -- Beam Settings
    beam_width DECIMAL(10, 3),             -- mm
    focus_position DECIMAL(10, 3),         -- mm (focal offset)
    
    -- Timing Settings
    laser_on_delay DECIMAL(10, 3),         -- milliseconds
    laser_off_delay DECIMAL(10, 3),        -- milliseconds
    
    -- Power Curve
    power_curve VARCHAR(20),               -- "On" or "Off"
    
    -- Additional Information
    notes TEXT,
    is_active BOOLEAN DEFAULT 1,
    
    -- Metadata
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(100),
    updated_by VARCHAR(100),
    
    -- Constraints
    UNIQUE(material_type, thickness),
    CHECK(is_active IN (0, 1))
);

-- Indexes
CREATE INDEX idx_presets_material_type ON machine_settings_presets(material_type);
CREATE INDEX idx_presets_thickness ON machine_settings_presets(thickness);
CREATE INDEX idx_presets_active ON machine_settings_presets(is_active);
CREATE INDEX idx_presets_material_thickness ON machine_settings_presets(material_type, thickness);
```

### 1.2 Operators Table

```sql
CREATE TABLE operators (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(100) NOT NULL UNIQUE,
    email VARCHAR(100),
    phone VARCHAR(50),
    is_active BOOLEAN DEFAULT 1,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    
    CHECK(is_active IN (0, 1))
);

-- Indexes
CREATE INDEX idx_operators_name ON operators(name);
CREATE INDEX idx_operators_active ON operators(is_active);
```

### 1.3 Projects Table Update

```sql
-- Add material_thickness column
ALTER TABLE projects ADD COLUMN material_thickness DECIMAL(10, 3);

-- Add index
CREATE INDEX idx_projects_material_thickness ON projects(material_thickness);
```

### 1.4 LaserRuns Table Update

```sql
-- Add preset reference
ALTER TABLE laser_runs ADD COLUMN preset_id INTEGER;
ALTER TABLE laser_runs ADD FOREIGN KEY (preset_id) 
    REFERENCES machine_settings_presets(id) ON DELETE SET NULL;

-- Add index
CREATE INDEX idx_laser_runs_preset_id ON laser_runs(preset_id);
```

---

## 2. Model Definitions

### 2.1 MachineSettingsPreset Model

```python
class MachineSettingsPreset(db.Model):
    """Machine settings preset for laser cutting operations."""
    
    __tablename__ = 'machine_settings_presets'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # Identification
    preset_name = db.Column(db.String(200), nullable=False)
    material_type = db.Column(db.String(100), nullable=False, index=True)
    thickness = db.Column(db.Numeric(10, 3), nullable=False, index=True)
    
    # Cutting Parameters
    nozzle = db.Column(db.String(50))
    cut_speed = db.Column(db.Numeric(10, 2))
    nozzle_height = db.Column(db.Numeric(10, 3))
    
    # Gas Settings
    gas_type = db.Column(db.String(50))
    gas_pressure = db.Column(db.Numeric(10, 2))
    
    # Power Settings
    peak_power = db.Column(db.Numeric(10, 2))
    actual_power = db.Column(db.Numeric(10, 2))
    duty_cycle = db.Column(db.Numeric(5, 2))
    pulse_frequency = db.Column(db.Numeric(10, 2))
    
    # Beam Settings
    beam_width = db.Column(db.Numeric(10, 3))
    focus_position = db.Column(db.Numeric(10, 3))
    
    # Timing Settings
    laser_on_delay = db.Column(db.Numeric(10, 3))
    laser_off_delay = db.Column(db.Numeric(10, 3))
    
    # Power Curve
    power_curve = db.Column(db.String(20))
    
    # Additional
    notes = db.Column(db.Text)
    is_active = db.Column(db.Boolean, default=True, index=True)
    
    # Metadata
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    created_by = db.Column(db.String(100))
    updated_by = db.Column(db.String(100))
    
    # Relationships
    laser_runs = db.relationship('LaserRun', backref='preset', lazy=True)
    
    def __repr__(self):
        return f'<Preset {self.material_type} {self.thickness}mm>'
    
    def to_dict(self):
        """Convert to dictionary for JSON serialization."""
        return {
            'id': self.id,
            'preset_name': self.preset_name,
            'material_type': self.material_type,
            'thickness': float(self.thickness) if self.thickness else None,
            'nozzle': self.nozzle,
            'cut_speed': float(self.cut_speed) if self.cut_speed else None,
            'nozzle_height': float(self.nozzle_height) if self.nozzle_height else None,
            'gas_type': self.gas_type,
            'gas_pressure': float(self.gas_pressure) if self.gas_pressure else None,
            'peak_power': float(self.peak_power) if self.peak_power else None,
            'actual_power': float(self.actual_power) if self.actual_power else None,
            'duty_cycle': float(self.duty_cycle) if self.duty_cycle else None,
            'pulse_frequency': float(self.pulse_frequency) if self.pulse_frequency else None,
            'beam_width': float(self.beam_width) if self.beam_width else None,
            'focus_position': float(self.focus_position) if self.focus_position else None,
            'laser_on_delay': float(self.laser_on_delay) if self.laser_on_delay else None,
            'laser_off_delay': float(self.laser_off_delay) if self.laser_off_delay else None,
            'power_curve': self.power_curve,
            'notes': self.notes,
            'is_active': self.is_active
        }
```

### 2.2 Operator Model

```python
class Operator(db.Model):
    """Operator/user who performs laser cutting operations."""
    
    __tablename__ = 'operators'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True, index=True)
    email = db.Column(db.String(100))
    phone = db.Column(db.String(50))
    is_active = db.Column(db.Boolean, default=True, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    def __repr__(self):
        return f'<Operator {self.name}>'
    
    @staticmethod
    def get_active_operators():
        """Get list of active operators."""
        return Operator.query.filter_by(is_active=True).order_by(Operator.name).all()
```

---

## 3. API Endpoints

### 3.1 Preset Management Routes

```python
# List all presets
GET /settings/presets
Response: HTML page with preset table

# Create new preset form
GET /settings/presets/new
Response: HTML form

# Save new preset
POST /settings/presets/new
Request Body: Form data with all preset fields
Response: Redirect to preset list

# Edit preset form
GET /settings/presets/<id>/edit
Response: HTML form with preset data

# Update preset
POST /settings/presets/<id>/edit
Request Body: Form data with updated fields
Response: Redirect to preset list

# Delete preset
POST /settings/presets/<id>/delete
Response: Redirect to preset list

# Toggle active status
POST /settings/presets/<id>/toggle
Response: JSON {success: true, is_active: boolean}
```

### 3.2 Preset API (AJAX)

```python
# Get presets by material and thickness
GET /api/presets?material=<type>&thickness=<value>
Response: JSON array of matching presets

Example:
GET /api/presets?material=Mild%20Steel&thickness=3.0
Response:
{
    "success": true,
    "presets": [
        {
            "id": 1,
            "preset_name": "Mild Steel 3mm Standard",
            "material_type": "Mild Steel",
            "thickness": 3.0,
            "nozzle": "1.5mm Single",
            "cut_speed": 1200.0,
            ...
        }
    ]
}

# Get single preset details
GET /api/presets/<id>
Response: JSON with full preset details
```

### 3.3 Operator Management Routes

```python
# List operators
GET /settings/operators
Response: HTML page with operator table

# Add operator
POST /settings/operators/new
Request Body: {name, email, phone}
Response: Redirect to operator list

# Delete operator
POST /settings/operators/<id>/delete
Response: Redirect to operator list

# Toggle active status
POST /settings/operators/<id>/toggle
Response: JSON {success: true, is_active: boolean}
```

---

## 4. Frontend Implementation

### 4.1 Laser Run Form Updates

**File:** `app/templates/queue/run_form.html`

```html
<!-- Material Type Dropdown -->
<div class="form-group">
    <label for="material_type">Material Type:</label>
    <select id="material_type" name="material_type" class="form-control">
        <option value="">Select material...</option>
        {% for material in material_types %}
        <option value="{{ material }}">{{ material }}</option>
        {% endfor %}
    </select>
</div>

<!-- Material Thickness -->
<div class="form-group">
    <label for="material_thickness">Material Thickness (mm):</label>
    <input type="number" id="material_thickness" name="material_thickness" 
           class="form-control" step="0.1" min="0" placeholder="e.g., 3.0">
</div>

<!-- Preset Selection -->
<div class="form-group">
    <label for="preset_id">Machine Settings Preset:</label>
    <select id="preset_id" name="preset_id" class="form-control">
        <option value="">Select preset...</option>
    </select>
    <small class="form-help">Select material and thickness first</small>
</div>

<!-- Preset Details Display (Read-only) -->
<div id="preset-details" class="preset-details" style="display: none;">
    <h4>Preset Settings</h4>
    <div class="grid grid-3">
        <div><strong>Nozzle:</strong> <span id="preset-nozzle">-</span></div>
        <div><strong>Cut Speed:</strong> <span id="preset-cut-speed">-</span> mm/min</div>
        <div><strong>Gas Type:</strong> <span id="preset-gas-type">-</span></div>
        <!-- ... more fields ... -->
    </div>
</div>

<!-- Operator Dropdown -->
<div class="form-group">
    <label for="operator">Operator:</label>
    <select id="operator" name="operator" class="form-control">
        <option value="">Select operator...</option>
        {% for op in operators %}
        <option value="{{ op.name }}">{{ op.name }}</option>
        {% endfor %}
    </select>
</div>
```

### 4.2 JavaScript for Dynamic Preset Loading

```javascript
// Listen for material and thickness changes
document.getElementById('material_type').addEventListener('change', loadPresets);
document.getElementById('material_thickness').addEventListener('input', loadPresets);

function loadPresets() {
    const material = document.getElementById('material_type').value;
    const thickness = document.getElementById('material_thickness').value;
    
    if (!material || !thickness) {
        document.getElementById('preset_id').innerHTML = '<option value="">Select material and thickness first</option>';
        document.getElementById('preset-details').style.display = 'none';
        return;
    }
    
    // Fetch presets
    fetch(`/api/presets?material=${encodeURIComponent(material)}&thickness=${thickness}`)
        .then(response => response.json())
        .then(data => {
            const presetSelect = document.getElementById('preset_id');
            presetSelect.innerHTML = '<option value="">Select preset...</option>';
            
            if (data.success && data.presets.length > 0) {
                data.presets.forEach(preset => {
                    const option = document.createElement('option');
                    option.value = preset.id;
                    option.textContent = preset.preset_name;
                    option.dataset.preset = JSON.stringify(preset);
                    presetSelect.appendChild(option);
                });
            } else {
                presetSelect.innerHTML = '<option value="">No presets found</option>';
            }
        });
}

// Display preset details when selected
document.getElementById('preset_id').addEventListener('change', function() {
    const selectedOption = this.options[this.selectedIndex];
    
    if (selectedOption.dataset.preset) {
        const preset = JSON.parse(selectedOption.dataset.preset);
        displayPresetDetails(preset);
    } else {
        document.getElementById('preset-details').style.display = 'none';
    }
});

function displayPresetDetails(preset) {
    document.getElementById('preset-nozzle').textContent = preset.nozzle || '-';
    document.getElementById('preset-cut-speed').textContent = preset.cut_speed || '-';
    document.getElementById('preset-gas-type').textContent = preset.gas_type || '-';
    // ... populate all fields ...
    
    document.getElementById('preset-details').style.display = 'block';
}
```

---

## 5. Migration Strategy

### 5.1 Migration Script

**File:** `migrations/schema_v10_enhancements.sql`

```sql
-- Create new tables
-- (See section 1 for full SQL)

-- Seed initial operators
INSERT INTO operators (name, is_active) VALUES
    ('Operator 1', 1),
    ('Operator 2', 1),
    ('Operator 3', 1);

-- Update schema version
UPDATE settings SET value = '10.0', updated_at = CURRENT_TIMESTAMP 
WHERE key = 'schema_version';
```

### 5.2 Python Migration Script

**File:** `apply_phase10_migration.py`

```python
import sqlite3
import os
from datetime import datetime

def apply_migration():
    db_path = 'data/laser_os.db'
    
    # Backup database
    backup_path = f'data/laser_os_backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.db'
    import shutil
    shutil.copy2(db_path, backup_path)
    print(f'✓ Database backed up to {backup_path}')
    
    # Apply migration
    conn = sqlite3.connect(db_path)
    with open('migrations/schema_v10_enhancements.sql', 'r') as f:
        migration_sql = f.read()
    
    conn.executescript(migration_sql)
    conn.close()
    
    print('✓ Migration applied successfully')

if __name__ == '__main__':
    apply_migration()
```

---

## 6. Testing Strategy

### 6.1 Unit Tests
- Test preset CRUD operations
- Test operator CRUD operations
- Test preset filtering by material/thickness
- Test model validations

### 6.2 Integration Tests
- Test laser run creation with preset
- Test preset API endpoints
- Test form submissions

### 6.3 UI Tests
- Test dropdown population
- Test preset selection and display
- Test auto-fill functionality

---

**End of Technical Specification**

