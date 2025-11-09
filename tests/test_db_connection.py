"""Test database connection"""
from app import create_app, db
from app.models import Client

app = create_app('development')

with app.app_context():
    try:
        # Test database connection
        count = Client.query.count()
        print(f"✅ Database connection successful!")
        print(f"✅ Total clients in database: {count}")
        
        # Test creating a client
        from app.services.id_generator import generate_client_code
        client_code = generate_client_code()
        print(f"✅ Generated client code: {client_code}")
        
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        import traceback
        traceback.print_exc()

