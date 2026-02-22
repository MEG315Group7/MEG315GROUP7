#!/usr/bin/env python3

import requests
import json

base_url = "http://localhost:8000"

# Test the scenario manager endpoint
print("=== Testing Scenario Manager ===")
scenario_response = requests.get(f"{base_url}/scenarios/base_case")
print(f"Scenario endpoint status: {scenario_response.status_code}")
if scenario_response.status_code == 200:
    scenario_data = scenario_response.json()
    print("Scenario data:", json.dumps(scenario_data, indent=2))
    
    # Check if it has parameters
    if 'scenario' in scenario_data and 'parameters' in scenario_data['scenario']:
        params = scenario_data['scenario']['parameters']
        print(f"Scenario parameters: {json.dumps(params, indent=2)}")
        
        # Check for biomass_rate
        if 'biomass_rate' in params:
            print(f"✅ biomass_rate found: {params['biomass_rate']}")
        else:
            print("❌ biomass_rate NOT found in scenario parameters")
            print("Available parameters:", list(params.keys()))
    else:
        print("❌ No parameters found in scenario data")
else:
    print(f"❌ Scenario endpoint failed: {scenario_response.text}")

# Test the scenarios list endpoint
print("\n=== Testing Scenarios List ===")
scenarios_response = requests.get(f"{base_url}/scenarios")
print(f"Scenarios endpoint status: {scenarios_response.status_code}")
if scenarios_response.status_code == 200:
    scenarios_data = scenarios_response.json()
    print("Available scenarios:", list(scenarios_data['scenarios'].keys()))
    # Check first scenario
    first_scenario = list(scenarios_data['scenarios'].values())[0]
    print("First scenario data:", json.dumps(first_scenario, indent=2))
else:
    print(f"❌ Scenarios endpoint failed: {scenarios_response.text}")