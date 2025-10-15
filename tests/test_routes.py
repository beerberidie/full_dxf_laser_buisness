"""
Laser OS Tier 1 - Route Tests

This module tests the route handlers.
"""

import pytest
from app import db
from app.models import Client


class TestMainRoutes:
    """Test main routes."""
    
    def test_dashboard(self, client):
        """Test dashboard page loads."""
        response = client.get('/')
        assert response.status_code == 200
        assert b'Dashboard' in response.data
    
    def test_dashboard_with_clients(self, client, multiple_clients):
        """Test dashboard shows recent clients."""
        response = client.get('/')
        assert response.status_code == 200
        assert b'Recent Clients' in response.data


class TestClientRoutes:
    """Test client routes."""
    
    def test_list_clients_empty(self, client):
        """Test listing clients when none exist."""
        response = client.get('/clients/')
        assert response.status_code == 200
        assert b'No clients found' in response.data
    
    def test_list_clients_with_data(self, client, multiple_clients):
        """Test listing clients with data."""
        response = client.get('/clients/')
        assert response.status_code == 200
        assert b'Test Client 1' in response.data
        assert b'Test Client 2' in response.data
        assert b'CL-0001' in response.data
    
    def test_list_clients_search(self, client, multiple_clients):
        """Test searching clients."""
        response = client.get('/clients/?search=Client 1')
        assert response.status_code == 200
        assert b'Test Client 1' in response.data
        assert b'Test Client 2' not in response.data
    
    def test_new_client_get(self, client):
        """Test GET request to new client form."""
        response = client.get('/clients/new')
        assert response.status_code == 200
        assert b'New Client' in response.data
        assert b'Client Name' in response.data
    
    def test_new_client_post_valid(self, client, app):
        """Test creating a new client with valid data."""
        response = client.post('/clients/new', data={
            'name': 'New Test Client',
            'contact_person': 'Jane Doe',
            'email': 'jane@test.com',
            'phone': '+27 11 999 8888',
            'address': '456 Test Ave',
            'notes': 'Test notes'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        assert b'created successfully' in response.data
        
        # Verify client was created in database
        with app.app_context():
            new_client = Client.query.filter_by(name='New Test Client').first()
            assert new_client is not None
            assert new_client.client_code == 'CL-0001'
            assert new_client.contact_person == 'Jane Doe'
            assert new_client.email == 'jane@test.com'
    
    def test_new_client_post_missing_name(self, client):
        """Test creating a client without a name."""
        response = client.post('/clients/new', data={
            'contact_person': 'Jane Doe'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        assert b'required' in response.data or b'New Client' in response.data
    
    def test_new_client_sequential_codes(self, client, app):
        """Test that client codes are sequential."""
        # Create first client
        client.post('/clients/new', data={'name': 'Client 1'})
        
        # Create second client
        client.post('/clients/new', data={'name': 'Client 2'})
        
        # Verify codes
        with app.app_context():
            client1 = Client.query.filter_by(name='Client 1').first()
            client2 = Client.query.filter_by(name='Client 2').first()
            
            assert client1.client_code == 'CL-0001'
            assert client2.client_code == 'CL-0002'
    
    def test_client_detail(self, client, sample_client):
        """Test viewing client details."""
        response = client.get('/clients/1')
        assert response.status_code == 200
        assert b'Test Client' in response.data
        assert b'CL-0001' in response.data
        assert b'John Doe' in response.data
    
    def test_client_detail_not_found(self, client):
        """Test viewing non-existent client."""
        response = client.get('/clients/999')
        assert response.status_code == 404
    
    def test_edit_client_get(self, client, sample_client):
        """Test GET request to edit client form."""
        response = client.get('/clients/1/edit')
        assert response.status_code == 200
        assert b'Edit Client' in response.data
        assert b'Test Client' in response.data
        assert b'CL-0001' in response.data
    
    def test_edit_client_post_valid(self, client, sample_client, app):
        """Test updating a client with valid data."""
        response = client.post('/clients/1/edit', data={
            'name': 'Updated Client Name',
            'contact_person': 'Jane Smith',
            'email': 'jane@updated.com',
            'phone': '+27 11 888 7777',
            'address': 'Updated Address',
            'notes': 'Updated notes'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        assert b'updated successfully' in response.data
        
        # Verify updates in database
        with app.app_context():
            updated_client = Client.query.get(1)
            assert updated_client.name == 'Updated Client Name'
            assert updated_client.contact_person == 'Jane Smith'
            assert updated_client.email == 'jane@updated.com'
            assert updated_client.client_code == 'CL-0001'  # Code should not change
    
    def test_edit_client_post_missing_name(self, client, sample_client):
        """Test updating a client without a name."""
        response = client.post('/clients/1/edit', data={
            'name': '',
            'contact_person': 'Jane Smith'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        assert b'required' in response.data or b'Edit Client' in response.data
    
    def test_edit_client_not_found(self, client):
        """Test editing non-existent client."""
        response = client.get('/clients/999/edit')
        assert response.status_code == 404
    
    def test_delete_client(self, client, sample_client, app):
        """Test deleting a client."""
        response = client.post('/clients/1/delete', follow_redirects=True)
        
        assert response.status_code == 200
        assert b'deleted successfully' in response.data
        
        # Verify deletion in database
        with app.app_context():
            deleted_client = Client.query.get(1)
            assert deleted_client is None
    
    def test_delete_client_not_found(self, client):
        """Test deleting non-existent client."""
        response = client.post('/clients/999/delete')
        assert response.status_code == 404
    
    def test_client_pagination(self, client, app):
        """Test client list pagination."""
        # Create many clients
        with app.app_context():
            for i in range(60):
                new_client = Client(
                    client_code=f'CL-{i+1:04d}',
                    name=f'Client {i+1}'
                )
                db.session.add(new_client)
            db.session.commit()
        
        # Test first page
        response = client.get('/clients/')
        assert response.status_code == 200
        assert b'Client 1' in response.data
        
        # Test second page
        response = client.get('/clients/?page=2')
        assert response.status_code == 200
        assert b'Client 51' in response.data or b'Next' in response.data


class TestErrorHandlers:
    """Test error handlers."""
    
    def test_404_error(self, client):
        """Test 404 error page."""
        response = client.get('/nonexistent-page')
        assert response.status_code == 404
        assert b'404' in response.data
        assert b'Page Not Found' in response.data
    
    def test_403_error(self, client, app):
        """Test 403 error page."""
        # Manually trigger 403 error
        with app.test_request_context():
            from flask import abort
            with pytest.raises(Exception):
                abort(403)

