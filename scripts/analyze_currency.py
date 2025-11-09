#!/usr/bin/env python3
"""
Script to analyze currency formatting in templates.
Finds all currency patterns and reports inconsistencies.
"""

import re
from pathlib import Path
from collections import defaultdict

# Project root
project_root = Path(__file__).parent.parent

# Templates directory
templates_dir = project_root / 'app' / 'templates'

# Currency patterns to find
CURRENCY_PATTERNS = [
    (r'\$\s*\{\{[^}]+\}\}', 'Dollar sign with variable'),
    (r'\{\{\s*["\']?\$[^}]+\}\}', 'Dollar sign inside variable'),
    (r'R\s*\{\{[^}]+\}\}', 'Rand sign with variable'),
    (r'\{\{\s*["\']?R[^}]+\}\}', 'Rand sign inside variable'),
    (r'\{\{\s*["\']?%.2f["\']?\|format\([^)]+\)', 'Format with 2 decimals'),
    (r'\{\{\s*[^}]+\|currency\s*\}\}', 'Currency filter'),
]

def analyze_file(file_path):
    """Analyze currency formatting in a single file."""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    findings = []
    
    for pattern, description in CURRENCY_PATTERNS:
        matches = re.findall(pattern, content)
        if matches:
            for match in matches:
                # Get line number
                line_num = content[:content.find(match)].count('\n') + 1
                findings.append({
                    'pattern': description,
                    'match': match,
                    'line': line_num
                })
    
    return findings

def main():
    """Main function to analyze all templates."""
    print("=" * 70)
    print("CURRENCY FORMATTING ANALYSIS")
    print("=" * 70)
    print()
    
    all_findings = defaultdict(list)
    total_files = 0
    files_with_currency = 0
    
    # Find all HTML templates
    html_files = list(templates_dir.rglob('*.html'))
    
    print(f"Analyzing {len(html_files)} HTML templates...")
    print()
    
    for html_file in sorted(html_files):
        relative_path = html_file.relative_to(project_root)
        findings = analyze_file(html_file)
        
        if findings:
            files_with_currency += 1
            all_findings[str(relative_path)] = findings
        
        total_files += 1
    
    # Report findings
    if all_findings:
        print(f"Found currency formatting in {files_with_currency} files:")
        print()
        
        for file_path, findings in sorted(all_findings.items()):
            print(f"📄 {file_path}")
            for finding in findings:
                print(f"   Line {finding['line']}: {finding['pattern']}")
                print(f"   → {finding['match'][:80]}")
            print()
    else:
        print("No currency formatting found.")
    
    print("=" * 70)
    print(f"SUMMARY:")
    print(f"  Total files scanned: {total_files}")
    print(f"  Files with currency: {files_with_currency}")
    print(f"  Total currency instances: {sum(len(f) for f in all_findings.values())}")
    print("=" * 70)
    print()

if __name__ == '__main__':
    main()

