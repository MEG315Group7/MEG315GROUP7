#!/usr/bin/env python3

import requests
import json

base_url = "http://localhost:8000"

# Test the presets endpoint
print("=== Testing Presets Endpoint ===")
presets_response = requests.get(f"{base_url}/presets")
if presets_response.status_code == 200:
    presets_data = presets_response.json()
    print("Available presets:", list(presets_data.keys()))
    
    # Check base case parameters
    if 'base_case' in presets_data:
        base_case = presets_data['base_case']
        print(f"Base case name: {base_case['name']}")
        print(f"Base case parameters: {json.dumps(base_case['parameters'], indent=2)}")
        
        # Check if biomass_rate exists
        if 'biomass_rate' in base_case['parameters']:
            print(f"✅ biomass_rate found: {base_case['parameters']['biomass_rate']}")
        else:
            print("❌ biomass_rate NOT found in parameters")
            print("Available parameters:", list(base_case['parameters'].keys()))
else:
    print(f"❌ Presets endpoint failed: {presets_response.status_code}")

print("\n=== Testing Scenario Calculation ===")
# Test scenario calculation
scenario_response = requests.post(f"{base_url}/scenarios/base_case/calculate")
print(f"Scenario calculation status: {scenario_response.status_code}")
if scenario_response.status_code != 200:
    print(f"Error: {scenario_response.text}")
else:
    print("✅ Scenario calculation successful")
    result = scenario_response.json()
    print(f"Results: {json.dumps(result, indent=2)}")