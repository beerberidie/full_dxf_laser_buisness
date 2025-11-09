# UI Consistency Quick Reference Guide
## Laser OS Tier 1 - Standardization Patterns

**Date:** October 18, 2025  
**Version:** 1.0  
**Related:** UI_UX_CONSISTENCY_AUDIT_REPORT.md

---

## Quick Stats

- **Total Issues Found:** 47
- **Critical:** 8 | **Moderate:** 22 | **Minor:** 17
- **Current Consistency Score:** 63.75/100
- **Target Consistency Score:** 92.5/100
- **Estimated Effort:** 36-52 hours

---

## Standard Patterns (Use These)

### 1. Page Header (List Pages)

```html
<div class="page-header">
    <div>
        <nav class="breadcrumb">
            <a href="{{ url_for('main.dashboard') }}">Dashboard</a>
            <span>/</span>
            <span>[Module Name]</span>
        </nav>
        <h1>[Page Title]</h1>
    </div>
    <div class="page-actions">
        <a href="{{ url_for('[module].new_[item]') }}" class="btn btn-primary">
            + New [Item]
        </a>
    </div>
</div>
```

### 2. Search Bar (Simple)

```html
<div class="search-bar">
    <form method="get" action="{{ url_for('[module].index') }}">
        <input 
            type="text" 
            name="search" 
            placeholder="Search [items] by..." 
            value="{{ search }}"
            class="search-input"
        >
        <button type="submit" class="btn btn-secondary">Search</button>
        {% if search %}
            <a href="{{ url_for('[module].index') }}" class="btn btn-ghost">Clear</a>
        {% endif %}
    </form>
</div>
```

### 3. Search + Filters (Advanced)

```html
<div class="card">
    <div class="card-body">
        <form method="GET" action="{{ url_for('[module].index') }}" class="search-form">
            <div class="grid grid-3 grid-gap-md">
                <div class="form-group form-group-no-margin">
                    <label for="search">Search:</label>
                    <input type="text" id="search" name="search" class="form-control" 
                           value="{{ search }}" placeholder="Search...">
                </div>
                <div class="form-group form-group-no-margin">
                    <label for="filter1">Filter 1:</label>
                    <select id="filter1" name="filter1" class="form-control">
                        <option value="">All</option>
                        <!-- Options -->
                    </select>
                </div>
                <div class="form-group form-group-no-margin">
                    <label for="filter2">Filter 2:</label>
                    <select id="filter2" name="filter2" class="form-control">
                        <option value="">All</option>
                        <!-- Options -->
                    </select>
                </div>
            </div>
            <div class="mt-md flex-row flex-gap-sm">
                <button type="submit" class="btn btn-primary">Apply Filters</button>
                <a href="{{ url_for('[module].index') }}" class="btn btn-secondary">Clear Filters</a>
            </div>
        </form>
    </div>
</div>
```

### 4. List Table with Card

```html
<div class="card">
    <div class="card-header">
        <h2>[Items] ({{ pagination.total }})</h2>
        <a href="{{ url_for('[module].index') }}" class="btn btn-sm btn-ghost">
            View All
        </a>
    </div>
    <div class="card-body">
        {% if items %}
        <table class="table">
            <thead>
                <tr>
                    <th>Column 1</th>
                    <th>Column 2</th>
                    <th>Actions</th>
                </tr>
            </thead>
            <tbody>
                {% for item in items %}
                <tr>
                    <td>
                        <a href="{{ url_for('[module].detail', id=item.id) }}" class="link-primary">
                            {{ item.name }}
                        </a>
                    </td>
                    <td>{{ item.value }}</td>
                    <td>
                        <div class="btn-group">
                            <a href="{{ url_for('[module].detail', id=item.id) }}" 
                               class="btn btn-sm btn-secondary">View</a>
                            {% if current_user.has_role('admin') or current_user.has_role('manager') %}
                            <a href="{{ url_for('[module].edit', id=item.id) }}" 
                               class="btn btn-sm btn-primary">Edit</a>
                            {% endif %}
                        </div>
                    </td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
        {% else %}
        <div class="empty-state">
            <p>No [items] found.</p>
            {% if search or filters %}
                <p>Try adjusting your search or filter criteria.</p>
            {% else %}
                <p>Get started by creating your first [item].</p>
                <a href="{{ url_for('[module].new_[item]') }}" class="btn btn-primary">
                    + New [Item]
                </a>
            {% endif %}
        </div>
        {% endif %}
    </div>
</div>
```

### 5. Pagination

```html
{% if pagination.pages > 1 %}
<div class="pagination">
    {% if pagination.has_prev %}
    <a href="{{ url_for('[module].index', page=pagination.prev_num, search=search) }}" 
       class="btn btn-ghost">&laquo; Previous</a>
    {% endif %}
    
    <span class="pagination-info">
        Page {{ pagination.page }} of {{ pagination.pages }}
    </span>
    
    {% if pagination.has_next %}
    <a href="{{ url_for('[module].index', page=pagination.next_num, search=search) }}" 
       class="btn btn-ghost">Next &raquo;</a>
    {% endif %}
</div>
{% endif %}
```

### 6. Empty State

```html
<div class="empty-state">
    <p>No [items] found.</p>
    {% if search or filters %}
        <p>Try adjusting your search or filter criteria.</p>
    {% else %}
        <p>Get started by creating your first [item].</p>
        {% if current_user.has_role('admin') or current_user.has_role('manager') %}
        <a href="{{ url_for('[module].new_[item]') }}" class="btn btn-primary">
            + New [Item]
        </a>
        {% endif %}
    {% endif %}
</div>
```

### 7. Statistics Cards

```html
<div class="grid grid-4">
    <div class="card">
        <div class="card-body">
            <h3 class="stat-card-title">Total [Items]</h3>
            <p class="stat-card-value">{{ stats.total }}</p>
            <p class="stat-card-subtitle">{{ stats.active }} active</p>
        </div>
    </div>
    <!-- More stat cards -->
</div>
```

### 8. Detail Page Header

```html
<div class="page-header">
    <div>
        <nav class="breadcrumb">
            <a href="{{ url_for('main.dashboard') }}">Dashboard</a>
            <span>/</span>
            <a href="{{ url_for('[module].index') }}">[Module]</a>
            <span>/</span>
            <span>{{ item.code }}</span>
        </nav>
        <h1>{{ item.name }}</h1>
        <p class="text-muted">{{ item.code }}</p>
    </div>
    <div class="page-actions">
        {% if current_user.has_role('admin') or current_user.has_role('manager') %}
        <a href="{{ url_for('[module].edit', id=item.id) }}" class="btn btn-secondary">
            Edit [Item]
        </a>
        <button onclick="confirmDelete()" class="btn btn-danger">
            Delete [Item]
        </button>
        {% endif %}
    </div>
</div>
```

### 9. Detail Information (Definition List)

```html
<div class="card">
    <div class="card-header">
        <h2>[Section Title]</h2>
    </div>
    <div class="card-body">
        <dl class="detail-list">
            <dt>Field Label</dt>
            <dd>{{ item.field or '-' }}</dd>
            
            <dt>Email</dt>
            <dd>
                {% if item.email %}
                    <a href="mailto:{{ item.email }}">{{ item.email }}</a>
                {% else %}
                    -
                {% endif %}
            </dd>
            
            <dt>Date Field</dt>
            <dd>{{ item.date|date }}</dd>
        </dl>
    </div>
</div>
```

### 10. Status Badges

```html
<!-- Use badge macro (create in app/templates/macros/badges.html) -->
{% from 'macros/badges.html' import status_badge, priority_badge %}

{{ status_badge(project.status) }}
{{ priority_badge(item.priority) }}

<!-- Or inline: -->
<span class="badge badge-{{ status|lower|replace(' ', '-') }}">
    {{ status }}
</span>
```

---

## Standard Button Patterns

### Action Buttons
- **View:** `btn btn-sm btn-secondary`
- **Edit:** `btn btn-sm btn-primary`
- **Delete:** `btn btn-sm btn-danger`
- **Create:** `btn btn-primary`
- **Cancel:** `btn btn-secondary`
- **Save:** `btn btn-primary`
- **Ghost/Subtle:** `btn btn-ghost`

### Button Text
- **Create:** "+ New [Item]" (no emojis)
- **Search:** "Search" (simple) or "Apply Filters" (complex)
- **Clear:** "Clear" or "Clear Filters"
- **Pagination:** "&laquo; Previous" and "Next &raquo;"

---

## Standard Classes Reference

### Layout
- `.page-header` - Page header container
- `.page-actions` - Action buttons container
- `.breadcrumb` - Breadcrumb navigation
- `.grid`, `.grid-2`, `.grid-3`, `.grid-4`, `.grid-5` - Grid layouts
- `.grid-gap-sm`, `.grid-gap-md`, `.grid-gap-lg` - Grid gaps

### Components
- `.card` - Card container
- `.card-header` - Card header
- `.card-body` - Card body
- `.table` - Table
- `.btn` - Button base
- `.btn-primary`, `.btn-secondary`, `.btn-danger`, `.btn-ghost`, `.btn-success`, `.btn-warning` - Button variants
- `.btn-sm` - Small button
- `.btn-group` - Button group
- `.badge` - Badge base
- `.badge-primary`, `.badge-secondary`, `.badge-success`, `.badge-danger`, `.badge-warning`, `.badge-info` - Badge variants
- `.alert` - Alert base
- `.alert-success`, `.alert-error`, `.alert-warning`, `.alert-info` - Alert variants

### Forms
- `.form-group` - Form group
- `.form-group-no-margin` - Form group without margin
- `.form-control` - Form input/select/textarea
- `.form-label` - Form label
- `.search-bar` - Search bar container
- `.search-input` - Search input
- `.search-form` - Search/filter form

### Lists & Tables
- `.detail-list` - Definition list for details
- `.empty-state` - Empty state container
- `.empty-state-sm` - Small empty state
- `.empty-state-title` - Empty state title
- `.pagination` - Pagination container
- `.pagination-info` - Pagination info text

### Statistics
- `.stat-card-title` - Stat card title
- `.stat-card-value` - Stat card value
- `.stat-card-subtitle` - Stat card subtitle

### Links
- `.link-primary` - Primary link
- `.link-secondary` - Secondary link

### Utilities
- `.text-muted` - Muted text
- `.text-primary` - Primary text color
- `.text-secondary` - Secondary text color
- `.mb-xs`, `.mb-sm`, `.mb-md`, `.mb-lg`, `.mb-xl`, `.mb-2xl` - Margin bottom
- `.mt-xs`, `.mt-sm`, `.mt-md`, `.mt-lg`, `.mt-xl` - Margin top
- `.flex-row`, `.flex-col` - Flex direction
- `.flex-gap-sm`, `.flex-gap-md`, `.flex-gap-lg` - Flex gap
- `.flex-justify-start`, `.flex-justify-end`, `.flex-justify-center`, `.flex-justify-between` - Justify content
- `.flex-align-start`, `.flex-align-end`, `.flex-align-center` - Align items
- `.flex-1`, `.flex-2`, `.flex-auto` - Flex sizing
- `.inline-form` - Inline form
- `.hidden` - Hidden element
- `.text-pre-wrap` - Pre-wrap text

---

## DON'T Use These

### ❌ Avoid Inline Styles
```html
<!-- DON'T -->
<div style="margin-bottom: 2rem;">
<div style="flex: 2;">
<div style="color: var(--warning-color);">

<!-- DO -->
<div class="mb-2xl">
<div class="flex-2">
<div class="text-warning">
```

### ❌ Avoid Embedded Style Blocks
```html
<!-- DON'T -->
<style>
.custom-class { ... }
</style>

<!-- DO -->
<!-- Add to main.css -->
```

### ❌ Avoid Inconsistent Button Classes
```html
<!-- DON'T -->
<a href="..." class="btn btn-sm btn-ghost">View</a>
<a href="..." class="btn btn-sm btn-primary">View</a>

<!-- DO -->
<a href="..." class="btn btn-sm btn-secondary">View</a>
```

### ❌ Avoid Emojis (Use Icon Library Instead)
```html
<!-- DON'T -->
<a href="..." class="btn btn-primary">📦 Add Item</a>

<!-- DO -->
<a href="..." class="btn btn-primary">+ Add Item</a>
<!-- Or with icon library: -->
<a href="..." class="btn btn-primary">
    <i class="icon-plus"></i> Add Item
</a>
```

### ❌ Avoid Inconsistent Date Formatting
```html
<!-- DON'T -->
{{ item.created_at.strftime('%Y-%m-%d') }}

<!-- DO -->
{{ item.created_at|date }}
```

### ❌ Avoid Inconsistent Currency
```html
<!-- DON'T -->
${{ "%.2f"|format(price) }}

<!-- DO -->
R{{ "%.2f"|format(price) }}
```

---

## Priority Fixes Checklist

### Phase 1: Critical (Week 1-2)
- [ ] Add breadcrumbs to all list pages
- [ ] Standardize search/filter UI
- [ ] Update button classes (View=secondary, Edit=primary)
- [ ] Remove all inline styles
- [ ] Standardize empty states
- [ ] Standardize pagination
- [ ] Remove emojis or standardize icon usage
- [ ] Standardize detail page layouts

### Phase 2: Moderate (Week 3-4)
- [ ] Add card headers to clients/projects lists
- [ ] Standardize stat card classes
- [ ] Add `.search-form` class to all search forms
- [ ] Add missing utility classes to main.css
- [ ] Standardize link classes
- [ ] Create status badge macro
- [ ] Standardize date formatting
- [ ] Standardize currency formatting

### Phase 3: Minor (Week 5-6)
- [ ] Standardize HTML indentation
- [ ] Add ARIA labels
- [ ] Add form validation
- [ ] Create modal component
- [ ] Add loading states
- [ ] Improve accessibility

---

**Quick Reference Version:** 1.0  
**Last Updated:** October 18, 2025  
**For Full Details:** See UI_UX_CONSISTENCY_AUDIT_REPORT.md

