#!/usr/bin/env python3
"""
MarkerAPI Trademark Search Script
A script for searching multiple trademark names using the MarkerAPI service
"""

import requests
import json
import os
import time
import sys
from datetime import datetime

class MarkerAPITrademarkSearch:
    """
    A class to search for trademarks using the MarkerAPI service
    MarkerAPI is a third-party service that provides access to USPTO trademark data
    You need to sign up at https://markerapi.com/ to get API credentials
    """
    
    def __init__(self, username, password):
        """
        Initialize with MarkerAPI credentials
        
        Args:
            username (str): Your MarkerAPI username
            password (str): Your MarkerAPI password
        """
        self.username = username
        self.password = password
        self.base_url = "https://markerapi.com/api/v2/trademarks"
        
        # Create results directory if it doesn't exist
        self.results_dir = os.path.join(os.getcwd(), "trademark_results")
        if not os.path.exists(self.results_dir):
            os.makedirs(self.results_dir)
            print(f"Created results directory: {self.results_dir}")
    
    def search_trademark(self, name, status="active", start=1):
        """
        Search for a trademark by name using MarkerAPI
        
        Args:
            name (str): The trademark name to search
            status (str): "active" for only active trademarks, "all" for all trademarks
            start (int): Starting point for pagination (1 for first page)
            
        Returns:
            dict: The search results or error information
        """
        # API endpoint for trademark search
        url = f"{self.base_url}/trademark/{name}/status/{status}/start/{start}/username/{self.username}/password/{self.password}"
        
        try:
            print(f"Searching for trademark: {name}")
            response = requests.get(url)
            
            # Check if the request was successful
            if response.status_code != 200:
                print(f"Error: HTTP {response.status_code} - {response.text}")
                return {"error": f"HTTP {response.status_code}", "message": response.text}
            
            # Parse and return the JSON response
            result = response.json()
            
            # Display count of trademarks found
            if "count" in result:
                print(f"Found {result['count']} trademark matches for '{name}'")
            
            return result
        
        except requests.exceptions.RequestException as req_err:
            print(f"Request Error: {str(req_err)}")
            return {"error": "Request Error", "message": str(req_err)}
        
        except json.JSONDecodeError as json_err:
            print(f"JSON Decode Error: {str(json_err)}")
            print(f"Response text: {response.text[:200]}...")  # Show first 200 chars of response
            return {"error": "JSON Decode Error", "message": str(json_err)}
        
        except Exception as err:
            print(f"Unexpected Error: {str(err)}")
            return {"error": "Unexpected Error", "message": str(err)}
    
    def analyze_results(self, name, search_results):
        """
        Analyze the search results to determine potential conflicts
        
        Args:
            name (str): The trademark name that was searched
            search_results (dict): The search results from the MarkerAPI
            
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
        
        if not search_results or not isinstance(search_results, dict) or "count" not in search_results:
            return {
                "name": name,
                "potential_conflicts": [],
                "conflict_count": 0,
                "message": "No matching trademarks found or API returned unexpected format."
            }
        
        # Check if trademarks were found
        if search_results.get("count", 0) == 0 or "trademarks" not in search_results:
            return {
                "name": name,
                "potential_conflicts": [],
                "conflict_count": 0,
                "message": "No matching trademarks found."
            }
        
        trademarks = search_results.get("trademarks", [])
        potential_conflicts = []
        
        for tm in trademarks:
            # Extract relevant information from MarkerAPI format
            serialnumber = tm.get("serialnumber", "")
            wordmark = tm.get("wordmark", "")
            description = tm.get("description", "")
            code = tm.get("code", "")
            registrationdate = tm.get("registrationdate", "")
            status = tm.get("status", "")
            
            # For MarkerAPI, all returned results are potential conflicts
            potential_conflicts.append({
                "serial_number": serialnumber,
                "mark_text": wordmark,
                "description": description,
                "code": code,
                "registration_date": registrationdate,
                "status": status
            })
        
        analysis = {
            "name": name,
            "potential_conflicts": potential_conflicts,
            "conflict_count": len(potential_conflicts),
            "message": f"Found {len(potential_conflicts)} potential conflicts."
        }
        
        return analysis
    
    def save_results(self, name, analysis, search_results=None):
        """
        Save the search results and analysis to files
        
        Args:
            name (str): The trademark name that was searched
            analysis (dict): The analysis of potential conflicts
            search_results (dict, optional): The raw search results
            
        Returns:
            str: Path to the saved analysis file
        """
        # Create a timestamp for the filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Clean name for file system use
        clean_name = "".join(c if c.isalnum() else "_" for c in name)
        
        # Create a directory for this search if it doesn't exist
        search_dir = os.path.join(self.results_dir, f"{clean_name}_{timestamp}")
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

    def process_trademark_names(self, names, status="active"):
        """
        Process a list of trademark names to check for conflicts
        
        Args:
            names (list): List of trademark names to search
            status (str): "active" for only active trademarks, "all" for all trademarks
            
        Returns:
            list: Analysis results for each name
        """
        results = []
        
        for name in names:
            # Search for the trademark
            search_results = self.search_trademark(name, status)
            
            # Analyze the results
            analysis = self.analyze_results(name, search_results)
            
            # Save the results
            self.save_results(name, analysis, search_results)
            
            results.append(analysis)
            
            # Add a delay to avoid rate limiting
            time.sleep(2)
        
        return results

    def generate_summary_report(self, results):
        """
        Generate a summary report of the trademark search results
        
        Args:
            results (list): List of analysis results for each name
            
        Returns:
            str: Path to the saved summary report
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_path = os.path.join(self.results_dir, f"summary_report_{timestamp}.txt")
        
        with open(report_path, 'w') as f:
            f.write("TRADEMARK SEARCH SUMMARY REPORT\n")
            f.write(f"Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            for result in results:
                name = result.get("name", "")
                conflict_count = result.get("conflict_count", 0)
                message = result.get("message", "")
                
                f.write(f"Trademark: {name}\n")
                f.write(f"Potential Conflicts: {conflict_count}\n")
                f.write(f"Summary: {message}\n")
                
                if conflict_count > 0:
                    f.write("Conflicts:\n")
                    for i, conflict in enumerate(result.get("potential_conflicts", []), 1):
                        mark = conflict.get("mark_text", "")
                        description = conflict.get("description", "")
                        serial = conflict.get("serial_number", "")
                        
                        f.write(f"  {i}. Mark: {mark}\n")
                        f.write(f"     Description: {description}\n")
                        f.write(f"     Serial #: {serial}\n")
                        f.write("\n")
                
                f.write("-" * 60 + "\n\n")
            
            f.write("END OF REPORT\n")
        
        print(f"Summary report saved to {report_path}")
        return report_path

def test_connection(username, password):
    """Test if we can connect to the MarkerAPI service with the provided credentials"""
    print("Testing connection to MarkerAPI...")
    print(username)
    print(password)
    
    # Use a test search to verify credentials
    # url = f"https://markerapi.com/api/v2/trademarks/trademark/test/status/active/start/1/username/{username}/password/{password}"
    url = f"https://markerapi.com/api/v2/trademarks/trademark/test/status/active/start/1/username/{username}/password/{password}"
    
    try:
        response = requests.get(url)
        
        if response.status_code == 200:
            print("✅ Connection successful! MarkerAPI is accessible with your credentials.")
            return True
        else:
            print(f"❌ Connection test failed. Status code: {response.status_code}")
            print(f"Response: {response.text}")
            return False
    
    except requests.exceptions.RequestException as e:
        print(f"❌ Connection test failed. Error: {str(e)}")
        return False

def main():
    print("=" * 70)
    print("MARKERAPI TRADEMARK SEARCH TOOL")
    print("=" * 70)
    
    # Get MarkerAPI credentials
    username = os.environ.get("MARKER_API_USERNAME")
    password = os.environ.get("MARKER_API_PASSWORD")
    
    if not username or not password:
        print("MarkerAPI credentials not found in environment variables.")
        username = input("Enter your MarkerAPI username: ").strip()
        password = input("Enter your MarkerAPI password: ").strip()
        
        if not username or not password:
            print("Error: MarkerAPI credentials are required to use this tool.")
            print("Sign up at https://markerapi.com/ to get API credentials.")
            sys.exit(1)
    
    # Test connection before proceeding
    if not test_connection(username, password):
        print("\nUnable to connect to MarkerAPI. Please check your credentials and internet connection.")
        sys.exit(1)
    
    # Create an instance of the MarkerAPITrademarkSearch class
    api = MarkerAPITrademarkSearch(username, password)
    
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
    
    # Ask if user wants to search only active trademarks or all trademarks
    status = "active"  # Default to active trademarks
    status_choice = input("\nSearch only active trademarks? (y/n): ").lower()
    if status_choice == 'n':
        status = "all"
    
    print(f"\nWill search for the following trademarks with status={status}:")
    for i, name in enumerate(trademark_names, 1):
        print(f"{i}. {name}")
    
    confirm = input("\nProceed with search? (y/n): ").lower()
    if confirm != 'y':
        print("Search cancelled.")
        return
    
    print("\nStarting search process...")
    
    # Process the trademark names
    results = api.process_trademark_names(trademark_names, status)
    
    # Generate a summary report
    report_path = api.generate_summary_report(results)
    
    # Print a simple summary to the console
    print("\nSearch Results Summary:")
    print("-" * 40)
    for result in results:
        print(f"{result['name']}: {result['conflict_count']} potential conflicts")
    print("-" * 40)
    
    print(f"\nSearch complete! Results saved to: {api.results_dir}")
    print(f"Summary report: {report_path}")

if __name__ == "__main__":
    main()