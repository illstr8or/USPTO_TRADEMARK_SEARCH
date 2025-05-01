#!/usr/bin/env python3
"""
USPTO Trademark Search Tool - With typo handling for environment variables
"""

import requests
import json
import os
import time
import sys
from datetime import datetime
from dotenv import load_dotenv

def load_api_key():
    """
    Load API key from environment variable, checking for common typos
    """
    # Try getting the API key from both possible spellings
    api_key = os.environ.get("USPTO_API_KEY") or os.environ.get("USTPO_API_KEY")
    
    if api_key:
        print(f"Using API key from environment variable")
        return api_key
    
    # If API key is not found, ask the user
    api_key = input("Enter your USPTO API key: ").strip()
    
    # Offer to set the environment variable with the correct spelling
    if api_key:
        save = input("Would you like to save this API key as an environment variable? (y/n): ").lower()
        if save == 'y':
            correct_name = "USPTO_API_KEY"
            print(f"\nTo save your API key, run this command in your terminal:")
            print(f"\nexport {correct_name}=\"{api_key}\"")
            print("\nTo make it permanent, add this line to your ~/.bash_profile or ~/.zshrc file")
            
    return api_key

def test_api_connection(api_key):
    """
    Test the connection to the USPTO API with the provided API key
    
    Args:
        api_key (str): Your USPTO API key
        
    Returns:
        bool: True if connection is successful, False otherwise
    """
    # API endpoint for status check
    url = "https://tsdrapi.uspto.gov/ts/cd/status"
    
    # Request headers including the API key
    headers = {
        "accept": "application/json",
        "USPTO-API-KEY": api_key
    }
    
    try:
        print("Testing connection to USPTO API...")
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            print("✅ Connection successful! API is accessible.")
            return True
        elif response.status_code == 401:
            print("❌ Authentication failed. API key is invalid or missing.")
            return False
        else:
            print(f"❌ Connection test failed. Status code: {response.status_code}")
            print(f"Response: {response.text}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Connection test failed. Error: {str(e)}")
        return False

def search_trademark(search_text, api_key):
    """
    Search for a trademark by text using the USPTO TSDR API
    
    Args:
        search_text (str): The trademark text to search for
        api_key (str): Your USPTO API key
        
    Returns:
        dict: The search results or error information
    """
    # API endpoint for trademark search
    url = "https://tsdrapi.uspto.gov/ts/cd/casesearch/searchText"
    
    # Request headers including the API key
    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "USPTO-API-KEY": api_key
    }
    
    # Request body/payload
    data = {
        "searchText": search_text,
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
        print(f"Searching for trademark: {search_text}")
        response = requests.post(url, headers=headers, json=data)
        
        # Check if the request was successful
        response.raise_for_status()
        
        # Parse and return the JSON response
        result = response.json()
        return result
    except requests.exceptions.HTTPError as http_err:
        if response.status_code == 401:
            print("Authentication Error: API key is missing or invalid")
            print(f"Response: {response.text}")
            return {"error": "Authentication Error", "message": "API key is missing or invalid"}
        else:
            print(f"HTTP Error: {response.status_code}")
            print(f"Response: {response.text}")
            return {"error": f"HTTP Error: {response.status_code}", "message": str(http_err)}
    except requests.exceptions.RequestException as req_err:
        print(f"Request Error: {str(req_err)}")
        return {"error": "Request Error", "message": str(req_err)}
    except json.JSONDecodeError as json_err:
        print(f"JSON Decode Error: {str(json_err)}")
        return {"error": "JSON Decode Error", "message": str(json_err)}
    except Exception as err:
        print(f"Unexpected Error: {str(err)}")
        return {"error": "Unexpected Error", "message": str(err)}

def analyze_results(name, search_results):
    """
    Analyze the search results to determine potential conflicts.
    
    Args:
        name (str): The trademark name that was searched
        search_results (dict): The search results from the USPTO API
        
    Returns:
        dict: Analysis of potential conflicts
    """
    # Check for error in search results
    if isinstance(search_results, dict) and "error" in search_results:
        return {
            "name": name,
            "potential_conflicts": [],
            "conflict_count": 0,
            "message": f"Error occurred during search: {search_results.get('message', 'Unknown error')}"
        }
    
    if not search_results or not isinstance(search_results, dict) or "trademarks" not in search_results:
        return {
            "name": name,
            "potential_conflicts": [],
            "conflict_count": 0,
            "message": "No matching trademarks found or API returned unexpected format."
        }
    
    trademarks = search_results.get("trademarks", [])
    potential_conflicts = []
    
    for tm in trademarks:
        # Extract relevant information
        serial_number = tm.get("serialNumber", "")
        registration_number = tm.get("registrationNumber", "")
        mark_literal = tm.get("markText", "")
        status = tm.get("status", {})
        
        if isinstance(status, dict):
            status_code = status.get("code", "")
            status_desc = status.get("description", "")
        else:
            status_code = ""
            status_desc = ""
            
        filing_date = tm.get("filingDate", "")
        
        # Only consider active trademarks as potential conflicts
        if status_code in ["LIVE", "PENDING"]:
            potential_conflicts.append({
                "serial_number": serial_number,
                "registration_number": registration_number,
                "mark_literal": mark_literal,
                "status": f"{status_code} - {status_desc}",
                "filing_date": filing_date
            })
    
    analysis = {
        "name": name,
        "potential_conflicts": potential_conflicts,
        "conflict_count": len(potential_conflicts),
        "message": f"Found {len(potential_conflicts)} potential conflicts among {len(trademarks)} matches."
    }
    
    return analysis

def save_results(name, analysis, search_results=None):
    """
    Save the search results and analysis to files.
    
    Args:
        name (str): The trademark name that was searched
        analysis (dict): The analysis of potential conflicts
        search_results (dict, optional): The raw search results
        
    Returns:
        str: Path to the saved analysis file
    """
    # Create results directory if it doesn't exist
    results_dir = "ustpo_results"  # Using the typo to match existing directories
    if not os.path.exists(results_dir):
        results_dir = "uspto_results"  # Try the correct spelling
        if not os.path.exists(results_dir):
            # Create a new directory with the correct spelling
            os.makedirs(results_dir)
    
    # Create a timestamp for the filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Clean name for file system use
    clean_name = "".join(c if c.isalnum() else "_" for c in name)
    
    # Create a directory for this search if it doesn't exist
    search_dir = os.path.join(results_dir, f"{clean_name}_{timestamp}")
    if not os.path.exists(search_dir):
        os.makedirs(search_dir)
    
    # Save the analysis
    analysis_path = os.path.join(search_dir, "analysis.json")
    with open(analysis_path, 'w') as f:
        json.dump(analysis, f, indent=4)
    
    # Save the raw search results if provided
    if search_results:
        search_results_path = os.path.join(search_dir, "search_results.json")
        with open(search_results_path, 'w') as f:
            json.dump(search_results, f, indent=4)
    
    print(f"Results for '{name}' saved to {search_dir}")
    
    return analysis_path

def main():
    print("=" * 70)
    print("USPTO TRADEMARK SEARCH TOOL")
    print("=" * 70)
    
    # Load API key
    api_key = load_api_key()
    
    if not api_key:
        print("Error: API key is required to use the USPTO TSDR API.")
        sys.exit(1)
    
    # Test the API connection
    if not test_api_connection(api_key):
        print("Failed to connect to the USPTO API. Please check your API key and internet connection.")
        sys.exit(1)
    
    # List of trademark names to search
    trademark_names = [
        "SPRINGIFY",
        "LEAPWISE",
        "EXPERIENCE CONTINUITY",
        "MOBILE ERA OF INTENT",
        "LEAPWORKS",
        "SPRYNETIC",
        "SPRYNOVA",
        "STRIDEON"
    ]
    
    # Allow user to modify the list
    print("\nCurrent trademark names to search:")
    for i, name in enumerate(trademark_names, 1):
        print(f"{i}. {name}")
    
    modify = input("\nWould you like to modify this list? (y/n): ").lower()
    if modify == 'y':
        new_names = []
        print("Enter up to 8 trademark names (press Enter on an empty line to finish):")
        for i in range(8):
            name = input(f"Name {i+1}: ").strip()
            if not name:
                break
            new_names.append(name)
        
        if new_names:
            trademark_names = new_names
    
    # Process each trademark name
    all_results = []
    
    for name in trademark_names:
        # Search for the trademark
        search_results = search_trademark(name, api_key)
        
        # Analyze the results
        analysis = analyze_results(name, search_results)
        
        # Save the results
        save_results(name, analysis, search_results)
        
        all_results.append(analysis)
        
        # Add a delay to avoid rate limiting
        time.sleep(2)
    
    # Generate summary report
    results_dir = "ustpo_results" if os.path.exists("ustpo_results") else "uspto_results"
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_path = os.path.join(results_dir, f"summary_report_{timestamp}.txt")
    
    with open(report_path, 'w') as f:
        f.write("USPTO TRADEMARK SEARCH SUMMARY REPORT\n")
        f.write(f"Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        
        for result in all_results:
            name = result.get("name", "")
            conflict_count = result.get("conflict_count", 0)
            message = result.get("message", "")
            
            f.write(f"Trademark: {name}\n")
            f.write(f"Potential Conflicts: {conflict_count}\n")
            f.write(f"Summary: {message}\n")
            
            if conflict_count > 0:
                f.write("Conflicts:\n")
                for i, conflict in enumerate(result.get("potential_conflicts", []), 1):
                    mark = conflict.get("mark_literal", "")
                    status = conflict.get("status", "")
                    serial = conflict.get("serial_number", "")
                    reg = conflict.get("registration_number", "")
                    
                    f.write(f"  {i}. Mark: {mark}\n")
                    f.write(f"     Status: {status}\n")
                    f.write(f"     Serial #: {serial}\n")
                    if reg:
                        f.write(f"     Registration #: {reg}\n")
                    f.write("\n")
            
            f.write("-" * 60 + "\n\n")
        
        f.write("END OF REPORT\n")
    
    print(f"Summary report saved to {report_path}")
    
    # Print summary to console
    print("\nSearch Results Summary:")
    print("-" * 40)
    for result in all_results:
        print(f"{result['name']}: {result['conflict_count']} potential conflicts")
    print("-" * 40)
    print(f"\nSearch complete! All results saved to {results_dir}")

if __name__ == "__main__":
    main()