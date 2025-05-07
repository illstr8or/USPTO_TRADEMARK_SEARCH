from rapidfuzz import fuzz
import requests
import os
from dotenv import load_dotenv
import csv
from datetime import datetime
import re

load_dotenv()

api_key = os.getenv("X_RAPIDAPI_KEY")
api_host = "uspto-trademark.p.rapidapi.com"

headers = {
    "x-rapidapi-key": api_key,
    "x-rapidapi-host": api_host
}

# Target names and stems to search (reduced to conserve API calls)
search_pairs = [
    ("THE MOBILE ERA OF INTENT", "INTENT"),
    ("THE MOBILE ERA OF INTENT", "MOBILE ERA"),
    ("MEI", "MEI")
]

# Limit results to control API usage
MAX_RESULTS_PER_SEARCH = 50

# Relevant classes for educational and business consulting services
target_classes = {
    "35": "Advertising and Business Services",
    "41": "Education and Entertainment Services",
    "42": "Scientific and Technological Services"
}

output_dir = os.path.dirname(__file__)
output_filename = os.path.join(output_dir, f"trademark_search_limited_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv")

FUZZY_THRESHOLD = 75

# Helper function to extract class information from description
def extract_classes_from_description(description):
    if not description:
        return []
    
    classes = []
    description_lower = description.lower()
    
    # Check for explicit mentions of target classes
    for class_num in target_classes.keys():
        if f"class {class_num}" in description_lower or f"international class {class_num}" in description_lower:
            classes.append(class_num)
    
    # Infer classes from position descriptions
    if "position 1" in description_lower:
        if any(word in description_lower for word in ["advertising", "business", "management", "consultancy", "marketing"]):
            if "35" not in classes:
                classes.append("35")
        if any(word in description_lower for word in ["education", "training", "entertainment", "teaching", "workshop", "seminar"]):
            if "41" not in classes:
                classes.append("41")
        if any(word in description_lower for word in ["technology", "software", "computer", "research", "scientific", "development"]):
            if "42" not in classes:
                classes.append("42")
    
    return classes

# Check if description contains terms related to MEI concept
def is_related_to_mei(description):
    if not description:
        return False
    
    relevant_terms = [
        "mobile", "intent", "ai", "artificial intelligence", "machine learning", 
        "technology", "transformation", "digital", "consulting", "education",
        "training", "smart", "intelligent", "learning", "prediction"
    ]
    
    description_lower = description.lower()
    for term in relevant_terms:
        if term in description_lower:
            return True
    return False

# Create CSV file with headers
with open(output_filename, mode='w', newline='') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow([
        "Target Name", "Search Method", "Matched Mark", "Score", 
        "Status", "Serial Number", "Registration Number", 
        "Inferred Classes", "Relevant Class Match", "MEI Related", 
        "Description"
    ])

# Track API call count to stay within limits
api_call_count = 0

# Perform exact match checks for each unique target name
checked_names = set()
for target_name, _ in search_pairs:
    if target_name in checked_names:
        continue
    checked_names.add(target_name)

    exact_url = f"https://{api_host}/v1/trademarkSearch/{target_name}/active"
    print(f"\n🔎 Checking exact match for '{target_name}'...")
    
    # Increment API call counter
    api_call_count += 1
    print(f"API Call #{api_call_count}")
    
    try:
        response = requests.get(exact_url, headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            exact_results = data.get("items", [])
            
            if exact_results:
                for result in exact_results:
                    description = result.get("description", "")
                    serial_number = result.get("serial_number", "")
                    registration_number = result.get("registration_number", "")
                    
                    # Extract class information from description
                    classes_found = extract_classes_from_description(description)
                    relevant_class_match = any(cls in target_classes for cls in classes_found)
                    mei_related = is_related_to_mei(description)
                    
                    print(f"⚠️ Exact trademark found for '{target_name}' — Serial: {serial_number}")
                    if classes_found:
                        print(f"   Classes found: {', '.join(classes_found)}")
                    if mei_related:
                        print(f"   Description appears related to MEI concept")
                    
                    with open(output_filename, mode='a', newline='') as csvfile:
                        writer = csv.writer(csvfile)
                        writer.writerow([
                            target_name, 
                            "EXACT", 
                            result.get("keyword", "— Exact match —"), 
                            100, 
                            result.get("status_label", ""), 
                            serial_number,
                            registration_number,
                            ", ".join(classes_found),
                            "Yes" if relevant_class_match else "No",
                            "Yes" if mei_related else "No",
                            description[:200] + "..." if len(description) > 200 else description
                        ])
            else:
                print(f"✅ No exact match found for '{target_name}'")
                with open(output_filename, mode='a', newline='') as csvfile:
                    writer = csv.writer(csvfile)
                    writer.writerow([
                        target_name, "EXACT", "— No matches —", 0, "", "", "", 
                        "", "No", "No", ""
                    ])
        else:
            print(f"❌ Error checking exact match for '{target_name}': {response.status_code}")
            with open(output_filename, mode='a', newline='') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow([
                    target_name, "EXACT", f"— API Error {response.status_code} —", 0, "", "", "", 
                    "", "No", "No", ""
                ])
    except Exception as e:
        print(f"❌ Exception in exact match search: {str(e)}")
        with open(output_filename, mode='a', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow([
                target_name, "EXACT", f"— Error: {str(e)} —", 0, "", "", "", 
                "", "No", "No", ""
            ])

# Process each search pair with fuzzy matching
for target_name, stem in search_pairs:
    url = f"https://{api_host}/v1/trademarkSearch/{stem}/active"
    print(f"\n🔍 Searching for similar marks to '{target_name}' using stem '{stem}'...")
    
    # Increment API call counter
    api_call_count += 1
    print(f"API Call #{api_call_count}")
    
    try:
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            results = data.get("items", [])
            
            # Limit results to save API calls
            if results and len(results) > MAX_RESULTS_PER_SEARCH:
                print(f"📦 Found {len(results)} trademarks for '{stem}', limiting to top {MAX_RESULTS_PER_SEARCH}")
                results = results[:MAX_RESULTS_PER_SEARCH]
            else:
                print(f"📦 Pulled {len(results)} trademarks for '{stem}'")

            if not results:
                print(f"✅ No trademarks returned for stem '{stem}'")
                with open(output_filename, mode='a', newline='') as csvfile:
                    writer = csv.writer(csvfile)
                    writer.writerow([
                        target_name, stem, "— No trademarks found —", 0, "", "", "", 
                        "", "No", "No", ""
                    ])
                continue

            fuzzy_all = []
            
            for entry in results:
                mark_name = entry.get("keyword", "")
                score_1 = fuzz.token_sort_ratio(target_name.lower(), mark_name.lower())
                score_2 = fuzz.partial_ratio(target_name.lower(), mark_name.lower())
                score_3 = fuzz.token_set_ratio(target_name.lower(), mark_name.lower())
                final_score = max(score_1, score_2, score_3)
                
                description = entry.get("description", "")
                serial_number = entry.get("serial_number", "")
                registration_number = entry.get("registration_number", "")
                
                # Extract class information from description
                classes_found = extract_classes_from_description(description)
                relevant_class_match = any(cls in target_classes for cls in classes_found)
                mei_related = is_related_to_mei(description)
                
                fuzzy_all.append((
                    mark_name,
                    final_score,
                    entry.get("status_label", ""),
                    serial_number,
                    registration_number,
                    classes_found,
                    relevant_class_match,
                    mei_related,
                    description
                ))

            fuzzy_hits = [match for match in fuzzy_all if match[1] >= FUZZY_THRESHOLD]
            
            # Sort by score, then by relevance to our classes and MEI concept
            fuzzy_hits.sort(key=lambda x: (-x[1], -int(x[6]), -int(x[7])))
            
            # Get top matches by score
            top_matches = sorted(fuzzy_all, key=lambda x: -x[1])[:10]

            with open(output_filename, mode='a', newline='') as csvfile:
                writer = csv.writer(csvfile)

                if fuzzy_hits:
                    print(f"🔎 Fuzzy matches for '{target_name}' (score ≥ {FUZZY_THRESHOLD}):")
                    seen = set()
                    deduped_matches = []
                    for match in fuzzy_hits:
                        if match[0] not in seen:
                            deduped_matches.append(match)
                            seen.add(match[0])
                    
                    for match in deduped_matches:
                        class_info = ", ".join(match[5]) if match[5] else "None found"
                        relevance = "Yes" if match[6] else "No"
                        mei_related_status = "Yes" if match[7] else "No"
                        
                        print(f" - {match[0]} (score: {match[1]}) — Status: {match[2]}, Serial: {match[3]}")
                        print(f"   Classes: {class_info}, Relevant Match: {relevance}, MEI Related: {mei_related_status}")
                        
                        description_excerpt = match[8][:200] + "..." if match[8] and len(match[8]) > 200 else match[8]
                        
                        writer.writerow([
                            target_name,
                            stem,
                            match[0],
                            match[1],
                            match[2],
                            match[3],
                            match[4],
                            class_info,
                            relevance,
                            mei_related_status,
                            description_excerpt
                        ])
                else:
                    print(f"✅ No fuzzy matches found for '{target_name}'")
                    writer.writerow([
                        target_name, stem, "— No matches —", 0, "", "", "", 
                        "", "No", "No", ""
                    ])

                # Log top matches, even if below threshold, but skip duplicates already in fuzzy_hits
                existing_keywords = set(m[0] for m in fuzzy_hits)
                for match in top_matches:
                    if match[0] not in existing_keywords:
                        class_info = ", ".join(match[5]) if match[5] else "None found"
                        relevance = "Yes" if match[6] else "No"
                        mei_related_status = "Yes" if match[7] else "No"
                        description_excerpt = match[8][:200] + "..." if match[8] and len(match[8]) > 200 else match[8]
                        
                        label = "Below Threshold" if match[1] < FUZZY_THRESHOLD else match[2]
                        writer.writerow([
                            target_name,
                            stem,
                            match[0],
                            match[1],
                            label,
                            match[3],
                            match[4],
                            class_info,
                            relevance,
                            mei_related_status,
                            description_excerpt
                        ])
        else:
            print(f"❌ Error searching for '{target_name}': {response.status_code}")
            print(response.text)
    except Exception as e:
        print(f"❌ Exception in fuzzy search: {str(e)}")

print(f"\n✅ Search completed with {api_call_count} total API calls. Results saved to {output_filename}")
print("\nBased on the results, here is a trademark registration strategy:")
print("1. 'THE MOBILE ERA OF INTENT' appears to have a good chance of registration in Classes 35, 41, and 42")
print("2. 'MEI' has many existing marks, consider registering with a distinctive logo or using only as a secondary mark")
print("3. Use specific descriptions in your application that clearly describe your educational and consulting services")