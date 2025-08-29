import streamlit as st
import pandas as pd
from domain_utils import (
    check_availability,
    get_traffic,
    get_backlinks,
    logger,
)

st.title("Domain Checker 2.0")

uploaded_file = st.file_uploader("Upload CSV", type="csv")
if uploaded_file:
    # Attempt to read CSV with optional header
    df = pd.read_csv(uploaded_file)
    if len(df.columns) != 1 or df.columns[0].strip().lower() != "domain":
        uploaded_file.seek(0)
        df = pd.read_csv(uploaded_file, header=None, names=["domain"])
    else:
        df = df[["domain"]]
    df = df.dropna(subset=["domain"])
    df["domain"] = df["domain"].astype(str).str.strip()
    df = df[df["domain"] != ""]
    results = []
    progress = st.progress(0)
    status_placeholder = st.empty()
    total = len(df)
    for idx, domain in enumerate(df["domain"], start=1):
        status_placeholder.text(f"Checking {idx}/{total}: {domain}")

        # Determine availability first.  Free domains should not have any
        # measurable traffic or backlinks, so we avoid querying external
        # services for them.
        available = check_availability(domain)
        if available is None:
            availability_status = "unbekannt"
            traffic = 0
            backlinks = 0
        elif available:
            availability_status = "frei"
            traffic = 0
            backlinks = 0
        else:
            availability_status = "vergeben"
            traffic = get_traffic(domain)
            backlinks = get_backlinks(domain)

        logger.info(
            "Finished %s: available=%s, traffic=%s, backlinks=%s",
            domain,
            availability_status,
            traffic,
            backlinks,
        )
        results.append({
            "domain": domain,
            "available": availability_status,
            "traffic": traffic,
            "backlinks": backlinks,
        })
        progress.progress(idx / total)
    result_df = pd.DataFrame(results).fillna("N/A")
    st.dataframe(result_df)
    csv = result_df.to_csv(index=False).encode("utf-8")
    st.download_button("Download Results CSV", data=csv, file_name="domain_results.csv", mime="text/csv")
    logger.info("Completed processing %d domains", total)
