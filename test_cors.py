#!/usr/bin/env python3
"""
CORS Test Script for JobPsych AI Backend
Tests if CORS is properly configured for frontend requests
"""

import requests
import json

def test_cors_configuration():
    """Test CORS configuration for different origins"""
    
    base_url = "https://hr-resume-analyzer-backend.vercel.app"  # Replace with your actual backend URL
    test_origins = [
        "https://jobpsych.vercel.app",
        "https://hiredesk.vercel.app", 
        "http://localhost:3000"
    ]
    
    print("🧪 Testing CORS Configuration...")
    print("=" * 50)
    
    # Test basic health endpoint
    try:
        response = requests.get(f"{base_url}/health", timeout=10)
        print(f"✅ Health endpoint: {response.status_code}")
    except Exception as e:
        print(f"❌ Health endpoint failed: {e}")
        return
    
    # Test CORS test endpoint
    try:
        response = requests.get(f"{base_url}/api/cors-test", timeout=10)
        print(f"✅ CORS test endpoint: {response.status_code}")
        if response.status_code == 200:
            print(f"   Response: {response.json()}")
    except Exception as e:
        print(f"❌ CORS test endpoint failed: {e}")
    
    # Test preflight requests for each origin
    for origin in test_origins:
        print(f"\n🌐 Testing origin: {origin}")
        
        # Test OPTIONS preflight request
        headers = {
            'Origin': origin,
            'Access-Control-Request-Method': 'POST',
            'Access-Control-Request-Headers': 'Content-Type'
        }
        
        try:
            response = requests.options(
                f"{base_url}/api/analyze-resume", 
                headers=headers,
                timeout=10
            )
            
            print(f"   OPTIONS preflight: {response.status_code}")
            
            # Check CORS headers in response
            cors_headers = {
                'Access-Control-Allow-Origin': response.headers.get('Access-Control-Allow-Origin'),
                'Access-Control-Allow-Methods': response.headers.get('Access-Control-Allow-Methods'),
                'Access-Control-Allow-Headers': response.headers.get('Access-Control-Allow-Headers'),
                'Access-Control-Allow-Credentials': response.headers.get('Access-Control-Allow-Credentials')
            }
            
            for header_name, header_value in cors_headers.items():
                if header_value:
                    print(f"   ✅ {header_name}: {header_value}")
                else:
                    print(f"   ❌ {header_name}: Not present")
                    
        except Exception as e:
            print(f"   ❌ OPTIONS request failed: {e}")

def test_analyze_resume_endpoint():
    """Test the actual analyze-resume endpoint"""
    
    base_url = "https://hr-resume-analyzer-backend.vercel.app"  # Replace with actual URL
    
    print("\n📄 Testing /api/analyze-resume endpoint...")
    print("=" * 50)
    
    # Test without file (should get validation error, not CORS error)
    headers = {
        'Origin': 'https://jobpsych.vercel.app'
    }
    
    try:
        response = requests.post(
            f"{base_url}/api/analyze-resume",
            headers=headers,
            timeout=10
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        
        if response.status_code != 422:  # 422 is expected for missing file
            print(f"Response Body: {response.text}")
        else:
            print("✅ Got expected validation error (not CORS error)")
            
    except Exception as e:
        print(f"❌ Request failed: {e}")

if __name__ == "__main__":
    print("🚀 JobPsych AI Backend CORS Test")
    print("=" * 50)
    
    test_cors_configuration()
    test_analyze_resume_endpoint()
    
    print("\n📋 CORS Troubleshooting Tips:")
    print("1. Make sure your backend is deployed with the latest CORS config")
    print("2. Check if your frontend is sending the correct Origin header")
    print("3. Verify the backend URL in your frontend matches the deployed URL")
    print("4. Test with browser dev tools Network tab to see exact headers")