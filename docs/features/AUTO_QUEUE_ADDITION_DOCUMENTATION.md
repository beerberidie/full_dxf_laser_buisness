# Automatic Queue Addition Feature

## Overview
The Laser OS application now automatically adds projects to the production queue when POP (Proof of Payment) is marked as received. This streamlines the workflow and ensures projects are scheduled for cutting within the 3-day POP deadline.

## Feature Description

### What It Does
When a user marks POP as received on a project (via the "Toggle POP" button on the project detail page), the system automatically:

1. ✅ Creates a QueueItem for the project
2. ✅ Assigns the next available queue position
3. ✅ Sets sensible default values
4. ✅ Logs the activity for audit trail
5. ✅ Notifies the user with flash messages

### Default Values

When a project is automatically added to the queue, the following defaults are used:

| Field | Default Value | Source |
|-------|---------------|--------|
| **Status** | `Queued` | System constant |
| **Priority** | `Normal` | System constant |
| **Scheduled Date** | Today's date | `date.today()` |
| **Estimated Cut Time** | Project's estimated cut time | `project.estimated_cut_time` |
| **Queue Position** | Next available position | Auto-calculated |
| **Added By** | `System (Auto)` | System identifier |
| **Notes** | "Automatically added to queue when POP was received" | System message |

## How It Works

### User Workflow

1. **Navigate to Project Detail Page**
   - Go to http://127.0.0.1:5000/projects/{project_id}

2. **Mark POP as Received**
   - Click the "Toggle POP" button
   - System sets POP received date to today
   - System calculates POP deadline (today + 3 days)

3. **Automatic Queue Addition**
   - System automatically creates a queue item
   - User sees success messages:
     - "✓ POP marked as received. Deadline: {date}"
     - "✓ Project automatically added to queue at position {position}"

4. **View in Queue**
   - Navigate to http://127.0.0.1:5000/queue/
   - Project appears in the production queue

### Technical Implementation

#### Modified Function: `toggle_pop()`
**File:** `app/routes/projects.py`

The `toggle_pop()` function now includes automatic queue addition:

```python
@bp.route('/<int:id>/toggle-pop', methods=['POST'])
def toggle_pop(id):
    """Toggle POP received status and calculate deadline."""
    project = Project.query.get_or_404(id)
    
    # Toggle POP received
    project.pop_received = not project.pop_received
    
    if project.pop_received:
        # Set POP dates
        project.pop_received_date = date.today()
        project.calculate_pop_deadline()
        
        # Automatically add to queue
        success, message = auto_add_to_queue(project)
        
        if success:
            db.session.commit()
            flash(f'✓ {message}', 'success')
        else:
            # Handle duplicates gracefully
            flash(f'ℹ {message}', 'info')
```

#### New Helper Function: `auto_add_to_queue()`
**File:** `app/routes/projects.py`

This function handles the automatic queue addition logic:

```python
def auto_add_to_queue(project):
    """
    Automatically add a project to the production queue.
    
    Returns:
        tuple: (success: bool, message: str)
    """
    # Check for duplicates
    # Calculate next position
    # Create QueueItem with defaults
    # Log activity
    # Return success/failure
```

## Duplicate Prevention

The system prevents duplicate queue entries:

### Scenarios Handled:

1. **Project Already Queued**
   - Message: "Project {code} is already in the queue"
   - Action: No new queue item created
   - User notification: Info message (blue)

2. **Project Already In Progress**
   - Message: "Project {code} is already in progress"
   - Action: No new queue item created
   - User notification: Info message (blue)

3. **First Time Adding**
   - Message: "Project automatically added to queue at position {position}"
   - Action: Queue item created successfully
   - User notification: Success message (green)

## Activity Logging

All automatic queue additions are logged in the `activity_logs` table:

```json
{
  "entity_type": "QUEUE",
  "entity_id": 123,
  "action": "ADDED",
  "details": "Automatically added project JB-2025-10-CL0001-002 to queue at position 1 (POP received)",
  "user": "System (Auto)"
}
```

This provides a complete audit trail for compliance and troubleshooting.

## Manual Override

The existing manual "Add to Queue" functionality remains available:

### When to Use Manual Addition:

1. **Override Defaults**
   - Set custom priority (High, Urgent)
   - Schedule for a different date
   - Add custom notes

2. **Re-queue Completed Projects**
   - Add a project back to queue after completion
   - Useful for repeat orders

3. **Add Without POP**
   - Add projects to queue before POP is received
   - Useful for rush orders or special cases

### How to Manually Add:

1. Navigate to project detail page
2. Scroll to "Queue Management" section
3. Click "Add to Queue" button
4. Fill in the form with custom values
5. Click "Add to Queue"

## Testing

### Automated Tests

Run the test script to verify functionality:

```bash
python test_auto_queue_addition.py
```

**Test Coverage:**
- ✅ Automatic queue addition on POP received
- ✅ Duplicate prevention (already queued)
- ✅ Duplicate prevention (already in progress)
- ✅ Queue position calculation
- ✅ Default values assignment
- ✅ Activity logging

### Manual Testing

1. **Test Basic Flow:**
   ```
   1. Create a new project
   2. Mark POP as received
   3. Verify project appears in queue
   4. Check queue position and defaults
   ```

2. **Test Duplicate Prevention:**
   ```
   1. Mark POP as received (project added to queue)
   2. Unmark POP
   3. Mark POP as received again
   4. Verify no duplicate queue item created
   ```

3. **Test Manual Override:**
   ```
   1. Mark POP as received (auto-added to queue)
   2. Remove from queue
   3. Manually add with custom priority
   4. Verify custom values are used
   ```

## Benefits

### For Users:
- ✅ **Faster Workflow** - No need to manually add to queue
- ✅ **Fewer Errors** - Automatic process reduces human error
- ✅ **Better Compliance** - Projects are scheduled within POP deadline
- ✅ **Clear Audit Trail** - All actions are logged

### For Business:
- ✅ **Improved SLA** - Projects scheduled within 3-day deadline
- ✅ **Better Tracking** - All queue additions are logged
- ✅ **Reduced Manual Work** - Automation saves time
- ✅ **Consistent Process** - Same defaults applied every time

## Configuration

### Environment Variables

No new environment variables are required. The feature uses existing configuration:

- `POP_DEADLINE_DAYS` - Days after POP to schedule (default: 3)
- `MAX_HOURS_PER_DAY` - Maximum working hours per day (default: 8)

### Database Changes

No database schema changes required. Uses existing tables:
- `projects` - POP tracking fields
- `queue_items` - Queue management
- `activity_logs` - Audit trail

## Troubleshooting

### Issue: Project Not Added to Queue

**Possible Causes:**
1. Project already in queue
2. Project already in progress
3. Database error

**Solution:**
- Check flash messages for specific error
- View queue page to verify status
- Check activity logs for details

### Issue: Wrong Queue Position

**Possible Causes:**
1. Multiple users adding simultaneously
2. Queue positions not sequential

**Solution:**
- Queue positions are auto-calculated
- Use drag-and-drop to reorder if needed
- Positions are relative, not absolute

### Issue: Missing Estimated Cut Time

**Possible Causes:**
1. Project doesn't have estimated_cut_time set

**Solution:**
- Edit project to add estimated cut time
- Queue item will have NULL cut time
- Can be updated manually in queue

## Future Enhancements

### Potential Improvements:

1. **Smart Scheduling**
   - Consider business hours
   - Skip weekends
   - Account for capacity

2. **Priority Rules**
   - Auto-set priority based on deadline
   - Urgent if deadline < 1 day
   - High if deadline < 2 days

3. **Notifications**
   - Email notification when added to queue
   - SMS for urgent items
   - Dashboard alerts

4. **Batch Operations**
   - Mark multiple POPs as received
   - Bulk add to queue
   - Batch scheduling

## Related Documentation

- `PHASE_3_IMPLEMENTATION_SUMMARY.md` - POP deadline validation
- `PHASE5_COMPLETE.md` - Queue management features
- `USAGE_GUIDE.md` - User workflow documentation
- `laser_ops_app_spec_Update.md` - Application specification

## Support

For issues or questions:
1. Check the activity logs for error details
2. Review the flash messages on screen
3. Verify project and queue status
4. Run the test script to verify functionality

## Version History

- **v1.0** (2025-10-17) - Initial implementation
  - Automatic queue addition on POP received
  - Duplicate prevention
  - Activity logging
  - Test coverage

