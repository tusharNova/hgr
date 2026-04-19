#!/usr/bin/env python3
"""
Test Script for Neo Smart Home Control System
Tests API endpoints and functionality
"""

import requests
import json
import time

BASE_URL = "http://localhost:8000"

def print_header(text):
    print("\n" + "=" * 60)
    print(f"  {text}")
    print("=" * 60)

def test_health():
    print_header("Testing Health Check")
    try:
        response = requests.get(f"{BASE_URL}/health")
        print(f"✓ Status: {response.status_code}")
        print(f"✓ Response: {response.json()}")
        return True
    except Exception as e:
        print(f"✗ Error: {e}")
        return False

def test_get_devices():
    print_header("Testing Get All Devices")
    try:
        response = requests.get(f"{BASE_URL}/api/devices")
        data = response.json()
        print(f"✓ Status: {response.status_code}")
        print(f"✓ Found {len(data['devices'])} devices:")
        for device in data['devices']:
            print(f"  - {device['name']} ({device['type']}): {device['state']}")
        return True
    except Exception as e:
        print(f"✗ Error: {e}")
        return False

def test_control_device():
    print_header("Testing Device Control")
    
    # Turn on device 1
    print("\n1. Turning ON device 1...")
    try:
        response = requests.post(
            f"{BASE_URL}/api/control",
            json={"device_id": 1, "action": "on"}
        )
        data = response.json()
        print(f"✓ Status: {response.status_code}")
        print(f"✓ Response: {data}")
    except Exception as e:
        print(f"✗ Error: {e}")
        return False
    
    time.sleep(1)
    
    # Turn off device 1
    print("\n2. Turning OFF device 1...")
    try:
        response = requests.post(
            f"{BASE_URL}/api/control",
            json={"device_id": 1, "action": "off"}
        )
        data = response.json()
        print(f"✓ Status: {response.status_code}")
        print(f"✓ Response: {data}")
    except Exception as e:
        print(f"✗ Error: {e}")
        return False
    
    return True

def test_gesture():
    print_header("Testing Gesture Processing")
    
    # Test open palm gesture
    print("\n1. Testing OPEN PALM gesture (turn on)...")
    try:
        response = requests.post(
            f"{BASE_URL}/api/gesture",
            json={"gesture": "open_palm", "device_id": 2}
        )
        data = response.json()
        print(f"✓ Status: {response.status_code}")
        print(f"✓ Response: {data}")
    except Exception as e:
        print(f"✗ Error: {e}")
        return False
    
    time.sleep(1)
    
    # Test fist gesture
    print("\n2. Testing FIST gesture (turn off)...")
    try:
        response = requests.post(
            f"{BASE_URL}/api/gesture",
            json={"gesture": "fist", "device_id": 2}
        )
        data = response.json()
        print(f"✓ Status: {response.status_code}")
        print(f"✓ Response: {data}")
    except Exception as e:
        print(f"✗ Error: {e}")
        return False
    
    return True

def test_get_device():
    print_header("Testing Get Single Device")
    try:
        response = requests.get(f"{BASE_URL}/api/device/1")
        data = response.json()
        print(f"✓ Status: {response.status_code}")
        print(f"✓ Device Info:")
        print(f"  Name: {data['name']}")
        print(f"  Type: {data['type']}")
        print(f"  State: {data['state']}")
        print(f"  Icon: {data['icon']}")
        return True
    except Exception as e:
        print(f"✗ Error: {e}")
        return False

def test_api_info():
    print_header("Testing API Info")
    try:
        response = requests.get(f"{BASE_URL}/api/info")
        data = response.json()
        print(f"✓ Status: {response.status_code}")
        print(f"✓ API Name: {data['name']}")
        print(f"✓ Version: {data['version']}")
        print(f"✓ Total Devices: {data['devices']}")
        return True
    except Exception as e:
        print(f"✗ Error: {e}")
        return False

def main():
    print("\n" + "=" * 60)
    print("  🧪 NEO SMART HOME - API TEST SUITE")
    print("=" * 60)
    print("\n⚠️  Make sure the server is running on http://localhost:8000")
    print("    Run: python run_server.py")
    print()
    input("Press Enter to start tests...")
    
    results = []
    
    # Run all tests
    results.append(("Health Check", test_health()))
    results.append(("API Info", test_api_info()))
    results.append(("Get All Devices", test_get_devices()))
    results.append(("Get Single Device", test_get_device()))
    results.append(("Device Control", test_control_device()))
    results.append(("Gesture Processing", test_gesture()))
    
    # Summary
    print_header("TEST SUMMARY")
    total = len(results)
    passed = sum(1 for _, result in results if result)
    failed = total - passed
    
    print()
    for test_name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status} - {test_name}")
    
    print(f"\nTotal: {total} | Passed: {passed} | Failed: {failed}")
    
    if failed == 0:
        print("\n🎉 All tests passed! System is working correctly!")
    else:
        print(f"\n⚠️  {failed} test(s) failed. Check the output above.")
    
    print("\n" + "=" * 60)
    print("  🌐 Access Points:")
    print("     Landing Page:    http://localhost:8000")
    print("     Gesture Control: http://localhost:8000/gesture")
    print("     Voice Bot:       http://localhost:8000/voice")
    print("=" * 60)
    print()

if __name__ == "__main__":
    main()