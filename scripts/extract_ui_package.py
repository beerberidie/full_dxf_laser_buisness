#!/usr/bin/env python
"""
Extract UI Package for Laser OS Tier 1

This script extracts all frontend assets and creates a comprehensive package
for UI enhancement by an AI tool.
"""

import os
import sys
import shutil
import json
from pathlib import Path
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def create_ui_package():
    """Create a comprehensive UI package for enhancement."""
    
    # Create output directory
    output_dir = project_root / 'ui_package'
    if output_dir.exists():
        shutil.rmtree(output_dir)
    output_dir.mkdir()
    
    print("=" * 80)
    print("LASER OS TIER 1 - UI PACKAGE EXTRACTION")
    print("=" * 80)
    print()
    
    # 1. Copy all templates
    print("1. Extracting HTML Templates...")
    templates_src = project_root / 'app' / 'templates'
    templates_dest = output_dir / 'templates'
    shutil.copytree(templates_src, templates_dest)
    
    template_count = sum(1 for _ in templates_dest.rglob('*.html'))
    print(f"   ✓ Copied {template_count} HTML templates")
    
    # 2. Copy all CSS
    print("\n2. Extracting CSS Files...")
    css_src = project_root / 'app' / 'static' / 'css'
    css_dest = output_dir / 'static' / 'css'
    css_dest.mkdir(parents=True)
    shutil.copytree(css_src, css_dest, dirs_exist_ok=True)
    
    css_count = sum(1 for _ in css_dest.rglob('*.css'))
    print(f"   ✓ Copied {css_count} CSS file(s)")
    
    # 3. Copy all JavaScript
    print("\n3. Extracting JavaScript Files...")
    js_src = project_root / 'app' / 'static' / 'js'
    js_dest = output_dir / 'static' / 'js'
    js_dest.mkdir(parents=True, exist_ok=True)
    if js_src.exists():
        shutil.copytree(js_src, js_dest, dirs_exist_ok=True)
        js_count = sum(1 for _ in js_dest.rglob('*.js'))
        print(f"   ✓ Copied {js_count} JavaScript file(s)")
    else:
        print(f"   ⚠ No JavaScript directory found")
    
    # 4. Create template hierarchy map
    print("\n4. Analyzing Template Structure...")
    template_hierarchy = analyze_template_hierarchy(templates_dest)
    
    with open(output_dir / 'template_hierarchy.json', 'w') as f:
        json.dump(template_hierarchy, f, indent=2)
    print(f"   ✓ Created template hierarchy map")
    
    # 5. Extract CSS variables and design tokens
    print("\n5. Extracting Design System...")
    design_system = extract_design_system(css_dest / 'main.css')
    
    with open(output_dir / 'design_system.json', 'w') as f:
        json.dump(design_system, f, indent=2)
    print(f"   ✓ Extracted design system tokens")
    
    # 6. Create package manifest
    print("\n6. Creating Package Manifest...")
    manifest = {
        'package_name': 'Laser OS Tier 1 - UI Package',
        'extraction_date': datetime.now().isoformat(),
        'version': '1.0',
        'statistics': {
            'html_templates': template_count,
            'css_files': css_count,
            'js_files': js_count if js_src.exists() else 0,
        },
        'structure': {
            'templates': 'templates/',
            'css': 'static/css/',
            'js': 'static/js/',
            'template_hierarchy': 'template_hierarchy.json',
            'design_system': 'design_system.json',
        }
    }
    
    with open(output_dir / 'manifest.json', 'w') as f:
        json.dump(manifest, f, indent=2)
    print(f"   ✓ Created package manifest")
    
    print("\n" + "=" * 80)
    print("UI PACKAGE EXTRACTION COMPLETE")
    print("=" * 80)
    print(f"\nPackage Location: {output_dir}")
    print(f"Total Files: {template_count + css_count + (js_count if js_src.exists() else 0)}")
    print()


def analyze_template_hierarchy(templates_dir):
    """Analyze template inheritance hierarchy."""
    hierarchy = {
        'base_template': 'base.html',
        'extends_base': [],
        'template_blocks': {},
    }
    
    for template_file in templates_dir.rglob('*.html'):
        rel_path = template_file.relative_to(templates_dir)
        
        with open(template_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check if extends base.html
        if '{% extends "base.html" %}' in content:
            hierarchy['extends_base'].append(str(rel_path))
        
        # Extract blocks
        import re
        blocks = re.findall(r'{%\s*block\s+(\w+)\s*%}', content)
        if blocks:
            hierarchy['template_blocks'][str(rel_path)] = blocks
    
    return hierarchy


def extract_design_system(css_file):
    """Extract design system tokens from CSS."""
    design_system = {
        'colors': {},
        'typography': {},
        'spacing': {},
        'borders': {},
        'shadows': {},
        'other': {}
    }
    
    if not css_file.exists():
        return design_system
    
    with open(css_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Extract CSS variables
    import re
    variables = re.findall(r'--([a-z0-9-]+):\s*([^;]+);', content)
    
    for var_name, var_value in variables:
        if 'color' in var_name or var_name.startswith('bg-') or var_name.startswith('text-'):
            design_system['colors'][var_name] = var_value.strip()
        elif 'font' in var_name:
            design_system['typography'][var_name] = var_value.strip()
        elif 'spacing' in var_name:
            design_system['spacing'][var_name] = var_value.strip()
        elif 'border' in var_name or 'radius' in var_name:
            design_system['borders'][var_name] = var_value.strip()
        elif 'shadow' in var_name:
            design_system['shadows'][var_name] = var_value.strip()
        else:
            design_system['other'][var_name] = var_value.strip()
    
    return design_system


if __name__ == '__main__':
    create_ui_package()

