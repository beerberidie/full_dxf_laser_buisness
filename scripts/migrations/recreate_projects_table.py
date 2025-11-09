"""
Recreate Projects Table with Phase 2 Schema
"""

import sqlite3
from pathlib import Path

# Database path
db_path = Path(__file__).parent / 'data' / 'laser_os.db'

print("="*80)
print("RECREATING PROJECTS TABLE FOR PHASE 2")
print("="*80)

try:
    # Connect to database
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    
    # Drop existing projects table
    print("\n🗑️  Dropping existing projects table...")
    cursor.execute("DROP TABLE IF EXISTS projects")
    conn.commit()
    print("✅ Old table dropped")
    
    # Create new projects table with Phase 2 schema
    print("\n📝 Creating new projects table...")
    cursor.execute("""
        CREATE TABLE projects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_code VARCHAR(30) UNIQUE NOT NULL,
            client_id INTEGER NOT NULL,
            name VARCHAR(200) NOT NULL,
            description TEXT,
            status VARCHAR(20) NOT NULL DEFAULT 'Quote',
            
            -- Timeline
            quote_date DATE,
            approval_date DATE,
            due_date DATE,
            completion_date DATE,
            
            -- Pricing
            quoted_price DECIMAL(10, 2),
            final_price DECIMAL(10, 2),
            
            -- Additional info
            notes TEXT,
            
            -- Metadata
            created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
            
            -- Foreign Keys
            FOREIGN KEY (client_id) REFERENCES clients(id) ON DELETE CASCADE,
            
            -- Constraints
            CHECK (status IN ('Quote', 'Approved', 'In Progress', 'Completed', 'Cancelled'))
        )
    """)
    conn.commit()
    print("✅ New table created")
    
    # Create indexes
    print("\n📊 Creating indexes...")
    indexes = [
        "CREATE INDEX idx_projects_client_id ON projects(client_id)",
        "CREATE INDEX idx_projects_status ON projects(status)",
        "CREATE INDEX idx_projects_project_code ON projects(project_code)",
        "CREATE INDEX idx_projects_due_date ON projects(due_date)",
        "CREATE INDEX idx_projects_created_at ON projects(created_at)"
    ]
    
    for idx_sql in indexes:
        cursor.execute(idx_sql)
    conn.commit()
    print(f"✅ Created {len(indexes)} indexes")
    
    # Update schema version
    cursor.execute("""
        UPDATE settings 
        SET value = '2.0', updated_at = CURRENT_TIMESTAMP 
        WHERE key = 'schema_version'
    """)
    conn.commit()
    print("✅ Schema version updated to 2.0")
    
    # Verify table structure
    cursor.execute("PRAGMA table_info(projects)")
    columns = cursor.fetchall()
    print(f"\n✅ Projects table has {len(columns)} columns:")
    for col in columns:
        nullable = "NULL" if col[3] == 0 else "NOT NULL"
        default = f" DEFAULT {col[4]}" if col[4] else ""
        print(f"   - {col[1]:<20} {col[2]:<15} {nullable}{default}")
    
    conn.close()
    print("\n" + "="*80)
    print("✅ PROJECTS TABLE RECREATED SUCCESSFULLY!")
    print("="*80)
    
except Exception as e:
    print(f"\n❌ Failed: {e}")
    import traceback
    traceback.print_exc()

