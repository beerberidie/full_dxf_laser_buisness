#!/usr/bin/env python
"""
Generate comprehensive template documentation for UI package.

This script analyzes all routes and templates to create documentation
about template variables, route mappings, and Flask integration requirements.
"""

import os
import sys
import re
import ast
from pathlib import Path
from collections import defaultdict

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def extract_render_template_calls(file_path):
    """Extract all render_template calls from a Python file."""
    renders = []
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find all render_template calls
    pattern = r'render_template\s*\(\s*[\'"]([^\'"]+)[\'"]([^)]*)\)'
    matches = re.findall(pattern, content)
    
    for template, args in matches:
        # Extract variable names from arguments
        var_pattern = r'(\w+)\s*='
        variables = re.findall(var_pattern, args)
        
        renders.append({
            'template': template,
            'variables': variables
        })
    
    return renders


def analyze_all_routes():
    """Analyze all route files to extract template usage."""
    routes_dir = project_root / 'app' / 'routes'
    route_template_map = defaultdict(list)
    template_variables = defaultdict(set)
    
    for route_file in routes_dir.glob('*.py'):
        if route_file.name.startswith('__'):
            continue
        
        blueprint_name = route_file.stem
        renders = extract_render_template_calls(route_file)
        
        for render in renders:
            template = render['template']
            variables = render['variables']
            
            route_template_map[blueprint_name].append({
                'template': template,
                'variables': variables
            })
            
            for var in variables:
                template_variables[template].add(var)
    
    return route_template_map, template_variables


def extract_jinja_variables_from_template(template_path):
    """Extract Jinja2 variables used in a template."""
    with open(template_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find all {{ variable }} patterns
    var_pattern = r'\{\{\s*([a-zA-Z_][a-zA-Z0-9_\.]*)'
    variables = set(re.findall(var_pattern, content))
    
    # Find all {% for item in items %} patterns
    for_pattern = r'\{%\s*for\s+\w+\s+in\s+([a-zA-Z_][a-zA-Z0-9_\.]*)'
    for_vars = set(re.findall(for_pattern, content))
    variables.update(for_vars)
    
    # Find all {% if variable %} patterns
    if_pattern = r'\{%\s*if\s+([a-zA-Z_][a-zA-Z0-9_\.]*)'
    if_vars = set(re.findall(if_pattern, content))
    variables.update(if_vars)
    
    return variables


def generate_template_variables_doc():
    """Generate template variables reference document."""
    print("Generating Template Variables Reference...")
    
    route_template_map, template_variables = analyze_all_routes()
    
    doc = []
    doc.append("# Template Variables Reference\n")
    doc.append("**Generated:** October 18, 2025\n")
    doc.append("\nThis document lists all variables passed to templates from Flask routes.\n")
    doc.append("\n---\n")
    
    doc.append("\n## Global Template Variables\n")
    doc.append("\nThese variables are available in ALL templates:\n\n")
    doc.append("- `current_user` - Currently logged-in user object\n")
    doc.append("  - `current_user.username` - Username\n")
    doc.append("  - `current_user.email` - Email address\n")
    doc.append("  - `current_user.is_authenticated` - Boolean, True if logged in\n")
    doc.append("  - `current_user.has_role('role_name')` - Check if user has specific role\n")
    doc.append("  - `current_user.roles` - List of user roles\n")
    doc.append("  - `current_user.is_superuser` - Boolean, True if superuser\n")
    doc.append("- `company_name` - Company name from config\n")
    doc.append("- `current_year` - Current year for footer\n")
    doc.append("- `request` - Flask request object\n")
    doc.append("  - `request.endpoint` - Current route endpoint\n")
    doc.append("  - `request.args` - URL query parameters\n")
    doc.append("  - `request.form` - Form data\n")
    doc.append("- `url_for()` - Function to generate URLs\n")
    doc.append("- `get_flashed_messages()` - Function to get flash messages\n")
    
    doc.append("\n---\n")
    doc.append("\n## Template-Specific Variables\n")
    
    # Sort templates alphabetically
    for template in sorted(template_variables.keys()):
        variables = sorted(template_variables[template])
        
        doc.append(f"\n### `{template}`\n\n")
        
        if variables:
            for var in variables:
                doc.append(f"- `{var}`\n")
        else:
            doc.append("*No specific variables (uses only global variables)*\n")
    
    # Write to file
    output_path = project_root / 'ui_package' / 'TEMPLATE_VARIABLES_REFERENCE.md'
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(''.join(doc))
    
    print(f"   ✓ Created {output_path}")
    return len(template_variables)


def generate_route_template_mapping_doc():
    """Generate route-to-template mapping document."""
    print("Generating Route-Template Mapping...")
    
    route_template_map, _ = analyze_all_routes()
    
    doc = []
    doc.append("# Route-Template Mapping\n")
    doc.append("**Generated:** October 18, 2025\n")
    doc.append("\nThis document maps Flask routes (blueprints) to their templates.\n")
    doc.append("\n---\n")
    
    for blueprint in sorted(route_template_map.keys()):
        doc.append(f"\n## {blueprint.capitalize()} Blueprint\n\n")
        doc.append(f"**URL Prefix:** `/{blueprint}/` (except 'main' which is `/`)\n\n")
        
        templates = route_template_map[blueprint]
        
        # Group by template
        template_groups = defaultdict(list)
        for item in templates:
            template_groups[item['template']].append(item['variables'])
        
        for template in sorted(template_groups.keys()):
            var_lists = template_groups[template]
            all_vars = set()
            for var_list in var_lists:
                all_vars.update(var_list)
            
            doc.append(f"### `{template}`\n\n")
            if all_vars:
                doc.append("**Variables:**\n")
                for var in sorted(all_vars):
                    doc.append(f"- `{var}`\n")
            doc.append("\n")
    
    # Write to file
    output_path = project_root / 'ui_package' / 'ROUTE_TEMPLATE_MAPPING.md'
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(''.join(doc))
    
    print(f"   ✓ Created {output_path}")
    return len(route_template_map)


if __name__ == '__main__':
    print("=" * 80)
    print("GENERATING TEMPLATE DOCUMENTATION")
    print("=" * 80)
    print()
    
    template_count = generate_template_variables_doc()
    blueprint_count = generate_route_template_mapping_doc()
    
    print()
    print("=" * 80)
    print("DOCUMENTATION GENERATION COMPLETE")
    print("=" * 80)
    print(f"\nTemplates Documented: {template_count}")
    print(f"Blueprints Analyzed: {blueprint_count}")
    print()

