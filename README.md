# USPTO Trademark Search Tool

This project provides a Python-based tool for searching the USPTO's Trademark Status and Document Retrieval (TSDR) API to identify potential trademark conflicts or matches for your proposed trademark names.

## Project Overview

The tool allows you to:
- Search for exact or similar matches to your proposed trademark names
- Retrieve detailed information about existing trademarks
- Analyze potential conflicts with active trademarks
- Save search results and generate summary reports

## Setup Instructions

### Prerequisites
- Python 3.6 or higher
- Visual Studio Code
- An internet connection

### Installation Steps

1. **Create a new project folder and open it in VS Code**
   ```
   mkdir uspto_trademark_search
   cd uspto_trademark_search
   code .
   ```

2. **Create a Python virtual environment**
   ```
   # For macOS/Linux
   python3 -m venv venv
   
   # For Windows
   python -m venv venv
   ```

3. **Activate the virtual environment**
   ```
   # For macOS/Linux
   source venv/bin/activate
   
   # For Windows
   venv\Scripts\activate
   ```

4. **Install required packages**
   ```
   pip install requests
   ```

5. **Save the code from the provided artifact as `uspto_search.py` in your project folder**

6. **Test the installation**
   ```
   python uspto_search.py
   ```

## Usage Guide

### Basic Usage

1. Open `uspto_search.py` in VS Code
2. Modify the `trademark_names` list in the `main()` function to include your desired trademark names:
   ```python
   trademark_names = [
       "YOUR_FIRST_NAME",
       "YOUR_SECOND_NAME",
       # Add up to 6 names
   ]
   ```
3. Run the script using VS Code's built-in tools or from the terminal:
   ```
   python uspto_search.py
   ```

### Customizing Search Parameters

You can customize the search behavior by modifying the `search_trademark` method. For example:

- To perform a prefix search (finding trademarks that start with your search term) instead of an exact match:
  ```python
  data = {
      "searchText": name,
      "options": {
          "searchType": "PREFIX_SEARCH",  # Change from EXACT_SEARCH
          # ... other options remain the same
      }
  }
  ```

- To perform a suffix search (finding trademarks that end with your search term):
  ```python
  data = {
      "searchText": name,
      "options": {
          "searchType": "SUFFIX_SEARCH",  # Change from EXACT_SEARCH
          # ... other options remain the same
      }
  }
  ```

### Understanding Results

The script creates a directory structure in your project folder:
- `uspto_results/` - Base directory for all results
  - `{trademark_name}_{timestamp}/` - Directory for each trademark search
    - `analysis.json` - Analysis of potential conflicts
    - `search_results.json` - Raw search results from the USPTO API
  - `summary_report_{timestamp}.txt` - A human-readable summary of all search results

### Interpreting Conflicts

A trademark is considered a potential conflict if:
1. It matches or is similar to your search term
2. It has a status of "LIVE" or "PENDING"

When reviewing results, pay special attention to:
- Marks in similar goods/services classes
- Marks with visual or phonetic similarities
- Recently registered marks

## Troubleshooting

If you encounter issues:

1. **API Rate Limiting**: If you receive HTTP 429 errors, the script may be hitting rate limits. Increase the `time.sleep()` duration in the `process_trademark_names` method.

2. **Network Issues**: Ensure you have a stable internet connection. The script requires access to the USPTO's API.

3. **JSON Parsing Errors**: If the API returns unexpected data formats, check the USPTO documentation for any API changes.

## Note on Legal Advice

This tool provides informational results only and should not be considered legal advice. For definitive trademark clearance, consult with a qualified trademark attorney who can provide a comprehensive analysis.

## Next Steps

After identifying potential conflicts:
1. Review the detailed information for each conflict
2. Consider consulting a trademark attorney for professional guidance
3. Explore alternative trademark names if significant conflicts exist
4. For marks with minimal conflicts, consider proceeding with formal trademark application

## Resources

- [USPTO TSDR API Documentation](https://developer.uspto.gov/ibd-api/swagger-ui.html)
- [USPTO Trademark Basics](https://www.uspto.gov/trademarks/basics)
- [USPTO Trademark Search](https://tmsearch.uspto.gov/)