"""Company Screener: Input financial data and get automated forensic analysis."""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from core.forensic_analyzer import FinancialData, analyze, calculate_ratios

st.set_page_config(page_title="Company Screener", page_icon="📊", layout="wide")
st.title("Forensic Company Screener")
st.caption("Input 10-year financial data. Get automated forensic analysis with risk scoring.")

# Sidebar config
with st.sidebar:
    st.subheader("Configuration")
    num_years = st.slider("Number of years", 3, 15, 10)
    gsec_rate = st.number_input("G-Sec Rate (%)", 4.0, 12.0, 7.0, 0.5)
    company_name = st.text_input("Company Name", "Sample Company")
    pe_ratio = st.number_input("Current P/E Ratio", 0.0, 500.0, 20.0, 0.5)
    market_cap = st.number_input("Market Cap (Cr)", 0.0, 1000000.0, 5000.0, 100.0)

    st.divider()
    use_sample = st.checkbox("Load sample data (MRF-like)", value=False)

# Generate year labels
years = [f"FY{2025-num_years+i+1}" for i in range(num_years)]

# Sample data (MRF-inspired)
if use_sample:
    sample = {
        "sales": [9000, 10200, 11500, 12000, 11800, 12500, 13200, 14500, 15000, 16500],
        "operating_profit": [1200, 1500, 1800, 1700, 1600, 1900, 2100, 2300, 2400, 2800],
        "net_profit": [600, 800, 1000, 950, 850, 1050, 1200, 1350, 1400, 1650],
        "tax": [300, 400, 500, 480, 420, 530, 600, 680, 700, 830],
        "pbt": [900, 1200, 1500, 1430, 1270, 1580, 1800, 2030, 2100, 2480],
        "cfo": [800, 1100, 1300, 1200, 1000, 1350, 1500, 1700, 1800, 2000],
        "capex": [500, 700, 800, 900, 600, 700, 800, 1000, 900, 950],
        "net_fixed_assets": [4000, 4300, 4800, 5200, 5300, 5500, 5800, 6200, 6500, 7000],
        "inventory": [1500, 1600, 1700, 1800, 1700, 1750, 1800, 1900, 2000, 2100],
        "trade_receivables": [800, 850, 900, 950, 900, 920, 950, 1000, 1050, 1100],
        "total_debt": [2000, 1800, 1600, 1500, 1400, 1300, 1100, 900, 700, 500],
        "equity": [5000, 5500, 6200, 6800, 7300, 8000, 8800, 9700, 10500, 11600],
        "dividends_paid": [80, 90, 100, 100, 100, 110, 120, 130, 140, 150],
        "interest_expense": [200, 180, 160, 150, 140, 130, 110, 90, 70, 50],
        "depreciation": [400, 420, 450, 480, 500, 520, 550, 580, 600, 630],
        "promoter_salary": [5, 5.5, 6, 6.5, 7, 7.5, 8, 8.5, 9, 10],
        "promoter_holding_pct": [27.5, 27.5, 27.5, 27.5, 27.5, 27.5, 27.5, 27.5, 27.5, 27.5],
    }
    default_values = sample
else:
    default_values = {k: [0.0] * num_years for k in [
        "sales", "operating_profit", "net_profit", "tax", "pbt", "cfo", "capex",
        "net_fixed_assets", "inventory", "trade_receivables", "total_debt", "equity",
        "dividends_paid", "interest_expense", "depreciation", "promoter_salary", "promoter_holding_pct",
    ]}

# Data input tabs
tab_input, tab_results = st.tabs(["Data Input", "Analysis Results"])

with tab_input:
    st.subheader("Enter Financial Data (all values in Crores)")
    st.caption("Fill in the data below or load sample data from the sidebar.")

    field_labels = {
        "sales": "Revenue / Sales",
        "operating_profit": "Operating Profit",
        "net_profit": "Net Profit (PAT)",
        "tax": "Tax Paid",
        "pbt": "Profit Before Tax",
        "cfo": "Cash Flow from Operations",
        "capex": "Capital Expenditure",
        "net_fixed_assets": "Net Fixed Assets",
        "inventory": "Inventory",
        "trade_receivables": "Trade Receivables",
        "total_debt": "Total Debt",
        "equity": "Shareholders' Equity",
        "dividends_paid": "Dividends Paid",
        "interest_expense": "Interest Expense",
        "depreciation": "Depreciation",
        "promoter_salary": "Promoter Total Remuneration",
        "promoter_holding_pct": "Promoter Holding (%)",
    }

    input_data = {}
    for field_key, label in field_labels.items():
        st.markdown(f"**{label}**")
        cols = st.columns(num_years)
        row_values = []
        for i, col in enumerate(cols):
            default = default_values[field_key][i] if i < len(default_values[field_key]) else 0.0
            val = col.number_input(
                years[i], value=float(default), key=f"{field_key}_{i}",
                label_visibility="collapsed" if i > 0 else "visible",
                step=1.0,
            )
            row_values.append(val)
        input_data[field_key] = row_values

    # Show year headers
    st.markdown("**Years:** " + " | ".join(years))

    run_analysis = st.button("Run Forensic Analysis", type="primary", use_container_width=True)

with tab_results:
    if run_analysis or use_sample:
        # Build FinancialData object
        fd = FinancialData(
            company_name=company_name,
            years=years[:num_years],
            pe_ratio=pe_ratio,
            current_market_cap=market_cap,
            gsec_rate=gsec_rate,
            **{k: v[:num_years] for k, v in input_data.items()},
        )

        # Run analysis
        report = analyze(fd)

        # Summary banner
        risk_color = {"Low Risk": "green", "Moderate Risk": "orange", "High Risk": "red", "Critical Risk": "red"}.get(report.risk_level, "gray")
        st.markdown(f"""
        ### {report.company_name}
        **Risk Score:** :{risk_color}[{report.risk_score}/50] | **Level:** :{risk_color}[{report.risk_level}] | **Verdict:** :{risk_color}[{report.verdict}]

        {len(report.red_flags)} Red Flags | {len(report.green_flags)} Green Flags
        """)

        st.divider()

        # Charts row
        col1, col2 = st.columns(2)

        with col1:
            # cPAT vs cCFO chart
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=years, y=report.ratios.get("cumulative_pat", []), name="Cumulative PAT", line=dict(color="#e74c3c")))
            fig.add_trace(go.Scatter(x=years, y=report.ratios.get("cumulative_cfo", []), name="Cumulative CFO", line=dict(color="#2ecc71")))
            fig.update_layout(title="Cumulative PAT vs CFO (Cash Conversion Test)", height=350, template="plotly_white")
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            # FCF chart
            fcf = report.ratios.get("fcf", [])
            colors = ["#2ecc71" if v >= 0 else "#e74c3c" for v in fcf]
            fig = go.Figure(go.Bar(x=years, y=fcf, marker_color=colors))
            fig.update_layout(title="Free Cash Flow (CFO - Capex)", height=350, template="plotly_white")
            st.plotly_chart(fig, use_container_width=True)

        col1, col2 = st.columns(2)

        with col1:
            # OPM & NPM
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=years, y=report.ratios.get("opm", []), name="OPM %", line=dict(color="#3498db")))
            fig.add_trace(go.Scatter(x=years, y=report.ratios.get("npm", []), name="NPM %", line=dict(color="#9b59b6")))
            fig.update_layout(title="Profitability Margins", height=350, template="plotly_white")
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            # SSGR vs Growth
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=years, y=report.ratios.get("ssgr", []), name="SSGR %", line=dict(color="#2ecc71", dash="dash")))
            fig.add_trace(go.Scatter(x=years, y=report.ratios.get("sales_growth", []), name="Sales Growth %", line=dict(color="#e74c3c")))
            fig.update_layout(title="SSGR vs Actual Growth (Sustainability Check)", height=350, template="plotly_white")
            st.plotly_chart(fig, use_container_width=True)

        st.divider()

        # Red & Green Flags
        col1, col2 = st.columns(2)

        with col1:
            st.subheader(f"Red Flags ({len(report.red_flags)})")
            for rf in sorted(report.red_flags, key=lambda x: x.severity, reverse=True):
                severity_icons = {5: "🔴🔴🔴", 4: "🔴🔴", 3: "🔴", 2: "🟡", 1: "⚪"}
                with st.expander(f"{severity_icons.get(rf.severity, '⚪')} [{rf.category}] {rf.title}"):
                    st.markdown(f"**{rf.detail}**")
                    st.caption(rf.evidence)

        with col2:
            st.subheader(f"Green Flags ({len(report.green_flags)})")
            for gf in report.green_flags:
                with st.expander(f"🟢 [{gf.category}] {gf.title}"):
                    st.markdown(gf.detail)

        st.divider()

        # Ratios table
        st.subheader("Detailed Ratios")
        ratio_display = {
            "OPM (%)": report.ratios.get("opm", []),
            "NPM (%)": report.ratios.get("npm", []),
            "NFAT": report.ratios.get("nfat", []),
            "ITR": report.ratios.get("itr", []),
            "Receivables Days": report.ratios.get("receivables_days", []),
            "SSGR (%)": report.ratios.get("ssgr", []),
            "Sales Growth (%)": report.ratios.get("sales_growth", []),
            "FCF (Cr)": report.ratios.get("fcf", []),
            "Debt/Equity": report.ratios.get("debt_equity", []),
            "Tax Payout (%)": report.ratios.get("tax_payout", []),
            "Promoter Salary % of PAT": report.ratios.get("promoter_salary_pct", []),
            "PBT/NFA (%)": report.ratios.get("pbt_nfa", []),
        }

        df_ratios = pd.DataFrame(ratio_display, index=years).T
        st.dataframe(df_ratios, use_container_width=True)

        # Summary metrics
        st.subheader("Summary Metrics")
        scol1, scol2, scol3, scol4 = st.columns(4)
        scol1.metric("10Y cCFO/cPAT", f"{report.ratios.get('ccfo_cpat_ratio', 'N/A')}")
        scol2.metric("10Y Total FCF", f"{report.ratios.get('total_fcf', 'N/A')} Cr")
        scol3.metric("Sales CAGR", f"{report.ratios.get('sales_cagr', 'N/A')}%")
        scol4.metric("Earnings Yield", f"{report.ratios.get('earnings_yield', 'N/A')}%")

    else:
        st.info("Enter financial data in the 'Data Input' tab and click 'Run Forensic Analysis'.")
