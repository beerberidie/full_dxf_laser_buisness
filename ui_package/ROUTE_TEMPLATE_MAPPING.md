# Route-Template Mapping
**Generated:** October 18, 2025

This document maps Flask routes (blueprints) to their templates.

---

## Admin Blueprint

**URL Prefix:** `/admin/` (except 'main' which is `/`)

### `admin/login_history.html`

**Variables:**
- `pagination`

### `admin/users/detail.html`

**Variables:**
- `login_history`
- `user`

### `admin/users/form.html`

**Variables:**
- `form`
- `user`

### `admin/users/list.html`

**Variables:**
- `users`

### `admin/users/reset_password.html`

**Variables:**
- `form`
- `user`


## Auth Blueprint

**URL Prefix:** `/auth/` (except 'main' which is `/`)

### `auth/change_password.html`

**Variables:**
- `form`

### `auth/login.html`

**Variables:**
- `form`

### `auth/profile.html`

**Variables:**
- `recent_logins`


## Clients Blueprint

**URL Prefix:** `/clients/` (except 'main' which is `/`)

### `clients/detail.html`

**Variables:**
- `activities`
- `client`
- `projects`

### `clients/form.html`

**Variables:**
- `client`

### `clients/list.html`

**Variables:**
- `clients`
- `pagination`
- `search`


## Comms Blueprint

**URL Prefix:** `/comms/` (except 'main' which is `/`)

### `comms/detail.html`

**Variables:**
- `clients`
- `communication`
- `projects`

### `comms/form.html`

**Variables:**
- `clients`
- `communication`
- `projects`

### `comms/list.html`

**Variables:**
- `clients`
- `comm_types`
- `communications`
- `directions`
- `pagination`
- `projects`
- `search`
- `selected_client_id`
- `selected_comm_type`
- `selected_direction`
- `selected_is_linked`
- `selected_project_id`
- `selected_status`
- `statuses`


## Files Blueprint

**URL Prefix:** `/files/` (except 'main' which is `/`)

### `files/detail.html`

**Variables:**
- `file`
- `logs`


## Inventory Blueprint

**URL Prefix:** `/inventory/` (except 'main' which is `/`)

### `inventory/detail.html`

**Variables:**
- `item`
- `logs`
- `transactions`

### `inventory/form.html`

**Variables:**
- `categories`
- `item`
- `material_types`
- `thicknesses`
- `units`

### `inventory/index.html`

**Variables:**
- `categories`
- `category_filter`
- `items`
- `low_stock_only`
- `search`
- `stats`

### `inventory/low_stock.html`

**Variables:**
- `items`

### `inventory/transactions.html`

**Variables:**
- `item_id`
- `transaction_type`
- `transaction_types`
- `transactions`


## Invoices Blueprint

**URL Prefix:** `/invoices/` (except 'main' which is `/`)

### `invoices/detail.html`

**Variables:**
- `invoice`

### `invoices/form.html`

**Variables:**
- `clients`
- `invoice`
- `projects`
- `quotes`

### `invoices/index.html`

**Variables:**
- `clients`
- `invoices`


## Main Blueprint

**URL Prefix:** `/main/` (except 'main' which is `/`)

### `dashboard.html`

**Variables:**
- `queue_items`
- `recent_clients`
- `recent_files`
- `recent_products`
- `recent_projects`
- `stats`


## Presets Blueprint

**URL Prefix:** `/presets/` (except 'main' which is `/`)

### `presets/form.html`

**Variables:**
- `action`
- `material_types`
- `preset`

### `presets/index.html`

**Variables:**
- `active_filter`
- `material_filter`
- `material_types`
- `presets`
- `search`


## Products Blueprint

**URL Prefix:** `/products/` (except 'main' which is `/`)

### `products/detail.html`

**Variables:**
- `activity_logs`
- `product`
- `product_files`
- `project_products`

### `products/form.html`

**Variables:**
- `materials`
- `product`
- `thicknesses`

### `products/list.html`

**Variables:**
- `material_filter`
- `materials`
- `pagination`
- `products`
- `search`


## Projects Blueprint

**URL Prefix:** `/projects/` (except 'main' which is `/`)

### `projects/detail.html`

**Variables:**
- `logs`
- `project`
- `today`

### `projects/form.html`

**Variables:**
- `clients`
- `material_types`
- `project`
- `statuses`

### `projects/list.html`

**Variables:**
- `clients`
- `pagination`
- `projects`
- `search`
- `selected_client_id`
- `selected_status`
- `statuses`


## Queue Blueprint

**URL Prefix:** `/queue/` (except 'main' which is `/`)

### `queue/detail.html`

**Variables:**
- `logs`
- `queue_item`
- `runs`

### `queue/index.html`

**Variables:**
- `queue_items`
- `stats`
- `status_filter`
- `today`

### `queue/run_form.html`

**Variables:**
- `material_types`
- `operators`
- `presets`
- `project`
- `queue_items`

### `queue/runs.html`

**Variables:**
- `date_from`
- `date_to`
- `operator_filter`
- `operators`
- `runs`


## Quotes Blueprint

**URL Prefix:** `/quotes/` (except 'main' which is `/`)

### `quotes/detail.html`

**Variables:**
- `quote`

### `quotes/form.html`

**Variables:**
- `clients`
- `projects`
- `quote`

### `quotes/index.html`

**Variables:**
- `clients`
- `quotes`


## Reports Blueprint

**URL Prefix:** `/reports/` (except 'main' which is `/`)

### `reports/clients.html`

**Variables:**
- `client_data`
- `stats`

### `reports/efficiency.html`

**Variables:**
- `efficiency_data`
- `stats`

### `reports/index.html`


### `reports/inventory.html`

**Variables:**
- `category_stats`
- `items`
- `recent_transactions`
- `stats`

### `reports/production.html`

**Variables:**
- `material_stats`
- `operator_stats`
- `runs`
- `start_date`
- `stats`


## Templates Blueprint

**URL Prefix:** `/templates/` (except 'main' which is `/`)

### `templates/detail.html`

**Variables:**
- `placeholders`
- `template`

### `templates/form.html`

**Variables:**
- `placeholders`
- `template`
- `template_types`

### `templates/list.html`

**Variables:**
- `current_active`
- `current_search`
- `current_type`
- `template_types`
- `templates`

