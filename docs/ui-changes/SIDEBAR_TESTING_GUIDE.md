# Sidebar Navigation - Testing Guide

## 🧪 Testing Checklist

Use this guide to verify that the sidebar navigation is working correctly across all scenarios.

---

## 1️⃣ Desktop Testing (Screen Width > 768px)

### Basic Functionality
- [ ] **Sidebar is visible** on page load
- [ ] **Sidebar shows icons + text** by default
- [ ] **Hamburger button** is visible in top-left of header
- [ ] **All navigation links** are displayed correctly
- [ ] **Icons** are visible next to each link

### Toggle Functionality
- [ ] **Click hamburger button** → Sidebar collapses to icon-only view
- [ ] **Sidebar width changes** from 250px to 70px smoothly
- [ ] **Text labels fade out** when collapsing
- [ ] **Icons remain visible** when collapsed
- [ ] **Main content area expands** to use freed space
- [ ] **Click hamburger again** → Sidebar expands back to full width
- [ ] **Text labels fade in** when expanding
- [ ] **Transition is smooth** (0.3s animation)

### State Persistence
- [ ] **Collapse sidebar** and refresh page
- [ ] **Sidebar remains collapsed** after refresh
- [ ] **Expand sidebar** and refresh page
- [ ] **Sidebar remains expanded** after refresh
- [ ] **State is saved** in browser localStorage

### Navigation
- [ ] **Click Dashboard link** → Navigates to Dashboard
- [ ] **Active page is highlighted** with blue background
- [ ] **Active page has left border** accent
- [ ] **Click each navigation link** → All routes work correctly
- [ ] **Communications section** shows submenu (Templates)
- [ ] **Admin link** shows only if user has admin role

### Hover Effects
- [ ] **Hover over link** → Background changes to light gray
- [ ] **Hover over collapsed icon** → Tooltip appears (if implemented)
- [ ] **Hover over hamburger** → Background changes

---

## 2️⃣ Mobile Testing (Screen Width ≤ 768px)

### Initial State
- [ ] **Sidebar is hidden** on page load
- [ ] **Main content uses full width**
- [ ] **Hamburger button** is visible in header
- [ ] **No overlay** is visible

### Opening Sidebar
- [ ] **Tap hamburger button** → Sidebar slides in from left
- [ ] **Dark overlay appears** behind sidebar
- [ ] **Sidebar is 250px wide**
- [ ] **Animation is smooth** (slide-in effect)
- [ ] **Content is dimmed** by overlay

### Closing Sidebar
- [ ] **Tap outside sidebar** (on overlay) → Sidebar closes
- [ ] **Sidebar slides out** to the left
- [ ] **Overlay fades out**
- [ ] **Tap hamburger button** → Sidebar closes
- [ ] **Animation is smooth** (slide-out effect)

### Navigation on Mobile
- [ ] **Tap any navigation link** → Navigates to page
- [ ] **Sidebar closes** after navigation (if desired)
- [ ] **Active page is highlighted** correctly

### Orientation Change
- [ ] **Rotate device to landscape** → Sidebar behavior adapts
- [ ] **Rotate back to portrait** → Sidebar behavior correct

---

## 3️⃣ Responsive Breakpoint Testing

### At 768px Breakpoint
- [ ] **Resize browser** from desktop to mobile width
- [ ] **Sidebar behavior changes** at 768px
- [ ] **Desktop collapsed state** doesn't affect mobile
- [ ] **Resize back to desktop** → Sidebar returns to saved state
- [ ] **No layout jumps** or glitches during resize

### Different Screen Sizes
- [ ] **Test at 1920px** (large desktop) → Works correctly
- [ ] **Test at 1366px** (laptop) → Works correctly
- [ ] **Test at 1024px** (tablet landscape) → Works correctly
- [ ] **Test at 768px** (tablet portrait) → Works correctly
- [ ] **Test at 375px** (mobile) → Works correctly
- [ ] **Test at 320px** (small mobile) → Works correctly

---

## 4️⃣ Browser Compatibility Testing

### Chrome/Edge
- [ ] **Sidebar toggle** works
- [ ] **Animations** are smooth
- [ ] **localStorage** persists state
- [ ] **No console errors**

### Firefox
- [ ] **Sidebar toggle** works
- [ ] **Animations** are smooth
- [ ] **localStorage** persists state
- [ ] **No console errors**

### Safari (Desktop)
- [ ] **Sidebar toggle** works
- [ ] **Animations** are smooth
- [ ] **localStorage** persists state
- [ ] **No console errors**

### Safari (iOS)
- [ ] **Sidebar overlay** works
- [ ] **Touch interactions** work
- [ ] **Animations** are smooth
- [ ] **No console errors**

### Chrome (Android)
- [ ] **Sidebar overlay** works
- [ ] **Touch interactions** work
- [ ] **Animations** are smooth
- [ ] **No console errors**

---

## 5️⃣ Accessibility Testing

### Keyboard Navigation
- [ ] **Tab to hamburger button** → Button is focused
- [ ] **Press Enter/Space** → Sidebar toggles
- [ ] **Tab through sidebar links** → All links are focusable
- [ ] **Press Enter on link** → Navigates to page
- [ ] **ESC key** closes sidebar on mobile (if implemented)

### Screen Reader
- [ ] **Hamburger button** has proper ARIA label
- [ ] **Navigation links** are announced correctly
- [ ] **Active page** is indicated to screen reader
- [ ] **Sidebar state** is communicated

### Focus Management
- [ ] **Focus is visible** on all interactive elements
- [ ] **Focus order** is logical
- [ ] **No focus traps**

---

## 6️⃣ Visual Testing

### Layout
- [ ] **Header is fixed** at top
- [ ] **Sidebar is fixed** on left
- [ ] **Main content scrolls** independently
- [ ] **Footer is positioned** correctly
- [ ] **No horizontal scrollbar** appears
- [ ] **No content overflow**

### Styling
- [ ] **Colors match** design system
- [ ] **Fonts are consistent**
- [ ] **Icons are aligned** properly
- [ ] **Spacing is even**
- [ ] **Borders are crisp**
- [ ] **Shadows are subtle**

### Animations
- [ ] **Sidebar width transition** is smooth
- [ ] **Text fade in/out** is smooth
- [ ] **Mobile slide in/out** is smooth
- [ ] **Overlay fade** is smooth
- [ ] **No janky animations**
- [ ] **No layout shifts**

---

## 7️⃣ Functionality Testing

### All Pages
- [ ] **Dashboard** → Sidebar works correctly
- [ ] **Clients** → Sidebar works correctly
- [ ] **Projects** → Sidebar works correctly
- [ ] **Products** → Sidebar works correctly
- [ ] **Queue** → Sidebar works correctly
- [ ] **Presets** → Sidebar works correctly
- [ ] **Inventory** → Sidebar works correctly
- [ ] **Reports** → Sidebar works correctly
- [ ] **Quotes** → Sidebar works correctly
- [ ] **Invoices** → Sidebar works correctly
- [ ] **Communications** → Sidebar works correctly
- [ ] **Templates** → Sidebar works correctly
- [ ] **Admin** → Sidebar works correctly (if admin)

### User Menu
- [ ] **Profile dropdown** still works
- [ ] **Logout button** still works
- [ ] **User menu** doesn't interfere with sidebar

### Flash Messages
- [ ] **Flash messages** display correctly
- [ ] **Messages don't overlap** sidebar
- [ ] **Auto-dismiss** still works

---

## 8️⃣ Performance Testing

### Load Time
- [ ] **Page loads quickly** with sidebar
- [ ] **No delay** in sidebar rendering
- [ ] **JavaScript loads** without errors

### Animation Performance
- [ ] **60fps** during sidebar toggle
- [ ] **No lag** during transitions
- [ ] **Smooth on low-end devices**

### Memory
- [ ] **No memory leaks** after multiple toggles
- [ ] **localStorage** doesn't grow excessively

---

## 9️⃣ Edge Cases

### Empty States
- [ ] **No navigation items** → Sidebar still renders
- [ ] **Single navigation item** → Sidebar looks correct

### Long Labels
- [ ] **Very long link text** → Doesn't break layout
- [ ] **Text wraps** or truncates appropriately

### Many Items
- [ ] **20+ navigation items** → Sidebar scrolls
- [ ] **Scroll is smooth**
- [ ] **Active item is visible**

### Rapid Toggling
- [ ] **Click hamburger rapidly** → No glitches
- [ ] **Animations queue** properly
- [ ] **State remains consistent**

### Browser Back/Forward
- [ ] **Navigate to page** → Active state correct
- [ ] **Click back button** → Active state updates
- [ ] **Click forward button** → Active state updates

---

## 🔟 Integration Testing

### With Existing Features
- [ ] **Search functionality** still works (if exists)
- [ ] **Notifications** still work (if exists)
- [ ] **Modals** display correctly over sidebar
- [ ] **Dropdowns** don't get cut off by sidebar
- [ ] **Forms** submit correctly
- [ ] **Tables** display correctly with sidebar

### With Authentication
- [ ] **Login** → Sidebar appears after login
- [ ] **Logout** → Sidebar disappears after logout
- [ ] **Session timeout** → Sidebar state preserved

---

## 🐛 Common Issues to Check

### Desktop
- ❌ **Sidebar doesn't collapse** → Check JavaScript loaded
- ❌ **State not persisting** → Check localStorage permissions
- ❌ **Content doesn't shift** → Check CSS main-wrapper margin
- ❌ **Text doesn't hide** → Check CSS transitions
- ❌ **Icons misaligned** → Check flexbox alignment

### Mobile
- ❌ **Sidebar doesn't open** → Check JavaScript mobile detection
- ❌ **Overlay doesn't appear** → Check CSS ::before pseudo-element
- ❌ **Can't close sidebar** → Check click event listener
- ❌ **Sidebar too wide** → Check viewport width
- ❌ **Content scrolls behind sidebar** → Check z-index

### Both
- ❌ **Active state wrong** → Check Jinja2 template logic
- ❌ **Links don't work** → Check route URLs
- ❌ **Animations jerky** → Check CSS transitions
- ❌ **Console errors** → Check JavaScript syntax

---

## ✅ Sign-Off Checklist

Before marking this feature as complete:

- [ ] All desktop tests pass
- [ ] All mobile tests pass
- [ ] All responsive tests pass
- [ ] All browser tests pass
- [ ] All accessibility tests pass
- [ ] All visual tests pass
- [ ] All functionality tests pass
- [ ] All performance tests pass
- [ ] All edge cases handled
- [ ] All integration tests pass
- [ ] No console errors
- [ ] No layout issues
- [ ] Documentation complete
- [ ] User feedback positive

---

## 📝 Testing Notes

**Tester Name**: _________________  
**Date**: _________________  
**Browser**: _________________  
**Device**: _________________  

**Issues Found**:
1. _________________
2. _________________
3. _________________

**Overall Status**: ⬜ Pass | ⬜ Fail | ⬜ Needs Review

---

## 🚀 Quick Test Script

For rapid testing, run through this minimal checklist:

1. ✅ Desktop: Toggle sidebar (collapse/expand)
2. ✅ Desktop: Refresh page (state persists)
3. ✅ Desktop: Click all navigation links
4. ✅ Mobile: Open sidebar (overlay appears)
5. ✅ Mobile: Close sidebar (tap outside)
6. ✅ Mobile: Navigate to different page
7. ✅ Resize: Desktop → Mobile → Desktop
8. ✅ Check: No console errors

**If all 8 pass → Feature is working! 🎉**

