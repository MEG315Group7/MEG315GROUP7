#!/usr/bin/env python3
"""
Debug test script to find the exact division by zero error
"""

import requests
import json

def test_debug():
    """Test backend with debug output"""
    base_url = "http://localhost:8000"
    
    print("Testing Scenario Calculation with Debug...")
    
    # First, let's test the individual components
    print("\n1. Testing AD System...")
    try:
        response = requests.post(f"{base_url}/scenarios/base_case/calculate")
        print(f"Status Code: {response.status_code}")
        
        if response.status_code != 200:
            print(f"Error Response: {response.text}")
            
            # Let's try to get more details by testing the individual components
            print("\n2. Testing individual AD calculation...")
            
            # Test with a simple AD calculation
            ad_test = requests.post(f"{base_url}/calculate", json={
                "ambient_temp": 298.15,
                "pressure_ratio": 12.0,
                "max_turbine_temp": 1400.0,
                "compressor_efficiency": 0.85,
                "turbine_efficiency": 0.88,
                "ad_feedstock_rate": 3000.0,
                "ad_retention_time": 20.0,
                "htc_biomass_rate": 500.0,
                "htc_temperature": 473.0,
                "scenario": "base_case"
            })
            
            if ad_test.status_code == 200:
                result = ad_test.json()
                print("Custom calculation successful!")
                print(f"AD Results: {result.get('ad_performance', {}).keys()}")
                print(f"HTC Results: {result.get('htc_performance', {}).keys()}")
                print(f"Overall Results: {result.get('overall_performance', {}).keys()}")
                
                # Check specific values
                overall = result.get('overall_performance', {})
                print(f"Net power: {overall.get('net_power_output_kw', 'N/A')}")
                print(f"Biogas energy: {overall.get('biogas_energy_input_kw', 'N/A')}")
                print(f"Overall efficiency: {overall.get('overall_efficiency', 'N/A')}")
            else:
                print(f"Custom calculation failed: {ad_test.text}")
                
    except Exception as e:
        print(f"Request failed: {e}")

if __name__ == "__main__":
    test_debug()