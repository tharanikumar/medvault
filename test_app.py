#!/usr/bin/env python3
"""
MedVault Application Test Script
Tests all routes and functionality
"""

import requests
import sys

BASE_URL = "http://localhost:5001"
DEMO_MODE = True

def test_route(path, expected_status=200, method="GET"):
    """Test a route and return success/failure"""
    url = f"{BASE_URL}{path}"
    try:
        if method == "GET":
            response = requests.get(url, timeout=5)
        else:
            response = requests.post(url, timeout=5)
        
        status = "✓" if response.status_code == expected_status else "✗"
        print(f"{status} {method} {path}: {response.status_code}")
        return response.status_code == expected_status
    except Exception as e:
        print(f"✗ {method} {path}: ERROR - {e}")
        return False

def test_registration():
    """Test complete registration flow"""
    print("\n=== Testing Registration Flow ===")
    
    # 1. Test GET register page
    if not test_route("/register", 200):
        return False
    
    # 2. Test registration with DEMO MODE
    print("\n--- Testing Registration with DEMO MODE ---")
    try:
        # Register new user
        register_data = {
            "email": "testuser@demo.com",
            "user_type": "patient",
            "password": "testpass123",
            "confirm_password": "testpass123",
            "action": "send_otp"
        }
        response = requests.post(f"{BASE_URL}/register", data=register_data, timeout=5)
        print(f"  POST /register: {response.status_code}")
        
        if response.status_code in [200, 302]:
            # Check if it redirects to verify_otp
            if "/verify_otp" in response.url or response.status_code == 302:
                print("  ✓ Registration started, redirecting to OTP verification...")
                print("  ✓ DEMO MODE OTP: See output above")
                print("  ✓ Registration flow initiated successfully")
                return True
        else:
            print("  ✗ Registration failed")
            return False
    except Exception as e:
        print(f"  ✗ Error: {e}")
        return False
    
    return True

def test_login_flow():
    """Test login flow"""
    print("\n=== Testing Login Flow ===")
    
    # 1. Test GET login page
    if not test_route("/login", 200):
        return False
    
    # 2. Test login POST
    try:
        login_data = {
            "email": "test@example.com",
            "action": "send_otp"
        }
        response = requests.post(f"{BASE_URL}/login", data=login_data, timeout=5)
        print(f"  POST /login (send_otp): {response.status_code}")
        return response.status_code in [200, 302]
    except Exception as e:
        print(f"  ✗ Error: {e}")
        return False

def test_public_routes():
    """Test all public routes"""
    print("\n=== Testing Public Routes ===")
    
    routes = [
        "/",
        "/about",
        "/contact",
        "/login",
        "/register",
        "/static/css/styles.css",
        "/static/js/main.js",
    ]
    
    results = [test_route(r) for r in routes]
    return all(results)

def test_auth_routes():
    """Test authentication-protected routes"""
    print("\n=== Testing Auth Routes (should redirect) ===")
    
    routes = [
        "/patient/dashboard",
        "/doctor/dashboard", 
        "/hospital/dashboard",
        "/appointments",
        "/records",
    ]
    
    # These should redirect (302) to login for unauthenticated users
    results = []
    for route in routes:
        response = requests.get(f"{BASE_URL}{route}", allow_redirects=False, timeout=5)
        status = "✓" if response.status_code in [302, 401, 403] else "✗"
        print(f"{status} GET {route}: {response.status_code} (redirects to login)")
        results.append(response.status_code in [302, 401, 403])
    
    return all(results)

def main():
    """Run all tests"""
    print("=" * 60)
    print("MedVault Application Test Suite")
    print("=" * 60)
    print(f"Base URL: {BASE_URL}")
    print(f"DEMO MODE: {DEMO_MODE}")
    
    all_passed = True
    
    # Test public routes
    if not test_public_routes():
        all_passed = False
    
    # Test auth routes
    if not test_auth_routes():
        all_passed = False
    
    # Test registration flow
    if not test_registration():
        all_passed = False
    
    # Test login flow
    if not test_login_flow():
        all_passed = False
    
    print("\n" + "=" * 60)
    if all_passed:
        print("✅ ALL TESTS PASSED!")
        print("=" * 60)
        print("\nMedVault is running successfully!")
        print(f"Access the application at: {BASE_URL}")
        return 0
    else:
        print("❌ SOME TESTS FAILED")
        print("=" * 60)
        return 1

if __name__ == "__main__":
    sys.exit(main())

