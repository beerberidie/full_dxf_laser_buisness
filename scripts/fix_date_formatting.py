#!/usr/bin/env python3
"""
Script to fix date formatting in templates.
Replaces strftime() calls with Jinja2 |date and |datetime filters.
"""

import re
from pathlib import Path

# Project root
project_root = Path(__file__).parent.parent

# Templates directory
templates_dir = project_root / 'app' / 'templates'

# Patterns to replace
REPLACEMENTS = [
    # Date only patterns
    (r'\.strftime\([\'"]%Y-%m-%d[\'"]\)', '|date'),
    (r'\.strftime\([\'"]%d/%m/%Y[\'"]\)', '|date'),
    (r'\.strftime\([\'"]%m/%d/%Y[\'"]\)', '|date'),
    
    # DateTime patterns
    (r'\.strftime\([\'"]%Y-%m-%d %H:%M:%S[\'"]\)', '|datetime'),
    (r'\.strftime\([\'"]%Y-%m-%d %H:%M[\'"]\)', '|datetime'),
    (r'\.strftime\([\'"]%d/%m/%Y %H:%M[\'"]\)', '|datetime'),
]

def fix_file(file_path):
    """Fix date formatting in a single file."""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_content = content
    changes = []
    
    for pattern, replacement in REPLACEMENTS:
        matches = re.findall(pattern, content)
        if matches:
            content = re.sub(pattern, replacement, content)
            changes.append(f"  - Replaced {len(matches)} occurrence(s) of {pattern}")
    
    if content != original_content:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return True, changes
    
    return False, []

def main():
    """Main function to process all templates."""
    print("=" * 70)
    print("DATE FORMATTING FIX SCRIPT")
    print("=" * 70)
    print()
    
    total_files = 0
    modified_files = 0
    
    # Find all HTML templates
    html_files = list(templates_dir.rglob('*.html'))
    
    print(f"Found {len(html_files)} HTML templates")
    print()
    
    for html_file in sorted(html_files):
        relative_path = html_file.relative_to(project_root)
        modified, changes = fix_file(html_file)
        
        if modified:
            modified_files += 1
            print(f"✓ Modified: {relative_path}")
            for change in changes:
                print(change)
            print()
        
        total_files += 1
    
    print("=" * 70)
    print(f"SUMMARY:")
    print(f"  Total files scanned: {total_files}")
    print(f"  Files modified: {modified_files}")
    print(f"  Files unchanged: {total_files - modified_files}")
    print("=" * 70)
    print()
    print("✓ Date formatting fix complete!")
    print()

if __name__ == '__main__':
    main()

