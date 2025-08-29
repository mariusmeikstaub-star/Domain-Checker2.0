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
    df = pd.read_csv(uploaded_file, header=None, names=["domain"])
    df = df.dropna(subset=["domain"])
    df["domain"] = df["domain"].astype(str).str.strip()
    df = df[df["domain"] != ""]
    results = []
    progress = st.progress(0)
    status_placeholder = st.empty()
    total = len(df)
    for idx, domain in enumerate(df["domain"], start=1):
        status_placeholder.text(f"Checking {idx}/{total}: {domain}")
        traffic = get_traffic(domain)
        backlinks = get_backlinks(domain)
        available = check_availability(domain)
        logger.info(
            "Finished %s: available=%s, traffic=%s, backlinks=%s",
            domain,
            available,
            traffic,
            backlinks,
        )
        results.append({
            "domain": domain,
            "available": available,
            "traffic": traffic,
            "backlinks": backlinks,
        })
        progress.progress(idx / total)
    result_df = pd.DataFrame(results).fillna("N/A")
    st.dataframe(result_df)
    csv = result_df.to_csv(index=False).encode("utf-8")
    st.download_button("Download Results CSV", data=csv, file_name="domain_results.csv", mime="text/csv")
    logger.info("Completed processing %d domains", total)
