"""Annual Report Analyzer: Upload PDF and get instant forensic red flag scan."""

import streamlit as st
import sys
from pathlib import Path
from io import BytesIO

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from core.pdf_parser import extract_text_pypdf2, extract_tables, extract_sections, search_for_red_flags

st.set_page_config(page_title="Report Analyzer", page_icon="📄", layout="wide")
st.title("Annual Report Analyzer")
st.caption("Upload any annual report PDF for instant forensic red flag scanning and section extraction.")

uploaded_file = st.file_uploader("Upload Annual Report (PDF)", type=["pdf"], help="Works best with Indian company annual reports")

if uploaded_file:
    file_bytes = BytesIO(uploaded_file.read())
    file_size_mb = len(file_bytes.getvalue()) / (1024 * 1024)
    st.info(f"File: {uploaded_file.name} | Size: {file_size_mb:.1f} MB")

    with st.spinner("Extracting text from PDF..."):
        text = extract_text_pypdf2(file_bytes)

    st.success(f"Extracted {len(text):,} characters from PDF")

    tab1, tab2, tab3, tab4 = st.tabs(["Red Flag Scan", "Section Analysis", "Table Extraction", "Full Text Search"])

    with tab1:
        st.subheader("Automated Red Flag Scan")
        with st.spinner("Scanning for red flags..."):
            flags = search_for_red_flags(text)

        if flags:
            # Summary metrics
            col1, col2, col3 = st.columns(3)
            high_sev = len([f for f in flags if f["severity"] >= 4])
            med_sev = len([f for f in flags if f["severity"] == 3])
            low_sev = len([f for f in flags if f["severity"] <= 2])
            col1.metric("High Severity", high_sev)
            col2.metric("Medium Severity", med_sev)
            col3.metric("Low Severity", low_sev)

            total_score = sum(f["severity"] * f["count"] for f in flags)
            risk_level = "Low" if total_score < 20 else "Medium" if total_score < 50 else "High" if total_score < 100 else "Critical"
            risk_color = {"Low": "green", "Medium": "orange", "High": "red", "Critical": "red"}[risk_level]
            st.markdown(f"### Aggregate Risk: :{risk_color}[{risk_level}] (Score: {total_score})")

            st.divider()

            for flag in flags:
                severity_bar = "🔴" * flag["severity"] + "⚪" * (5 - flag["severity"])
                with st.expander(f"{severity_bar} **{flag['label']}** ({flag['count']} occurrences)"):
                    for j, ctx in enumerate(flag["contexts"]):
                        st.markdown(f"**Context {j+1}:** ...{ctx}...")
                    st.caption(f"Severity: {flag['severity']}/5 | Total occurrences: {flag['count']}")
        else:
            st.success("No red flag keywords detected. Note: this is a keyword-based scan -- manual review is still recommended.")

    with tab2:
        st.subheader("Key Sections Extracted")
        with st.spinner("Extracting sections..."):
            sections = extract_sections(text)

        if sections:
            section_labels = {
                "directors_report": "Director's Report",
                "mda": "Management Discussion & Analysis",
                "auditors_report": "Auditor's Report",
                "related_party": "Related Party Transactions",
                "contingent_liabilities": "Contingent Liabilities",
                "cash_flow": "Cash Flow Statement",
                "notes_to_accounts": "Notes to Accounts",
                "corporate_governance": "Corporate Governance",
                "shareholding_pattern": "Shareholding Pattern",
                "remuneration": "Remuneration Details",
                "csr": "CSR Report",
            }
            found = []
            not_found = []
            for key, label in section_labels.items():
                if key in sections:
                    found.append((key, label))
                else:
                    not_found.append(label)

            col1, col2 = st.columns([3, 1])
            with col2:
                st.markdown("**Sections Found:**")
                for _, label in found:
                    st.markdown(f"- :green[{label}]")
                if not_found:
                    st.markdown("**Not Found:**")
                    for label in not_found:
                        st.markdown(f"- :red[{label}]")

            with col1:
                for key, label in found:
                    with st.expander(f"{label}", expanded=False):
                        st.text(sections[key][:3000])
        else:
            st.warning("Could not identify standard sections. The PDF may have non-standard formatting.")

    with tab3:
        st.subheader("Table Extraction")
        st.caption("Extract tables from specific pages of the PDF.")
        page_range = st.text_input("Pages to extract (e.g., 1-10, 15, 20-25)", "1-5")

        if st.button("Extract Tables"):
            # Parse page range
            pages = []
            for part in page_range.split(","):
                part = part.strip()
                if "-" in part:
                    start, end = part.split("-")
                    pages.extend(range(int(start) - 1, int(end)))
                else:
                    pages.append(int(part) - 1)

            file_bytes.seek(0)
            with st.spinner("Extracting tables..."):
                tables = extract_tables(file_bytes, pages)

            if tables:
                for i, table in enumerate(tables):
                    with st.expander(f"Table {i+1} (Page {table['page']})", expanded=(i < 3)):
                        try:
                            df = pd.DataFrame(table["rows"], columns=table["headers"])
                            st.dataframe(df, use_container_width=True)
                        except Exception:
                            st.text(str(table["rows"][:5]))
            else:
                st.info("No tables found on the specified pages.")

    with tab4:
        st.subheader("Full Text Search")
        search_term = st.text_input("Search in annual report", placeholder="e.g., related party, pledge, derivative")
        if search_term:
            import re
            matches = list(re.finditer(re.escape(search_term), text, re.IGNORECASE))
            st.markdown(f"Found **{len(matches)}** occurrences")
            for i, m in enumerate(matches[:20]):
                start = max(0, m.start() - 200)
                end = min(len(text), m.end() + 200)
                context = text[start:end].replace("\n", " ")
                highlighted = context.replace(search_term, f"**{search_term}**")
                st.markdown(f"**{i+1}.** ...{highlighted}...")
                st.divider()
            if len(matches) > 20:
                st.caption(f"Showing first 20 of {len(matches)} results.")

    # Download extracted text
    st.sidebar.download_button(
        "Download Extracted Text",
        text,
        file_name=f"{uploaded_file.name.replace('.pdf', '')}_extracted.txt",
        mime="text/plain",
    )

else:
    st.info("Upload an annual report PDF to begin analysis.")
    st.markdown("""
    ### What this tool does:
    1. **Red Flag Scan** -- Searches for 19 forensic red flag keywords (pledging, defaults, fraud, derivatives, etc.)
    2. **Section Extraction** -- Identifies key sections (Director's Report, Auditor's Report, Related Party, etc.)
    3. **Table Extraction** -- Pulls tabular data from specified pages
    4. **Full Text Search** -- Search for any term across the entire document

    ### Tips for best results:
    - Use digitally-generated PDFs (not scanned images)
    - Indian company annual reports from BSE/NSE work best
    - Combine with the Company Screener for quantitative analysis
    """)

import pandas as pd
