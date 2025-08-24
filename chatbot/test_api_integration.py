#!/usr/bin/env python3
"""
Test script for Driving License API Integration
This script tests the API endpoints and configuration.
"""

import os
import sys
import requests
import json
from datetime import datetime

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from api_config import APIConfig, APIResponse, APIError

def test_api_connectivity():
    """Test basic API connectivity."""
    print("🔍 Testing API connectivity...")
    
    try:
        response = requests.get(APIConfig.BASE_URL, timeout=5)
        print(f"✅ API base URL accessible: {response.status_code}")
        return True
    except Exception as e:
        print(f"❌ API connectivity failed: {e}")
        return False

def test_get_license_details():
    """Test getting license details endpoint."""
    print("\n🔍 Testing get license details endpoint...")
    
    try:
        # Test with a sample license number (you'll need to replace this with a real one)
        test_license = "DL-102-175578760328916906"  # Replace with actual license from your API
        
        response = requests.get(
            APIConfig.get_endpoint_url("get_license_details"),
            headers=APIConfig.get_auth_headers(),
            params={"licenseNumber": test_license},
            timeout=APIConfig.TIMEOUT
        )
        
        print(f"📡 Response status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ API call successful")
            print(f"📊 Response data: {json.dumps(data, indent=2)}")
            
            # Parse the response
            api_response = APIResponse.from_dict(data)
            if api_response.is_success():
                print(f"✅ Response indicates success: {api_response.message}")
                if api_response.data:
                    print(f"📋 License holder: {api_response.get_data('firstName')} {api_response.get_data('lastName')}")
                    print(f"🚗 Vehicle type: {api_response.get_data('vehicleType')}")
                    print(f"📍 Address: {api_response.get_data('address')}")
            else:
                print(f"⚠️ Response indicates failure: {api_response.message}")
        else:
            print(f"❌ API call failed with status {response.status_code}")
            print(f"📄 Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Test failed: {e}")

def test_create_license():
    """Test creating a new license endpoint."""
    print("\n🔍 Testing create license endpoint...")
    
    try:
        # Sample license data
        license_data = {
            "firstName": "Test",
            "lastName": "User",
            "vehicleType": "Car",
            "vehicleMake": "Honda",
            "address": "456 Test Street, Test City, TS 12345"
        }
        
        response = requests.post(
            APIConfig.get_endpoint_url("create_license"),
            headers=APIConfig.get_auth_headers(),
            json=license_data,
            timeout=APIConfig.TIMEOUT
        )
        
        print(f"📡 Response status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ License creation successful")
            print(f"📊 Response data: {json.dumps(data, indent=2)}")
        else:
            print(f"❌ License creation failed with status {response.status_code}")
            print(f"📄 Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Test failed: {e}")

def test_configuration():
    """Test configuration settings."""
    print("\n🔍 Testing configuration...")
    
    print(f"📍 Base URL: {APIConfig.BASE_URL}")
    print(f"⏱️ Timeout: {APIConfig.TIMEOUT}s")
    print(f"🔄 Max retries: {APIConfig.MAX_RETRIES}")
    print(f"🔑 Auth token: {APIConfig.AUTH_TOKEN[:10]}..." if len(APIConfig.AUTH_TOKEN) > 10 else "🔑 Auth token: <not set>")
    
    # Test endpoint URL generation
    try:
        endpoint_url = APIConfig.get_endpoint_url("get_license_details")
        print(f"🔗 Sample endpoint URL: {endpoint_url}")
    except Exception as e:
        print(f"❌ Endpoint URL generation failed: {e}")
    
    # Test auth headers
    headers = APIConfig.get_auth_headers()
    print(f"📋 Auth headers: {headers}")

def main():
    """Main test function."""
    print("🚗 Driving License API Integration Test")
    print("=" * 50)
    
    # Test configuration
    test_configuration()
    
    # Test API connectivity
    if not test_api_connectivity():
        print("\n❌ Cannot proceed with API tests due to connectivity issues.")
        print("Please check your API backend and configuration.")
        return
    
    # Test API endpoints
    test_get_license_details()
    test_create_license()
    
    print("\n" + "=" * 50)
    print("🏁 API integration test completed!")
    
    print("\n📋 Next steps:")
    print("1. Ensure your API backend is running on localhost:7500")
    print("2. Set your actual API_AUTH_TOKEN in environment variables")
    print("3. Update test_license in this script with a real license number")
    print("4. Run the tests again to verify full functionality")

if __name__ == "__main__":
    main()
