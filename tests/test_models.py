"""
Laser OS Tier 1 - Model Tests

This module tests the database models.
"""

import pytest
from datetime import datetime
from app import db
from app.models import Client, ActivityLog, Setting


class TestClientModel:
    """Test the Client model."""
    
    def test_create_client(self, app):
        """Test creating a new client."""
        with app.app_context():
            client = Client(
                client_code='CL-0001',
                name='Test Company',
                contact_person='John Doe',
                email='john@test.com',
                phone='+27 11 123 4567'
            )
            db.session.add(client)
            db.session.commit()
            
            assert client.id is not None
            assert client.client_code == 'CL-0001'
            assert client.name == 'Test Company'
            assert client.contact_person == 'John Doe'
            assert client.email == 'john@test.com'
            assert client.phone == '+27 11 123 4567'
            assert client.created_at is not None
            assert client.updated_at is not None
    
    def test_client_unique_code(self, app):
        """Test that client codes must be unique."""
        with app.app_context():
            client1 = Client(client_code='CL-0001', name='Client 1')
            client2 = Client(client_code='CL-0001', name='Client 2')
            
            db.session.add(client1)
            db.session.commit()
            
            db.session.add(client2)
            with pytest.raises(Exception):  # Should raise IntegrityError
                db.session.commit()
    
    def test_client_to_dict(self, app, sample_client):
        """Test converting client to dictionary."""
        with app.app_context():
            client = Client.query.first()
            data = client.to_dict()
            
            assert data['id'] == client.id
            assert data['client_code'] == client.client_code
            assert data['name'] == client.name
            assert data['contact_person'] == client.contact_person
            assert data['email'] == client.email
            assert data['phone'] == client.phone
            assert 'created_at' in data
            assert 'updated_at' in data
    
    def test_client_repr(self, app, sample_client):
        """Test client string representation."""
        with app.app_context():
            client = Client.query.first()
            repr_str = repr(client)
            
            assert 'Client' in repr_str
            assert client.client_code in repr_str
            assert client.name in repr_str
    
    def test_client_optional_fields(self, app):
        """Test that optional fields can be None."""
        with app.app_context():
            client = Client(
                client_code='CL-0002',
                name='Minimal Client'
            )
            db.session.add(client)
            db.session.commit()
            
            assert client.contact_person is None
            assert client.email is None
            assert client.phone is None
            assert client.address is None
            assert client.notes is None
    
    def test_client_update(self, app, sample_client):
        """Test updating a client."""
        with app.app_context():
            client = Client.query.first()
            original_updated_at = client.updated_at
            
            # Update client
            client.name = 'Updated Name'
            client.email = 'updated@test.com'
            db.session.commit()
            
            # Verify updates
            updated_client = Client.query.first()
            assert updated_client.name == 'Updated Name'
            assert updated_client.email == 'updated@test.com'
    
    def test_client_delete(self, app, sample_client):
        """Test deleting a client."""
        with app.app_context():
            client = Client.query.first()
            client_id = client.id
            
            db.session.delete(client)
            db.session.commit()
            
            # Verify deletion
            deleted_client = Client.query.get(client_id)
            assert deleted_client is None


class TestActivityLogModel:
    """Test the ActivityLog model."""
    
    def test_create_activity_log(self, app):
        """Test creating an activity log entry."""
        with app.app_context():
            log = ActivityLog(
                entity_type='CLIENT',
                entity_id=1,
                action='CREATED',
                user='admin',
                details='{"name": "Test Client"}',
                ip_address='127.0.0.1'
            )
            db.session.add(log)
            db.session.commit()
            
            assert log.id is not None
            assert log.entity_type == 'CLIENT'
            assert log.entity_id == 1
            assert log.action == 'CREATED'
            assert log.user == 'admin'
            assert log.details == '{"name": "Test Client"}'
            assert log.ip_address == '127.0.0.1'
            assert log.created_at is not None
    
    def test_activity_log_to_dict(self, app):
        """Test converting activity log to dictionary."""
        with app.app_context():
            log = ActivityLog(
                entity_type='CLIENT',
                entity_id=1,
                action='CREATED',
                user='admin'
            )
            db.session.add(log)
            db.session.commit()
            
            data = log.to_dict()
            
            assert data['id'] == log.id
            assert data['entity_type'] == log.entity_type
            assert data['entity_id'] == log.entity_id
            assert data['action'] == log.action
            assert data['user'] == log.user
            assert 'created_at' in data
    
    def test_activity_log_repr(self, app):
        """Test activity log string representation."""
        with app.app_context():
            log = ActivityLog(
                entity_type='CLIENT',
                entity_id=1,
                action='CREATED'
            )
            db.session.add(log)
            db.session.commit()
            
            repr_str = repr(log)
            
            assert 'ActivityLog' in repr_str
            assert 'CLIENT' in repr_str
            assert 'CREATED' in repr_str


class TestSettingModel:
    """Test the Setting model."""
    
    def test_create_setting(self, app):
        """Test creating a setting."""
        with app.app_context():
            setting = Setting(
                key='test_key',
                value='test_value',
                description='Test setting'
            )
            db.session.add(setting)
            db.session.commit()
            
            assert setting.key == 'test_key'
            assert setting.value == 'test_value'
            assert setting.description == 'Test setting'
            assert setting.updated_at is not None
    
    def test_setting_get(self, app):
        """Test getting a setting value."""
        with app.app_context():
            # Create a setting
            setting = Setting(key='test_key', value='test_value')
            db.session.add(setting)
            db.session.commit()
            
            # Get the setting
            value = Setting.get('test_key')
            assert value == 'test_value'
            
            # Get non-existent setting with default
            value = Setting.get('non_existent', 'default_value')
            assert value == 'default_value'
    
    def test_setting_set(self, app):
        """Test setting a value."""
        with app.app_context():
            # Set a new setting
            Setting.set('new_key', 'new_value', 'New setting')
            
            setting = Setting.query.get('new_key')
            assert setting is not None
            assert setting.value == 'new_value'
            assert setting.description == 'New setting'
            
            # Update existing setting
            Setting.set('new_key', 'updated_value')
            
            setting = Setting.query.get('new_key')
            assert setting.value == 'updated_value'
    
    def test_setting_repr(self, app):
        """Test setting string representation."""
        with app.app_context():
            setting = Setting(key='test_key', value='test_value')
            db.session.add(setting)
            db.session.commit()
            
            repr_str = repr(setting)
            
            assert 'Setting' in repr_str
            assert 'test_key' in repr_str
            assert 'test_value' in repr_str

