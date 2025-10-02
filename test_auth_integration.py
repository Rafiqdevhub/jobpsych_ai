#!/usr/bin/env python3
"""
Test script for JWT authentication and rate limiting on hiredesk-analyze endpoint.

This script tests:
1. JWT token validation
2. Rate limit checking
3. File upload with authentication

Prerequisites:
1. Set JWT_SECRET in .env file (same as your auth server)
2. Set AUTH_SERVICE_URL in .env file
3. Have a valid JWT token for testing
4. Your auth server should have the rate limiting endpoints implemented

Usage:
python test_auth_integration.py
"""

import asyncio
import aiohttp
import json
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

async def test_auth_integration():
    """Test the authentication and rate limiting integration"""
    
    # Configuration
    base_url = "http://localhost:8000"
    
    # You'll need to replace this with a valid JWT token from your auth server
    # You can get this from your frontend's localStorage after login
    test_jwt_token = "YOUR_JWT_TOKEN_HERE"
    
    print("🔐 Testing JWT Authentication & Rate Limiting Integration")
    print("=" * 60)
    
    # Test 1: Health check (no auth required)
    print("\n1. Testing health endpoint (no auth)...")
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{base_url}/health") as response:
                if response.status == 200:
                    print("✅ Health check passed")
                else:
                    print(f"❌ Health check failed: {response.status}")
    except Exception as e:
        print(f"❌ Health check error: {e}")
    
    # Test 2: Analyze without authentication (should fail)
    print("\n2. Testing hiredesk-analyze without authentication...")
    try:
        async with aiohttp.ClientSession() as session:
            data = aiohttp.FormData()
            data.add_field('target_role', 'Software Engineer')
            data.add_field('job_description', 'Looking for a skilled developer')
            
            async with session.post(f"{base_url}/api/hiredesk-analyze", data=data) as response:
                if response.status == 401:
                    print("✅ Correctly rejected request without authentication")
                else:
                    print(f"❌ Unexpected response: {response.status}")
                    text = await response.text()
                    print(f"Response: {text}")
    except Exception as e:
        print(f"❌ Test error: {e}")
    
    # Test 3: Analyze with invalid token (should fail)
    print("\n3. Testing hiredesk-analyze with invalid token...")
    try:
        async with aiohttp.ClientSession() as session:
            headers = {"Authorization": "Bearer invalid_token_here"}
            data = aiohttp.FormData()
            data.add_field('target_role', 'Software Engineer')
            data.add_field('job_description', 'Looking for a skilled developer')
            
            async with session.post(f"{base_url}/api/hiredesk-analyze", data=data, headers=headers) as response:
                if response.status == 401:
                    print("✅ Correctly rejected request with invalid token")
                else:
                    print(f"❌ Unexpected response: {response.status}")
                    text = await response.text()
                    print(f"Response: {text[:200]}...")
    except Exception as e:
        print(f"❌ Test error: {e}")
    
    # Test 4: Test with valid token (if provided)
    if test_jwt_token != "YOUR_JWT_TOKEN_HERE":
        print("\n4. Testing hiredesk-analyze with valid token...")
        try:
            async with aiohttp.ClientSession() as session:
                headers = {"Authorization": f"Bearer {test_jwt_token}"}
                data = aiohttp.FormData()
                data.add_field('target_role', 'Software Engineer')
                data.add_field('job_description', 'Looking for a skilled developer')
                # You would add a file here: data.add_field('file', open('sample_resume.pdf', 'rb'))
                
                async with session.post(f"{base_url}/api/hiredesk-analyze", data=data, headers=headers) as response:
                    print(f"Status: {response.status}")
                    text = await response.text()
                    print(f"Response: {text[:300]}...")
                    
                    if response.status == 422:
                        print("✅ Validation working (file required)")
                    elif response.status == 429:
                        print("✅ Rate limiting working (limit exceeded)")
                    elif response.status == 200:
                        print("✅ Authentication and processing working")
                    else:
                        print(f"❌ Unexpected response: {response.status}")
        except Exception as e:
            print(f"❌ Test error: {e}")
    else:
        print("\n4. Skipping valid token test (no token provided)")
        print("   To test with a valid token:")
        print("   1. Login to your frontend")
        print("   2. Get the JWT token from localStorage")
        print("   3. Replace 'YOUR_JWT_TOKEN_HERE' in this script")
    
    print("\n" + "=" * 60)
    print("🧪 Test Configuration:")
    print(f"   JWT_SECRET: {'✅ Set' if os.getenv('JWT_SECRET') else '❌ Not set'}")
    print(f"   AUTH_SERVICE_URL: {os.getenv('AUTH_SERVICE_URL', '❌ Not set')}")
    print(f"   Base URL: {base_url}")
    
    print("\n📋 Next Steps:")
    print("1. Make sure your auth server has these endpoints:")
    print("   - GET /api/auth/user-uploads/{email}")
    print("   - POST /api/auth/increment-upload")
    print("2. Test with a real JWT token from your frontend")
    print("3. Test file upload with a sample resume PDF")

if __name__ == "__main__":
    asyncio.run(test_auth_integration())