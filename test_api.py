#!/usr/bin/env python3
"""
Test script to verify FastAPI server endpoints
Run this after starting the server to test if everything works
"""

import requests
import json
import sys

BASE_URL = "http://localhost:8000"

def print_section(title):
    """Print a formatted section header"""
    print("\n" + "="*60)
    print(f"  {title}")
    print("="*60)

def test_health():
    """Test health check endpoint"""
    print_section("Testing Health Check")
    try:
        response = requests.get(f"{BASE_URL}/api/health")
        if response.status_code == 200:
            data = response.json()
            print("✅ Health check passed")
            print(f"   Status: {data['status']}")
            print(f"   Total devices: {data['total_devices']}")
            print(f"   Active connections: {data['active_connections']}")
            return True
        else:
            print(f"❌ Health check failed with status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_get_devices():
    """Test getting all devices"""
    print_section("Testing Get All Devices")
    try:
        response = requests.get(f"{BASE_URL}/api/devices")
        if response.status_code == 200:
            data = response.json()
            print("✅ Get devices successful")
            print(f"   Total devices: {len(data['devices'])}")
            print(f"   Current device: {data['current_device']}")
            print("\n   Devices:")
            for device_id, device in data['devices'].items():
                state = "ON" if device['state'] else "OFF"
                print(f"      - {device['name']} ({device_id}): {state}")
            return True
        else:
            print(f"❌ Failed with status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_get_single_device():
    """Test getting a single device"""
    print_section("Testing Get Single Device")
    device_id = "device_1"
    try:
        response = requests.get(f"{BASE_URL}/api/devices/{device_id}")
        if response.status_code == 200:
            data = response.json()
            device = data['device']
            print(f"✅ Get device '{device_id}' successful")
            print(f"   Name: {device['name']}")
            print(f"   Type: {device['type']}")
            print(f"   State: {'ON' if device['state'] else 'OFF'}")
            return True
        else:
            print(f"❌ Failed with status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_toggle_device():
    """Test toggling a device"""
    print_section("Testing Device Toggle")
    device_id = "device_1"
    try:
        # Get current state
        response = requests.get(f"{BASE_URL}/api/devices/{device_id}")
        old_state = response.json()['device']['state']
        
        # Toggle
        response = requests.post(f"{BASE_URL}/api/devices/{device_id}/toggle")
        if response.status_code == 200:
            data = response.json()
            new_state = data['device']['state']
            print(f"✅ Toggle successful")
            print(f"   Device: {data['device']['name']}")
            print(f"   Old state: {'ON' if old_state else 'OFF'}")
            print(f"   New state: {'ON' if new_state else 'OFF'}")
            
            # Toggle back
            requests.post(f"{BASE_URL}/api/devices/{device_id}/toggle")
            print(f"   (Toggled back to original state)")
            return True
        else:
            print(f"❌ Failed with status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_set_device_state():
    """Test setting device state"""
    print_section("Testing Set Device State")
    device_id = "device_2"
    try:
        # Turn ON
        response = requests.post(
            f"{BASE_URL}/api/devices/{device_id}/state",
            json={"state": True}
        )
        if response.status_code == 200:
            print(f"✅ Set state to ON successful")
            
            # Turn OFF
            response = requests.post(
                f"{BASE_URL}/api/devices/{device_id}/state",
                json={"state": False}
            )
            print(f"✅ Set state to OFF successful")
            return True
        else:
            print(f"❌ Failed with status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_select_device():
    """Test selecting a device"""
    print_section("Testing Device Selection")
    device_id = "device_3"
    try:
        response = requests.post(f"{BASE_URL}/api/select-device/{device_id}")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Device selection successful")
            print(f"   Selected device: {data['current_device']}")
            
            # Reset to device_1
            requests.post(f"{BASE_URL}/api/select-device/device_1")
            print(f"   (Reset to device_1)")
            return True
        else:
            print(f"❌ Failed with status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_settings():
    """Test getting and updating settings"""
    print_section("Testing Settings")
    try:
        # Get settings
        response = requests.get(f"{BASE_URL}/api/settings")
        if response.status_code == 200:
            data = response.json()
            print("✅ Get settings successful")
            print(f"   Enabled: {data['settings']['enabled']}")
            print(f"   Confidence: {data['settings']['confidence']}")
            print(f"   Hold time: {data['settings']['hold_time']}s")
            return True
        else:
            print(f"❌ Failed with status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_web_page():
    """Test if web page loads"""
    print_section("Testing Web Page")
    try:
        response = requests.get(f"{BASE_URL}/")
        if response.status_code == 200:
            print("✅ Web page loads successfully")
            print(f"   Content length: {len(response.text)} bytes")
            return True
        else:
            print(f"❌ Failed with status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    """Run all tests"""
    print("\n" + "🧪"*30)
    print("  FASTAPI SERVER TEST SUITE")
    print("🧪"*30)
    
    print("\n⚠️  Make sure the server is running before running tests!")
    print("   Start server with: python run_server.py")
    
    input("\nPress Enter to start tests...")
    
    tests = [
        ("Health Check", test_health),
        ("Web Page", test_web_page),
        ("Get All Devices", test_get_devices),
        ("Get Single Device", test_get_single_device),
        ("Toggle Device", test_toggle_device),
        ("Set Device State", test_set_device_state),
        ("Select Device", test_select_device),
        ("Settings", test_settings),
    ]
    
    results = []
    for test_name, test_func in tests:
        result = test_func()
        results.append((test_name, result))
    
    # Print summary
    print_section("TEST SUMMARY")
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {status} - {test_name}")
    
    print(f"\n  Total: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n  🎉 All tests passed! Server is working correctly.")
        return 0
    else:
        print(f"\n  ⚠️  {total - passed} test(s) failed. Please check the server.")
        return 1

if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\n👋 Tests interrupted. Goodbye!")
        sys.exit(0)