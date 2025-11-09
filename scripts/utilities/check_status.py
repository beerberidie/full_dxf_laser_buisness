"""Quick status check script"""
import sqlite3

conn = sqlite3.connect('data/laser_os.db')
cursor = conn.cursor()

tables = ['clients', 'projects', 'products', 'design_files', 'queue_items', 
          'laser_runs', 'inventory_items', 'quotes', 'invoices', 'activity_log']

print("Database Record Counts:")
print("="*50)
for table in tables:
    try:
        cursor.execute(f'SELECT COUNT(*) FROM {table}')
        count = cursor.fetchone()[0]
        print(f'{table:25} {count:5} records')
    except Exception as e:
        print(f'{table:25} ERROR: {e}')

conn.close()

