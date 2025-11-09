#!/usr/bin/env python3
"""
UI/UX Consistency Testing Script
Tests all Phase 1 and Phase 2 changes to ensure they work correctly.
"""

import re
from pathlib import Path
from collections import defaultdict

# Project root
project_root = Path(__file__).parent.parent

# Templates directory
templates_dir = project_root / 'app' / 'templates'

# CSS file
css_file = project_root / 'app' / 'static' / 'css' / 'main.css'

def test_breadcrumbs():
    """Test that breadcrumbs are present in list pages."""
    print("=" * 70)
    print("TEST 1: Breadcrumbs in List Pages")
    print("=" * 70)
    
    pages_to_check = [
        'inventory/index.html',
        'clients/list.html',
        'projects/list.html',
        'products/list.html',
    ]
    
    passed = 0
    failed = 0
    
    for page in pages_to_check:
        file_path = templates_dir / page
        if not file_path.exists():
            print(f"❌ FAIL: {page} - File not found")
            failed += 1
            continue
        
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        if '<nav class="breadcrumb">' in content:
            print(f"✅ PASS: {page} - Breadcrumbs present")
            passed += 1
        else:
            print(f"❌ FAIL: {page} - Breadcrumbs missing")
            failed += 1
    
    print(f"\nResult: {passed} passed, {failed} failed")
    return passed, failed

def test_no_inline_styles():
    """Test that inline styles have been removed."""
    print("\n" + "=" * 70)
    print("TEST 2: No Inline Styles")
    print("=" * 70)
    
    pages_to_check = [
        'products/detail.html',
        'clients/detail.html',
        'inventory/index.html',
    ]
    
    passed = 0
    failed = 0
    
    for page in pages_to_check:
        file_path = templates_dir / page
        if not file_path.exists():
            print(f"❌ FAIL: {page} - File not found")
            failed += 1
            continue
        
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check for inline styles (excluding style="" which might be empty)
        inline_styles = re.findall(r'style="[^"]+"', content)
        if not inline_styles:
            print(f"✅ PASS: {page} - No inline styles")
            passed += 1
        else:
            print(f"❌ FAIL: {page} - Found {len(inline_styles)} inline styles")
            for style in inline_styles[:3]:  # Show first 3
                print(f"   → {style}")
            failed += 1
    
    print(f"\nResult: {passed} passed, {failed} failed")
    return passed, failed

def test_no_strftime():
    """Test that strftime() has been replaced with filters."""
    print("\n" + "=" * 70)
    print("TEST 3: No strftime() Calls")
    print("=" * 70)
    
    html_files = list(templates_dir.rglob('*.html'))
    
    files_with_strftime = []
    
    for html_file in html_files:
        with open(html_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        if '.strftime(' in content:
            relative_path = html_file.relative_to(project_root)
            count = content.count('.strftime(')
            files_with_strftime.append((str(relative_path), count))
    
    if not files_with_strftime:
        print("✅ PASS: No strftime() calls found in any template")
        return 1, 0
    else:
        print(f"❌ FAIL: Found strftime() in {len(files_with_strftime)} files:")
        for file_path, count in files_with_strftime[:10]:
            print(f"   → {file_path}: {count} occurrence(s)")
        return 0, 1

def test_currency_formatting():
    """Test that currency uses R prefix."""
    print("\n" + "=" * 70)
    print("TEST 4: Currency Formatting (R prefix)")
    print("=" * 70)
    
    html_files = list(templates_dir.rglob('*.html'))
    
    files_with_dollar = []
    
    for html_file in html_files:
        with open(html_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Look for ${{ pattern
        if '${{' in content:
            relative_path = html_file.relative_to(project_root)
            count = content.count('${{')
            files_with_dollar.append((str(relative_path), count))
    
    if not files_with_dollar:
        print("✅ PASS: No $ currency symbols found (all using R)")
        return 1, 0
    else:
        print(f"❌ FAIL: Found $ symbols in {len(files_with_dollar)} files:")
        for file_path, count in files_with_dollar[:10]:
            print(f"   → {file_path}: {count} occurrence(s)")
        return 0, 1

def test_stat_cards():
    """Test that stat cards use consistent classes."""
    print("\n" + "=" * 70)
    print("TEST 5: Stat Card Classes")
    print("=" * 70)
    
    pages_to_check = [
        'dashboard.html',
        'comms/list.html',
        'inventory/index.html',
    ]
    
    passed = 0
    failed = 0
    
    for page in pages_to_check:
        file_path = templates_dir / page
        if not file_path.exists():
            print(f"❌ FAIL: {page} - File not found")
            failed += 1
            continue
        
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check for stat-card classes
        has_stat_card = 'stat-card' in content
        has_old_classes = 'dashboard-stat-' in content
        
        if has_stat_card and not has_old_classes:
            print(f"✅ PASS: {page} - Using stat-card classes")
            passed += 1
        elif has_old_classes:
            print(f"❌ FAIL: {page} - Still using old dashboard-stat-* classes")
            failed += 1
        else:
            print(f"⚠️  SKIP: {page} - No stat cards found")
    
    print(f"\nResult: {passed} passed, {failed} failed")
    return passed, failed

def test_utility_classes():
    """Test that utility classes were added to CSS."""
    print("\n" + "=" * 70)
    print("TEST 6: Utility Classes in CSS")
    print("=" * 70)
    
    if not css_file.exists():
        print("❌ FAIL: main.css not found")
        return 0, 1
    
    with open(css_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    required_classes = [
        '.mb-xs', '.mb-sm', '.mb-md', '.mb-lg',
        '.mt-xs', '.mt-sm', '.mt-md',
        '.flex-row', '.flex-col', '.flex-gap-sm',
        '.grid-gap-sm', '.grid-gap-md',
        '.detail-list',
        '.stat-card', '.stat-card-title', '.stat-card-value',
    ]
    
    passed = 0
    failed = 0
    
    for class_name in required_classes:
        if class_name in content:
            passed += 1
        else:
            print(f"❌ FAIL: {class_name} not found in CSS")
            failed += 1
    
    if failed == 0:
        print(f"✅ PASS: All {passed} utility classes present in CSS")
    else:
        print(f"\nResult: {passed} passed, {failed} failed")
    
    return 1 if failed == 0 else 0, 1 if failed > 0 else 0

def test_no_emojis():
    """Test that emojis have been removed."""
    print("\n" + "=" * 70)
    print("TEST 7: No Emojis in Templates")
    print("=" * 70)
    
    pages_to_check = [
        'inventory/index.html',
        'comms/list.html',
        'projects/detail.html',
        'queue/index.html',
    ]
    
    # Common emojis to check for
    emojis = ['📦', '📊', '✉️', '📧', '🔔', '⚠️', '✓', '☰', '📁', '🎯']
    
    passed = 0
    failed = 0
    
    for page in pages_to_check:
        file_path = templates_dir / page
        if not file_path.exists():
            print(f"❌ FAIL: {page} - File not found")
            failed += 1
            continue
        
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        found_emojis = [emoji for emoji in emojis if emoji in content]
        
        if not found_emojis:
            print(f"✅ PASS: {page} - No emojis found")
            passed += 1
        else:
            print(f"❌ FAIL: {page} - Found emojis: {', '.join(found_emojis)}")
            failed += 1
    
    print(f"\nResult: {passed} passed, {failed} failed")
    return passed, failed

def main():
    """Run all tests."""
    print("\n")
    print("=" * 70)
    print("UI/UX CONSISTENCY TEST SUITE")
    print("=" * 70)
    print()
    
    total_passed = 0
    total_failed = 0
    
    # Run all tests
    p, f = test_breadcrumbs()
    total_passed += p
    total_failed += f
    
    p, f = test_no_inline_styles()
    total_passed += p
    total_failed += f
    
    p, f = test_no_strftime()
    total_passed += p
    total_failed += f
    
    p, f = test_currency_formatting()
    total_passed += p
    total_failed += f
    
    p, f = test_stat_cards()
    total_passed += p
    total_failed += f
    
    p, f = test_utility_classes()
    total_passed += p
    total_failed += f
    
    p, f = test_no_emojis()
    total_passed += p
    total_failed += f
    
    # Final summary
    print("\n" + "=" * 70)
    print("FINAL SUMMARY")
    print("=" * 70)
    print(f"Total Tests Passed: {total_passed}")
    print(f"Total Tests Failed: {total_failed}")
    print(f"Success Rate: {total_passed / (total_passed + total_failed) * 100:.1f}%")
    print("=" * 70)
    print()
    
    if total_failed == 0:
        print("✅ ALL TESTS PASSED! UI/UX consistency implementation is successful.")
    else:
        print(f"⚠️  {total_failed} test(s) failed. Please review the failures above.")
    
    print()

if __name__ == '__main__':
    main()

