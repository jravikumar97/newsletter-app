#!/usr/bin/env python3
"""
Test script to verify the Newsletter Curator API is working correctly.
Run this after starting the application to test basic functionality.
"""

import requests
import json
from datetime import datetime

# API base URL
BASE_URL = "http://localhost:8000"

def test_health_check():
    """Test the health check endpoint"""
    print("🔍 Testing health check...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Health check passed: {data}")
            return True
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return False

def test_root_endpoint():
    """Test the root endpoint"""
    print("\n🔍 Testing root endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Root endpoint working: {data}")
            return True
        else:
            print(f"❌ Root endpoint failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Root endpoint error: {e}")
        return False

def test_api_info():
    """Test the API info endpoint"""
    print("\n🔍 Testing API info...")
    try:
        response = requests.get(f"{BASE_URL}/api/v1/")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ API info working: {data}")
            return True
        else:
            print(f"❌ API info failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ API info error: {e}")
        return False

def test_create_user():
    """Test creating a new user"""
    print("\n🔍 Testing user creation...")
    
    # Generate unique email for testing
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    test_user = {
        "email": f"test_user_{timestamp}@example.com",
        "name": "Test User",
        "password": "testpassword123",
        "phone": "+1234567890",
        "age": 28,
        "location_city": "New York",
        "location_country": "USA",
        "job_title": "Software Developer",
        "industry": "Technology",
        "company_size": "50-200",
        "education_level": "Bachelor's Degree",
        "experience_level": "Mid-level"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/v1/users/",
            json=test_user,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 201:
            data = response.json()
            print(f"✅ User created successfully: {data['email']} (ID: {data['id']})")
            return data['id']
        else:
            print(f"❌ User creation failed: {response.status_code}")
            print(f"Response: {response.text}")
            return None
    except Exception as e:
        print(f"❌ User creation error: {e}")
        return None

def test_get_user(user_id):
    """Test retrieving a user by ID"""
    if not user_id:
        print("\n⏭️  Skipping user retrieval test (no user ID)")
        return False
        
    print(f"\n🔍 Testing user retrieval (ID: {user_id})...")
    try:
        response = requests.get(f"{BASE_URL}/api/v1/users/{user_id}")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ User retrieved successfully: {data['email']}")
            return True
        else:
            print(f"❌ User retrieval failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ User retrieval error: {e}")
        return False

def test_list_users():
    """Test listing users"""
    print("\n🔍 Testing user listing...")
    try:
        response = requests.get(f"{BASE_URL}/api/v1/users/?limit=5")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ User listing successful: Found {len(data)} users")
            return True
        else:
            print(f"❌ User listing failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ User listing error: {e}")
        return False

def test_update_user(user_id):
    """Test updating a user"""
    if not user_id:
        print("\n⏭️  Skipping user update test (no user ID)")
        return False
        
    print(f"\n🔍 Testing user update (ID: {user_id})...")
    
    update_data = {
        "job_title": "Senior Software Developer",
        "location_city": "San Francisco"
    }
    
    try:
        response = requests.put(
            f"{BASE_URL}/api/v1/users/{user_id}",
            json=update_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ User updated successfully: {data['job_title']}")
            return True
        else:
            print(f"❌ User update failed: {response.status_code}")
            print(f"Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ User update error: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 Starting Newsletter Curator API Tests")
    print("=" * 50)
    
    results = []
    
    # Test basic endpoints
    results.append(test_health_check())
    results.append(test_root_endpoint())
    results.append(test_api_info())
    
    # Test user operations
    user_id = test_create_user()
    results.append(user_id is not None)
    results.append(test_get_user(user_id))
    results.append(test_list_users())
    results.append(test_update_user(user_id))
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 Test Results Summary")
    print("=" * 50)
    
    passed = sum(results)
    total = len(results)
    
    print(f"✅ Passed: {passed}/{total}")
    print(f"❌ Failed: {total - passed}/{total}")
    
    if passed == total:
        print("\n🎉 All tests passed! Your API is working correctly.")
    else:
        print(f"\n⚠️  Some tests failed. Please check the logs above.")
    
    return passed == total

if __name__ == "__main__":
    main()