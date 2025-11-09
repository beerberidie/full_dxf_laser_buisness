-- Laser OS - Sage Business Cloud Accounting Integration Schema
-- Version: Sage Integration v1.0
-- Date: 2025-10-24
-- Description: Creates tables for Sage OAuth connection, business management, sync tracking, and audit logging

-- Enable foreign keys
PRAGMA foreign_keys = ON;

-- ============================================================================
-- Sage OAuth Connection Table
-- ============================================================================

CREATE TABLE IF NOT EXISTS sage_connections (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL UNIQUE,
    access_token TEXT NOT NULL,
    refresh_token TEXT NOT NULL,
    token_type VARCHAR(50) NOT NULL DEFAULT 'Bearer',
    expires_at DATETIME NOT NULL,
    scope VARCHAR(500),
    is_active BOOLEAN NOT NULL DEFAULT 1,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE INDEX idx_sage_connections_user ON sage_connections(user_id);
CREATE INDEX idx_sage_connections_active ON sage_connections(is_active);

-- ============================================================================
-- Sage Business Contexts Table
-- ============================================================================

CREATE TABLE IF NOT EXISTS sage_businesses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    connection_id INTEGER NOT NULL,
    sage_business_id VARCHAR(100) NOT NULL,
    name VARCHAR(200),
    displayed_as VARCHAR(200),
    is_selected BOOLEAN NOT NULL DEFAULT 0,
    business_metadata TEXT,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (connection_id) REFERENCES sage_connections(id) ON DELETE CASCADE,
    UNIQUE (connection_id, sage_business_id)
);

CREATE INDEX idx_sage_businesses_connection ON sage_businesses(connection_id);
CREATE INDEX idx_sage_businesses_sage_id ON sage_businesses(sage_business_id);
CREATE INDEX idx_sage_businesses_selected ON sage_businesses(is_selected);

-- ============================================================================
-- Sage Sync Cursors Table
-- ============================================================================

CREATE TABLE IF NOT EXISTS sage_sync_cursors (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    business_id INTEGER NOT NULL,
    resource_type VARCHAR(100) NOT NULL,
    last_sync_at DATETIME,
    cursor_value VARCHAR(500),
    sync_status VARCHAR(50) NOT NULL DEFAULT 'pending',
    error_message TEXT,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (business_id) REFERENCES sage_businesses(id) ON DELETE CASCADE,
    UNIQUE (business_id, resource_type),
    CHECK (sync_status IN ('pending', 'in_progress', 'success', 'failed'))
);

CREATE INDEX idx_sage_sync_cursors_business ON sage_sync_cursors(business_id);
CREATE INDEX idx_sage_sync_cursors_resource ON sage_sync_cursors(resource_type);
CREATE INDEX idx_sage_sync_cursors_status ON sage_sync_cursors(sync_status);

-- ============================================================================
-- Sage Audit Log Table
-- ============================================================================

CREATE TABLE IF NOT EXISTS sage_audit_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    connection_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    operation_type VARCHAR(50) NOT NULL,
    resource_type VARCHAR(100) NOT NULL,
    resource_id VARCHAR(100),
    status VARCHAR(50) NOT NULL,
    request_data TEXT,
    response_data TEXT,
    error_message TEXT,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (connection_id) REFERENCES sage_connections(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    CHECK (operation_type IN ('create', 'update', 'delete', 'read')),
    CHECK (status IN ('preview', 'confirmed', 'success', 'failed'))
);

CREATE INDEX idx_sage_audit_logs_connection ON sage_audit_logs(connection_id);
CREATE INDEX idx_sage_audit_logs_user ON sage_audit_logs(user_id);
CREATE INDEX idx_sage_audit_logs_operation ON sage_audit_logs(operation_type);
CREATE INDEX idx_sage_audit_logs_resource ON sage_audit_logs(resource_type);
CREATE INDEX idx_sage_audit_logs_status ON sage_audit_logs(status);
CREATE INDEX idx_sage_audit_logs_created ON sage_audit_logs(created_at);

-- ============================================================================
-- Schema Version Tracking
-- ============================================================================

INSERT INTO schema_version (version) VALUES ('sage_integration_v1.0');

-- ============================================================================
-- Migration Complete
-- ============================================================================

-- Verify tables were created
SELECT 'Sage Integration Schema v1.0 applied successfully' AS status;
SELECT 'Created tables: sage_connections, sage_businesses, sage_sync_cursors, sage_audit_logs' AS tables;

