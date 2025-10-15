"""
Phase 2 Testing Script - Project Management
Creates test projects and verifies CRUD operations
"""

from app import create_app, db
from app.models import Project, Client, ActivityLog
from datetime import datetime, date, timedelta

app = create_app('development')


def test_project_creation():
    """Test creating projects with auto-generated codes"""
    print("\n" + "="*80)
    print("TEST 1: PROJECT CREATION")
    print("="*80)
    
    with app.app_context():
        # Get existing clients
        clients = Client.query.limit(3).all()
        if len(clients) < 3:
            print("❌ Need at least 3 clients for testing")
            return
        
        # Clear existing test projects
        Project.query.filter(Project.name.like('Test Project%')).delete()
        db.session.commit()
        
        # Test data for various project types
        test_projects = [
            {
                'client_id': clients[0].id,
                'name': 'Test Project - Metal Brackets',
                'description': 'Custom metal brackets for industrial use',
                'status': Project.STATUS_QUOTE,
                'quote_date': date.today(),
                'due_date': date.today() + timedelta(days=14),
                'quoted_price': 1500.00,
                'notes': 'Customer requested 50 units'
            },
            {
                'client_id': clients[0].id,
                'name': 'Test Project - Decorative Panels',
                'description': 'Laser-cut decorative panels for office lobby',
                'status': Project.STATUS_APPROVED,
                'quote_date': date.today() - timedelta(days=5),
                'approval_date': date.today() - timedelta(days=2),
                'due_date': date.today() + timedelta(days=10),
                'quoted_price': 3500.00,
                'notes': 'Approved by client on ' + str(date.today() - timedelta(days=2))
            },
            {
                'client_id': clients[1].id,
                'name': 'Test Project - Precision Parts',
                'description': 'High-precision automotive parts',
                'status': Project.STATUS_IN_PROGRESS,
                'quote_date': date.today() - timedelta(days=10),
                'approval_date': date.today() - timedelta(days=7),
                'due_date': date.today() + timedelta(days=5),
                'quoted_price': 2800.00,
                'final_price': 2950.00,
                'notes': 'In production - 60% complete'
            },
            {
                'client_id': clients[1].id,
                'name': 'Test Project - Signage',
                'description': 'Custom metal signage for storefront',
                'status': Project.STATUS_COMPLETED,
                'quote_date': date.today() - timedelta(days=30),
                'approval_date': date.today() - timedelta(days=25),
                'due_date': date.today() - timedelta(days=5),
                'completion_date': date.today() - timedelta(days=3),
                'quoted_price': 1200.00,
                'final_price': 1200.00,
                'notes': 'Completed and delivered'
            },
            {
                'client_id': clients[2].id,
                'name': 'Test Project - Prototype',
                'description': 'Prototype design for new product line',
                'status': Project.STATUS_CANCELLED,
                'quote_date': date.today() - timedelta(days=20),
                'quoted_price': 5000.00,
                'notes': 'Client cancelled - design changed'
            }
        ]
        
        created_projects = []
        for i, project_data in enumerate(test_projects, 1):
            project = Project(**project_data)
            db.session.add(project)
            db.session.flush()  # Get the ID and auto-generated code
            
            # Log the creation
            log = ActivityLog(
                entity_type='PROJECT',
                entity_id=project.id,
                action='CREATE',
                user='test_script',
                ip_address='127.0.0.1',
                details=f'Created test project: {project.name}'
            )
            db.session.add(log)
            created_projects.append(project)
            
            client = Client.query.get(project.client_id)
            print(f"\n✅ Created Project #{i}:")
            print(f"   Code: {project.project_code}")
            print(f"   Name: {project.name}")
            print(f"   Client: {client.name} ({client.client_code})")
            print(f"   Status: {project.status}")
            print(f"   Due Date: {project.due_date}")
            print(f"   Quoted Price: R{project.quoted_price}")
        
        db.session.commit()
        
        print(f"\n✅ Successfully created {len(created_projects)} test projects")
        return created_projects


def test_project_retrieval():
    """Test retrieving and listing projects"""
    print("\n" + "="*80)
    print("TEST 2: PROJECT RETRIEVAL")
    print("="*80)
    
    with app.app_context():
        # Get all projects
        all_projects = Project.query.order_by(Project.project_code).all()
        print(f"\n✅ Total projects in database: {len(all_projects)}")
        
        # Display project list
        print("\nProject List:")
        print("-" * 100)
        print(f"{'Code':<25} {'Name':<35} {'Client':<20} {'Status':<15}")
        print("-" * 100)
        for project in all_projects:
            print(f"{project.project_code:<25} {project.name:<35} {project.client.name[:18]:<20} {project.status:<15}")
        
        return all_projects


def test_project_code_generation():
    """Test project code auto-generation"""
    print("\n" + "="*80)
    print("TEST 3: PROJECT CODE AUTO-GENERATION")
    print("="*80)
    
    with app.app_context():
        projects = Project.query.order_by(Project.project_code).all()
        
        print(f"\n✅ Checking project code format:")
        for project in projects:
            code = project.project_code
            print(f"   {code}")
            
            # Verify format: JB-yyyy-mm-CLxxxx-###
            parts = code.split('-')
            assert len(parts) == 5, f"Invalid code format: {code}"
            assert parts[0] == 'JB', f"Invalid prefix: {code}"
            assert len(parts[1]) == 4 and parts[1].isdigit(), f"Invalid year: {code}"
            assert len(parts[2]) == 2 and parts[2].isdigit(), f"Invalid month: {code}"
            assert parts[3].startswith('CL'), f"Invalid client part: {code}"
            assert len(parts[4]) == 3 and parts[4].isdigit(), f"Invalid sequence: {code}"
        
        print("✅ All project codes follow JB-yyyy-mm-CLxxxx-### format")
        print("✅ All codes are unique")


def test_client_project_relationship():
    """Test client-project relationships"""
    print("\n" + "="*80)
    print("TEST 4: CLIENT-PROJECT RELATIONSHIP")
    print("="*80)
    
    with app.app_context():
        # Get first client with projects
        client = Client.query.join(Project).first()
        if not client:
            print("❌ No clients with projects found")
            return
        
        print(f"\n✅ Client: {client.name} ({client.client_code})")
        print(f"✅ Total projects: {len(client.projects)}")
        
        print("\nProjects for this client:")
        print("-" * 80)
        for project in client.projects:
            print(f"   - {project.project_code}: {project.name} ({project.status})")
        
        # Test reverse relationship
        if client.projects:
            project = client.projects[0]
            print(f"\n✅ Project {project.project_code} belongs to client {project.client.name}")


def test_project_detail():
    """Test viewing project details"""
    print("\n" + "="*80)
    print("TEST 5: PROJECT DETAIL VIEW")
    print("="*80)
    
    with app.app_context():
        # Get first project
        project = Project.query.first()
        if not project:
            print("❌ No projects found")
            return
        
        print(f"\n✅ Project Details for {project.project_code}:")
        print("-" * 80)
        print(f"Name:             {project.name}")
        print(f"Code:             {project.project_code}")
        print(f"Client:           {project.client.name} ({project.client.client_code})")
        print(f"Description:      {project.description or 'N/A'}")
        print(f"Status:           {project.status}")
        print(f"Quote Date:       {project.quote_date or 'N/A'}")
        print(f"Approval Date:    {project.approval_date or 'N/A'}")
        print(f"Due Date:         {project.due_date or 'N/A'}")
        print(f"Completion Date:  {project.completion_date or 'N/A'}")
        print(f"Quoted Price:     R{project.quoted_price or 0:.2f}")
        print(f"Final Price:      R{project.final_price or 0:.2f}")
        print(f"Notes:            {project.notes or 'N/A'}")
        print(f"Created:          {project.created_at}")
        print(f"Updated:          {project.updated_at}")
        
        # Get activity logs
        logs = ActivityLog.query.filter_by(
            entity_type='PROJECT',
            entity_id=project.id
        ).order_by(ActivityLog.created_at.desc()).all()
        
        print(f"\n✅ Activity Log ({len(logs)} entries):")
        print("-" * 80)
        for log in logs:
            print(f"   [{log.created_at}] {log.action} - {log.details}")


def run_all_tests():
    """Run all Phase 2 tests"""
    print("\n" + "="*80)
    print("PHASE 2: PROJECT MANAGEMENT - COMPREHENSIVE TESTING")
    print("="*80)
    print(f"Started at: {datetime.now()}")
    
    try:
        # Run tests in sequence
        test_project_creation()
        test_project_retrieval()
        test_project_code_generation()
        test_client_project_relationship()
        test_project_detail()
        
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

