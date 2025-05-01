# USPTO Trademark Search Tool

This Python tool allows you to perform batch trademark name analysis using the USPTO’s trademark database via RapidAPI. It includes fuzzy matching logic to help identify potentially conflicting or similar trademarks based on keyword stems and brand name intent.

---

## ✅ Features

- 🔍 Batch-check potential trademarks via keyword stem search
- 🤖 Fuzzy match using `rapidfuzz` to find similar or lookalike names
- 📊 Outputs results to both terminal and CSV for analysis
- ⚡ Lightweight, fast, and customizable — ideal for early-stage naming research

---

## 📦 Requirements

- Python 3.8+
- RapidAPI account with access to [`uspto-trademark`](https://rapidapi.com/jaredcwilson/api/uspto-trademark/)
- Internet connection

---

## 🔧 Setup

### 1. Clone the repo

```bash
git clone https://github.com/illstr8or/USPTO_TRADEMARK_SEARCH.git
cd USPTO_TRADEMARK_SEARCH
```

### 2. Create and activate a virtual environment (optional but recommended)

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

Or manually:

```bash
pip install requests python-dotenv rapidfuzz
```

### 4. Create a `.env` file with your API key

```env
X_RAPIDAPI_KEY=your-rapidapi-key-here
```

---

## 🧠 How It Works

The tool takes a list of brand names and matches each against broader **stem keywords** (e.g., `"LEAPWISE"` vs. `"LEAP"` and `"WISE"`). It queries the USPTO API, pulls up to 250 trademarks per stem, and then uses `rapidfuzz` to compare your brand name to each trademark's name.

---

## ✏️ Customization

Edit the `search_pairs` list in `rapidapi_batchtrademarksearch.py` to define your desired names and stems:

```python
search_pairs = [
    ("LEAPWISE", "LEAP"),
    ("LEAPWISE", "WISE"),
    ("SPRINGIFY", "SPRING"),
    ("STRIDEON", "STRIDE"),
]
```

You can set your **fuzzy match threshold** like so:

```python
FUZZY_THRESHOLD = 75
```

---

## 🚀 Running the Script

```bash
python rapidapi_batchtrademarksearch.py
```

You’ll see output like this in your terminal:

```
🔍 Searching for similar marks to 'LEAPWISE' using stem 'LEAP'...
📦 Pulled 250 trademarks for 'LEAP'
🔎 Fuzzy matches for 'LEAPWISE':
 - LEAPWIT (score: 80.0) — Status: Live/Registered, Serial: 90291861
```

And a timestamped CSV will be created like:

```
trademark_fuzzy_matches_20250430_121530.csv
```

---

## 📊 Streamlit Dashboard

You can also explore your results using the included dashboard:

```bash
streamlit run trademark_dashboard_fixed.py
```

This dashboard allows you to:
- View fuzzy match verdicts at a glance (✅ Clear, ⚠️ Risk, ❌ Blocked)
- Filter and sort based on match type and confidence
- Share screenshots or deploy it for collaborators

To deploy publicly via Streamlit Cloud, make sure your repo includes:
- This `README.md`
- A `requirements.txt` file with `streamlit`, `pandas`, and `requests` listed
- Your dashboard file (e.g., `trademark_dashboard_fixed.py`)

---

## 🗂 Example CSV Output

| Target Name | Search Stem | Matched Mark | Score | Status          | Serial Number |
|-------------|-------------|---------------|-------|------------------|----------------|
| LEAPWISE    | LEAP        | LEAPWIT       | 80.0  | Live/Registered | 90291861       |
| STRIDEON    | STRIDE      | STRIDER       | 80.0  | Live/Registered | 87708995       |

---

## 🛡 Recommended .gitignore

```gitignore
# Python
*.pyc
__pycache__/
.env
*.csv
venv/
.vscode/
```

---

## 🧪 Future Ideas

- Class code filtering (e.g., only tech/education trademarks)
- Merge active + inactive trademark pools
- Web-based UI with search history
- Phonetic matching (e.g., Metaphone or Soundex)
- Batch export across mark categories

---

## 📘 Disclaimer

This tool is provided for exploratory research only and **does not constitute legal advice**. Always consult a trademark attorney before filing or investing in a brand name.

---

## 📝 License

MIT License © 2025 [@illstr8or](https://github.com/illstr8or)
