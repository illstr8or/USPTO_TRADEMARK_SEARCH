import streamlit as st
import pandas as pd

st.set_page_config(page_title="Trademark Search Dashboard", layout="wide")

st.title("🛡️ USPTO Trademark Search Dashboard")

# Upload CSV
uploaded_file = st.file_uploader("Upload your trademark search CSV", type=["csv"])

if uploaded_file:
    df = pd.read_csv(uploaded_file)
    df.columns = df.columns.str.strip().str.lower()
    df["search stem"] = df["search stem"].str.strip().str.lower()
    # st.write("Columns loaded:", list(df.columns))
    df["score"] = pd.to_numeric(df["score"], errors="coerce")

    # Clean up missing values in string columns only
    for col in df.select_dtypes(include="object").columns:
        df[col] = df[col].fillna("")

    st.subheader("📊 Summary Table")

    # Determine unique Target Names
    target_names = df["target name"].unique()

    # Initialize result dictionary
    summary_rows = []

    for name in target_names:
        df_name = df[df["target name"] == name]
        has_exact = any(
            (df_name["search stem"] == "exact") & (df_name["matched mark"] != "— No matches —")
        )
        has_fuzzy = any((df_name["search stem"] != "exact") & (df_name["score"] >= 75))
        score_row = df_name[df_name["search stem"] == "exact"]
        top_score = float(score_row["score"].iloc[0]) if not score_row.empty else 0.0

        if has_exact:
            verdict = "❌ Blocked"
        elif has_fuzzy:
            verdict = "⚠️ Risk"
        else:
            verdict = "✅ Clear"

        summary_rows.append({
            "Target Name": name,
            "Exact Match": "✅" if has_exact else "",
            "Fuzzy Hit": "✅" if has_fuzzy else "",
            "Exact Match Score": top_score,
            "Verdict": verdict
        })

    summary_table = pd.DataFrame(summary_rows)

    st.dataframe(summary_table)

    st.subheader("🔍 Full Match Details")
    fuzzy_filter = st.checkbox("Show only fuzzy matches (score ≥ 75)", value=True)
    if fuzzy_filter:
        display_df = df[(df["score"] >= 75) & (df["search stem"] != "exact")]
    else:
        display_df = df.copy()
    st.dataframe(display_df)

    st.subheader("📥 Download Filtered Data")
    st.download_button("Download CSV", display_df.to_csv(index=False), "filtered_results.csv")
else:
    st.info("Upload your CSV file to begin.")
