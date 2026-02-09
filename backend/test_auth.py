#!/usr/bin/env python3
"""
Test script for JWT Authentication
Run: python test_auth.py
"""

import requests
import json
import sys

BASE_URL = "http://localhost:8001/api/auth"


def test_register():
    """Test user registration."""
    print("=" * 50)
    print("Test 1: User Registration")
    print("=" * 50)
    
    # Generate unique email
    import uuid
    email = f"test_{uuid.uuid4().hex[:8]}@example.com"
    
    payload = {
        "email": email,
        "name": "Test User",
        "password": "TestPass123",
        "confirm_password": "TestPass123"
    }
    
    try:
        r = requests.post(f"{BASE_URL}/register", json=payload)
        data = r.json()
        
        if r.status_code == 200:
            print(f"✅ Registration successful!")
            print(f"Email: {email}")
            print(f"Token: {data.get('access_token', '')[:50]}...")
            print(f"User: {data.get('user', {})}")
            return data.get('access_token'), email
        else:
            print(f"❌ Registration failed: {data}")
            return None, email
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return None, email


def test_login(email, password="TestPass123"):
    """Test user login."""
    print("\n" + "=" * 50)
    print("Test 2: User Login")
    print("=" * 50)
    
    payload = {
        "email": email,
        "password": password
    }
    
    try:
        r = requests.post(f"{BASE_URL}/login", json=payload)
        data = r.json()
        
        if r.status_code == 200:
            print(f"✅ Login successful!")
            print(f"Token: {data.get('access_token', '')[:50]}...")
            print(f"User: {data.get('user', {})}")
            return data.get('access_token')
        else:
            print(f"❌ Login failed: {data}")
            return None
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return None


def test_protected_endpoint(token):
    """Test accessing protected endpoint with token."""
    print("\n" + "=" * 50)
    print("Test 3: Protected Endpoint (Chat API)")
    print("=" * 50)
    
    if not token:
        print("❌ No token provided")
        return False
    
    headers = {"Authorization": f"Bearer {token}"}
    
    payload = {"message": "Show me blue dresses"}
    
    try:
        r = requests.post(
            f"http://localhost:8001/api/chat/send",
            json=payload,
            headers=headers
        )
        
        if r.status_code == 200:
            data = r.json()
            print(f"✅ Protected endpoint accessible!")
            print(f"Intent: {data.get('intent')}")
            print(f"Results: {data.get('database_results', {}).get('row_count', 0)} rows")
            return True
        else:
            print(f"❌ Access denied: {r.status_code}")
            print(f"Response: {r.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def test_logout():
    """Test logout."""
    print("\n" + "=" * 50)
    print("Test 4: Logout")
    print("=" * 50)
    
    try:
        r = requests.post(f"{BASE_URL}/logout")
        data = r.json()
        
        if r.status_code == 200:
            print(f"✅ Logout successful!")
            print(f"Message: {data.get('message')}")
            return True
        else:
            print(f"❌ Logout failed: {data}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def test_invalid_login():
    """Test login with invalid credentials."""
    print("\n" + "=" * 50)
    print("Test 5: Invalid Login (should fail)")
    print("=" * 50)
    
    payload = {
        "email": "nonexistent@example.com",
        "password": "wrongpassword"
    }
    
    try:
        r = requests.post(f"{BASE_URL}/login", json=payload)
        
        if r.status_code == 401:
            print(f"✅ Correctly rejected invalid login")
            print(f"Response: {r.json().get('detail')}")
            return True
        else:
            print(f"❌ Expected 401, got {r.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def main():
    print("\n" + "=" * 50)
    print("JWT Authentication Test Suite")
    print("=" * 50 + "\n")

    # Check if server is running
    try:
        r = requests.get(f"{BASE_URL}/register")
        if r.status_code != 200 and r.status_code != 400:
            print("❌ Server not responding. Start backend first:")
            print("   cd backend && python -m uvicorn app.main:app --port 8001")
            sys.exit(1)
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to server. Start backend first:")
        print("   cd backend && python -m uvicorn app.main:app --port 8001")
        sys.exit(1)

    # Run tests
    token, email = test_register()
    
    if token:
        test_login(email)
        test_protected_endpoint(token)
        test_logout()
    
    test_invalid_login()

    print("\n" + "=" * 50)
    print("Test Suite Complete!")
    print("=" * 50)


if __name__ == "__main__":
    main()
