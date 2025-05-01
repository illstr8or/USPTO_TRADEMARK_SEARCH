
import streamlit as st
import pandas as pd

st.set_page_config(page_title="Trademark Search Dashboard", layout="wide")

st.title("🛡️ USPTO Trademark Search Dashboard")

# Upload CSV
uploaded_file = st.file_uploader("Upload your trademark search CSV", type=["csv"])

if uploaded_file:
    df = pd.read_csv(uploaded_file)

    # Clean up missing values
    df.fillna("", inplace=True)
    df.columns = [col.strip() for col in df.columns]

    st.subheader("📊 Summary Table")

    # Group-level boolean flags
    exact_match = df[df["Search Stem"] == "EXACT"].groupby("Target Name").size() > 0
    fuzzy_match = df[(df["Search Stem"] != "EXACT") & (df["Score"] >= 75)].groupby("Target Name").size() > 0
    max_score = df.groupby("Target Name")["Score"].max()

    summary_table = pd.DataFrame({
        "Exact Match": exact_match,
        "Fuzzy Hit": fuzzy_match,
        "Top Score": max_score
    }).fillna(False).reset_index()

    def verdict(row):
        if row["Exact Match"]:
            return "❌ Blocked"
        elif row["Fuzzy Hit"]:
            return "⚠️ Risk"
        else:
            return "✅ Clear"

    summary_table["Verdict"] = summary_table.apply(verdict, axis=1)
    st.dataframe(summary_table)

    st.subheader("🔍 Full Match Details")
    fuzzy_filter = st.checkbox("Show only fuzzy matches (score ≥ 75)", value=True)
    if fuzzy_filter:
        display_df = df[(df["Score"] >= 75) & (df["Search Stem"] != "EXACT")]
    else:
        display_df = df.copy()
    st.dataframe(display_df)

    st.subheader("📥 Download Filtered Data")
    st.download_button("Download CSV", display_df.to_csv(index=False), "filtered_results.csv")
else:
    st.info("Upload your CSV file to begin.")
