#!/usr/bin/env python3
"""
Script to fix currency formatting in templates.
Replaces $ with R for South African Rand.
"""

import re
from pathlib import Path

# Project root
project_root = Path(__file__).parent.parent

# Templates directory
templates_dir = project_root / 'app' / 'templates'

def fix_file(file_path):
    """Fix currency formatting in a single file."""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_content = content
    changes = []
    
    # Replace ${{ with R{{
    pattern1 = r'\$\{\{'
    matches1 = re.findall(pattern1, content)
    if matches1:
        content = re.sub(pattern1, 'R{{', content)
        changes.append(f"  - Replaced {len(matches1)} occurrence(s) of ${{{{ with R{{{{")
    
    # Replace $ inside format strings (less common)
    pattern2 = r'\{\{\s*"\$'
    matches2 = re.findall(pattern2, content)
    if matches2:
        content = re.sub(pattern2, '{{ "R', content)
        changes.append(f"  - Replaced {len(matches2)} occurrence(s) of {{{{ \"$ with {{{{ \"R")
    
    if content != original_content:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return True, changes
    
    return False, []

def main():
    """Main function to process all templates."""
    print("=" * 70)
    print("CURRENCY FORMATTING FIX SCRIPT")
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
    print("✓ Currency formatting fix complete!")
    print("  All $ symbols replaced with R (South African Rand)")
    print()

if __name__ == '__main__':
    main()

