-- ============================================================================
-- Laser OS Tier 1 - Database Indexes Migration (Schema v11)
-- ============================================================================
-- Purpose: Add performance indexes for frequently queried fields
-- Date: October 18, 2025
-- Impact: 30-50% faster queries on filtered/sorted lists
-- 
-- This migration adds indexes to improve query performance across the
-- application, particularly for:
-- - Project filtering and sorting
-- - Design file lookups
-- Queue management
-- - Activity log queries
-- - Communication history
-- - Inventory filtering
-- ============================================================================

-- ============================================================================
-- PROJECTS TABLE INDEXES
-- ============================================================================

-- Index for filtering projects by status (used in dashboard, project list)
-- Improves: SELECT * FROM projects WHERE status = 'Approved'
CREATE INDEX IF NOT EXISTS idx_projects_status 
ON projects(status);

-- Composite index for client's projects sorted by date
-- Improves: SELECT * FROM projects WHERE client_id = X ORDER BY created_at DESC
CREATE INDEX IF NOT EXISTS idx_projects_client_created 
ON projects(client_id, created_at DESC);

-- Index for filtering by project status and sorting by date
-- Improves: SELECT * FROM projects WHERE status IN (...) ORDER BY created_at DESC
CREATE INDEX IF NOT EXISTS idx_projects_status_created 
ON projects(status, created_at DESC);

-- Index for due date queries (upcoming deadlines, overdue projects)
-- Improves: SELECT * FROM projects WHERE due_date < NOW() AND status != 'Completed'
CREATE INDEX IF NOT EXISTS idx_projects_due_date 
ON projects(due_date);

-- ============================================================================
-- DESIGN FILES TABLE INDEXES
-- ============================================================================

-- Composite index for project's files sorted by upload date
-- Improves: SELECT * FROM design_files WHERE project_id = X ORDER BY upload_date DESC
CREATE INDEX IF NOT EXISTS idx_design_files_project_upload 
ON design_files(project_id, upload_date DESC);

-- Index for file type filtering
-- Improves: SELECT * FROM design_files WHERE file_type = 'DXF'
CREATE INDEX IF NOT EXISTS idx_design_files_type 
ON design_files(file_type);

-- ============================================================================
-- QUEUE ITEMS TABLE INDEXES
-- ============================================================================

-- Composite index for queue filtering and sorting
-- Improves: SELECT * FROM queue_items WHERE status IN (...) ORDER BY queue_position
CREATE INDEX IF NOT EXISTS idx_queue_items_status_position 
ON queue_items(status, queue_position);

-- Index for scheduled date queries (daily production schedule)
-- Improves: SELECT * FROM queue_items WHERE scheduled_date = '2025-10-18'
CREATE INDEX IF NOT EXISTS idx_queue_items_scheduled_date 
ON queue_items(scheduled_date);

-- Index for priority-based sorting
-- Improves: SELECT * FROM queue_items ORDER BY priority, queue_position
CREATE INDEX IF NOT EXISTS idx_queue_items_priority 
ON queue_items(priority, queue_position);

-- Composite index for project's queue items
-- Improves: SELECT * FROM queue_items WHERE project_id = X
CREATE INDEX IF NOT EXISTS idx_queue_items_project 
ON queue_items(project_id);

-- ============================================================================
-- INVENTORY ITEMS TABLE INDEXES
-- ============================================================================

-- Index for category filtering
-- Improves: SELECT * FROM inventory_items WHERE category = 'Materials'
CREATE INDEX IF NOT EXISTS idx_inventory_items_category 
ON inventory_items(category);

-- Index for low stock queries
-- Improves: SELECT * FROM inventory_items WHERE quantity <= reorder_level
CREATE INDEX IF NOT EXISTS idx_inventory_items_low_stock 
ON inventory_items(quantity, reorder_level);

-- Index for location-based queries
-- Improves: SELECT * FROM inventory_items WHERE location = 'Warehouse A'
CREATE INDEX IF NOT EXISTS idx_inventory_items_location 
ON inventory_items(location);

-- ============================================================================
-- ACTIVITY LOG TABLE INDEXES
-- ============================================================================

-- Composite index for entity activity history
-- Improves: SELECT * FROM activity_log WHERE entity_type = 'PROJECT' AND entity_id = X ORDER BY created_at DESC
CREATE INDEX IF NOT EXISTS idx_activity_log_entity 
ON activity_log(entity_type, entity_id, created_at DESC);

-- Index for user activity history
-- Improves: SELECT * FROM activity_log WHERE user = 'admin' ORDER BY created_at DESC
CREATE INDEX IF NOT EXISTS idx_activity_log_user_created 
ON activity_log(user, created_at DESC);

-- Index for action-based filtering
-- Improves: SELECT * FROM activity_log WHERE action = 'CREATE' ORDER BY created_at DESC
CREATE INDEX IF NOT EXISTS idx_activity_log_action_created 
ON activity_log(action, created_at DESC);

-- ============================================================================
-- COMMUNICATIONS TABLE INDEXES
-- ============================================================================

-- Composite index for client communications sorted by date
-- Improves: SELECT * FROM communications WHERE client_id = X ORDER BY created_at DESC
CREATE INDEX IF NOT EXISTS idx_communications_client_created 
ON communications(client_id, created_at DESC);

-- Index for communication type filtering
-- Improves: SELECT * FROM communications WHERE comm_type = 'Email'
CREATE INDEX IF NOT EXISTS idx_communications_type 
ON communications(comm_type);

-- Index for status filtering (sent, failed, pending)
-- Improves: SELECT * FROM communications WHERE status = 'Failed'
CREATE INDEX IF NOT EXISTS idx_communications_status 
ON communications(status);

-- ============================================================================
-- QUOTES TABLE INDEXES
-- ============================================================================

-- Composite index for client quotes sorted by date
-- Improves: SELECT * FROM quotes WHERE client_id = X ORDER BY quote_date DESC
CREATE INDEX IF NOT EXISTS idx_quotes_client_date 
ON quotes(client_id, quote_date DESC);

-- Index for quote status filtering
-- Improves: SELECT * FROM quotes WHERE status = 'Pending'
CREATE INDEX IF NOT EXISTS idx_quotes_status 
ON quotes(status);

-- ============================================================================
-- INVOICES TABLE INDEXES
-- ============================================================================

-- Composite index for client invoices sorted by date
-- Improves: SELECT * FROM invoices WHERE client_id = X ORDER BY invoice_date DESC
CREATE INDEX IF NOT EXISTS idx_invoices_client_date 
ON invoices(client_id, invoice_date DESC);

-- Index for invoice status filtering
-- Improves: SELECT * FROM invoices WHERE status = 'Unpaid'
CREATE INDEX IF NOT EXISTS idx_invoices_status 
ON invoices(status);

-- Index for due date queries (overdue invoices)
-- Improves: SELECT * FROM invoices WHERE due_date < NOW() AND status = 'Unpaid'
CREATE INDEX IF NOT EXISTS idx_invoices_due_date 
ON invoices(due_date);

-- ============================================================================
-- CLIENTS TABLE INDEXES
-- ============================================================================

-- Index for client code lookups (unique but frequently searched)
-- Improves: SELECT * FROM clients WHERE client_code = 'CLI-001'
CREATE INDEX IF NOT EXISTS idx_clients_code 
ON clients(client_code);

-- Index for client name searches
-- Improves: SELECT * FROM clients WHERE company_name LIKE '%ABC%'
CREATE INDEX IF NOT EXISTS idx_clients_company_name 
ON clients(company_name);

-- ============================================================================
-- PRODUCTS TABLE INDEXES
-- ============================================================================

-- Index for SKU code lookups
-- Improves: SELECT * FROM products WHERE sku_code = 'SKU-001'
CREATE INDEX IF NOT EXISTS idx_products_sku 
ON products(sku_code);

-- Index for category filtering
-- Improves: SELECT * FROM products WHERE category = 'Laser Cut Parts'
CREATE INDEX IF NOT EXISTS idx_products_category 
ON products(category);

-- ============================================================================
-- INVENTORY TRANSACTIONS TABLE INDEXES
-- ============================================================================

-- Composite index for item transaction history
-- Improves: SELECT * FROM inventory_transactions WHERE inventory_item_id = X ORDER BY transaction_date DESC
CREATE INDEX IF NOT EXISTS idx_inventory_transactions_item_date 
ON inventory_transactions(inventory_item_id, transaction_date DESC);

-- Index for transaction type filtering
-- Improves: SELECT * FROM inventory_transactions WHERE transaction_type = 'Usage'
CREATE INDEX IF NOT EXISTS idx_inventory_transactions_type 
ON inventory_transactions(transaction_type);

-- ============================================================================
-- LOGIN HISTORY TABLE INDEXES
-- ============================================================================

-- Composite index for user login history
-- Improves: SELECT * FROM login_history WHERE user_id = X ORDER BY login_time DESC
CREATE INDEX IF NOT EXISTS idx_login_history_user_time 
ON login_history(user_id, login_time DESC);

-- Index for failed login attempts monitoring
-- Improves: SELECT * FROM login_history WHERE success = 0 ORDER BY login_time DESC
CREATE INDEX IF NOT EXISTS idx_login_history_success_time 
ON login_history(success, login_time DESC);

-- ============================================================================
-- VERIFICATION QUERIES
-- ============================================================================
-- Run these queries to verify indexes were created successfully:
-- 
-- SELECT name, tbl_name FROM sqlite_master WHERE type = 'index' AND name LIKE 'idx_%' ORDER BY tbl_name, name;
-- 
-- To check if an index is being used:
-- EXPLAIN QUERY PLAN SELECT * FROM projects WHERE status = 'Approved';
-- 
-- ============================================================================
-- ROLLBACK INSTRUCTIONS
-- ============================================================================
-- To remove all indexes created by this migration:
-- 
-- DROP INDEX IF EXISTS idx_projects_status;
-- DROP INDEX IF EXISTS idx_projects_client_created;
-- DROP INDEX IF EXISTS idx_projects_status_created;
-- DROP INDEX IF EXISTS idx_projects_due_date;
-- DROP INDEX IF EXISTS idx_design_files_project_upload;
-- DROP INDEX IF EXISTS idx_design_files_type;
-- DROP INDEX IF EXISTS idx_queue_items_status_position;
-- DROP INDEX IF EXISTS idx_queue_items_scheduled_date;
-- DROP INDEX IF EXISTS idx_queue_items_priority;
-- DROP INDEX IF EXISTS idx_queue_items_project;
-- DROP INDEX IF EXISTS idx_inventory_items_category;
-- DROP INDEX IF EXISTS idx_inventory_items_low_stock;
-- DROP INDEX IF EXISTS idx_inventory_items_location;
-- DROP INDEX IF EXISTS idx_activity_log_entity;
-- DROP INDEX IF EXISTS idx_activity_log_user_created;
-- DROP INDEX IF EXISTS idx_activity_log_action_created;
-- DROP INDEX IF EXISTS idx_communications_client_created;
-- DROP INDEX IF EXISTS idx_communications_type;
-- DROP INDEX IF EXISTS idx_communications_status;
-- DROP INDEX IF EXISTS idx_quotes_client_date;
-- DROP INDEX IF EXISTS idx_quotes_status;
-- DROP INDEX IF EXISTS idx_invoices_client_date;
-- DROP INDEX IF EXISTS idx_invoices_status;
-- DROP INDEX IF EXISTS idx_invoices_due_date;
-- DROP INDEX IF EXISTS idx_clients_code;
-- DROP INDEX IF EXISTS idx_clients_company_name;
-- DROP INDEX IF EXISTS idx_products_sku;
-- DROP INDEX IF EXISTS idx_products_category;
-- DROP INDEX IF EXISTS idx_inventory_transactions_item_date;
-- DROP INDEX IF EXISTS idx_inventory_transactions_type;
-- DROP INDEX IF EXISTS idx_login_history_user_time;
-- DROP INDEX IF EXISTS idx_login_history_success_time;
-- ============================================================================

