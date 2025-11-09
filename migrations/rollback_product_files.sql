-- Rollback: Remove product_files table
-- Date: 2025-10-16
-- Description: Drops product_files table and related indexes

-- Drop indexes
DROP INDEX IF EXISTS idx_product_files_created_at;
DROP INDEX IF EXISTS idx_product_files_upload_date;
DROP INDEX IF EXISTS idx_product_files_product_id;

-- Drop table
DROP TABLE IF EXISTS product_files;

-- Verify rollback
SELECT 'product_files table dropped successfully' AS status;

