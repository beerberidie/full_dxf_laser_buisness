"""Test the running Flask server"""
import urllib.request
import urllib.error

try:
    response = urllib.request.urlopen('http://127.0.0.1:5000')
    content = response.read().decode('utf-8')
    print(f"✅ Server responded with status: {response.status}")
    print(f"✅ Response contains 'Laser OS': {'Laser OS' in content}")
    print(f"✅ Response contains 'Dashboard': {'Dashboard' in content}")
except urllib.error.HTTPError as e:
    print(f"❌ Server returned HTTP error: {e.code}")
    print(f"❌ Error message: {e.read().decode('utf-8')[:500]}")
except Exception as e:
    print(f"❌ Failed to connect to server: {e}")

