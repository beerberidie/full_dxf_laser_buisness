#!/usr/bin/env python
"""
Apply database indexes from schema_v11_indexes.sql

This script reads the SQL file and executes each CREATE INDEX statement.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app import create_app, db

def apply_indexes():
    """Apply database indexes from migration file."""
    app = create_app()
    
    with app.app_context():
        # Read the SQL file
        sql_file = project_root / 'migrations' / 'schema_v11_indexes.sql'
        
        print('=' * 80)
        print('Applying Database Indexes (Schema v11)')
        print('=' * 80)
        print(f'Reading: {sql_file}')
        
        with open(sql_file, 'r', encoding='utf-8') as f:
            sql_content = f.read()
        
        # Split by semicolons and filter out comments and empty lines
        statements = []
        for statement in sql_content.split(';'):
            # Remove comments and whitespace
            lines = []
            for line in statement.split('\n'):
                # Remove inline comments
                if '--' in line:
                    line = line[:line.index('--')]
                line = line.strip()
                if line:
                    lines.append(line)
            
            statement_clean = ' '.join(lines)
            if statement_clean and statement_clean.upper().startswith('CREATE INDEX'):
                statements.append(statement_clean)
        
        print(f'\nFound {len(statements)} CREATE INDEX statements')
        print('\nApplying indexes...\n')
        
        # Execute each CREATE INDEX statement
        success_count = 0
        for i, statement in enumerate(statements, 1):
            try:
                # Extract index name for display
                index_name = statement.split('IF NOT EXISTS')[1].split('ON')[0].strip()
                
                db.session.execute(db.text(statement))
                db.session.commit()
                
                print(f'✓ [{i}/{len(statements)}] Created index: {index_name}')
                success_count += 1
                
            except Exception as e:
                print(f'✗ [{i}/{len(statements)}] Failed: {str(e)}')
                db.session.rollback()
        
        print('\n' + '=' * 80)
        print(f'Indexes Applied: {success_count}/{len(statements)}')
        print('=' * 80)
        
        # Verify indexes were created
        print('\nVerifying indexes...')
        result = db.session.execute(db.text(
            "SELECT name, tbl_name FROM sqlite_master WHERE type = 'index' AND name LIKE 'idx_%' ORDER BY tbl_name, name"
        ))
        indexes = result.fetchall()
        
        print(f'\nTotal indexes with prefix "idx_": {len(indexes)}')
        print('\nIndexes by table:')
        
        current_table = None
        for index_name, table_name in indexes:
            if table_name != current_table:
                print(f'\n{table_name}:')
                current_table = table_name
            print(f'  - {index_name}')
        
        print('\n' + '=' * 80)
        print('✓ Index migration complete!')
        print('=' * 80)

if __name__ == '__main__':
    apply_indexes()

