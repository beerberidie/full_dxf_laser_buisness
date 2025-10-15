"""
Laser OS Tier 1 - Service Tests

This module tests the service functions.
"""

import pytest
from app import db
from app.models import Client, ActivityLog
from app.services.id_generator import (
    generate_client_code,
    generate_project_code,
    validate_client_code,
    validate_project_code
)
from app.services.activity_logger import (
    log_activity,
    get_entity_activities,
    get_recent_activities,
    get_user_activities
)


class TestIDGenerator:
    """Test ID generation functions."""
    
    def test_generate_client_code_first(self, app):
        """Test generating the first client code."""
        with app.app_context():
            code = generate_client_code()
            assert code == 'CL-0001'
    
    def test_generate_client_code_sequential(self, app, sample_client):
        """Test generating sequential client codes."""
        with app.app_context():
            # First client already exists (CL-0001)
            code = generate_client_code()
            assert code == 'CL-0002'
            
            # Create another client
            client = Client(client_code=code, name='Client 2')
            db.session.add(client)
            db.session.commit()
            
            # Generate next code
            code = generate_client_code()
            assert code == 'CL-0003'
    
    def test_generate_client_code_with_gaps(self, app):
        """Test generating client codes with gaps in sequence."""
        with app.app_context():
            # Create clients with gaps
            client1 = Client(client_code='CL-0001', name='Client 1')
            client3 = Client(client_code='CL-0003', name='Client 3')
            db.session.add(client1)
            db.session.add(client3)
            db.session.commit()
            
            # Should generate CL-0004 (next after highest)
            code = generate_client_code()
            assert code == 'CL-0004'
    
    def test_generate_project_code_format(self, app):
        """Test project code format."""
        with app.app_context():
            code = generate_project_code('CL-0001')
            
            # Should be in format JB-yyyy-mm-CLxxxx-###
            parts = code.split('-')
            assert len(parts) == 5
            assert parts[0] == 'JB'
            assert len(parts[1]) == 4  # Year
            assert len(parts[2]) == 2  # Month
            assert parts[3] == 'CL0001'  # Client code without hyphen
            assert parts[4] == '001'  # Sequence
    
    def test_validate_client_code_valid(self, app):
        """Test validating valid client codes."""
        with app.app_context():
            assert validate_client_code('CL-0001') is True
            assert validate_client_code('CL-0999') is True
            assert validate_client_code('CL-9999') is True
    
    def test_validate_client_code_invalid(self, app):
        """Test validating invalid client codes."""
        with app.app_context():
            assert validate_client_code('') is False
            assert validate_client_code('INVALID') is False
            assert validate_client_code('CL0001') is False  # Missing hyphen
            assert validate_client_code('CL-') is False  # Missing number
            assert validate_client_code('CL-ABC') is False  # Non-numeric
            assert validate_client_code('XX-0001') is False  # Wrong prefix
            assert validate_client_code('CL-00001') is False  # Too many digits
    
    def test_validate_project_code_valid(self, app):
        """Test validating valid project codes."""
        with app.app_context():
            assert validate_project_code('JB-2025-10-CL0001-001') is True
            assert validate_project_code('JB-2024-01-CL9999-999') is True
            assert validate_project_code('JB-2030-12-CL0123-456') is True
    
    def test_validate_project_code_invalid(self, app):
        """Test validating invalid project codes."""
        with app.app_context():
            assert validate_project_code('') is False
            assert validate_project_code('INVALID') is False
            assert validate_project_code('JB-2025-10-CL0001') is False  # Missing sequence
            assert validate_project_code('XX-2025-10-CL0001-001') is False  # Wrong prefix
            assert validate_project_code('JB-25-10-CL0001-001') is False  # Year too short
            assert validate_project_code('JB-2025-13-CL0001-001') is False  # Invalid month
            assert validate_project_code('JB-2025-00-CL0001-001') is False  # Invalid month
            assert validate_project_code('JB-2025-10-XX0001-001') is False  # Wrong client prefix


class TestActivityLogger:
    """Test activity logging functions."""
    
    def test_log_activity_basic(self, app):
        """Test logging a basic activity."""
        with app.app_context():
            log = log_activity('CLIENT', 1, 'CREATED')
            
            assert log is not None
            assert log.entity_type == 'CLIENT'
            assert log.entity_id == 1
            assert log.action == 'CREATED'
            assert log.user == 'admin'
    
    def test_log_activity_with_details(self, app):
        """Test logging activity with details."""
        with app.app_context():
            details = {'name': 'Test Client', 'code': 'CL-0001'}
            log = log_activity('CLIENT', 1, 'CREATED', details=details)
            
            assert log.details is not None
            assert 'Test Client' in log.details
            assert 'CL-0001' in log.details
    
    def test_log_activity_with_user(self, app):
        """Test logging activity with custom user."""
        with app.app_context():
            log = log_activity('CLIENT', 1, 'UPDATED', user='testuser')
            
            assert log.user == 'testuser'
    
    def test_log_activity_case_normalization(self, app):
        """Test that entity type and action are normalized to uppercase."""
        with app.app_context():
            log = log_activity('client', 1, 'created')
            
            assert log.entity_type == 'CLIENT'
            assert log.action == 'CREATED'
    
    def test_get_entity_activities(self, app):
        """Test getting activities for a specific entity."""
        with app.app_context():
            # Create multiple activities
            log_activity('CLIENT', 1, 'CREATED')
            log_activity('CLIENT', 1, 'UPDATED')
            log_activity('CLIENT', 2, 'CREATED')
            log_activity('PROJECT', 1, 'CREATED')
            
            # Get activities for CLIENT 1
            activities = get_entity_activities('CLIENT', 1)
            
            assert len(activities) == 2
            assert all(a.entity_type == 'CLIENT' for a in activities)
            assert all(a.entity_id == 1 for a in activities)
            
            # Should be ordered by most recent first
            assert activities[0].action == 'UPDATED'
            assert activities[1].action == 'CREATED'
    
    def test_get_entity_activities_limit(self, app):
        """Test limiting the number of activities returned."""
        with app.app_context():
            # Create many activities
            for i in range(10):
                log_activity('CLIENT', 1, 'UPDATED')
            
            # Get with limit
            activities = get_entity_activities('CLIENT', 1, limit=5)
            
            assert len(activities) == 5
    
    def test_get_recent_activities(self, app):
        """Test getting recent activities across all entities."""
        with app.app_context():
            # Create activities for different entities
            log_activity('CLIENT', 1, 'CREATED')
            log_activity('CLIENT', 2, 'CREATED')
            log_activity('PROJECT', 1, 'CREATED')
            
            # Get recent activities
            activities = get_recent_activities(limit=10)
            
            assert len(activities) == 3
            
            # Should be ordered by most recent first
            assert activities[0].entity_type == 'PROJECT'
            assert activities[1].entity_type == 'CLIENT'
            assert activities[1].entity_id == 2
    
    def test_get_user_activities(self, app):
        """Test getting activities for a specific user."""
        with app.app_context():
            # Create activities for different users
            log_activity('CLIENT', 1, 'CREATED', user='admin')
            log_activity('CLIENT', 2, 'CREATED', user='admin')
            log_activity('CLIENT', 3, 'CREATED', user='testuser')
            
            # Get activities for admin
            activities = get_user_activities('admin')
            
            assert len(activities) == 2
            assert all(a.user == 'admin' for a in activities)
    
    def test_get_user_activities_limit(self, app):
        """Test limiting user activities."""
        with app.app_context():
            # Create many activities
            for i in range(10):
                log_activity('CLIENT', i, 'CREATED', user='admin')
            
            # Get with limit
            activities = get_user_activities('admin', limit=5)
            
            assert len(activities) == 5

