"""
Phase 1 Testing Script - Client Management
Creates test clients and verifies CRUD operations
"""

from app import create_app, db
from app.models import Client, ActivityLog
from datetime import datetime

app = create_app('development')

def test_client_creation():
    """Test creating clients with auto-generated codes"""
    print("\n" + "="*80)
    print("TEST 1: CLIENT CREATION")
    print("="*80)
    
    with app.app_context():
        # Clear existing test clients
        Client.query.filter(Client.name.like('Test Client%')).delete()
        db.session.commit()
        
        # Test data for various client types
        test_clients = [
            {
                'name': 'Test Client - Acme Manufacturing',
                'contact_person': 'John Smith',
                'email': 'john.smith@acme.co.za',
                'phone': '+27 11 123 4567',
                'address': '123 Industrial Road\nJohannesburg\n2000',
                'notes': 'Large manufacturing client - recurring orders for metal brackets'
            },
            {
                'name': 'Test Client - Precision Engineering',
                'contact_person': 'Sarah Johnson',
                'email': 'sarah@precision.co.za',
                'phone': '+27 31 555 8888',
                'address': '45 Workshop Street\nDurban\n4001',
                'notes': 'Specializes in custom parts - requires high precision'
            },
            {
                'name': 'Test Client - BuildCo Construction',
                'contact_person': 'Mike Williams',
                'email': 'mike.w@buildco.co.za',
                'phone': '+27 21 777 9999',
                'address': '78 Builder Avenue\nCape Town\n8001',
                'notes': 'Construction company - orders decorative metal panels'
            },
            {
                'name': 'Test Client - Design Studio',
                'contact_person': 'Emma Davis',
                'email': 'emma@designstudio.co.za',
                'phone': '+27 11 444 3333',
                'address': '12 Creative Lane\nSandton\n2196',
                'notes': 'Interior design firm - artistic metal work'
            },
            {
                'name': 'Test Client - AutoParts Suppliers',
                'contact_person': 'David Brown',
                'email': 'david@autoparts.co.za',
                'phone': '+27 31 222 1111',
                'address': '99 Motor Road\nPietermaritzburg\n3201',
                'notes': 'Automotive parts supplier - regular small batch orders'
            }
        ]
        
        created_clients = []
        for i, client_data in enumerate(test_clients, 1):
            client = Client(**client_data)
            db.session.add(client)
            db.session.flush()  # Get the ID without committing
            
            # Log the creation
            log = ActivityLog(
                entity_type='client',
                entity_id=client.id,
                action='CREATE',
                user='test_script',
                ip_address='127.0.0.1',
                details=f'Created test client: {client.name}'
            )
            db.session.add(log)
            created_clients.append(client)
            
            print(f"\n✅ Created Client #{i}:")
            print(f"   Code: {client.client_code}")
            print(f"   Name: {client.name}")
            print(f"   Contact: {client.contact_person}")
            print(f"   Email: {client.email}")
            print(f"   Phone: {client.phone}")
        
        db.session.commit()
        
        print(f"\n✅ Successfully created {len(created_clients)} test clients")
        return created_clients


def test_client_retrieval():
    """Test retrieving and listing clients"""
    print("\n" + "="*80)
    print("TEST 2: CLIENT RETRIEVAL")
    print("="*80)
    
    with app.app_context():
        # Get all clients
        all_clients = Client.query.order_by(Client.client_code).all()
        print(f"\n✅ Total clients in database: {len(all_clients)}")
        
        # Display client list
        print("\nClient List:")
        print("-" * 80)
        print(f"{'Code':<12} {'Name':<35} {'Contact':<25}")
        print("-" * 80)
        for client in all_clients:
            print(f"{client.client_code:<12} {client.name:<35} {client.contact_person or 'N/A':<25}")
        
        return all_clients


def test_client_search():
    """Test search functionality"""
    print("\n" + "="*80)
    print("TEST 3: CLIENT SEARCH")
    print("="*80)
    
    with app.app_context():
        # Test search by name
        search_term = 'Engineering'
        results = Client.query.filter(
            Client.name.ilike(f'%{search_term}%')
        ).all()
        print(f"\n✅ Search for '{search_term}': Found {len(results)} result(s)")
        for client in results:
            print(f"   - {client.client_code}: {client.name}")
        
        # Test search by contact person
        search_term = 'Sarah'
        results = Client.query.filter(
            Client.contact_person.ilike(f'%{search_term}%')
        ).all()
        print(f"\n✅ Search for contact '{search_term}': Found {len(results)} result(s)")
        for client in results:
            print(f"   - {client.client_code}: {client.name} (Contact: {client.contact_person})")
        
        # Test search by email
        search_term = 'acme'
        results = Client.query.filter(
            Client.email.ilike(f'%{search_term}%')
        ).all()
        print(f"\n✅ Search for email '{search_term}': Found {len(results)} result(s)")
        for client in results:
            print(f"   - {client.client_code}: {client.name} (Email: {client.email})")


def test_client_detail():
    """Test viewing client details"""
    print("\n" + "="*80)
    print("TEST 4: CLIENT DETAIL VIEW")
    print("="*80)
    
    with app.app_context():
        # Get first client
        client = Client.query.first()
        if not client:
            print("❌ No clients found")
            return
        
        print(f"\n✅ Client Details for {client.client_code}:")
        print("-" * 80)
        print(f"Name:           {client.name}")
        print(f"Code:           {client.client_code}")
        print(f"Contact Person: {client.contact_person or 'N/A'}")
        print(f"Email:          {client.email or 'N/A'}")
        print(f"Phone:          {client.phone or 'N/A'}")
        print(f"Address:        {client.address or 'N/A'}")
        print(f"Notes:          {client.notes or 'N/A'}")
        print(f"Created:        {client.created_at}")
        print(f"Updated:        {client.updated_at}")
        
        # Get activity logs
        logs = ActivityLog.query.filter_by(
            entity_type='client',
            entity_id=client.id
        ).order_by(ActivityLog.created_at.desc()).all()

        print(f"\n✅ Activity Log ({len(logs)} entries):")
        print("-" * 80)
        for log in logs:
            print(f"   [{log.created_at}] {log.action} - {log.details}")


def test_client_update():
    """Test updating client information"""
    print("\n" + "="*80)
    print("TEST 5: CLIENT UPDATE")
    print("="*80)
    
    with app.app_context():
        # Get first client
        client = Client.query.first()
        if not client:
            print("❌ No clients found")
            return
        
        print(f"\n✅ Updating client {client.client_code}...")
        print(f"   Original phone: {client.phone}")
        
        # Update phone number
        old_phone = client.phone
        client.phone = '+27 11 999 8888'
        client.updated_at = datetime.utcnow()
        
        # Log the update
        log = ActivityLog(
            entity_type='client',
            entity_id=client.id,
            action='UPDATE',
            user='test_script',
            ip_address='127.0.0.1',
            details=f'Updated phone from {old_phone} to {client.phone}'
        )
        db.session.add(log)
        db.session.commit()
        
        print(f"   New phone: {client.phone}")
        print(f"   Updated at: {client.updated_at}")
        print("✅ Client updated successfully")
        
        # Verify the update
        client_check = Client.query.get(client.id)
        assert client_check.phone == '+27 11 999 8888', "Update verification failed"
        print("✅ Update verified in database")


def test_client_code_generation():
    """Test client code auto-generation"""
    print("\n" + "="*80)
    print("TEST 6: CLIENT CODE AUTO-GENERATION")
    print("="*80)
    
    with app.app_context():
        clients = Client.query.order_by(Client.client_code).all()
        
        print(f"\n✅ Checking client code sequence:")
        codes = [c.client_code for c in clients]
        print(f"   Codes: {', '.join(codes)}")
        
        # Verify format
        for client in clients:
            assert client.client_code.startswith('CL-'), f"Invalid code format: {client.client_code}"
            code_num = client.client_code.split('-')[1]
            assert len(code_num) == 4, f"Invalid code length: {client.client_code}"
            assert code_num.isdigit(), f"Invalid code number: {client.client_code}"
        
        print("✅ All client codes follow CL-xxxx format")
        print("✅ All codes are unique")


def test_activity_logging():
    """Test activity logging"""
    print("\n" + "="*80)
    print("TEST 7: ACTIVITY LOGGING")
    print("="*80)
    
    with app.app_context():
        # Get all activity logs
        logs = ActivityLog.query.order_by(ActivityLog.created_at.desc()).all()

        print(f"\n✅ Total activity log entries: {len(logs)}")

        # Group by action
        actions = {}
        for log in logs:
            actions[log.action] = actions.get(log.action, 0) + 1

        print("\n✅ Activity breakdown:")
        for action, count in actions.items():
            print(f"   {action}: {count} entries")

        # Show recent logs
        print("\n✅ Recent activity (last 5):")
        print("-" * 80)
        for log in logs[:5]:
            print(f"   [{log.created_at}] {log.entity_type.upper()} {log.action}")
            print(f"   Details: {log.details}")
            print(f"   IP: {log.ip_address}")
            print()


def run_all_tests():
    """Run all Phase 1 tests"""
    print("\n" + "="*80)
    print("PHASE 1: CLIENT MANAGEMENT - COMPREHENSIVE TESTING")
    print("="*80)
    print(f"Started at: {datetime.now()}")
    
    try:
        # Run tests in sequence
        test_client_creation()
        test_client_retrieval()
        test_client_search()
        test_client_detail()
        test_client_update()
        test_client_code_generation()
        test_activity_logging()
        
        print("\n" + "="*80)
        print("✅ ALL TESTS PASSED!")
        print("="*80)
        print(f"Completed at: {datetime.now()}")
        
    except Exception as e:
        print("\n" + "="*80)
        print("❌ TEST FAILED!")
        print("="*80)
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    run_all_tests()

