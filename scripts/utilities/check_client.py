"""Check if client CL-0003 exists in the database."""

from app import create_app, db
from app.models import Client

app = create_app()

with app.app_context():
    client = Client.query.filter_by(client_code='CL-0003').first()
    
    if client:
        print("✅ CLIENT FOUND IN DATABASE")
        print("=" * 70)
        print(f"Client Code: {client.client_code}")
        print(f"Client Name: {client.name}")
        print(f"Client ID: {client.id}")
        print(f"Email: {getattr(client, 'email', 'N/A') or 'N/A'}")
        print(f"Phone: {getattr(client, 'phone', 'N/A') or 'N/A'}")
    else:
        print("❌ CLIENT NOT FOUND")
        print("=" * 70)
        print("Client code 'CL-0003' does not exist in the database.")
        print("\nAvailable clients:")
        clients = Client.query.all()
        for c in clients[:10]:
            print(f"  - {c.client_code}: {c.name}")

