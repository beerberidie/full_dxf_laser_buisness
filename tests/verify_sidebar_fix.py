#!/usr/bin/env python3
"""
Verify that the Sage Information section exists in the sidebar templates.
"""

import os

def check_file(filepath):
    """Check if Sage Information section exists in the file."""
    print(f"\nChecking: {filepath}")
    print("=" * 70)
    
    if not os.path.exists(filepath):
        print(f"❌ File not found: {filepath}")
        return False
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check for Sage Information section
    checks = {
        "Sage Information comment": "<!-- Sage Information Section -->",
        "Sage Information div": '<div class="sidebar-section">',
        "Sage Information parent": 'Sage Information',
        "Briefcase icon": '💼',
        "Quotes sublink": 'sidebar-sublink',
        "Invoices route": "url_for('invoices.index')",
        "Quotes route": "url_for('quotes.index')",
    }
    
    all_passed = True
    for check_name, check_string in checks.items():
        if check_string in content:
            print(f"✅ {check_name}: FOUND")
        else:
            print(f"❌ {check_name}: NOT FOUND")
            all_passed = False
    
    # Show the actual Sage section if found
    if "<!-- Sage Information Section -->" in content:
        print("\n📋 Sage Information Section Content:")
        print("-" * 70)
        
        # Extract the section
        start_idx = content.find("<!-- Sage Information Section -->")
        end_idx = content.find("<!-- Communications Section -->", start_idx)
        
        if start_idx != -1 and end_idx != -1:
            section = content[start_idx:end_idx].strip()
            # Show first 500 characters
            print(section[:500])
            if len(section) > 500:
                print("... (truncated)")
        print("-" * 70)
    
    return all_passed

def main():
    """Main verification function."""
    print("\n" + "=" * 70)
    print("SIDEBAR SAGE INFORMATION SECTION VERIFICATION")
    print("=" * 70)
    
    files_to_check = [
        "app/templates/base.html",
        "ui_package/templates/base.html"
    ]
    
    results = {}
    for filepath in files_to_check:
        results[filepath] = check_file(filepath)
    
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    
    all_good = True
    for filepath, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status}: {filepath}")
        if not passed:
            all_good = False
    
    print("\n" + "=" * 70)
    if all_good:
        print("✅ ALL CHECKS PASSED!")
        print("\nThe Sage Information section is correctly implemented in both templates.")
        print("\nIf you're not seeing it in your browser:")
        print("1. Stop Flask (Ctrl+C)")
        print("2. Restart Flask: python run.py")
        print("3. Hard refresh browser: Ctrl+Shift+R (Windows) or Cmd+Shift+R (Mac)")
        print("4. Or try Incognito/Private mode")
    else:
        print("❌ SOME CHECKS FAILED!")
        print("\nPlease review the output above to see what's missing.")
    print("=" * 70)
    
    return all_good

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)

