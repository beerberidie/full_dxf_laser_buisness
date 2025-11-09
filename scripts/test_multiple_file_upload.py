"""
Test script to verify multiple file upload implementation.

This script checks:
1. HTML templates have 'multiple' attribute on file inputs
2. Backend routes handle request.files.getlist('files')
3. JavaScript functions exist for file count display
4. Backward compatibility is maintained
"""

import sys
import os
from pathlib import Path
import re

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


def check_template_file(file_path):
    """Check if a template file has multiple file upload support."""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find all file input elements
    file_inputs = re.findall(r'<input[^>]*type="file"[^>]*>', content, re.IGNORECASE)
    
    results = {
        'file': file_path,
        'file_inputs': len(file_inputs),
        'multiple_support': 0,
        'has_onchange': 0,
        'has_count_div': 0,
        'issues': []
    }
    
    for input_tag in file_inputs:
        # Check for multiple attribute
        if 'multiple' in input_tag:
            results['multiple_support'] += 1
        else:
            results['issues'].append(f"File input missing 'multiple' attribute: {input_tag[:80]}...")
        
        # Check for onchange handler
        if 'onchange' in input_tag and 'updateFileCount' in input_tag:
            results['has_onchange'] += 1
        
        # Check for name="files" (new) or name="file" (old)
        if 'name="files"' in input_tag:
            pass  # Good - new format
        elif 'name="file"' in input_tag:
            results['issues'].append(f"File input still uses name='file' instead of name='files': {input_tag[:80]}...")
    
    # Check for file count display divs
    count_divs = re.findall(r'<div[^>]*id="[^"]*[Ff]ile[Cc]ount"[^>]*>', content)
    results['has_count_div'] = len(count_divs)
    
    return results


def check_route_file(file_path):
    """Check if a route file handles multiple file uploads."""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    results = {
        'file': file_path,
        'has_getlist': False,
        'has_backward_compat': False,
        'has_loop': False,
        'has_error_tracking': False,
        'issues': []
    }
    
    # Check for request.files.getlist('files')
    if "request.files.getlist('files')" in content or 'request.files.getlist("files")' in content:
        results['has_getlist'] = True
    else:
        results['issues'].append("Missing request.files.getlist('files')")
    
    # Check for backward compatibility
    if "'file' in request.files" in content or '"file" in request.files' in content:
        results['has_backward_compat'] = True
    else:
        results['issues'].append("Missing backward compatibility for single file uploads")
    
    # Check for file processing loop (or service function that handles it)
    if 'for file in files:' in content or 'for file in files' in content or 'save_documents(' in content:
        results['has_loop'] = True
    else:
        results['issues'].append("Missing loop to process multiple files")

    # Check for error tracking (or service function that returns it)
    if 'uploaded_count' in content and 'failed_count' in content:
        results['has_error_tracking'] = True
    elif "result['uploaded_count']" in content or "result['failed_count']" in content:
        results['has_error_tracking'] = True  # Service function returns these
    else:
        results['issues'].append("Missing upload/failure count tracking")
    
    return results


def check_javascript_file(file_path):
    """Check if JavaScript file has file upload utilities."""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    results = {
        'file': file_path,
        'has_update_file_count': False,
        'has_validate_file_upload': False,
        'has_format_file_size': False,
        'issues': []
    }
    
    # Check for updateFileCount function
    if 'function updateFileCount' in content:
        results['has_update_file_count'] = True
    else:
        results['issues'].append("Missing updateFileCount() function")
    
    # Check for validateFileUpload function
    if 'function validateFileUpload' in content:
        results['has_validate_file_upload'] = True
    else:
        results['issues'].append("Missing validateFileUpload() function")
    
    # Check for formatFileSize function
    if 'function formatFileSize' in content:
        results['has_format_file_size'] = True
    else:
        results['issues'].append("Missing formatFileSize() function")
    
    return results


def main():
    print("=" * 80)
    print("MULTIPLE FILE UPLOAD IMPLEMENTATION TEST")
    print("=" * 80)
    
    base_dir = Path(__file__).parent.parent
    
    # Template files to check
    template_files = [
        'app/templates/projects/detail.html',
        'app/templates/products/form.html',
        'app/templates/products/detail.html',
        'ui_package/templates/projects/detail.html',
        'ui_package/templates/products/form.html',
        'ui_package/templates/products/detail.html',
    ]
    
    # Route files to check
    route_files = [
        'app/routes/files.py',
        'app/routes/products.py',
        'app/routes/projects.py',
    ]
    
    # JavaScript files to check
    js_files = [
        'app/static/js/main.js',
    ]
    
    # Check templates
    print("\n" + "=" * 70)
    print("STEP 1: Check HTML Templates")
    print("=" * 70)
    
    template_results = []
    for template_file in template_files:
        file_path = base_dir / template_file
        if file_path.exists():
            result = check_template_file(file_path)
            template_results.append(result)
            
            print(f"\n📄 {template_file}")
            print(f"   File inputs found: {result['file_inputs']}")
            print(f"   With 'multiple' attribute: {result['multiple_support']}")
            print(f"   With onchange handler: {result['has_onchange']}")
            print(f"   File count divs: {result['has_count_div']}")
            
            if result['issues']:
                print(f"   ⚠️  Issues:")
                for issue in result['issues']:
                    print(f"      - {issue}")
            else:
                print(f"   ✅ All checks passed!")
        else:
            print(f"\n⚠️  {template_file} - File not found")
    
    # Check routes
    print("\n" + "=" * 70)
    print("STEP 2: Check Backend Routes")
    print("=" * 70)
    
    route_results = []
    for route_file in route_files:
        file_path = base_dir / route_file
        if file_path.exists():
            result = check_route_file(file_path)
            route_results.append(result)
            
            print(f"\n📄 {route_file}")
            print(f"   Has getlist('files'): {'✅' if result['has_getlist'] else '❌'}")
            print(f"   Has backward compatibility: {'✅' if result['has_backward_compat'] else '❌'}")
            print(f"   Has file processing loop: {'✅' if result['has_loop'] else '❌'}")
            print(f"   Has error tracking: {'✅' if result['has_error_tracking'] else '❌'}")
            
            if result['issues']:
                print(f"   ⚠️  Issues:")
                for issue in result['issues']:
                    print(f"      - {issue}")
            else:
                print(f"   ✅ All checks passed!")
        else:
            print(f"\n⚠️  {route_file} - File not found")
    
    # Check JavaScript
    print("\n" + "=" * 70)
    print("STEP 3: Check JavaScript Utilities")
    print("=" * 70)
    
    js_results = []
    for js_file in js_files:
        file_path = base_dir / js_file
        if file_path.exists():
            result = check_javascript_file(file_path)
            js_results.append(result)
            
            print(f"\n📄 {js_file}")
            print(f"   Has updateFileCount(): {'✅' if result['has_update_file_count'] else '❌'}")
            print(f"   Has validateFileUpload(): {'✅' if result['has_validate_file_upload'] else '❌'}")
            print(f"   Has formatFileSize(): {'✅' if result['has_format_file_size'] else '❌'}")
            
            if result['issues']:
                print(f"   ⚠️  Issues:")
                for issue in result['issues']:
                    print(f"      - {issue}")
            else:
                print(f"   ✅ All checks passed!")
        else:
            print(f"\n⚠️  {js_file} - File not found")
    
    # Summary
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    
    total_issues = sum(len(r['issues']) for r in template_results + route_results + js_results)
    
    print(f"\n📊 Templates checked: {len(template_results)}")
    print(f"📊 Routes checked: {len(route_results)}")
    print(f"📊 JavaScript files checked: {len(js_results)}")
    print(f"📊 Total issues found: {total_issues}")
    
    if total_issues == 0:
        print("\n✅ All checks passed! Multiple file upload implementation is complete.")
        print("\n📋 Next steps:")
        print("   1. Restart Flask application")
        print("   2. Test file uploads manually:")
        print("      - Upload single file (backward compatibility)")
        print("      - Upload multiple files (new feature)")
        print("      - Upload mix of valid/invalid files (error handling)")
        return True
    else:
        print("\n⚠️  Some issues found. Please review and fix before testing.")
        return False


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)

