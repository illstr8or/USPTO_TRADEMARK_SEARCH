#!/usr/bin/env python3
"""
USPTO API Key Verification Script
Tests your API key with a working endpoint
"""

import requests
import json
import os
import sys

def test_api_key_with_status_endpoint(api_key):
    """
    Test the API key using a casestatus endpoint with a known serial number
    This is a more reliable test than the status endpoint which may be deprecated
    """
    print("Testing USPTO API key with case status endpoint...")
    
    # Use a specific serial number for testing
    # 78787878 is a sample serial number used in the USPTO documentation
    test_serial = "78787878"
    url = f"https://tsdrapi.uspto.gov/ts/cd/casestatus/sn{test_serial}/info.json"
    
    headers = {
        "accept": "application/json",
        "USPTO-API-KEY": api_key
    }
    
    try:
        # Send the request
        response = requests.get(url, headers=headers)
        
        # Check the status code
        if response.status_code == 200:
            print(f"✅ Success! Your API key is valid.")
            print(f"Successfully retrieved information for serial number: {test_serial}")
            return True
        elif response.status_code == 401:
            print(f"❌ Authentication failed. Your API key is invalid or missing.")
            print(f"Status code: {response.status_code}")
            print(f"Response: {response.text}")
            return False
        else:
            print(f"❌ Unexpected status code: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Connection failed: {str(e)}")
        return False
        
    except Exception as e:
        print(f"❌ Unexpected error: {str(e)}")
        return False

def test_search_endpoint(api_key):
    """
    Test a simple search with the API key
    """
    print("\nTesting USPTO API key with search endpoint...")
    
    # Endpoint for free-form text search
    url = "https://tsdrapi.uspto.gov/ts/cd/casesearch/searchText"
    
    # Request headers including the API key
    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "USPTO-API-KEY": api_key
    }
    
    # Request body/payload for a simple test search
    data = {
        "searchText": "APPLE",
        "options": {
            "searchType": "EXACT_SEARCH",
            "includeClasses": True,
            "includeCriteria": True,
            "includeLabels": True,
            "includeStatus": True,
            "includeTransactionRecords": True
        }
    }
    
    try:
        # Send the request
        response = requests.post(url, headers=headers, json=data)
        
        # Check the status code
        if response.status_code == 200:
            print(f"✅ Search endpoint is working with your API key!")
            try:
                result = response.json()
                if "trademarks" in result:
                    print(f"Found {len(result['trademarks'])} trademark matches for 'APPLE'")
                return True
            except:
                print("Response received but couldn't parse JSON")
                return True
        elif response.status_code == 401:
            print(f"❌ Authentication failed for search endpoint.")
            print(f"Status code: {response.status_code}")
            print(f"Response: {response.text}")
            return False
        else:
            print(f"❌ Unexpected status code from search endpoint: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Connection to search endpoint failed: {str(e)}")
        return False
        
    except Exception as e:
        print(f"❌ Unexpected error with search endpoint: {str(e)}")
        return False

def main():
    print("=" * 70)
    print("USPTO API KEY VERIFICATION TOOL")
    print("=" * 70)
    
    # Get API key from environment variable or user input
    api_key = os.environ.get("USPTO_API_KEY") or os.environ.get("USTPO_API_KEY")
    
    if not api_key:
        api_key = input("Enter your USPTO API key: ").strip()
        
        if not api_key:
            print("Error: API key is required for verification.")
            sys.exit(1)
    
    # Test the API key with a case status endpoint
    case_status_test = test_api_key_with_status_endpoint(api_key)
    
    # Test the search endpoint if the case status test passed
    if case_status_test:
        search_test = test_search_endpoint(api_key)
    else:
        search_test = False
    
    # Report overall results
    print("\n" + "=" * 70)
    print("VERIFICATION RESULTS:")
    print("=" * 70)
    
    if case_status_test and search_test:
        print("✅ Your API key is fully verified and working with all tested endpoints!")
        print("   You can now use the USPTO search script without issues.")
    elif case_status_test:
        print("⚠️ Your API key works with the case status endpoint, but not with the search endpoint.")
        print("   This is unusual - the search script might encounter issues.")
    else:
        print("❌ Your API key could not be verified with any endpoints.")
        print("   Please check that you have the correct key and try again.")
    
    print("\nIf you encounter issues, contact USPTO support at APIhelp@uspto.gov")
    print("=" * 70)

if __name__ == "__main__":
    main()