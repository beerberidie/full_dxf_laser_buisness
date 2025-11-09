#!/usr/bin/env python3
"""
Configuration Checker for Email Ingest System
Validates that all required environment variables are set correctly.
"""

import os
import sys
from pathlib import Path

# Add the app directory to the path
sys.path.insert(0, str(Path(__file__).parent))

from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def check_config():
    """Check and validate configuration."""
    print("=" * 70)
    print("EMAIL INGEST SYSTEM - CONFIGURATION CHECKER")
    print("=" * 70)
    print()
    
    issues = []
    warnings = []
    
    # Check .env file exists
    env_file = Path(__file__).parent / ".env"
    if not env_file.exists():
        print("❌ ERROR: .env file not found!")
        print(f"   Expected location: {env_file}")
        print("   Please create a .env file based on the template.")
        return False
    else:
        print(f"✅ .env file found: {env_file}")
    
    print()
    print("-" * 70)
    print("CHECKING REQUIRED CONFIGURATION...")
    print("-" * 70)
    print()
    
    # Check FERNET_KEY
    fernet_key = os.getenv("FERNET_KEY", "")
    if not fernet_key or fernet_key == "CHANGE_ME_GENERATE_A_NEW_KEY":
        issues.append("FERNET_KEY is not set or using default value")
        print("❌ FERNET_KEY: Not configured properly")
    else:
        print(f"✅ FERNET_KEY: Set (length: {len(fernet_key)})")
    
    # Check Google OAuth
    print()
    print("Google OAuth Configuration:")
    google_client_id = os.getenv("GOOGLE_CLIENT_ID", "")
    google_client_secret = os.getenv("GOOGLE_CLIENT_SECRET", "")
    google_redirect_uri = os.getenv("GOOGLE_REDIRECT_URI", "")
    
    if not google_client_id or google_client_id == "YOUR_GOOGLE_CLIENT_ID_HERE":
        issues.append("GOOGLE_CLIENT_ID is not set")
        print("  ❌ GOOGLE_CLIENT_ID: Not configured")
    else:
        print(f"  ✅ GOOGLE_CLIENT_ID: {google_client_id[:20]}...")
    
    if not google_client_secret or google_client_secret == "YOUR_GOOGLE_CLIENT_SECRET_HERE":
        issues.append("GOOGLE_CLIENT_SECRET is not set")
        print("  ❌ GOOGLE_CLIENT_SECRET: Not configured")
    else:
        print(f"  ✅ GOOGLE_CLIENT_SECRET: {google_client_secret[:10]}... (hidden)")
    
    if google_redirect_uri:
        print(f"  ✅ GOOGLE_REDIRECT_URI: {google_redirect_uri}")
        if "localhost" in google_redirect_uri or "127.0.0.1" in google_redirect_uri:
            warnings.append("GOOGLE_REDIRECT_URI uses localhost (OK for development)")
    else:
        print("  ⚠️  GOOGLE_REDIRECT_URI: Using default")
    
    # Check Gmail Pub/Sub (optional)
    print()
    print("Gmail Pub/Sub Configuration (Optional):")
    pubsub_topic = os.getenv("GMAIL_PUBSUB_TOPIC", "")
    if pubsub_topic:
        print(f"  ✅ GMAIL_PUBSUB_TOPIC: {pubsub_topic}")
    else:
        warnings.append("GMAIL_PUBSUB_TOPIC not set (webhooks won't work)")
        print("  ⚠️  GMAIL_PUBSUB_TOPIC: Not set (polling mode only)")
    
    # Check Microsoft OAuth (optional)
    print()
    print("Microsoft 365 Configuration (Optional):")
    ms_client_id = os.getenv("MS_CLIENT_ID", "")
    if ms_client_id and ms_client_id != "YOUR_MS_CLIENT_ID_HERE":
        print(f"  ✅ MS_CLIENT_ID: {ms_client_id[:20]}...")
    else:
        print("  ⚠️  MS_CLIENT_ID: Not configured (M365 integration disabled)")
    
    # Check URLs
    print()
    print("Application URLs:")
    app_base_url = os.getenv("APP_BASE_URL", "http://localhost:8000")
    public_webhook_base = os.getenv("PUBLIC_WEBHOOK_BASE", app_base_url)
    print(f"  ✅ APP_BASE_URL: {app_base_url}")
    print(f"  ✅ PUBLIC_WEBHOOK_BASE: {public_webhook_base}")
    
    if "localhost" in public_webhook_base or "127.0.0.1" in public_webhook_base:
        warnings.append("PUBLIC_WEBHOOK_BASE uses localhost (webhooks won't work from external services)")
    
    # Summary
    print()
    print("=" * 70)
    print("SUMMARY")
    print("=" * 70)
    
    if not issues:
        print("✅ All required configuration is set!")
        print()
        if warnings:
            print("⚠️  Warnings:")
            for warning in warnings:
                print(f"   - {warning}")
        print()
        print("🚀 You can now start the backend server:")
        print("   python -m uvicorn app.main:app --reload")
        return True
    else:
        print("❌ Configuration issues found:")
        for issue in issues:
            print(f"   - {issue}")
        print()
        print("📝 Please update your .env file with the correct values.")
        print("   See SETUP_GUIDE.md for detailed instructions.")
        print()
        if warnings:
            print("⚠️  Warnings:")
            for warning in warnings:
                print(f"   - {warning}")
        return False

if __name__ == "__main__":
    success = check_config()
    sys.exit(0 if success else 1)

