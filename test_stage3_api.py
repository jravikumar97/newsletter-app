#!/usr/bin/env python3
"""
Test script for Stage 3: Email Integration & Newsletter Processing
Run this after starting the application to test email functionality.
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

def create_test_user_and_login():
    """Create test user and get authentication token"""
    print("\n🔍 Creating test user and logging in...")
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    test_user = {
        "email": f"stage3_user_{timestamp}@example.com",
        "name": "Stage 3 Test User", 
        "password": "testpassword123",
        "job_title": "Newsletter Enthusiast",
        "industry": "Technology"
    }
    
    try:
        # Create user
        response = requests.post(
            f"{BASE_URL}/api/v1/users/",
            json=test_user,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code != 201:
            print(f"❌ User creation failed: {response.status_code}")
            return None
        
        # Login
        login_data = {
            "email": test_user["email"],
            "password": test_user["password"]
        }
        
        response = requests.post(
            f"{BASE_URL}/api/v1/auth/login",
            json=login_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ User created and logged in: {data['email']}")
            return data["access_token"]
        else:
            print(f"❌ Login failed: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def test_api_info(token):
    """Test the enhanced API info endpoint"""
    print("\n🔍 Testing enhanced API info...")
    
    try:
        response = requests.get(f"{BASE_URL}/api/v1/")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ API info retrieved:")
            print(f"   Features: {', '.join(data['features'])}")
            print(f"   New endpoints: {data['endpoints'].get('email', 'Not found')}")
            return True
        else:
            print(f"❌ API info failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ API info error: {e}")
        return False

def test_email_connection_status(token):
    """Test getting email connection status"""
    if not token:
        print("\n⏭️  Skipping email connection test (no token)")
        return False
        
    print("\n🔍 Testing email connection status...")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.get(f"{BASE_URL}/api/v1/email/connection", headers=headers)
        
        if response.status_code == 404:
            print("✅ No email connection found (expected for new user)")
            return True
        elif response.status_code == 200:
            data = response.json()
            print(f"✅ Email connection found: {data['email_address']}")
            return True
        else:
            print(f"❌ Email connection test failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Email connection error: {e}")
        return False

def test_oauth_authorization_url(token):
    """Test getting OAuth authorization URL"""
    if not token:
        print("\n⏭️  Skipping OAuth test (no token)")
        return False
        
    print("\n🔍 Testing OAuth authorization URL generation...")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.get(f"{BASE_URL}/api/v1/email/oauth/authorize", headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            print("✅ OAuth authorization URL generated successfully")
            print(f"   URL starts with: {data['authorization_url'][:50]}...")
            return True
        else:
            print(f"❌ OAuth URL generation failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ OAuth URL error: {e}")
        return False

def test_newsletter_search(token):
    """Test newsletter search functionality"""
    if not token:
        print("\n⏭️  Skipping newsletter search test (no token)")
        return False
        
    print("\n🔍 Testing newsletter search...")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.get(
            f"{BASE_URL}/api/v1/email/search?q=tech",
            headers=headers
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Newsletter search working (found {len(data)} results)")
            return True
        else:
            print(f"❌ Newsletter search failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Newsletter search error: {e}")
        return False

def test_newsletter_stats(token):
    """Test newsletter statistics"""
    if not token:
        print("\n⏭️  Skipping newsletter stats test (no token)")
        return False
        
    print("\n🔍 Testing newsletter statistics...")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.get(f"{BASE_URL}/api/v1/email/stats", headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Newsletter stats retrieved:")
            print(f"   Total newsletters: {data['total_newsletters']}")
            print(f"   Active subscriptions: {data['active_subscriptions']}")
            print(f"   Total emails: {data['total_emails']}")
            return True
        else:
            print(f"❌ Newsletter stats failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Newsletter stats error: {e}")
        return False

def test_my_newsletters(token):
    """Test getting user's newsletters"""
    if not token:
        print("\n⏭️  Skipping my newsletters test (no token)")
        return False
        
    print("\n🔍 Testing get my newsletters...")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.get(f"{BASE_URL}/api/v1/email/newsletters", headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ My newsletters retrieved: {len(data)} subscriptions found")
            return True
        else:
            print(f"❌ My newsletters failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ My newsletters error: {e}")
        return False

def test_all_newsletter_emails(token):
    """Test getting all newsletter emails"""
    if not token:
        print("\n⏭️  Skipping newsletter emails test (no token)")
        return False
        
    print("\n🔍 Testing get all newsletter emails...")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.get(f"{BASE_URL}/api/v1/email/emails", headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Newsletter emails retrieved: {len(data)} emails found")
            return True
        else:
            print(f"❌ Newsletter emails failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Newsletter emails error: {e}")
        return False

def test_disconnect_email(token):
    """Test disconnecting email (should fail gracefully)"""
    if not token:
        print("\n⏭️  Skipping email disconnect test (no token)")
        return False
        
    print("\n🔍 Testing email disconnection...")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.delete(f"{BASE_URL}/api/v1/email/disconnect", headers=headers)
        
        if response.status_code == 404:
            print("✅ Email disconnect handled correctly (no connection to disconnect)")
            return True
        elif response.status_code == 200:
            print("✅ Email disconnected successfully")
            return True
        else:
            print(f"❌ Email disconnect failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Email disconnect error: {e}")
        return False

def main():
    """Run all Stage 3 tests"""
    print("🚀 Starting Newsletter Curator API - Stage 3 Tests")
    print("=" * 60)
    
    results = []
    
    # Basic tests
    results.append(test_health_check())
    
    # Create user and get token
    token = create_test_user_and_login()
    results.append(token is not None)
    
    # Test new Stage 3 features
    results.append(test_api_info(token))
    results.append(test_email_connection_status(token))
    results.append(test_oauth_authorization_url(token))
    results.append(test_newsletter_search(token))
    results.append(test_newsletter_stats(token))
    results.append(test_my_newsletters(token))
    results.append(test_all_newsletter_emails(token))
    results.append(test_disconnect_email(token))
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 Stage 3 Test Results Summary")
    print("=" * 60)
    
    passed = sum(results)
    total = len(results)
    
    print(f"✅ Passed: {passed}/{total}")
    print(f"❌ Failed: {total - passed}/{total}")
    
    if passed == total:
        print("\n🎉 All Stage 3 tests passed! Email integration is working correctly.")
        print("\n📧 Available Features:")
        print("   ✅ Gmail OAuth authorization")
        print("   ✅ Email connection management")
        print("   ✅ Newsletter detection endpoints")
        print("   ✅ Newsletter statistics")
        print("   ✅ Email synchronization framework")
        print("   ✅ Newsletter search functionality")
        print("\n📝 Next Steps:")
        print("   1. Connect your Gmail account through the OAuth flow")
        print("   2. Sync your emails to detect newsletters")
        print("   3. Explore your personalized newsletter feed")
    else:
        print(f"\n⚠️  Some tests failed. Please check the logs above.")
    
    return passed == total

if __name__ == "__main__":
    main()