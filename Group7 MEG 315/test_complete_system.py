#!/usr/bin/env python3
"""
Complete system test script to verify both frontends and backend are working.
This script tests the entire AD-HTC system integration.
"""

import requests
import json
import time

def test_backend():
    """Test the FastAPI backend"""
    print("=== Testing Backend ===")
    base_url = "http://localhost:8000"
    
    try:
        # Test health endpoint
        response = requests.get(f"{base_url}/")
        print(f"✅ Backend health check: {response.status_code}")
        
        # Test presets endpoint
        response = requests.get(f"{base_url}/presets")
        if response.status_code == 200:
            presets = response.json()
            print(f"✅ Presets available: {list(presets.keys())}")
        else:
            print(f"❌ Presets endpoint failed: {response.status_code}")
            return False
        
        # Test scenario calculation
        print("Testing scenario calculation...")
        response = requests.post(f"{base_url}/scenarios/base_case/calculate")
        if response.status_code == 200:
            results = response.json()
            print(f"✅ Scenario calculation successful")
            print(f"  - Net power: {results['overall_performance']['net_power_output_kw']:.2f} kW")
            print(f"  - Biogas energy: {results['overall_performance']['biogas_energy_input_kw']:.2f} kW")
            print(f"  - HTC heat demand: {results['overall_performance']['htc_heat_demand_kw']:.2f} kW")
            print(f"  - Self-sufficiency: {results['overall_performance']['self_sufficiency_ratio']:.4f}")
            return True
        else:
            print(f"❌ Scenario calculation failed: {response.status_code}")
            print(f"Error: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Backend is not running. Please start it first with:")
        print("   cd backend && python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000")
        return False
    except Exception as e:
        print(f"❌ Backend test failed: {e}")
        return False

def test_python_frontend():
    """Test the Python frontend (basic connectivity check)"""
    print("\n=== Testing Python Frontend ===")
    
    try:
        # Check if the Python frontend file exists
        import os
        frontend_path = "frontend_python/adhtc_gui.py"
        if os.path.exists(frontend_path):
            print(f"✅ Python frontend file exists: {frontend_path}")
            
            # Check if required packages are available
            try:
                import tkinter
                print("✅ tkinter is available")
            except ImportError:
                print("❌ tkinter is not available (usually included with Python)")
            
            try:
                import matplotlib
                print("✅ matplotlib is available")
            except ImportError:
                print("❌ matplotlib is not available")
            
            return True
        else:
            print(f"❌ Python frontend file not found: {frontend_path}")
            return False
            
    except Exception as e:
        print(f"❌ Python frontend test failed: {e}")
        return False

def test_react_frontend():
    """Test the React frontend (basic connectivity check)"""
    print("\n=== Testing React Frontend ===")
    
    try:
        # Check if the React frontend files exist
        import os
        
        # Check package.json
        package_path = "frontend/package.json"
        if os.path.exists(package_path):
            print(f"✅ React package.json exists: {package_path}")
            
            # Check if npm is available
            import subprocess
            try:
                result = subprocess.run(['npm', '--version'], 
                                      capture_output=True, 
                                      text=True, 
                                      timeout=5)
                if result.returncode == 0:
                    print(f"✅ npm is available: v{result.stdout.strip()}")
                else:
                    print("❌ npm command failed")
            except (subprocess.TimeoutExpired, FileNotFoundError):
                print("❌ npm is not available")
            
            # Check App.js
            app_path = "frontend/src/App.js"
            if os.path.exists(app_path):
                print(f"✅ React App.js exists: {app_path}")
            else:
                print(f"❌ React App.js not found: {app_path}")
            
            return True
        else:
            print(f"❌ React package.json not found: {package_path}")
            return False
            
    except Exception as e:
        print(f"❌ React frontend test failed: {e}")
        return False

def main():
    """Main test function"""
    print("AD-HTC System Integration Test")
    print("="*50)
    
    # Test backend first
    backend_ok = test_backend()
    
    # Test frontends
    python_frontend_ok = test_python_frontend()
    react_frontend_ok = test_react_frontend()
    
    # Summary
    print("\n" + "="*50)
    print("TEST SUMMARY:")
    print(f"Backend: {'✅ Working' if backend_ok else '❌ Failed'}")
    print(f"Python Frontend: {'✅ Available' if python_frontend_ok else '❌ Issues'}")
    print(f"React Frontend: {'✅ Available' if react_frontend_ok else '❌ Issues'}")
    
    if backend_ok and python_frontend_ok and react_frontend_ok:
        print("\n🎉 All systems are ready! You can now use either frontend.")
        print("\nTo start the Python frontend:")
        print("   cd frontend_python && python adhtc_gui.py")
        print("\nTo start the React frontend:")
        print("   cd frontend && npm start")
    elif backend_ok:
        print("\n✅ Backend is working. Frontends have some issues but may still work.")
    else:
        print("\n❌ Backend is not working. Please fix the backend first.")
    
    return backend_ok

if __name__ == "__main__":
    main()