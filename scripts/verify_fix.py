"""
Verify that project JB-2025-10-CL0002-009 is now in the queue.
"""

import sqlite3
from pathlib import Path

db_path = Path(__file__).parent.parent / 'data' / 'laser_os.db'
conn = sqlite3.connect(str(db_path))
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

print('=== VERIFICATION SUMMARY ===\n')

# 1. Check project status
cursor.execute('''
    SELECT project_code, name, status, pop_received, material_type, material_thickness
    FROM projects 
    WHERE project_code = ?
''', ('JB-2025-10-CL0002-009',))

project = cursor.fetchone()
print('1. PROJECT STATUS:')
print(f'   Code: {project["project_code"]}')
print(f'   Name: {project["name"]}')
print(f'   Status: {project["status"]}')
print(f'   POP Received: {"Yes" if project["pop_received"] else "No"}')
print()

# 2. Check inventory match
print('2. INVENTORY AVAILABILITY:')
cursor.execute('''
    SELECT name, thickness, quantity_on_hand
    FROM inventory_items
    WHERE material_type = ? AND thickness = ?
''', (project['material_type'], float(project['material_thickness'])))

inventory = cursor.fetchone()
if inventory:
    print(f'   Found: {inventory["name"]} @ {inventory["thickness"]}mm')
    print(f'   Available: {inventory["quantity_on_hand"]} sheets')
    print(f'   Status: MATCH FOUND')
else:
    print('   Status: NO MATCH')
print()

# 3. Check queue entry
print('3. QUEUE STATUS:')
cursor.execute('''
    SELECT qi.queue_position, qi.status, qi.priority, qi.scheduled_date
    FROM queue_items qi
    JOIN projects p ON qi.project_id = p.id
    WHERE p.project_code = ?
''', ('JB-2025-10-CL0002-009',))

queue_item = cursor.fetchone()
if queue_item:
    print(f'   Position: {queue_item["queue_position"]}')
    print(f'   Status: {queue_item["status"]}')
    print(f'   Priority: {queue_item["priority"]}')
    print(f'   Scheduled: {queue_item["scheduled_date"]}')
    print(f'   IN QUEUE: YES')
else:
    print('   IN QUEUE: NO')
print()

print('=== RESULT ===')
if queue_item:
    print('SUCCESS: Project is in the Queue!')
else:
    print('FAILED: Project is not in the Queue')

conn.close()

