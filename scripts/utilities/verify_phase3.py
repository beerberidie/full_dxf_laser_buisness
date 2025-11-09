import sqlite3

conn = sqlite3.connect('data/laser_os.db')
cursor = conn.cursor()

# Get all tables
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
tables = [t[0] for t in cursor.fetchall()]

print(f"Total tables: {len(tables)}")
print("\nNew tables:")
for t in tables:
    if t in ['operators', 'machine_settings_presets']:
        print(f"  ✅ {t}")

# Get counts
cursor.execute("SELECT COUNT(*) FROM operators")
op_count = cursor.fetchone()[0]

cursor.execute("SELECT COUNT(*) FROM machine_settings_presets")
preset_count = cursor.fetchone()[0]

print(f"\nData:")
print(f"  • Operators: {op_count}")
print(f"  • Presets: {preset_count}")

# Show sample data
print(f"\nSample Operators:")
cursor.execute("SELECT id, name FROM operators")
for op in cursor.fetchall():
    print(f"  • ID {op[0]}: {op[1]}")

print(f"\nSample Presets:")
cursor.execute("SELECT id, preset_name, material_type, thickness FROM machine_settings_presets LIMIT 3")
for preset in cursor.fetchall():
    print(f"  • ID {preset[0]}: {preset[1]} ({preset[2]} {preset[3]}mm)")

conn.close()
print("\n✅ Phase 3 migration verified successfully!")

