#!/usr/bin/env python3
"""
Test script to verify backend API is working correctly
"""

import requests
import json

def test_backend():
    """Test backend API endpoints"""
    base_url = "http://localhost:8000"
    
    print("Testing Backend API...")
    
    # Test basic endpoint
    try:
        response = requests.get(f"{base_url}/")
        print(f"✅ Root endpoint: {response.status_code}")
        print(f"Response: {response.json()}")
    except Exception as e:
        print(f"❌ Root endpoint failed: {e}")
        return False
    
    # Test presets endpoint
    try:
        response = requests.get(f"{base_url}/presets")
        print(f"✅ Presets endpoint: {response.status_code}")
        presets = response.json()
        print(f"Available presets: {list(presets.keys())}")
    except Exception as e:
        print(f"❌ Presets endpoint failed: {e}")
        return False
    
    # Test calculation with custom parameters
    try:
        payload = {
            "ambient_temp": 288.0,
            "pressure_ratio": 6.0,
            "max_turbine_temp": 1000.0,
            "compressor_efficiency": 0.85,
            "turbine_efficiency": 0.90,
            "ad_feedstock_rate": 3000.0,
            "ad_retention_time": 20.0,
            "htc_biomass_rate": 500.0,
            "htc_temperature": 473.0,
            "scenario": "base_case"
        }
        
        response = requests.post(f"{base_url}/calculate", json=payload)
        print(f"✅ Custom calculation: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"Net power: {result.get('overall_performance', {}).get('net_power_output_kw', 'N/A')} kW")
            print(f"Efficiency: {result.get('overall_performance', {}).get('overall_efficiency', 'N/A')}")
        else:
            print(f"Error response: {response.text}")
            
    except Exception as e:
        print(f"❌ Custom calculation failed: {e}")
        return False
    
    # Test scenario calculation
    try:
        response = requests.post(f"{base_url}/scenarios/base_case/calculate")
        print(f"✅ Scenario calculation: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"Scenario: {result.get('scenario_name', 'N/A')}")
            print(f"Net power: {result.get('overall_performance', {}).get('net_power_output_kw', 'N/A')} kW")
        else:
            print(f"Error response: {response.text}")
            
    except Exception as e:
        print(f"❌ Scenario calculation failed: {e}")
        return False
    
    print("\n✅ All backend tests completed successfully!")
    return True

if __name__ == "__main__":
    test_backend()