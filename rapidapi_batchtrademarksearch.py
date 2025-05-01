from rapidfuzz import fuzz
import requests
import os
from dotenv import load_dotenv
import csv
from datetime import datetime

load_dotenv()

api_key = os.getenv("X_RAPIDAPI_KEY")
api_host = "uspto-trademark.p.rapidapi.com"

headers = {
    "x-rapidapi-key": api_key,
    "x-rapidapi-host": api_host
}

# (target_name, broader_stem_to_search)
search_pairs = [
    ("LEAPWISE", "LEAP"),
    ("LEAPWISE", "WISE"),
    ("LEAPWORKS", "LEAP"),
    ("LEAPWORKS", "WORKS"),
    ("SPRINGIFY", "SPRING"),
    ("SPRYNOVA", "SPRY"),
    ("STRIDEON", "STRIDE"),
    ("MOBILE ERA OF INTENT", "MOBILE"),
    ("MOBILE ERA OF INTENT", "INTENT"),
    ("MOBILE ERA OF INTENT", "ERA"),
    ("EXPERIENCE CONTINUITY", "EXPERIENCE"),
    ("EXPERIENCE CONTINUITY", "CONTINUITY"),
    ("SPRYNETIC", "SPRY")
]

output_dir = os.path.dirname(__file__)
output_filename = os.path.join(output_dir, f"trademark_fuzzy_matches_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv")
with open(output_filename, mode='w', newline='') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(["Target Name", "Search Stem", "Matched Mark", "Score", "Status", "Serial Number"])

FUZZY_THRESHOLD = 75

for target_name, stem in search_pairs:
    url = f"https://{api_host}/v1/trademarkSearch/{stem}/active"
    print(f"\n🔍 Searching for similar marks to '{target_name}' using stem '{stem}'...")
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        data = response.json()
        results = data.get("items", [])
        print(f"📦 Pulled {len(results)} trademarks for '{stem}'")

        fuzzy_hits = []
        for entry in results:
            mark_name = entry.get("keyword", "")
            score = fuzz.token_sort_ratio(target_name.lower(), mark_name.lower())
            if score >= FUZZY_THRESHOLD:
                fuzzy_hits.append((mark_name, score, entry.get("status_label"), entry.get("serial_number")))

        if fuzzy_hits:
            print(f"🔎 Fuzzy matches for '{target_name}' (score ≥ {FUZZY_THRESHOLD}):")
            with open(output_filename, mode='a', newline='') as csvfile:
                writer = csv.writer(csvfile)
                for match in sorted(fuzzy_hits, key=lambda x: -x[1]):
                    print(f" - {match[0]} (score: {match[1]}) — Status: {match[2]}, Serial: {match[3]}")
                    writer.writerow([target_name, stem, match[0], match[1], match[2], match[3]])
        else:
            print(f"✅ No fuzzy matches found for '{target_name}'")
    else:
        print(f"❌ Error searching for '{target_name}': {response.status_code}")
        print(response.text)