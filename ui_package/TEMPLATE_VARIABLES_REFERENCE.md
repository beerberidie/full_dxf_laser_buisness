# Template Variables Reference
**Generated:** October 18, 2025

This document lists all variables passed to templates from Flask routes.

---

## Global Template Variables

These variables are available in ALL templates:

- `current_user` - Currently logged-in user object
  - `current_user.username` - Username
  - `current_user.email` - Email address
  - `current_user.is_authenticated` - Boolean, True if logged in
  - `current_user.has_role('role_name')` - Check if user has specific role
  - `current_user.roles` - List of user roles
  - `current_user.is_superuser` - Boolean, True if superuser
- `company_name` - Company name from config
- `current_year` - Current year for footer
- `request` - Flask request object
  - `request.endpoint` - Current route endpoint
  - `request.args` - URL query parameters
  - `request.form` - Form data
- `url_for()` - Function to generate URLs
- `get_flashed_messages()` - Function to get flash messages

---

## Template-Specific Variables

### `admin/login_history.html`

- `pagination`

### `admin/users/detail.html`

- `login_history`
- `user`

### `admin/users/form.html`

- `form`
- `user`

### `admin/users/list.html`

- `users`

### `admin/users/reset_password.html`

- `form`
- `user`

### `auth/change_password.html`

- `form`

### `auth/login.html`

- `form`

### `auth/profile.html`

- `recent_logins`

### `clients/detail.html`

- `activities`
- `client`
- `projects`

### `clients/form.html`

- `client`

### `clients/list.html`

- `clients`
- `pagination`
- `search`

### `comms/detail.html`

- `clients`
- `communication`
- `projects`

### `comms/form.html`

- `clients`
- `communication`
- `projects`

### `comms/list.html`

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

### `dashboard.html`

- `queue_items`
- `recent_clients`
- `recent_files`
- `recent_products`
- `recent_projects`
- `stats`

### `files/detail.html`

- `file`
- `logs`

### `inventory/detail.html`

- `item`
- `logs`
- `transactions`

### `inventory/form.html`

- `categories`
- `item`
- `material_types`
- `thicknesses`
- `units`

### `inventory/index.html`

- `categories`
- `category_filter`
- `items`
- `low_stock_only`
- `search`
- `stats`

### `inventory/low_stock.html`

- `items`

### `inventory/transactions.html`

- `item_id`
- `transaction_type`
- `transaction_types`
- `transactions`

### `invoices/detail.html`

- `invoice`

### `invoices/form.html`

- `clients`
- `invoice`
- `projects`
- `quotes`

### `invoices/index.html`

- `clients`
- `invoices`

### `presets/form.html`

- `action`
- `material_types`
- `preset`

### `presets/index.html`

- `active_filter`
- `material_filter`
- `material_types`
- `presets`
- `search`

### `products/detail.html`

- `activity_logs`
- `product`
- `product_files`
- `project_products`

### `products/form.html`

- `materials`
- `product`
- `thicknesses`

### `products/list.html`

- `material_filter`
- `materials`
- `pagination`
- `products`
- `search`

### `projects/detail.html`

- `logs`
- `project`
- `today`

### `projects/form.html`

- `clients`
- `material_types`
- `project`
- `statuses`

### `projects/list.html`

- `clients`
- `pagination`
- `projects`
- `search`
- `selected_client_id`
- `selected_status`
- `statuses`

### `queue/detail.html`

- `logs`
- `queue_item`
- `runs`

### `queue/index.html`

- `queue_items`
- `stats`
- `status_filter`
- `today`

### `queue/run_form.html`

- `material_types`
- `operators`
- `presets`
- `project`
- `queue_items`

### `queue/runs.html`

- `date_from`
- `date_to`
- `operator_filter`
- `operators`
- `runs`

### `quotes/detail.html`

- `quote`

### `quotes/form.html`

- `clients`
- `projects`
- `quote`

### `quotes/index.html`

- `clients`
- `quotes`

### `reports/clients.html`

- `client_data`
- `stats`

### `reports/efficiency.html`

- `efficiency_data`
- `stats`

### `reports/inventory.html`

- `category_stats`
- `items`
- `recent_transactions`
- `stats`

### `reports/production.html`

- `material_stats`
- `operator_stats`
- `runs`
- `start_date`
- `stats`

### `templates/detail.html`

- `placeholders`
- `template`

### `templates/form.html`

- `placeholders`
- `template`
- `template_types`

### `templates/list.html`

- `current_active`
- `current_search`
- `current_type`
- `template_types`
- `templates`
