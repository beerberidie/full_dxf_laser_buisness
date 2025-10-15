"""Test the Flask application"""
from app import create_app

app = create_app('development')

with app.test_client() as client:
    try:
        response = client.get('/')
        print(f"✅ Response status: {response.status_code}")
        if response.status_code == 200:
            print(f"✅ Application is working!")
            print(f"✅ Response contains 'Laser OS': {'Laser OS' in response.data.decode()}")
        else:
            print(f"❌ Application returned error: {response.status_code}")
            print(response.data.decode())
    except Exception as e:
        print(f"❌ Application test failed: {e}")
        import traceback
        traceback.print_exc()

