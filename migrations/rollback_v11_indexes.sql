-- ============================================================================
-- Laser OS Tier 1 - Rollback Database Indexes (Schema v11)
-- ============================================================================
-- Purpose: Remove all indexes created by schema_v11_indexes.sql
-- Date: October 18, 2025
-- ============================================================================

-- Projects table indexes
DROP INDEX IF EXISTS idx_projects_status;
DROP INDEX IF EXISTS idx_projects_client_created;
DROP INDEX IF EXISTS idx_projects_status_created;
DROP INDEX IF EXISTS idx_projects_due_date;

-- Design files table indexes
DROP INDEX IF EXISTS idx_design_files_project_upload;
DROP INDEX IF EXISTS idx_design_files_type;

-- Queue items table indexes
DROP INDEX IF EXISTS idx_queue_items_status_position;
DROP INDEX IF EXISTS idx_queue_items_scheduled_date;
DROP INDEX IF EXISTS idx_queue_items_priority;
DROP INDEX IF EXISTS idx_queue_items_project;

-- Inventory items table indexes
DROP INDEX IF EXISTS idx_inventory_items_category;
DROP INDEX IF EXISTS idx_inventory_items_low_stock;
DROP INDEX IF EXISTS idx_inventory_items_location;

-- Activity log table indexes
DROP INDEX IF EXISTS idx_activity_log_entity;
DROP INDEX IF EXISTS idx_activity_log_user_created;
DROP INDEX IF EXISTS idx_activity_log_action_created;

-- Communications table indexes
DROP INDEX IF EXISTS idx_communications_client_created;
DROP INDEX IF EXISTS idx_communications_type;
DROP INDEX IF EXISTS idx_communications_status;

-- Quotes table indexes
DROP INDEX IF EXISTS idx_quotes_client_date;
DROP INDEX IF EXISTS idx_quotes_status;

-- Invoices table indexes
DROP INDEX IF EXISTS idx_invoices_client_date;
DROP INDEX IF EXISTS idx_invoices_status;
DROP INDEX IF EXISTS idx_invoices_due_date;

-- Clients table indexes
DROP INDEX IF EXISTS idx_clients_code;
DROP INDEX IF EXISTS idx_clients_company_name;

-- Products table indexes
DROP INDEX IF EXISTS idx_products_sku;
DROP INDEX IF EXISTS idx_products_category;

-- Inventory transactions table indexes
DROP INDEX IF EXISTS idx_inventory_transactions_item_date;
DROP INDEX IF EXISTS idx_inventory_transactions_type;

-- Login history table indexes
DROP INDEX IF EXISTS idx_login_history_user_time;
DROP INDEX IF EXISTS idx_login_history_success_time;

-- ============================================================================
-- Verification: Check that all indexes were removed
-- ============================================================================
-- SELECT name, tbl_name FROM sqlite_master WHERE type = 'index' AND name LIKE 'idx_%' ORDER BY tbl_name, name;
-- ============================================================================

