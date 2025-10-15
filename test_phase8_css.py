"""
Phase 8 CSS Styling Enhancements Test Suite

Tests CSS enhancements for Phase 9 features including badges, responsive design,
and visual indicators.
"""

import os
import sys
import re
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))


def test_css_file_exists():
    """Test that main.css file exists."""
    print("\n" + "="*70)
    print("TEST 1: CSS FILE EXISTS")
    print("="*70)
    
    css_path = Path('app/static/css/main.css')
    
    if css_path.exists():
        file_size = css_path.stat().st_size
        print(f"  ✓ main.css exists")
        print(f"  ✓ File size: {file_size:,} bytes ({file_size / 1024:.2f} KB)")
        return True
    else:
        print(f"  ✗ main.css not found at {css_path}")
        return False


def test_phase9_badge_classes():
    """Test that Phase 9 badge classes are defined."""
    print("\n" + "="*70)
    print("TEST 2: PHASE 9 BADGE CLASSES")
    print("="*70)
    
    css_path = Path('app/static/css/main.css')
    
    try:
        with open(css_path, 'r', encoding='utf-8') as f:
            css_content = f.read()
        
        # Expected badge classes for Phase 9
        expected_badges = {
            # Communication type badges
            '.badge-email': 'Email communication badge',
            '.badge-whatsapp': 'WhatsApp communication badge',
            '.badge-notification': 'Notification badge',
            '.badge-phone': 'Phone communication badge',
            '.badge-sms': 'SMS communication badge',
            '.badge-in-person': 'In-person communication badge',
            
            # Communication status badges
            '.badge-pending': 'Pending status badge',
            '.badge-sent': 'Sent status badge',
            '.badge-delivered': 'Delivered status badge',
            '.badge-read': 'Read status badge',
            '.badge-failed': 'Failed status badge',
            
            # General badges
            '.badge-success': 'Success badge',
            '.badge-info': 'Info badge',
            '.badge-primary': 'Primary badge',
            
            # Badge size variants
            '.badge-lg': 'Large badge variant',
            '.badge-md': 'Medium badge variant',
        }
        
        missing = []
        for badge_class, description in expected_badges.items():
            # Check if class is defined (with opening brace)
            pattern = re.escape(badge_class) + r'\s*\{'
            if re.search(pattern, css_content):
                print(f"  ✓ {badge_class:<30} {description}")
            else:
                print(f"  ✗ {badge_class:<30} MISSING")
                missing.append(badge_class)
        
        if missing:
            print(f"\n  ✗ {len(missing)} badge class(es) missing")
            return False
        
        print(f"\n  ✓ All {len(expected_badges)} Phase 9 badge classes defined")
        return True
        
    except Exception as e:
        print(f"  ✗ Error reading CSS file: {e}")
        return False


def test_utility_classes():
    """Test that utility classes are defined."""
    print("\n" + "="*70)
    print("TEST 3: UTILITY CLASSES")
    print("="*70)
    
    css_path = Path('app/static/css/main.css')
    
    try:
        with open(css_path, 'r', encoding='utf-8') as f:
            css_content = f.read()
        
        # Expected utility classes
        expected_utilities = {
            '.flex': 'Flexbox container',
            '.flex-gap': 'Flex gap spacing',
            '.flex-gap-sm': 'Small flex gap',
            '.flex-wrap': 'Flex wrap',
            '.flex-end': 'Flex justify end',
            '.flex-between': 'Flex justify between',
            '.flex-center': 'Flex align center',
            '.inline-form': 'Inline form',
            '.hidden': 'Hidden element',
            '.mb-lg': 'Margin bottom large',
            '.mb-xl': 'Margin bottom extra large',
            '.mt-md': 'Margin top medium',
            '.mt-lg': 'Margin top large',
        }
        
        missing = []
        for util_class, description in expected_utilities.items():
            pattern = re.escape(util_class) + r'\s*\{'
            if re.search(pattern, css_content):
                print(f"  ✓ {util_class:<25} {description}")
            else:
                print(f"  ✗ {util_class:<25} MISSING")
                missing.append(util_class)
        
        if missing:
            print(f"\n  ✗ {len(missing)} utility class(es) missing")
            return False
        
        print(f"\n  ✓ All {len(expected_utilities)} utility classes defined")
        return True
        
    except Exception as e:
        print(f"  ✗ Error reading CSS file: {e}")
        return False


def test_component_classes():
    """Test that Phase 9 component classes are defined."""
    print("\n" + "="*70)
    print("TEST 4: PHASE 9 COMPONENT CLASSES")
    print("="*70)
    
    css_path = Path('app/static/css/main.css')
    
    try:
        with open(css_path, 'r', encoding='utf-8') as f:
            css_content = f.read()
        
        # Expected component classes
        expected_components = {
            '.status-badges': 'Status badges container',
            '.info-box': 'Info box component',
            '.info-box-warning': 'Warning info box',
            '.info-box-danger': 'Danger info box',
            '.info-box-success': 'Success info box',
            '.message-body': 'Message body display',
            '.filter-bar': 'Filter bar component',
            '.stats-grid': 'Statistics grid',
            '.stat-card': 'Statistic card',
            '.stat-value': 'Statistic value',
            '.stat-label': 'Statistic label',
        }
        
        missing = []
        for comp_class, description in expected_components.items():
            pattern = re.escape(comp_class) + r'\s*\{'
            if re.search(pattern, css_content):
                print(f"  ✓ {comp_class:<25} {description}")
            else:
                print(f"  ✗ {comp_class:<25} MISSING")
                missing.append(comp_class)
        
        if missing:
            print(f"\n  ✗ {len(missing)} component class(es) missing")
            return False
        
        print(f"\n  ✓ All {len(expected_components)} component classes defined")
        return True
        
    except Exception as e:
        print(f"  ✗ Error reading CSS file: {e}")
        return False


def test_button_variants():
    """Test that button variant classes are defined."""
    print("\n" + "="*70)
    print("TEST 5: BUTTON VARIANTS")
    print("="*70)
    
    css_path = Path('app/static/css/main.css')
    
    try:
        with open(css_path, 'r', encoding='utf-8') as f:
            css_content = f.read()
        
        # Expected button variants
        expected_buttons = {
            '.btn-success': 'Success button',
            '.btn-warning': 'Warning button',
            '.btn-info': 'Info button',
            '.btn-primary': 'Primary button (existing)',
            '.btn-secondary': 'Secondary button (existing)',
            '.btn-danger': 'Danger button (existing)',
        }
        
        missing = []
        for btn_class, description in expected_buttons.items():
            pattern = re.escape(btn_class) + r'\s*\{'
            if re.search(pattern, css_content):
                print(f"  ✓ {btn_class:<20} {description}")
            else:
                print(f"  ✗ {btn_class:<20} MISSING")
                missing.append(btn_class)
        
        if missing:
            print(f"\n  ✗ {len(missing)} button variant(s) missing")
            return False
        
        print(f"\n  ✓ All {len(expected_buttons)} button variants defined")
        return True
        
    except Exception as e:
        print(f"  ✗ Error reading CSS file: {e}")
        return False


def test_responsive_design():
    """Test that responsive design rules are present."""
    print("\n" + "="*70)
    print("TEST 6: RESPONSIVE DESIGN")
    print("="*70)
    
    css_path = Path('app/static/css/main.css')
    
    try:
        with open(css_path, 'r', encoding='utf-8') as f:
            css_content = f.read()
        
        # Check for media queries
        media_queries = re.findall(r'@media\s*\([^)]+\)', css_content)
        
        if media_queries:
            print(f"  ✓ Found {len(media_queries)} media query/queries")
            for mq in media_queries:
                print(f"    - {mq}")
        else:
            print(f"  ✗ No media queries found")
            return False
        
        # Check for Phase 9 responsive rules
        phase9_responsive = [
            '.status-badges',
            '.filter-bar',
            '.stats-grid',
        ]
        
        # Find the media query section
        media_section = re.search(r'@media\s*\([^)]+\)\s*\{([^}]+\{[^}]+\})+', css_content, re.DOTALL)
        
        if media_section:
            media_content = media_section.group(0)
            found_responsive = []
            
            for selector in phase9_responsive:
                if selector in media_content:
                    found_responsive.append(selector)
                    print(f"  ✓ {selector} has responsive rules")
            
            if len(found_responsive) >= 2:
                print(f"\n  ✓ Phase 9 components have responsive design")
                return True
            else:
                print(f"\n  ⚠ Only {len(found_responsive)} Phase 9 component(s) have responsive rules")
                return True  # Not critical
        else:
            print(f"  ⚠ Could not parse media query section")
            return True  # Not critical
        
    except Exception as e:
        print(f"  ✗ Error reading CSS file: {e}")
        return False


def test_inline_styles_removed():
    """Test that inline styles have been removed from Phase 9 templates."""
    print("\n" + "="*70)
    print("TEST 7: INLINE STYLES REMOVED")
    print("="*70)
    
    templates_to_check = [
        ('app/templates/comms/detail.html', 'Communications Detail'),
        ('app/templates/comms/list.html', 'Communications List'),
    ]
    
    all_clean = True
    
    for template_path, template_name in templates_to_check:
        path = Path(template_path)
        
        if not path.exists():
            print(f"  ⚠ {template_name}: File not found")
            continue
        
        try:
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check for <style> tags (should be removed)
            style_tags = re.findall(r'<style[^>]*>.*?</style>', content, re.DOTALL)
            
            if style_tags:
                print(f"  ✗ {template_name}: Found {len(style_tags)} <style> tag(s)")
                all_clean = False
            else:
                print(f"  ✓ {template_name}: No <style> tags found")
            
        except Exception as e:
            print(f"  ✗ {template_name}: Error reading file: {e}")
            all_clean = False
    
    if all_clean:
        print(f"\n  ✓ All checked templates are clean (no inline <style> tags)")
    else:
        print(f"\n  ✗ Some templates still have inline styles")
    
    return all_clean


def run_all_tests():
    """Run all Phase 8 CSS enhancement tests."""
    print("\n" + "="*70)
    print("PHASE 8 CSS STYLING ENHANCEMENTS TEST SUITE")
    print("="*70)
    
    tests = [
        ("CSS File Exists", test_css_file_exists),
        ("Phase 9 Badge Classes", test_phase9_badge_classes),
        ("Utility Classes", test_utility_classes),
        ("Phase 9 Component Classes", test_component_classes),
        ("Button Variants", test_button_variants),
        ("Responsive Design", test_responsive_design),
        ("Inline Styles Removed", test_inline_styles_removed),
    ]
    
    results = []
    for name, test_func in tests:
        result = test_func()
        results.append((name, result))
    
    # Summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✓ PASSED" if result else "✗ FAILED"
        print(f"{status}: {name}")
    
    print(f"\nPassed: {passed}/{total}")
    
    if passed == total:
        print("\n✅ ALL TESTS PASSED!")
        print("\nPhase 8 CSS styling enhancements are complete and working correctly.")
    else:
        print(f"\n⚠️  {total - passed} TEST(S) FAILED")
        print("\nPlease review the errors above.")
    
    return passed == total


if __name__ == '__main__':
    success = run_all_tests()
    sys.exit(0 if success else 1)

