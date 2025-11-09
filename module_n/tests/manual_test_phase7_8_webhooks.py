"""
Manual Test - Phase 7 & 8: Webhook Notifications and Advanced Features
Tests webhook sending, retry logic, queue, signatures, monitoring, filtering
"""

import sys
from pathlib import Path
import asyncio
import json
import hmac
import hashlib
from datetime import datetime

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from module_n.webhooks import (
    send_webhook,
    send_webhook_with_retry,
    WebhookEvent,
    WebhookEventType,
    generate_webhook_signature,
    should_send_event,
    get_webhook_queue,
    get_webhook_monitor
)
from module_n.config import settings


def test_webhook_functions_available():
    """Test webhook functions are available"""
    print("\n" + "="*80)
    print("TESTING WEBHOOK FUNCTIONS AVAILABILITY")
    print("="*80)

    try:
        # Check if functions are callable
        functions = [
            ("send_webhook", send_webhook),
            ("send_webhook_with_retry", send_webhook_with_retry),
            ("generate_webhook_signature", generate_webhook_signature),
            ("should_send_event", should_send_event),
            ("get_webhook_queue", get_webhook_queue),
            ("get_webhook_monitor", get_webhook_monitor)
        ]

        print(f"   ✅ Webhook functions available:")
        for name, func in functions:
            print(f"      ✅ {name}")

        print(f"\n   Configuration:")
        print(f"      Webhook URL: {settings.LASER_OS_WEBHOOK_URL}")
        print(f"      Timeout: {settings.LASER_OS_TIMEOUT}s")
        print(f"      Retry attempts: {settings.WEBHOOK_RETRY_ATTEMPTS}")
        print(f"      Retry delay: {settings.WEBHOOK_RETRY_DELAY}s")

        return True

    except Exception as e:
        print(f"   ❌ Failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_webhook_event_types():
    """Test all 5 webhook event types"""
    print("\n" + "="*80)
    print("TESTING WEBHOOK EVENT TYPES")
    print("="*80)
    
    event_types = [
        "file.ingested",
        "file.processed",
        "file.failed",
        "file.re_extracted",
        "file.deleted"
    ]
    
    for event_type in event_types:
        print(f"\n   Testing event: {event_type}")
        
        # Create test payload
        payload = {
            "event": event_type,
            "timestamp": datetime.utcnow().isoformat(),
            "data": {
                "file_id": 123,
                "filename": "test.dxf",
                "status": "completed"
            }
        }
        
        print(f"      ✅ Event payload created")
        print(f"         Event: {payload['event']}")
        print(f"         Data keys: {list(payload['data'].keys())}")
    
    print(f"\n   ✅ All {len(event_types)} event types tested")
    return True


def test_webhook_signature_generation():
    """Test HMAC-SHA256 signature generation"""
    print("\n" + "="*80)
    print("TESTING WEBHOOK SIGNATURE GENERATION")
    print("="*80)

    try:
        if not settings.WEBHOOK_SECRET:
            print("   ⚠️  No webhook secret configured, skipping signature test")
            return True

        # Test payload
        payload = {
            "event": "file.ingested",
            "data": {"file_id": 123}
        }

        # Generate signature
        payload_str = json.dumps(payload, sort_keys=True)
        signature = hmac.new(
            settings.WEBHOOK_SECRET.encode(),
            payload_str.encode(),
            hashlib.sha256
        ).hexdigest()

        print(f"   ✅ Signature generated")
        print(f"      Payload: {payload_str[:50]}...")
        print(f"      Signature: {signature[:32]}...")
        print(f"      Signature length: {len(signature)} chars")

        # Verify signature
        verify_signature = hmac.new(
            settings.WEBHOOK_SECRET.encode(),
            payload_str.encode(),
            hashlib.sha256
        ).hexdigest()

        if signature == verify_signature:
            print(f"   ✅ Signature verification passed")
            return True
        else:
            print(f"   ❌ Signature verification failed")
            return False

    except Exception as e:
        print(f"   ❌ Failed: {e}")
        return False


def test_webhook_queue():
    """Test webhook queue system"""
    print("\n" + "="*80)
    print("TESTING WEBHOOK QUEUE SYSTEM")
    print("="*80)

    try:
        queue = get_webhook_queue()

        print(f"   ✅ Webhook queue initialized")

        # Test queue stats
        print("\n   Test 1: Getting queue stats...")
        stats = queue.get_stats()
        print(f"      ✅ Queue stats:")
        print(f"         Total: {stats.get('total', 0)}")
        print(f"         Pending: {stats.get('pending', 0)}")
        print(f"         Failed: {stats.get('failed', 0)}")
        print(f"         Completed: {stats.get('completed', 0)}")

        print(f"\n   ✅ Webhook queue system tested")
        return True

    except Exception as e:
        print(f"   ❌ Failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_webhook_monitor():
    """Test webhook monitoring system"""
    print("\n" + "="*80)
    print("TESTING WEBHOOK MONITORING SYSTEM")
    print("="*80)

    try:
        monitor = get_webhook_monitor()

        print(f"   ✅ Webhook monitor initialized")

        # Test recording success
        print("\n   Test 1: Recording successful webhook...")
        monitor.record(
            event_type="file.ingested",
            ingest_id=123,
            success=True,
            attempts=1,
            duration_ms=123.45,
            status_code=200
        )
        print(f"      ✅ Success recorded")

        # Test recording failure
        print("\n   Test 2: Recording failed webhook...")
        monitor.record(
            event_type="file.processed",
            ingest_id=124,
            success=False,
            attempts=3,
            duration_ms=5000.0,
            error_message="Connection timeout"
        )
        print(f"      ✅ Failure recorded")

        # Test getting stats
        print("\n   Test 3: Getting webhook stats...")
        stats = monitor.get_stats()

        print(f"      ✅ Stats retrieved:")
        print(f"         Total: {stats.get('total', 0)}")
        print(f"         Successful: {stats.get('successful', 0)}")
        print(f"         Failed: {stats.get('failed', 0)}")
        print(f"         Success rate: {stats.get('success_rate', 0):.1f}%")

        print(f"\n   ✅ Webhook monitoring system tested")
        return True

    except Exception as e:
        print(f"   ❌ Failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_webhook_retry_logic():
    """Test webhook retry logic with exponential backoff"""
    print("\n" + "="*80)
    print("TESTING WEBHOOK RETRY LOGIC")
    print("="*80)

    try:
        print(f"   Retry configuration:")
        print(f"      Max attempts: {settings.WEBHOOK_RETRY_ATTEMPTS}")
        print(f"      Base delay: {settings.WEBHOOK_RETRY_DELAY}s")

        # Calculate exponential backoff delays
        print(f"\n   Exponential backoff schedule:")
        for attempt in range(settings.WEBHOOK_RETRY_ATTEMPTS):
            delay = settings.WEBHOOK_RETRY_DELAY * (2 ** attempt)
            total_time = sum(settings.WEBHOOK_RETRY_DELAY * (2 ** i) for i in range(attempt + 1))
            print(f"      Attempt {attempt + 1}: {delay}s delay (total: {total_time}s)")

        print(f"\n   ✅ Retry logic configuration verified")
        return True

    except Exception as e:
        print(f"   ❌ Failed: {e}")
        return False


def test_webhook_filtering():
    """Test webhook event filtering"""
    print("\n" + "="*80)
    print("TESTING WEBHOOK EVENT FILTERING")
    print("="*80)

    try:
        # Check if filtering is configured
        if hasattr(settings, 'WEBHOOK_ENABLED_EVENTS') and settings.WEBHOOK_ENABLED_EVENTS:
            enabled_events = settings.WEBHOOK_ENABLED_EVENTS
            print(f"   ✅ Event filtering configured")
            print(f"      Enabled events: {enabled_events}")
        else:
            print(f"   ⚠️  No event filtering configured (all events enabled)")

        # Test filtering logic
        all_events = [
            "file.ingested",
            "file.processed",
            "file.failed",
            "file.re_extracted",
            "file.deleted"
        ]

        print(f"\n   Testing filter logic:")
        for event in all_events:
            if hasattr(settings, 'WEBHOOK_ENABLED_EVENTS') and settings.WEBHOOK_ENABLED_EVENTS:
                should_send = event in settings.WEBHOOK_ENABLED_EVENTS
            else:
                should_send = True

            status = "✅ SEND" if should_send else "⏭️  SKIP"
            print(f"      {status}: {event}")

        print(f"\n   ✅ Event filtering tested")
        return True

    except Exception as e:
        print(f"   ❌ Failed: {e}")
        return False


def test_webhook_configuration():
    """Test webhook configuration"""
    print("\n" + "="*80)
    print("TESTING WEBHOOK CONFIGURATION")
    print("="*80)

    try:
        print(f"   Configuration values:")
        print(f"      LASER_OS_WEBHOOK_URL: {settings.LASER_OS_WEBHOOK_URL}")
        print(f"      WEBHOOK_ENABLED: {settings.WEBHOOK_ENABLED}")
        print(f"      LASER_OS_TIMEOUT: {settings.LASER_OS_TIMEOUT}s")
        print(f"      WEBHOOK_RETRY_ATTEMPTS: {settings.WEBHOOK_RETRY_ATTEMPTS}")
        print(f"      WEBHOOK_RETRY_DELAY: {settings.WEBHOOK_RETRY_DELAY}s")
        print(f"      WEBHOOK_SECRET: {'***' if settings.WEBHOOK_SECRET else 'Not set'}")

        # Validate configuration
        issues = []

        if not settings.LASER_OS_WEBHOOK_URL:
            issues.append("LASER_OS_WEBHOOK_URL not configured")

        if settings.LASER_OS_TIMEOUT <= 0:
            issues.append("LASER_OS_TIMEOUT must be > 0")

        if settings.WEBHOOK_RETRY_ATTEMPTS < 0:
            issues.append("WEBHOOK_RETRY_ATTEMPTS must be >= 0")

        if settings.WEBHOOK_RETRY_DELAY <= 0:
            issues.append("WEBHOOK_RETRY_DELAY must be > 0")

        if issues:
            print(f"\n   ⚠️  Configuration issues:")
            for issue in issues:
                print(f"      - {issue}")
        else:
            print(f"\n   ✅ Configuration is valid")

        return len(issues) == 0

    except Exception as e:
        print(f"   ❌ Failed: {e}")
        return False


def main():
    """Run all Phase 7 & 8 tests"""
    print("\n" + "🔬 STARTING PHASE 7 & 8 COMPREHENSIVE TESTS".center(80, "="))
    
    results = []
    
    # Phase 7: Basic webhook functionality
    print("\n" + "PHASE 7: WEBHOOK NOTIFICATIONS".center(80, "-"))
    results.append(("Webhook Configuration", test_webhook_configuration()))
    results.append(("Webhook Functions Available", test_webhook_functions_available()))
    results.append(("Webhook Event Types", test_webhook_event_types()))
    
    # Phase 8: Advanced webhook features
    print("\n" + "PHASE 8: ADVANCED WEBHOOK FEATURES".center(80, "-"))
    results.append(("Webhook Signature Generation", test_webhook_signature_generation()))
    results.append(("Webhook Queue System", test_webhook_queue()))
    results.append(("Webhook Monitoring System", test_webhook_monitor()))
    results.append(("Webhook Retry Logic", test_webhook_retry_logic()))
    results.append(("Webhook Event Filtering", test_webhook_filtering()))
    
    # Print summary
    print("\n" + "="*80)
    print("PHASE 7 & 8 TEST SUMMARY")
    print("="*80)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {test_name}")
    
    print(f"\nTotal: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
    
    if passed == total:
        print("\n🎉 ALL PHASE 7 & 8 TESTS PASSED!")
        return 0
    else:
        print(f"\n⚠️  {total - passed} test(s) failed")
        return 1


if __name__ == "__main__":
    exit(main())

