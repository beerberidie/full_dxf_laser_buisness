# Notification Bell Icon - Styling & Implementation Guide

## Overview

The notification bell icon is a V12.0 feature that provides real-time notifications to users in the Laser OS application. This document describes the professional styling implementation and how to customize it.

---

## 📍 Location

**HTML Template:** `app/templates/base.html` (lines 28-50)  
**CSS Styles:** `app/static/css/main.css` (lines 1828-2203)  
**JavaScript:** `app/templates/base.html` (lines 203-299)

---

## 🎨 Design Features

### 1. Bell Button
- **Transparent background** with subtle border
- **Hover effect** with background color change and scale animation
- **Active state** with scale-down effect for tactile feedback
- **Focus outline** for accessibility (keyboard navigation)
- **Bell ring animation** on hover for visual delight

### 2. Notification Badge (Counter)
- **Gradient background** (red) for high visibility
- **Positioned** at top-right corner of bell button
- **Pulse animation** to draw attention
- **Auto-hide** when count is 0
- **99+ display** for counts over 99
- **Border** matching header background for clean separation

### 3. Notification Dropdown
- **360px width** on desktop (320px on tablet, full-width on mobile)
- **Slide-in animation** when opening
- **Arrow pointer** at top for visual connection to bell
- **Box shadow** for depth and elevation
- **Max height** with scrollable content area
- **Custom scrollbar** styling for consistency

### 4. Notification Items
- **Hover effect** with background color change
- **Unread indicator** with blue background and left border
- **Icon, title, message, and timestamp** structure
- **Click handler** for navigation
- **Truncated messages** (2 lines max) with ellipsis

### 5. Responsive Design
- **Desktop (>768px):** Full-width dropdown (360px)
- **Tablet (480-768px):** Narrower dropdown (320px)
- **Mobile (<480px):** Full-screen dropdown from header

---

## 🎯 CSS Classes Reference

### Container & Button
```css
.notification-bell          /* Main container */
.notification-bell-btn      /* Bell button */
.bell-icon                  /* Bell emoji/icon */
.notification-badge         /* Counter badge */
```

### Dropdown Structure
```css
.notification-dropdown      /* Dropdown container */
.notification-header        /* Header section */
.notification-list          /* Scrollable list */
.notification-footer        /* Footer section */
```

### Notification Items
```css
.notification-item          /* Individual notification */
.notification-item.unread   /* Unread notification */
.notification-item-icon     /* Icon container */
.notification-item-content  /* Content wrapper */
.notification-item-title    /* Notification title */
.notification-item-message  /* Notification message */
.notification-item-time     /* Timestamp */
```

### States
```css
.notification-empty         /* Empty state */
.notification-loading       /* Loading state */
```

---

## 🔧 Customization Guide

### Change Bell Button Colors

Edit `app/static/css/main.css` around line 1850:

```css
.notification-bell-btn {
    border: 2px solid rgba(255, 255, 255, 0.2);  /* Border color */
}

.notification-bell-btn:hover {
    background: rgba(255, 255, 255, 0.1);        /* Hover background */
    border-color: rgba(255, 255, 255, 0.3);      /* Hover border */
}
```

### Change Badge Colors

Edit around line 1888:

```css
.notification-badge {
    background: linear-gradient(135deg, #ef4444, #dc2626);  /* Red gradient */
    /* Change to blue: */
    /* background: linear-gradient(135deg, #3b82f6, #2563eb); */
}
```

### Change Dropdown Width

Edit around line 1915:

```css
.notification-dropdown {
    width: 360px;  /* Desktop width */
}

@media (max-width: 768px) {
    .notification-dropdown {
        width: 320px;  /* Tablet width */
    }
}
```

### Disable Animations

To disable animations for performance or accessibility:

```css
/* Comment out or remove these animations */
@keyframes bellRing { ... }
@keyframes badgePulse { ... }
@keyframes dropdownSlideIn { ... }

/* And remove animation properties */
.notification-bell-btn:hover .bell-icon {
    /* animation: bellRing 0.5s ease-in-out; */
}

.notification-badge {
    /* animation: badgePulse 2s ease-in-out infinite; */
}
```

---

## 📱 Responsive Breakpoints

| Screen Size | Dropdown Width | Behavior |
|-------------|----------------|----------|
| **Desktop** (>768px) | 360px | Positioned below bell, right-aligned |
| **Tablet** (480-768px) | 320px | Positioned below bell, right-aligned |
| **Mobile** (<480px) | 100% | Full-screen from header, slide-up animation |

---

## 🎬 Animations

### 1. Bell Ring (on hover)
- **Duration:** 0.5s
- **Effect:** Rotates bell left/right
- **Trigger:** Hover on bell button

### 2. Badge Pulse (continuous)
- **Duration:** 2s (infinite loop)
- **Effect:** Scales badge 1.0 → 1.1 → 1.0
- **Trigger:** Always active when badge visible

### 3. Dropdown Slide-In (on open)
- **Duration:** 0.2s
- **Effect:** Fades in and slides down
- **Trigger:** Opening dropdown

### 4. Dropdown Slide-Up (mobile only)
- **Duration:** 0.3s
- **Effect:** Fades in and slides up
- **Trigger:** Opening dropdown on mobile

---

## 🔌 JavaScript API

### Functions

```javascript
// Toggle dropdown visibility
toggleNotifications()

// Load notifications from server (TODO: implement API)
loadNotifications()

// Mark all notifications as read (TODO: implement API)
markAllAsRead()

// Update notification count badge (TODO: implement API)
updateNotificationCount()
```

### Auto-Refresh

Notifications are automatically refreshed every 60 seconds:

```javascript
setInterval(updateNotificationCount, 60000);
```

To change the interval, edit line 293 in `base.html`:

```javascript
// Refresh every 30 seconds instead
setInterval(updateNotificationCount, 30000);
```

---

## 📊 Sample Notification Structure

When implementing the API endpoint, notifications should be rendered with this HTML structure:

```html
<div class="notification-item unread" onclick="window.location.href='/communications/1'">
    <div class="notification-item-icon">📧</div>
    <div class="notification-item-content">
        <div class="notification-item-title">Quote Expiry Reminder</div>
        <div class="notification-item-message">Quote for Project ABC-001 expires in 5 days</div>
        <div class="notification-item-time">2 hours ago</div>
    </div>
</div>
```

**Classes:**
- Add `unread` class for unread notifications (blue background + left border)
- Remove `unread` class for read notifications (white background)

**Icons:**
- 📧 Email/Quote notifications
- ✅ Payment/Approval notifications
- ⚙️ Production/Job notifications
- 🎉 Completion notifications
- ⚠️ Warning/Expiry notifications

---

## ✅ Testing Checklist

### Visual Testing
- [ ] Bell button displays correctly in header
- [ ] Badge appears when count > 0
- [ ] Badge hides when count = 0
- [ ] Hover effects work on bell button
- [ ] Dropdown opens/closes correctly
- [ ] Dropdown arrow points to bell
- [ ] Scrollbar appears when content overflows

### Responsive Testing
- [ ] Desktop (1920px): Dropdown 360px wide
- [ ] Tablet (768px): Dropdown 320px wide
- [ ] Mobile (375px): Dropdown full-width
- [ ] Mobile: Dropdown slides up from header
- [ ] No horizontal overflow on any screen size

### Interaction Testing
- [ ] Click bell → dropdown opens
- [ ] Click outside → dropdown closes
- [ ] Click notification item → navigates correctly
- [ ] "Mark all as read" button works
- [ ] "View all communications" link works
- [ ] Keyboard navigation works (Tab, Enter)

### Animation Testing
- [ ] Bell rings on hover
- [ ] Badge pulses continuously
- [ ] Dropdown slides in smoothly
- [ ] No janky animations or lag

---

## 🚀 Future Enhancements

### Phase 8: API Integration (Planned)
1. **GET /api/notifications** - Fetch recent notifications
2. **POST /api/notifications/mark-read** - Mark notifications as read
3. **GET /api/notifications/count** - Get unread count
4. **WebSocket support** - Real-time push notifications

### Phase 9: Advanced Features (Planned)
1. **Notification categories** - Filter by type (quotes, payments, jobs)
2. **Notification preferences** - User settings for which notifications to receive
3. **Sound alerts** - Optional audio notification
4. **Desktop notifications** - Browser push notifications
5. **Notification history** - View all past notifications

---

## 📝 Notes

- The current implementation uses placeholder data
- API endpoints need to be implemented in Phase 8
- The design follows Laser OS design system (CSS variables from main.css)
- All colors, spacing, and typography use CSS custom properties for consistency
- Animations are GPU-accelerated (transform, opacity) for smooth performance

---

## 🐛 Troubleshooting

### Badge not showing
- Check `updateNotificationCount()` function
- Verify count > 0
- Check `display: none` inline style

### Dropdown not opening
- Check JavaScript console for errors
- Verify `toggleNotifications()` function is called
- Check z-index conflicts with other elements

### Dropdown misaligned
- Check parent container positioning
- Verify `position: relative` on `.notification-bell`
- Check for CSS conflicts with other styles

### Animations not working
- Check browser support for CSS animations
- Verify animation keyframes are defined
- Check for `prefers-reduced-motion` media query

---

## 📚 Related Files

- `app/templates/base.html` - HTML structure and JavaScript
- `app/static/css/main.css` - CSS styling (lines 1828-2203)
- `app/services/notification_service.py` - Backend notification service
- `app/routes/comms.py` - Communications routes

---

**Last Updated:** V12.0 - Phase 6 (Frontend/UI Updates)  
**Author:** Laser OS Development Team

