#!/usr/bin/env python3
"""
Test script for Stage 2: Authentication and Interest Management
Run this after starting the application to test authentication functionality.
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

def test_create_user():
    """Test creating a new user"""
    print("\n🔍 Testing user creation...")
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    test_user = {
        "email": f"stage2_user_{timestamp}@example.com",
        "name": "Stage 2 Test User",
        "password": "securepassword123",
        "phone": "+1234567890",
        "age": 30,
        "location_city": "San Francisco",
        "location_country": "USA",
        "job_title": "Product Manager",
        "industry": "Technology",
        "company_size": "100-500",
        "education_level": "Master's Degree",
        "experience_level": "Senior"
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
            return test_user, data['id']
        else:
            print(f"❌ User creation failed: {response.status_code}")
            print(f"Response: {response.text}")
            return None, None
    except Exception as e:
        print(f"❌ User creation error: {e}")
        return None, None

def test_login(user_data):
    """Test user login"""
    if not user_data:
        print("\n⏭️  Skipping login test (no user data)")
        return None
        
    print("\n🔍 Testing user login...")
    
    login_data = {
        "email": user_data["email"],
        "password": user_data["password"]
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/v1/auth/login",
            json=login_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Login successful: {data['email']}")
            print(f"   Token type: {data['token_type']}")
            print(f"   Expires in: {data['expires_in']} seconds")
            return data["access_token"]
        else:
            print(f"❌ Login failed: {response.status_code}")
            print(f"Response: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Login error: {e}")
        return None

def test_get_current_user(token):
    """Test getting current user profile"""
    if not token:
        print("\n⏭️  Skipping current user test (no token)")
        return False
        
    print("\n🔍 Testing get current user...")
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.get(f"{BASE_URL}/api/v1/auth/me", headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Current user retrieved: {data['email']}")
            return True
        else:
            print(f"❌ Get current user failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Get current user error: {e}")
        return False

def test_interest_categories(token):
    """Test getting interest categories"""
    if not token:
        print("\n⏭️  Skipping interest categories test (no token)")
        return False
        
    print("\n🔍 Testing interest categories...")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.get(f"{BASE_URL}/api/v1/interests/categories", headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Interest categories retrieved: {len(data)} categories available")
            for category in data[:3]:  # Show first 3 categories
                print(f"   - {category['category']}: {len(category['subcategories'])} subcategories")
            return True
        else:
            print(f"❌ Get interest categories failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Interest categories error: {e}")
        return False

def test_create_interests(token):
    """Test creating user interests"""
    if not token:
        print("\n⏭️  Skipping create interests test (no token)")
        return False
        
    print("\n🔍 Testing create user interests...")
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    interests = [
        {
            "category": "Technology",
            "subcategory": "AI/Machine Learning",
            "interest_level": 9.0,
            "keywords": "artificial intelligence, machine learning, neural networks"
        },
        {
            "category": "Business",
            "subcategory": "Startups",
            "interest_level": 7.5,
            "keywords": "startup, entrepreneurship, venture capital"
        }
    ]
    
    created_interests = []
    
    for interest in interests:
        try:
            response = requests.post(
                f"{BASE_URL}/api/v1/interests/",
                json=interest,
                headers=headers
            )
            
            if response.status_code == 201:
                data = response.json()
                created_interests.append(data)
                print(f"✅ Interest created: {data['category']} - {data['subcategory']} (Level: {data['interest_level']})")
            else:
                print(f"❌ Create interest failed: {response.status_code}")
        except Exception as e:
            print(f"❌ Create interest error: {e}")
    
    return len(created_interests) > 0

def test_get_my_interests(token):
    """Test getting user's interests"""
    if not token:
        print("\n⏭️  Skipping get interests test (no token)")
        return False
        
    print("\n🔍 Testing get my interests...")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.get(f"{BASE_URL}/api/v1/interests/", headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ User interests retrieved: {len(data)} interests found")
            for interest in data:
                print(f"   - {interest['category']}: {interest['subcategory']} (Level: {interest['interest_level']})")
            return True
        else:
            print(f"❌ Get interests failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Get interests error: {e}")
        return False

def test_create_preferences(token):
    """Test creating user preferences"""
    if not token:
        print("\n⏭️  Skipping create preferences test (no token)")
        return False
        
    print("\n🔍 Testing create user preferences...")
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    preferences = {
        "reading_time_preference": "morning",
        "content_depth_preference": "detailed",
        "frequency_tolerance": "daily",
        "max_newsletters_per_day": 15,
        "auto_summarize_enabled": True
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/v1/interests/preferences",
            json=preferences,
            headers=headers
        )
        
        if response.status_code == 201:
            data = response.json()
            print(f"✅ Preferences created successfully")
            print(f"   Reading time: {data['reading_time_preference']}")
            print(f"   Content depth: {data['content_depth_preference']}")
            return True
        else:
            print(f"❌ Create preferences failed: {response.status_code}")
            print(f"Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Create preferences error: {e}")
        return False

def test_token_verification(token):
    """Test token verification"""
    if not token:
        print("\n⏭️  Skipping token verification test (no token)")
        return False
        
    print("\n🔍 Testing token verification...")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.get(f"{BASE_URL}/api/v1/auth/verify-token", headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Token verification successful: Valid={data['valid']}")
            return True
        else:
            print(f"❌ Token verification failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Token verification error: {e}")
        return False

def main():
    """Run all Stage 2 tests"""
    print("🚀 Starting Newsletter Curator API - Stage 2 Tests")
    print("=" * 60)
    
    results = []
    
    # Test basic functionality
    results.append(test_health_check())
    
    # Test user creation and authentication
    user_data, user_id = test_create_user()
    results.append(user_data is not None)
    
    # Test authentication
    token = test_login(user_data)
    results.append(token is not None)
    
    # Test authenticated endpoints
    results.append(test_get_current_user(token))
    results.append(test_token_verification(token))
    
    # Test interest management
    results.append(test_interest_categories(token))
    results.append(test_create_interests(token))
    results.append(test_get_my_interests(token))
    
    # Test preferences
    results.append(test_create_preferences(token))
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 Stage 2 Test Results Summary")
    print("=" * 60)
    
    passed = sum(results)
    total = len(results)
    
    print(f"✅ Passed: {passed}/{total}")
    print(f"❌ Failed: {total - passed}/{total}")
    
    if passed == total:
        print("\n🎉 All Stage 2 tests passed! Authentication and interests are working correctly.")
        print("\n🔐 Available Features:")
        print("   ✅ User registration and login")
        print("   ✅ JWT token authentication")
        print("   ✅ Protected endpoints")
        print("   ✅ Interest management")
        print("   ✅ User preferences")
        print("   ✅ Token verification")
    else:
        print(f"\n⚠️  Some tests failed. Please check the logs above.")
    
    return passed == total

if __name__ == "__main__":
    main()