#!/usr/bin/env python3
"""
Quick CORS test for JobPsych AI backend
"""

import requests
import json

def test_cors():
    """Test CORS configuration"""
    
    base_url = "http://localhost:8000"  # Local testing
    # For deployed version: "https://hr-resume-analyzer-backend.vercel.app"
    
    print("🧪 Testing CORS Configuration...")
    print("=" * 50)
    
    # Test 1: Health endpoint
    try:
        response = requests.get(f"{base_url}/health", timeout=5)
        print(f"✅ Health endpoint: {response.status_code}")
    except Exception as e:
        print(f"❌ Health endpoint failed: {e}")
        return False
    
    # Test 2: CORS test endpoint
    try:
        response = requests.get(f"{base_url}/api/cors-test", timeout=5)
        print(f"✅ CORS test endpoint: {response.status_code}")
        if response.status_code == 200:
            print(f"   Response: {response.json()}")
    except Exception as e:
        print(f"❌ CORS test endpoint failed: {e}")
    
    # Test 3: OPTIONS preflight request
    headers = {
        'Origin': 'http://localhost:3000',
        'Access-Control-Request-Method': 'POST',
        'Access-Control-Request-Headers': 'Content-Type'
    }
    
    try:
        response = requests.options(
            f"{base_url}/api/analyze-resume", 
            headers=headers,
            timeout=5
        )
        
        print(f"\n🌐 OPTIONS preflight test:")
        print(f"   Status: {response.status_code}")
        
        # Check CORS headers
        cors_headers = {
            'Access-Control-Allow-Origin': response.headers.get('Access-Control-Allow-Origin'),
            'Access-Control-Allow-Methods': response.headers.get('Access-Control-Allow-Methods'),
            'Access-Control-Allow-Headers': response.headers.get('Access-Control-Allow-Headers'),
        }
        
        for header_name, header_value in cors_headers.items():
            if header_value:
                print(f"   ✅ {header_name}: {header_value}")
            else:
                print(f"   ❌ {header_name}: Missing")
                
    except Exception as e:
        print(f"   ❌ OPTIONS request failed: {e}")
        return False
    
    # Test 4: Actual POST request (without file, should get validation error)
    try:
        headers = {'Origin': 'http://localhost:3000'}
        response = requests.post(
            f"{base_url}/api/analyze-resume",
            headers=headers,
            timeout=5
        )
        
        print(f"\n📄 POST request test:")
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 422:
            print("   ✅ Got expected validation error (not CORS error)")
        else:
            print(f"   Response: {response.text[:200]}...")
            
    except Exception as e:
        print(f"   ❌ POST request failed: {e}")
        return False
    
    print("\n🎉 CORS tests completed!")
    return True

if __name__ == "__main__":
    print("🚀 JobPsych AI CORS Test")
    print("Make sure your server is running on http://localhost:8000")
    print("=" * 60)
    
    success = test_cors()
    
    if success:
        print("\n✅ CORS appears to be working correctly!")
        print("Your frontend at http://localhost:3000 should be able to access the API.")
    else:
        print("\n❌ CORS issues detected. Check server logs and configuration.")
        
    print("\n📋 Next steps:")
    print("1. Open cors_test_localhost.html in your browser")
    print("2. Test from your actual frontend application")
    print("3. Deploy and test with production URLs")