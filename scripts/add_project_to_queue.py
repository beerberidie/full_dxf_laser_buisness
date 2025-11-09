"""
Script to manually add project JB-2025-10-CL0002-009 to the queue.
This fixes the issue where auto-queue didn't trigger due to inventory thickness mismatch.
"""

import sqlite3
import sys
from datetime import date
from pathlib import Path

# Get database path
db_path = Path(__file__).parent.parent / 'data' / 'laser_os.db'

if not db_path.exists():
    print(f'Error: Database not found at {db_path}')
    sys.exit(1)

# Connect to database
conn = sqlite3.connect(str(db_path))
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

try:
    # Get project details
    cursor.execute('''
        SELECT id, project_code, estimated_cut_time
        FROM projects 
        WHERE project_code = ?
    ''', ('JB-2025-10-CL0002-009',))

    project = cursor.fetchone()

    if not project:
        print('Error: Project JB-2025-10-CL0002-009 not found!')
        sys.exit(1)

    print('=== ADDING PROJECT TO QUEUE ===')
    print(f'Project: {project["project_code"]}')
    print(f'Estimated Cut Time: {project["estimated_cut_time"]} minutes')

    # Check if already in queue
    cursor.execute('''
        SELECT id, queue_position, status
        FROM queue_items
        WHERE project_id = ?
    ''', (project['id'],))
    
    existing = cursor.fetchone()
    if existing:
        print(f'\nProject is already in queue!')
        print(f'  Queue Item ID: {existing["id"]}')
        print(f'  Position: {existing["queue_position"]}')
        print(f'  Status: {existing["status"]}')
        sys.exit(0)

    # Get next queue position
    cursor.execute('SELECT MAX(queue_position) FROM queue_items')
    max_position = cursor.fetchone()[0] or 0
    next_position = max_position + 1

    print(f'Queue Position: {next_position}')

    # Create queue item
    today = date.today().isoformat()
    cursor.execute('''
        INSERT INTO queue_items (
            project_id, queue_position, status, priority, scheduled_date,
            estimated_cut_time, notes, added_by, added_at, created_at, updated_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
    ''', (
        project['id'],
        next_position,
        'Queued',
        'Normal',
        today,
        project['estimated_cut_time'],
        'Manually added after fixing inventory thickness mismatch',
        'System (Manual Fix)',
    ))

    queue_item_id = cursor.lastrowid

    # Log activity
    cursor.execute('''
        INSERT INTO activity_log (
            entity_type, entity_id, action, details, user, created_at
        ) VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
    ''', (
        'QUEUE',
        queue_item_id,
        'ADDED',
        f'Manually added project {project["project_code"]} to queue at position {next_position} (fixing missed auto-queue)',
        'System (Manual Fix)'
    ))

    conn.commit()

    print('\n✓ Queue item created successfully!')
    print(f'  Queue Item ID: {queue_item_id}')
    print(f'  Status: Queued')
    print(f'  Priority: Normal')
    print(f'  Scheduled Date: {today}')

    # Verify
    cursor.execute('''
        SELECT qi.id, qi.queue_position, qi.status, qi.priority, qi.scheduled_date,
               qi.estimated_cut_time, p.project_code, p.name
        FROM queue_items qi
        JOIN projects p ON qi.project_id = p.id
        WHERE qi.id = ?
    ''', (queue_item_id,))

    item = cursor.fetchone()
    if item:
        print('\n✓ Verified queue entry:')
        print(f'  Project: {item["project_code"]} - {item["name"]}')
        print(f'  Position: {item["queue_position"]}')
        print(f'  Status: {item["status"]}')
        print(f'  Priority: {item["priority"]}')
        print(f'  Scheduled: {item["scheduled_date"]}')
        print(f'  Est. Cut Time: {item["estimated_cut_time"]} min')

    print('\n✓ Project successfully added to Queue!')

except Exception as e:
    conn.rollback()
    print(f'\nError: {e}')
    import traceback
    traceback.print_exc()
    sys.exit(1)
finally:
    conn.close()

