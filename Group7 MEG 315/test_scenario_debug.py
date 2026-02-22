#!/usr/bin/env python3
"""
Debug test script to find the exact division by zero error in scenario calculation
"""

import requests
import json

def test_scenario_debug():
    """Test scenario calculation with detailed error tracking"""
    base_url = "http://localhost:8000"
    
    print("Testing Scenario Calculation with Detailed Debug...")
    
    # First, let's get the scenario parameters
    print("\n1. Getting scenario parameters...")
    try:
        response = requests.get(f"{base_url}/presets")
        if response.status_code == 200:
            presets = response.json()
            print(f"Available presets: {presets}")
            
            # Get the base case scenario
            scenario_response = requests.get(f"{base_url}/scenarios/base_case")
            if scenario_response.status_code == 200:
                scenario = scenario_response.json()
                print(f"Base case scenario parameters: {scenario.get('parameters', {})}")
                
                # Now try to calculate
                print("\n2. Testing scenario calculation...")
                calc_response = requests.post(f"{base_url}/scenarios/base_case/calculate")
                print(f"Calculation status: {calc_response.status_code}")
                if calc_response.status_code != 200:
                    print(f"Error response: {calc_response.text}")
                else:
                    print(f"Success response: {calc_response.json()}")
            else:
                print(f"Failed to get scenario: {scenario_response.text}")
        else:
            print(f"Failed to get presets: {response.text}")
            
    except Exception as e:
        print(f"Request failed: {e}")

if __name__ == "__main__":
    test_scenario_debug()