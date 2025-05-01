#!/usr/bin/env python3
"""
Simple USPTO API Key verification script with no external dependencies
"""

import urllib.request
import urllib.error
import json
import os
import sys

def test_api_key(api_key):
    """Test if the USPTO API key is valid"""
    print("Testing USPTO API key...")
    
    url = "https://tsdrapi.uspto.gov/ts/cd/status"
    headers = {
        "USPTO-API-KEY": api_key,
        "Accept": "application/json"
    }
    
    try:
        # Create a request with headers
        req = urllib.request.Request(url, headers=headers)
        
        # Send the request and get the response
        with urllib.request.urlopen(req) as response:
            # Read and decode the response
            data = response.read().decode('utf-8')
            status_code = response.getcode()
            
            if status_code == 200:
                print(f"✅ Success! Your API key is valid. Status code: {status_code}")
                print(f"Response: {data}")
                return True
            else:
                print(f"❌ Error: Unexpected status code: {status_code}")
                print(f"Response: {data}")
                return False
                
    except urllib.error.HTTPError as e:
        if e.code == 401:
            print(f"❌ Authentication failed. Your API key is invalid or missing.")
            print(f"Error code: {e.code}")
            print(f"Response: {e.read().decode('utf-8')}")
        else:
            print(f"❌ HTTP Error: {e.code}")
            print(f"Response: {e.read().decode('utf-8')}")
        return False
        
    except urllib.error.URLError as e:
        print(f"❌ Connection failed: {e.reason}")
        return False
        
    except Exception as e:
        print(f"❌ Unexpected error: {str(e)}")
        return False

def main():
    # Try both spellings of the environment variable
    api_key = os.environ.get("USPTO_API_KEY") or os.environ.get("USTPO_API_KEY")
    
    if not api_key:
        print("No API key found in environment variables.")
        api_key = input("Please enter your USPTO API key: ").strip()
        
        if not api_key:
            print("Error: API key is required to test the USPTO API.")
            sys.exit(1)
    
    # Test the API key
    if test_api_key(api_key):
        print("\nYour USPTO API key has been verified successfully!")
        print("You can now use this key with the full USPTO script.")
    else:
        print("\nThere was a problem with your USPTO API key.")
        print("Please check that you have the correct key and try again.")

if __name__ == "__main__":
    main()