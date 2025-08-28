#!/usr/bin/env python3
"""
Simple test script to verify OpenTelemetry tracing is working correctly.
Run this script to test if traces are being sent to your collector on port 4317.
"""

import time
import requests
from trace_stuff import trace_stuff, tracer

@trace_stuff("test_api_call")
def test_api_call():
    """Test function that makes an API call to verify tracing works."""
    try:
        # Make a simple HTTP request (this will be auto-instrumented)
        response = requests.get("https://httpbin.org/json", timeout=5)
        print(f"✅ API call successful: {response.status_code}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ API call failed: {e}")
        return False

@trace_stuff("test_manual_span")
def test_manual_span():
    """Test function with manual span creation."""
    with tracer.start_as_current_span("manual_operation") as span:
        span.set_attribute("operation.type", "test")
        span.set_attribute("test.duration", 2)
        
        print("🔄 Performing test operation...")
        time.sleep(2)  # Simulate some work
        
        span.add_event("Operation completed", {"status": "success"})
        print("✅ Test operation completed")

def main():
    """Main test function."""
    print("🚀 Starting OpenTelemetry tracing test...")
    print("📡 Sending traces to: http://localhost:4317")
    print("-" * 50)
    
    # Test 1: API call with auto-instrumentation
    print("1. Testing API call with auto-instrumentation...")
    test_api_call()
    
    # Test 2: Manual span creation
    print("\n2. Testing manual span creation...")
    test_manual_span()
    
    # Test 3: Nested spans
    print("\n3. Testing nested spans...")
    with tracer.start_as_current_span("parent_span") as parent:
        parent.set_attribute("span.type", "parent")
        
        with tracer.start_as_current_span("child_span") as child:
            child.set_attribute("span.type", "child")
            time.sleep(1)
            print("✅ Nested spans created")
    
    print("\n" + "-" * 50)
    print("🎉 Test completed! Check your tracing backend for spans.")
    print("💡 If you don't see traces, ensure:")
    print("   - Your tracing collector is running on port 4317")
    print("   - The collector is configured to accept OTLP gRPC")
    print("   - No firewall is blocking port 4317")

if __name__ == "__main__":
    main()
