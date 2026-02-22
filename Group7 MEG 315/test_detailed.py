#!/usr/bin/env python3
"""
Detailed test script to find the division by zero error
"""

import requests
import json
import traceback

def test_detailed():
    """Test backend with detailed error tracking"""
    base_url = "http://localhost:8000"
    
    print("Testing Scenario Calculation...")
    
    # Test scenario calculation with detailed logging
    try:
        response = requests.post(f"{base_url}/scenarios/base_case/calculate")
        print(f"Status Code: {response.status_code}")
        
        if response.status_code != 200:
            print(f"Error Response: {response.text}")
            
            # Try to get more details from the backend
            print("\nTrying to get more error details...")
            try:
                error_data = response.json()
                print(f"Error details: {error_data}")
            except:
                print(f"Raw error: {response.text}")
        else:
            result = response.json()
            print(f"Success! Result keys: {list(result.keys())}")
            
    except Exception as e:
        print(f"Request failed: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    test_detailed()