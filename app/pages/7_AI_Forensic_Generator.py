"""
AI Forensic Generator: Say a company name, get full forensic analysis.

Hybrid AI: Claude CLI (primary) + Ollama (fallback)
Data: RAG knowledge base + Annual Report extractions from D:\\Annual_report_extract
"""

import streamlit as st
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from core.llm_engine import query, get_available_providers, query_streaming
from core.rag_engine import RAGEngine
from core.annual_report_loader import (
    list_available_companies,
    load_extractions,
    get_all_extracted_json,
    load_annual_report_pdf_path,
)
from core.forensic_analyzer import FinancialData, analyze
from core.pdf_parser import extract_text_pypdf2, search_for_red_flags

st.set_page_config(page_title="AI Forensic Generator", page_icon="🧠", layout="wide")
st.title("AI Forensic Generator")
st.caption("Say a company name. Get full forensic analysis powered by Claude CLI + Ollama + Knowledge Base + Annual Reports.")

# --- Sidebar: Provider Status ---
with st.sidebar:
    st.subheader("AI Provider Status")
    providers = get_available_providers()

    if providers["claude_cli"]:
        st.success("Claude CLI: Available")
    else:
        st.warning("Claude CLI: Not available")

    if providers["ollama"]:
        st.success(f"Ollama: Available ({len(providers['ollama_models'])} models)")
        ollama_model = st.selectbox(
            "Ollama Model",
            providers["ollama_models"],
            index=0 if providers["ollama_models"] else 0,
        )
    else:
        st.warning("Ollama: Not running")
        ollama_model = None

    ai_preference = st.radio(
        "AI Provider Preference",
        ["Auto (Claude → Ollama)", "Claude CLI only", "Ollama only"],
        index=0,
    )
    prefer_map = {
        "Auto (Claude → Ollama)": "auto",
        "Claude CLI only": "claude",
        "Ollama only": "ollama",
    }

    st.divider()

    # RAG status
    st.subheader("Knowledge Base")
    rag = RAGEngine()
    try:
        rag.initialize()
        kb_count = rag.collection.count()
        st.metric("Indexed Chunks", kb_count)
        if kb_count == 0:
            if st.button("Index Knowledge Base"):
                with st.spinner("Indexing..."):
                    rag.index_knowledge_base(force=True)
                st.rerun()
    except Exception as e:
        st.error(f"RAG error: {e}")
        kb_count = 0

    st.divider()

    # Available companies from Annual Report Extract
    st.subheader("Extracted Annual Reports")
    companies = list_available_companies()
    if companies:
        st.metric("Companies Available", len(companies))
        for c in companies:
            st.caption(f"ID {c['id']}: {c['name']} ({', '.join(c['years'])})")
    else:
        st.caption("No extracted data found in D:\\Annual_report_extract")

# --- SYSTEM PROMPT ---
FORENSIC_SYSTEM_PROMPT = """You are an expert forensic accountant trained in Dr. Vijay Malik's "Peaceful Investing" methodology.
You have analyzed 80+ Indian companies and identified 74 distinct red flag patterns across 5 categories.

Your analysis framework covers 5 pillars:
1. FINANCIAL: Sales growth, OPM stability, cCFO vs cPAT, FCF, debt trajectory
2. EFFICIENCY: NFAT (Net Fixed Asset Turnover), ITR, Receivables Days
3. MARGIN OF SAFETY: SSGR vs actual growth, FCF quality
4. VALUATION: P/E margin of safety, earnings yield vs G-Sec rate
5. MANAGEMENT: Promoter salary, related party transactions, governance quality

You must compare findings against these known fraud patterns:
- Pattern 1: Trinity (Rising Sales + Rising Receivables + Rising Debt)
- Pattern 2: Credit Rating Shopping (switching agencies after downgrade)
- Pattern 3: Circular Shareholding (company funds used to buy own shares via promoter entities)
- Pattern 4: Vicious Cycle (high promoter salary -> cash shortfall -> promoter loans at high interest)
- Pattern 5: Pre-Event Extraction (large dividends before IPO/stake sale)
- Pattern 6: Accounting Gymnastics (revaluation, capitalization of expenses, depreciation method changes)
- Pattern 7: Unsustainable Growth (SSGR << actual growth, debt-funded)

Always provide:
- Specific numbers and calculations
- Red flags with severity (1-5) and evidence
- Green flags where present
- Pattern match scores (0-10 for each of 7 patterns)
- Overall Risk Score (0-50) and Verdict (Invest/Monitor/Avoid)
- Comparison to similar companies from the knowledge base where relevant"""


# --- Main Interface ---
tab_company, tab_custom = st.tabs(["Company from Annual Reports", "Custom Company Query"])

with tab_company:
    st.subheader("Analyze an Extracted Company")

    if companies:
        selected_company = st.selectbox(
            "Select Company",
            companies,
            format_func=lambda c: f"{c['name']} (ID: {c['id']}, Years: {', '.join(c['years'])})",
        )

        year = st.selectbox("Year", selected_company["years"], index=len(selected_company["years"]) - 1)
        qualifier = st.radio("Statement Type", ["standalone", "consolidated"], horizontal=True)

        if st.button("Run Full Forensic Analysis", type="primary", use_container_width=True, key="run_extracted"):
            company_id = selected_company["id"]
            company_name = selected_company["name"]

            # Step 1: Load extracted financial data
            with st.status("Loading extracted financial data...", expanded=True) as status:
                st.write("Reading extracted annual report data...")
                financials = load_extractions(company_id, year, qualifier)

                st.write(f"**Revenue:** {financials.revenue:,.0f} {financials.unit}")
                st.write(f"**PAT:** {financials.pat:,.0f} {financials.unit}")
                st.write(f"**CFO:** {financials.cfo:,.0f} {financials.unit}")
                st.write(f"**Net Fixed Assets:** {financials.net_fixed_assets:,.0f} {financials.unit}")
                st.write(f"**Total Debt:** {financials.total_debt:,.0f} {financials.unit}")

                # Get all JSONs for context
                all_data = get_all_extracted_json(company_id, year)
                status.update(label="Financial data loaded", state="complete")

            # Step 2: Get forensic knowledge context from RAG
            with st.status("Retrieving forensic patterns from knowledge base...", expanded=True) as status:
                if kb_count > 0:
                    rag_context = rag.get_context_for_prompt(
                        f"forensic red flags manipulation patterns for {company_name} annual report analysis",
                        n_results=10,
                    )
                    st.write(f"Retrieved {min(10, kb_count)} relevant knowledge chunks")
                else:
                    rag_context = "Knowledge base not indexed. Using built-in forensic patterns."
                    st.write("Knowledge base not indexed - using system prompt patterns")
                status.update(label="Knowledge base context ready", state="complete")

            # Step 3: Scan PDF for red flag keywords
            pdf_scan_results = ""
            pdf_path = load_annual_report_pdf_path(company_id, year)
            if pdf_path and pdf_path.exists():
                with st.status(f"Scanning PDF: {pdf_path.name}...", expanded=True) as status:
                    try:
                        text = extract_text_pypdf2(pdf_path)
                        flags = search_for_red_flags(text)
                        if flags:
                            pdf_scan_results = "RED FLAG KEYWORD SCAN RESULTS:\n"
                            for f in flags:
                                pdf_scan_results += f"- {f['label']} (severity {f['severity']}/5, {f['count']} occurrences)\n"
                                for ctx in f["contexts"][:1]:
                                    pdf_scan_results += f"  Context: ...{ctx[:200]}...\n"
                            st.write(f"Found {len(flags)} red flag categories in PDF")
                        else:
                            pdf_scan_results = "No red flag keywords detected in PDF scan."
                            st.write("No keyword red flags detected")
                    except Exception as e:
                        st.write(f"PDF scan failed: {e}")
                    status.update(label="PDF scan complete", state="complete")

            # Step 4: Build the comprehensive prompt
            financial_summary = f"""
EXTRACTED FINANCIAL DATA for {company_name} (ID: {company_id}, {year}, {qualifier}):
Unit: {financials.unit} INR

INCOME STATEMENT:
- Revenue from Operations: {financials.revenue:,.2f}
- Other Income: {financials.other_income:,.2f}
- Total Income: {financials.total_income:,.2f}
- Raw Material Cost: {financials.raw_material_cost:,.2f}
- Employee Cost: {financials.employee_cost:,.2f}
- Finance Cost: {financials.finance_cost:,.2f}
- Depreciation: {financials.depreciation:,.2f}
- Other Expenses: {financials.other_expenses:,.2f}
- Total Expenses: {financials.total_expenses:,.2f}
- PBT: {financials.pbt:,.2f}
- Tax: {financials.tax:,.2f}
- PAT: {financials.pat:,.2f}

BALANCE SHEET:
- Net Fixed Assets: {financials.net_fixed_assets:,.2f}
- Inventory: {financials.inventory:,.2f}
- Trade Receivables: {financials.trade_receivables:,.2f}
- Cash & Equivalents: {financials.cash_and_equivalents:,.2f}
- Total Assets: {financials.total_assets:,.2f}
- Total Debt: {financials.total_debt:,.2f}
- Equity: {financials.equity:,.2f}

CASH FLOW:
- CFO: {financials.cfo:,.2f}
- CFI: {financials.cfi:,.2f}
- CFF: {financials.cff:,.2f}

CALCULATED RATIOS:
- OPM: {((financials.revenue - financials.raw_material_cost - financials.employee_cost - financials.other_expenses) / financials.revenue * 100) if financials.revenue else 'N/A':.1f}%
- NPM: {(financials.pat / financials.revenue * 100) if financials.revenue else 'N/A':.1f}%
- NFAT: {(financials.revenue / financials.net_fixed_assets) if financials.net_fixed_assets else 'N/A':.2f}
- Receivables Days: {(financials.trade_receivables / financials.revenue * 365) if financials.revenue else 'N/A':.0f}
- Debt/Equity: {(financials.total_debt / financials.equity) if financials.equity else 'N/A':.2f}
- Tax Payout: {(financials.tax / financials.pbt * 100) if financials.pbt else 'N/A':.1f}%
- Raw Material % of Sales: {(financials.raw_material_cost / financials.revenue * 100) if financials.revenue else 'N/A':.1f}%
- Employee Cost % of Sales: {(financials.employee_cost / financials.revenue * 100) if financials.revenue else 'N/A':.1f}%
"""

            full_prompt = f"""Perform a comprehensive forensic analysis of {company_name}.

{financial_summary}

{pdf_scan_results}

FORENSIC KNOWLEDGE BASE CONTEXT (from 80+ analyzed companies):
{rag_context}

INSTRUCTIONS:
1. Calculate all available forensic ratios from the data provided
2. Compare each ratio against the benchmarks from Dr. Malik's framework
3. Check for ALL 7 fraud patterns and score each 0-10
4. Identify all red flags with severity (1-5) and specific evidence
5. Identify green flags
6. Compare to similar companies from the knowledge base
7. Provide overall Risk Score (0-50) and Verdict

NOTE: This is single-year data. For multi-year trend analysis, explicitly note what additional years of data would reveal. Focus on what CAN be determined from this snapshot.

Format your response with clear sections using markdown headers."""

            # Step 5: Call AI
            with st.status("Running AI forensic analysis...", expanded=True) as status:
                prefer = prefer_map[ai_preference]
                st.write(f"Using: {ai_preference}")

                response = query(
                    full_prompt,
                    system=FORENSIC_SYSTEM_PROMPT,
                    prefer=prefer,
                    ollama_model=ollama_model,
                )

                if response.success:
                    st.write(f"Response from: **{response.provider}** ({response.model})")
                    status.update(label=f"Analysis complete via {response.provider}", state="complete")
                else:
                    st.error(f"AI failed: {response.error}")
                    status.update(label="AI analysis failed", state="error")

            # Step 6: Display results
            if response.success:
                st.divider()
                st.subheader(f"Forensic Analysis: {company_name}")
                st.markdown(response.text)

                # Show raw data in expander
                with st.expander("Raw Financial Data (JSON)"):
                    st.json({
                        "company_id": company_id,
                        "year": year,
                        "qualifier": qualifier,
                        "revenue": financials.revenue,
                        "pat": financials.pat,
                        "cfo": financials.cfo,
                        "net_fixed_assets": financials.net_fixed_assets,
                        "total_debt": financials.total_debt,
                        "equity": financials.equity,
                        "trade_receivables": financials.trade_receivables,
                        "inventory": financials.inventory,
                    })

                if all_data:
                    with st.expander("All Extracted Data Files"):
                        for name, data in all_data.items():
                            st.markdown(f"**{name}**")
                            st.json(data)

                # Download
                st.download_button(
                    "Download Analysis Report",
                    response.text,
                    f"forensic_{company_name}_{year}.md",
                    "text/markdown",
                )
    else:
        st.info("No extracted annual reports found in D:\\Annual_report_extract\\output")
        st.markdown("Run the Annual Report Extract pipeline first to populate data.")


with tab_custom:
    st.subheader("Analyze Any Company by Name")
    st.caption("Enter a company name. AI will use the knowledge base to analyze it.")

    company_input = st.text_input("Company Name", placeholder="e.g., Infosys, TCS, HDFC Bank, Reliance Industries")

    custom_context = st.text_area(
        "Additional context (optional)",
        placeholder="Paste any financial data, annual report excerpts, or specific concerns here...",
        height=150,
    )

    analysis_depth = st.select_slider(
        "Analysis Depth",
        options=["Quick Scan", "Standard", "Deep Dive"],
        value="Standard",
    )

    if st.button("Generate Forensic Analysis", type="primary", use_container_width=True, key="run_custom"):
        if not company_input:
            st.warning("Please enter a company name.")
        else:
            # Get RAG context
            with st.spinner("Retrieving forensic patterns..."):
                if kb_count > 0:
                    rag_context = rag.get_context_for_prompt(
                        f"forensic analysis red flags for {company_input} company India",
                        n_results=10,
                    )
                else:
                    rag_context = "Using built-in forensic patterns."

            depth_instructions = {
                "Quick Scan": "Provide a concise 10-point red flag check with scoring. Keep response under 500 words.",
                "Standard": "Provide full 5-pillar analysis with all 7 pattern checks. Be thorough but focused.",
                "Deep Dive": "Provide exhaustive forensic analysis. Check every possible red flag. Compare with peers. Provide detailed evidence for each finding. Recommend specific sections of annual report to investigate further.",
            }

            prompt = f"""Perform a {analysis_depth.lower()} forensic analysis of {company_input}.

{f'ADDITIONAL CONTEXT PROVIDED BY USER:{chr(10)}{custom_context}' if custom_context else ''}

FORENSIC KNOWLEDGE BASE (from Dr. Vijay Malik's analysis of 80+ companies):
{rag_context}

{depth_instructions[analysis_depth]}

Check against all 7 known fraud patterns and score each 0-10.
Provide Risk Score (0-50) and Verdict.
If you don't have specific financial data, state what data points are needed and what to look for.
Use markdown formatting with clear headers."""

            prefer = prefer_map[ai_preference]

            with st.spinner(f"Generating forensic analysis via {ai_preference}..."):
                response = query(
                    prompt,
                    system=FORENSIC_SYSTEM_PROMPT,
                    prefer=prefer,
                    ollama_model=ollama_model,
                )

            if response.success:
                st.success(f"Analysis by: {response.provider} ({response.model})")
                st.divider()
                st.markdown(response.text)

                st.download_button(
                    "Download Analysis",
                    response.text,
                    f"forensic_{company_input.replace(' ', '_')}.md",
                    "text/markdown",
                )
            else:
                st.error(f"Analysis failed: {response.error}")
                st.info("Make sure either Claude CLI is installed or Ollama is running.")
