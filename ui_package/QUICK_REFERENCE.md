# Quick Reference Guide

**For AI Enhancement Tool**

---

## ⚡ Quick Start

1. **Read First:** `AI_ENHANCEMENT_BRIEF.md` - Complete enhancement requirements
2. **Reference:** `TEMPLATE_VARIABLES_REFERENCE.md` - All template variables
3. **Check:** `template_hierarchy.json` - Template inheritance structure
4. **Review:** `design_system.json` - Current design tokens

---

## 🎯 Key Rules

### **✅ DO:**

- Modernize visual design
- Improve layouts and spacing
- Add icons and animations
- Enhance mobile experience
- Improve accessibility
- Add charts and visualizations
- Update colors and typography
- Reorganize information architecture

### **❌ DON'T:**

- Change template file names/paths
- Modify Jinja2 syntax (`{% %}`, `{{ }}`)
- Change Flask functions (`url_for()`, `current_user`)
- Modify template variable names
- Remove role-based access controls
- Hardcode URLs
- Break template inheritance
- Change form input names

---

## 📝 Template Syntax Cheat Sheet

### **Template Inheritance:**
```jinja2
{% extends "base.html" %}
{% block title %}Page Title{% endblock %}
{% block content %}
    <!-- Page content here -->
{% endblock %}
```

### **Variables:**
```jinja2
{{ variable }}
{{ object.property }}
{{ list[0] }}
```

### **Conditionals:**
```jinja2
{% if condition %}
    <!-- Content -->
{% elif other_condition %}
    <!-- Other content -->
{% else %}
    <!-- Default content -->
{% endif %}
```

### **Loops:**
```jinja2
{% for item in items %}
    {{ item.name }}
{% endfor %}
```

### **URL Generation:**
```jinja2
{{ url_for('blueprint.endpoint') }}
{{ url_for('clients.detail', id=client.id) }}
{{ url_for('static', filename='css/main.css') }}
```

### **Current User:**
```jinja2
{{ current_user.username }}
{{ current_user.email }}
{% if current_user.is_authenticated %}...{% endif %}
{% if current_user.has_role('admin') %}...{% endif %}
```

### **Flash Messages:**
```jinja2
{% with messages = get_flashed_messages(with_categories=true) %}
    {% if messages %}
        {% for category, message in messages %}
            <div class="alert alert-{{ category }}">
                {{ message }}
            </div>
        {% endfor %}
    {% endif %}
{% endwith %}
```

---

## 🎨 Design System

### **Current Colors:**

```css
/* Primary */
--color-primary: #2563eb;
--color-primary-dark: #1e40af;
--color-primary-light: #3b82f6;

/* Semantic */
--color-success: #10b981;
--color-warning: #f59e0b;
--color-danger: #ef4444;
--color-info: #3b82f6;

/* Neutral */
--color-gray-50 to --color-gray-900
```

### **Typography:**

```css
--font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, ...;
--font-size-xs: 0.75rem;
--font-size-sm: 0.875rem;
--font-size-base: 1rem;
--font-size-lg: 1.125rem;
--font-size-xl: 1.25rem;
--font-size-2xl: 1.5rem;
```

### **Spacing:**

```css
--spacing-xs: 0.25rem;
--spacing-sm: 0.5rem;
--spacing-md: 1rem;
--spacing-lg: 1.5rem;
--spacing-xl: 2rem;
--spacing-2xl: 3rem;
```

---

## 📦 File Structure

```
ui_package/
├── templates/
│   ├── base.html              ← Base template (all extend this)
│   ├── dashboard.html         ← Main dashboard
│   ├── auth/                  ← Login, profile
│   ├── clients/               ← Client management
│   ├── projects/              ← Project management
│   ├── products/              ← Product catalog
│   ├── queue/                 ← Production queue
│   ├── inventory/             ← Inventory management
│   ├── quotes/                ← Quotes
│   ├── invoices/              ← Invoices
│   ├── comms/                 ← Communications
│   ├── reports/               ← Reports
│   ├── admin/                 ← Admin panel
│   └── errors/                ← Error pages
└── static/
    ├── css/
    │   └── main.css           ← Main stylesheet
    └── js/
        └── main.js            ← Main JavaScript
```

---

## 🔑 Common Template Variables

### **Global (Available Everywhere):**

- `current_user` - Logged-in user
- `company_name` - Company name
- `current_year` - Current year
- `request` - Flask request object

### **Dashboard:**

- `stats` - Statistics object
- `recent_clients` - Recent clients list
- `recent_projects` - Recent projects list
- `recent_products` - Recent products list
- `recent_files` - Recent files list
- `queue_items` - Queue items list

### **List Pages:**

- `clients` / `projects` / `products` - List of items
- `search` - Search query
- `pagination` - Pagination object

### **Detail Pages:**

- `client` / `project` / `product` - Single item
- `projects` - Related projects (on client detail)
- `activities` / `logs` - Activity logs

### **Forms:**

- `client` / `project` / `product` - Item being edited (or None for new)

---

## 🎯 Priority Templates

**Start with these:**

1. `base.html` - Affects all pages
2. `dashboard.html` - Main landing page
3. `clients/list.html` - Core functionality
4. `clients/detail.html` - Core functionality
5. `clients/form.html` - Core functionality
6. `projects/list.html` - Core functionality
7. `projects/detail.html` - Core functionality

---

## 🧪 Testing Checklist

Before delivering:

- [ ] All `{% %}` and `{{ }}` syntax intact
- [ ] All `url_for()` calls preserved
- [ ] All template variables used correctly
- [ ] Flash messages work
- [ ] Forms have correct action URLs
- [ ] Role checks preserved
- [ ] Template inheritance works
- [ ] No hardcoded URLs
- [ ] Responsive design works
- [ ] Accessibility standards met

---

## 📞 Questions?

Refer to:

- `AI_ENHANCEMENT_BRIEF.md` - Full requirements
- `TEMPLATE_VARIABLES_REFERENCE.md` - All variables
- `ROUTE_TEMPLATE_MAPPING.md` - Route mappings
- `FLASK_INTEGRATION_GUIDE.md` - Integration steps

---

**Happy Enhancing!** 🎨

