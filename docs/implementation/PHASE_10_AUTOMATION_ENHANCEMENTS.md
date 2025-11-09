# 🚀 Phase 10: Automation & Workflow Enhancements

**Date:** October 21, 2025  
**Status:** 📋 PLANNED  
**Priority:** HIGH

---

## 📖 Overview

This phase implements intelligent automation features to streamline the Laser OS workflow, reducing manual data entry and automating scheduling decisions based on inventory availability and project readiness.

### Key Objectives

1. **Smart Auto-Scheduling** - Automatically schedule projects for cutting when POP received and inventory available
2. **Material Management** - Add new material types and implement gas type rules
3. **Operator Management** - Create operator management system with user account linking
4. **Intelligent Pre-filling** - Auto-populate laser run forms from project data
5. **Workflow Optimization** - Remove obsolete POP deadline messages and update business logic

---

## 🎯 Business Rules & Logic

### Auto-Scheduling Conditions

A project is **automatically scheduled for cutting** when ALL conditions are met:

```
✅ POP Received (payment confirmed)
✅ All Material & Production Information fields are filled (NOT NULL):
   - material_type
   - material_thickness
   - material_quantity_sheets
   - parts_quantity
   - estimated_cut_time
✅ Inventory Available:
   - inventory_stock >= project.material_quantity_sheets
   - matching material_type AND material_thickness
```

**Action:** Add to Queue with:
- Priority: Normal (or High if urgent)
- Scheduled Date: Today or next business day
- Status: Ready to Cut
- **Reserve Inventory:** Deduct `material_quantity_sheets` from available stock

### Material Ordering Workflow

When POP is received but inventory is insufficient:

```
❌ POP Received
❌ Material & Production fields filled
❌ Inventory Available < Required

→ Show Alert: "Insufficient material - Order required"
→ Trigger Material Order (future: auto-order from suppliers)
→ Project Status: "Awaiting Material"
```

### Gas Type Rules

**Automatic gas type selection based on material thickness:**

| Thickness Range | Gas Type | Materials |
|----------------|----------|-----------|
| **6mm - 16mm** | **Oxygen (OXY)** | All materials |
| **< 6mm** | **Air** | Mild Steel, Stainless Steel, Carbon Steel |
| **< 6mm** | **Nitrogen** | Aluminum, Zinc (optional: user choice) |

### Material Thickness Options

**Allowed thickness values:**
- `0.47mm` (thin Carbon Steel)
- `0.53mm` (thin Carbon Steel)
- `1.0mm, 1.5mm, 2.0mm, 2.5mm, 3.0mm, 3.5mm, 4.0mm, 4.5mm, 5.0mm, 5.5mm, 6.0mm`
- `6.5mm, 7.0mm, 7.5mm, 8.0mm, 8.5mm, 9.0mm, 9.5mm, 10.0mm`
- `10.5mm, 11.0mm, 11.5mm, 12.0mm, 12.5mm, 13.0mm, 13.5mm, 14.0mm`
- `14.5mm, 15.0mm, 15.5mm, 16.0mm`

**Increments:** 0.5mm from 1mm to 16mm

---

## 📋 Implementation Phases

### **Phase 1: Material Type & Gas Rules Enhancement**

#### 1.1 Add New Material Types

**Files to Update:**
- `config.py` - Add to `MATERIAL_TYPES` list
- All templates with material dropdowns

**New Materials:**
- ✅ **Carbon Steel** - For thin materials (0.47mm/0.53mm primarily)
- ✅ **Zinc** - Requires Nitrogen gas for cutting

**Updated MATERIAL_TYPES:**
```python
MATERIAL_TYPES = [
    'Mild Steel',
    'Stainless Steel',
    'Carbon Steel',      # NEW
    'Aluminum',
    'Zinc',              # NEW
    'Copper',
    'Brass',
    'Other'
]
```

#### 1.2 Implement Gas Type Rules

**Create:** `app/services/gas_type_service.py`

```python
def get_recommended_gas_type(material_type: str, thickness: float) -> str:
    """
    Get recommended gas type based on material and thickness.
    
    Rules:
    - 6mm to 16mm: Always Oxygen (OXY)
    - < 6mm: Air (default) or Nitrogen (for Aluminum/Zinc)
    """
    if thickness >= 6.0:
        return 'Oxygen'
    
    if material_type in ['Aluminum', 'Zinc']:
        return 'Nitrogen'
    
    return 'Air'
```

**Update:** Machine Settings Presets form to auto-select gas type

#### 1.3 Material Thickness Validation

**Update:** Project form and Inventory form to validate thickness values

**Add:** Dropdown or input validation for allowed thickness increments

---

### **Phase 2: Operator Management Module**

#### 2.1 Update Operator Model

**File:** `app/models/business.py`

**Add field:**
```python
class Operator(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)  # NEW
    # ... existing fields
    
    # Relationship
    user = db.relationship('User', backref='operator_profile')
```

**Migration:** `migrations/schema_v10_operator_user_link.sql`

#### 2.2 Create Operator Routes

**Create:** `app/routes/operators.py`

**Routes:**
- `GET /operators` - List all operators
- `GET /operators/new` - New operator form
- `POST /operators` - Create operator
- `GET /operators/<id>` - Operator detail
- `GET /operators/<id>/edit` - Edit operator form
- `POST /operators/<id>/update` - Update operator
- `POST /operators/<id>/delete` - Delete operator

#### 2.3 Create Operator Templates

**Create:**
- `app/templates/operators/list.html` - Operators list with search/filter
- `app/templates/operators/form.html` - Create/Edit operator form
- `app/templates/operators/detail.html` - Operator detail page

**Features:**
- Link operator to user account (dropdown)
- Track operator skills/certifications (future)
- View operator's laser run history
- Performance metrics (future)

#### 2.4 Update Navigation

**File:** `app/templates/base.html`

**Add to sidebar:**
```html
<li>
    <a href="{{ url_for('operators.list') }}">
        <i class="fas fa-user-hard-hat"></i>
        <span>Operators</span>
    </a>
</li>
```

#### 2.5 Update Laser Run Form

**File:** `app/templates/queue/log_laser_run.html`

**Change:** Replace text input with operator dropdown

```html
<select name="operator_id" required>
    <option value="">Select Operator</option>
    {% for operator in operators %}
    <option value="{{ operator.id }}">{{ operator.name }}</option>
    {% endfor %}
</select>
```

---

### **Phase 3: Inventory-Based Auto-Scheduling**

#### 3.1 Create Inventory Availability Service

**Create:** `app/services/inventory_service.py`

```python
def check_material_availability(
    material_type: str,
    material_thickness: float,
    required_sheets: int
) -> dict:
    """
    Check if inventory has enough material for a project.
    
    Returns:
        {
            'available': bool,
            'current_stock': int,
            'required': int,
            'shortage': int (if available=False)
        }
    """
    # Query inventory for matching material
    inventory_items = Inventory.query.filter_by(
        material_type=material_type,
        thickness=material_thickness,
        status='In Stock'
    ).all()
    
    total_stock = sum(item.quantity for item in inventory_items)
    
    return {
        'available': total_stock >= required_sheets,
        'current_stock': total_stock,
        'required': required_sheets,
        'shortage': max(0, required_sheets - total_stock)
    }
```

#### 3.2 Create Auto-Scheduling Service

**Create:** `app/services/auto_scheduler.py`

```python
def auto_schedule_project(project_id: int) -> dict:
    """
    Automatically schedule project for cutting if conditions are met.
    
    Conditions:
    1. POP received
    2. All Material & Production fields filled
    3. Inventory available
    
    Returns:
        {
            'scheduled': bool,
            'message': str,
            'queue_item': QueueItem (if scheduled)
        }
    """
    project = Project.query.get(project_id)
    
    # Check POP received
    if not project.pop_received:
        return {'scheduled': False, 'message': 'POP not received'}
    
    # Check Material & Production fields
    if not all([
        project.material_type,
        project.material_thickness,
        project.material_quantity_sheets,
        project.parts_quantity,
        project.estimated_cut_time
    ]):
        return {'scheduled': False, 'message': 'Material & Production information incomplete'}
    
    # Check inventory
    availability = check_material_availability(
        project.material_type,
        project.material_thickness,
        project.material_quantity_sheets
    )
    
    if not availability['available']:
        return {
            'scheduled': False,
            'message': f"Insufficient material - Need {availability['shortage']} more sheets"
        }
    
    # All conditions met - Schedule!
    queue_item = add_to_queue(
        project_id=project.id,
        priority='Normal',
        scheduled_date=date.today(),  # or next business day
        notes='Auto-scheduled: POP received + inventory available'
    )
    
    # Reserve inventory
    reserve_inventory(
        material_type=project.material_type,
        material_thickness=project.material_thickness,
        quantity=project.material_quantity_sheets,
        project_id=project.id
    )
    
    return {
        'scheduled': True,
        'message': 'Project auto-scheduled for cutting',
        'queue_item': queue_item
    }
```

#### 3.3 Implement Inventory Reservation

**Update:** `app/services/inventory_service.py`

```python
def reserve_inventory(
    material_type: str,
    material_thickness: float,
    quantity: int,
    project_id: int
) -> bool:
    """
    Reserve/deduct inventory when project is scheduled.
    
    Creates inventory transaction record for tracking.
    """
    # Find inventory items with enough stock
    inventory_items = Inventory.query.filter_by(
        material_type=material_type,
        thickness=material_thickness,
        status='In Stock'
    ).order_by(Inventory.created_at).all()
    
    remaining = quantity
    
    for item in inventory_items:
        if remaining <= 0:
            break
        
        deduct = min(item.quantity, remaining)
        item.quantity -= deduct
        remaining -= deduct
        
        # Create transaction record
        transaction = InventoryTransaction(
            inventory_id=item.id,
            transaction_type='Reserved',
            quantity=deduct,
            project_id=project_id,
            notes=f'Reserved for project {project_id}'
        )
        db.session.add(transaction)
    
    db.session.commit()
    return True
```

#### 3.4 Update POP Received Handler

**File:** `app/routes/projects.py`

**Update:** `update_project()` route

```python
# After updating project
if request.form.get('pop_received') == 'on':
    # Trigger auto-scheduling
    from app.services.auto_scheduler import auto_schedule_project
    
    result = auto_schedule_project(project.id)
    
    if result['scheduled']:
        flash(f"✅ {result['message']} - Added to queue", 'success')
    else:
        flash(f"⚠️ {result['message']}", 'warning')
```

---

### **Phase 4: Laser Run Auto-Population**

#### 4.1 Update Log Laser Run Route

**File:** `app/routes/queue.py`

**Update:** `log_laser_run()` route

```python
@queue_bp.route('/<int:id>/log-run', methods=['GET', 'POST'])
def log_laser_run(id):
    queue_item = QueueItem.query.get_or_404(id)
    project = queue_item.project
    
    if request.method == 'GET':
        # Pre-fill form data from project
        form_data = {
            'cut_time': project.estimated_cut_time,
            'material_type': project.material_type,
            'material_thickness': project.material_thickness,
            'raw_material_count': project.material_quantity_sheets,
            'parts_produced': project.parts_quantity,
            'preset_id': get_matching_preset(
                project.material_type,
                project.material_thickness
            )
        }
        
        operators = Operator.query.order_by(Operator.name).all()
        presets = MachineSettingsPreset.query.all()
        
        return render_template(
            'queue/log_laser_run.html',
            queue_item=queue_item,
            project=project,
            form_data=form_data,  # Pre-filled data
            operators=operators,
            presets=presets
        )
    
    # POST handling...
```

#### 4.2 Auto-Suggest Machine Settings Preset

**Create:** `app/services/preset_service.py`

```python
def get_matching_preset(material_type: str, material_thickness: float) -> int:
    """
    Find matching machine settings preset based on material and thickness.
    
    Returns preset_id or None
    """
    preset = MachineSettingsPreset.query.filter_by(
        material_type=material_type,
        material_thickness=material_thickness
    ).first()
    
    return preset.id if preset else None
```

---

### **Phase 5: POP Deadline Message Refinement**

#### 5.1 Remove 3-Day Countdown Messages

**Files to Update:**
- `app/templates/dashboard.html`
- `app/templates/projects/list.html`
- `app/templates/projects/detail.html`

**Remove:**
- "POP deadline in X days"
- "POP deadline X days overdue"

#### 5.2 Update POP Status Messages

**New Messages:**
```
✅ POP Received - Auto-scheduled for cutting
⚠️ POP Received - Awaiting material (X sheets needed)
📋 POP Received - Missing production details
❌ Awaiting POP
```

#### 5.3 Update Dashboard Alerts

**File:** `app/routes/main.py`

**Update dashboard logic:**
```python
# Projects awaiting POP
awaiting_pop = Project.query.filter_by(
    pop_received=False,
    status='Approved'
).count()

# Projects auto-scheduled (POP + inventory OK)
auto_scheduled = QueueItem.query.join(Project).filter(
    Project.pop_received == True,
    QueueItem.status == 'Pending'
).count()

# Projects awaiting material (POP received but no inventory)
awaiting_material = Project.query.filter_by(
    pop_received=True
).filter(
    ~Project.id.in_(
        db.session.query(QueueItem.project_id)
    )
).count()
```

---

## 📊 Database Changes

### New Migration: `schema_v10_operator_user_link.sql`

```sql
-- Add user_id to operators table
ALTER TABLE operators ADD COLUMN user_id INTEGER;
ALTER TABLE operators ADD FOREIGN KEY (user_id) REFERENCES users(id);

-- Create index
CREATE INDEX idx_operators_user_id ON operators(user_id);
```

---

## 🧪 Testing Checklist

### Phase 1: Material & Gas Rules
- [ ] Carbon Steel appears in all material dropdowns
- [ ] Zinc appears in all material dropdowns
- [ ] Gas type auto-selects to OXY for 6mm+ thickness
- [ ] Gas type auto-selects to Nitrogen for Aluminum/Zinc < 6mm
- [ ] Thickness validation accepts 0.47mm, 0.53mm, and 0.5mm increments

### Phase 2: Operator Management
- [ ] Can create new operator
- [ ] Can link operator to user account
- [ ] Operator appears in laser run form dropdown
- [ ] Can view operator detail page
- [ ] Can edit/delete operator

### Phase 3: Auto-Scheduling
- [ ] POP received + inventory available → Auto-schedules to queue
- [ ] POP received + insufficient inventory → Shows warning
- [ ] Inventory is reserved when project scheduled
- [ ] Material ordering alert appears when needed
- [ ] Auto-scheduling only triggers when all conditions met

### Phase 4: Laser Run Auto-Population
- [ ] Laser run form pre-fills from project data
- [ ] Machine preset auto-suggests based on material/thickness
- [ ] Pre-filled fields are editable
- [ ] Actual vs estimated values are tracked

### Phase 5: POP Messaging
- [ ] Old "POP deadline in X days" messages removed
- [ ] New status messages appear correctly
- [ ] Dashboard shows correct project counts
- [ ] Alerts reflect new auto-scheduling logic

---

## 📁 Files to Create/Modify

### New Files (8)
1. `app/services/gas_type_service.py`
2. `app/services/inventory_service.py`
3. `app/services/auto_scheduler.py`
4. `app/services/preset_service.py`
5. `app/routes/operators.py`
6. `app/templates/operators/list.html`
7. `app/templates/operators/form.html`
8. `app/templates/operators/detail.html`
9. `migrations/schema_v10_operator_user_link.sql`

### Modified Files (15+)
1. `config.py` - Add material types
2. `app/models/business.py` - Update Operator model
3. `app/routes/projects.py` - Add auto-scheduling trigger
4. `app/routes/queue.py` - Update laser run pre-filling
5. `app/routes/main.py` - Update dashboard logic
6. `app/templates/base.html` - Add Operators to navigation
7. `app/templates/dashboard.html` - Update POP alerts
8. `app/templates/projects/list.html` - Update POP messages
9. `app/templates/projects/detail.html` - Update POP messages
10. `app/templates/projects/form.html` - Add gas type logic
11. `app/templates/queue/log_laser_run.html` - Pre-fill form
12. `app/templates/presets/form.html` - Add gas type auto-select
13. All templates with material dropdowns

---

## 🎯 Success Criteria

✅ **Automation:** Projects auto-schedule when POP received + inventory available  
✅ **Efficiency:** Laser run forms pre-fill from project data (80% less manual entry)  
✅ **Accuracy:** Gas type rules enforced across application  
✅ **Visibility:** Clear status messages show project readiness  
✅ **Tracking:** Operators linked to user accounts for accountability  
✅ **Inventory:** Material reserved when scheduled, preventing double-booking  

---

**Next Steps:** Begin Phase 1 implementation - Material Type & Gas Rules Enhancement

