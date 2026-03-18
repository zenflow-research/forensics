"""Portfolio Audit: Analyze multiple companies and get aggregate forensic risk."""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from core.forensic_analyzer import FinancialData, analyze

st.set_page_config(page_title="Portfolio Audit", page_icon="📋", layout="wide")
st.title("Portfolio Forensic Audit")
st.caption("Analyze your entire portfolio at once. Upload a CSV or enter holdings manually.")

# CSV template
template_csv = """company_name,weight_pct,sales_y1,sales_y5,sales_y10,opm_avg,npm_avg,cfo_total,capex_total,debt_current,equity_current,pat_total,dividends_total,nfa_current,receivables_current,promoter_salary_avg,promoter_holding,pe_ratio
MRF Ltd,25,16500,12500,9000,16,9,12700,7850,500,11600,9500,1120,7000,1100,8,27.5,25
Divi's Labs,20,7800,5000,2500,38,25,4700,2000,50,8000,5600,800,3000,600,7.5,52,55
Omkar Specialty,10,413,250,37,12,5,100,280,228,150,180,20,400,150,8,45,15
Supreme Industries,20,5500,3500,2500,15,7,4260,2140,440,4000,3330,1220,3000,450,3,71,40
Sample Risky Co,15,1000,500,200,8,2,150,400,800,300,100,50,1200,300,20,30,8
HEG Ltd,10,2750,1000,800,25,15,2590,740,300,3000,1750,500,1500,500,2,65,10"""

st.download_button("Download CSV Template", template_csv, "portfolio_template.csv", "text/csv")

upload_mode = st.radio("Input Method", ["Upload CSV", "Manual Entry"], horizontal=True)

holdings = []

if upload_mode == "Upload CSV":
    uploaded = st.file_uploader("Upload portfolio CSV", type=["csv"])
    if uploaded:
        df = pd.read_csv(uploaded)
        st.dataframe(df, use_container_width=True)
        holdings = df.to_dict("records")
else:
    num_holdings = st.number_input("Number of holdings", 1, 20, 3)
    for i in range(num_holdings):
        with st.expander(f"Company {i+1}", expanded=(i == 0)):
            cols = st.columns([2, 1, 1, 1, 1])
            name = cols[0].text_input("Name", f"Company {i+1}", key=f"name_{i}")
            weight = cols[1].number_input("Weight %", 0.0, 100.0, round(100 / num_holdings, 1), key=f"w_{i}")
            pe = cols[2].number_input("P/E", 0.0, 500.0, 20.0, key=f"pe_{i}")
            npm = cols[3].number_input("Avg NPM %", -50.0, 100.0, 10.0, key=f"npm_{i}")
            opm = cols[4].number_input("Avg OPM %", -50.0, 100.0, 15.0, key=f"opm_{i}")

            cols2 = st.columns(5)
            cfo_total = cols2[0].number_input("10Y Total CFO", 0.0, 100000.0, 1000.0, key=f"cfo_{i}")
            capex_total = cols2[1].number_input("10Y Total Capex", 0.0, 100000.0, 500.0, key=f"capex_{i}")
            pat_total = cols2[2].number_input("10Y Total PAT", 0.0, 100000.0, 800.0, key=f"pat_{i}")
            debt = cols2[3].number_input("Current Debt", 0.0, 100000.0, 200.0, key=f"debt_{i}")
            equity = cols2[4].number_input("Current Equity", 0.0, 100000.0, 2000.0, key=f"eq_{i}")

            cols3 = st.columns(5)
            sales_now = cols3[0].number_input("Sales (Latest)", 0.0, 100000.0, 1000.0, key=f"s1_{i}")
            sales_5 = cols3[1].number_input("Sales (5Y ago)", 0.0, 100000.0, 600.0, key=f"s5_{i}")
            sales_10 = cols3[2].number_input("Sales (10Y ago)", 0.0, 100000.0, 300.0, key=f"s10_{i}")
            nfa = cols3[3].number_input("Net Fixed Assets", 0.0, 100000.0, 500.0, key=f"nfa_{i}")
            ps_pct = cols3[4].number_input("Promoter Salary % PAT", 0.0, 100.0, 5.0, key=f"ps_{i}")

            divs = st.number_input("10Y Total Dividends", 0.0, 100000.0, 100.0, key=f"div_{i}")
            recv = st.number_input("Trade Receivables", 0.0, 100000.0, 100.0, key=f"recv_{i}")
            ph = st.number_input("Promoter Holding %", 0.0, 100.0, 50.0, key=f"ph_{i}")

            holdings.append({
                "company_name": name, "weight_pct": weight, "pe_ratio": pe,
                "opm_avg": opm, "npm_avg": npm,
                "cfo_total": cfo_total, "capex_total": capex_total, "pat_total": pat_total,
                "debt_current": debt, "equity_current": equity,
                "sales_y1": sales_now, "sales_y5": sales_5, "sales_y10": sales_10,
                "nfa_current": nfa, "promoter_salary_avg": ps_pct,
                "dividends_total": divs, "receivables_current": recv,
                "promoter_holding": ph,
            })

if holdings and st.button("Run Portfolio Audit", type="primary", use_container_width=True):
    results = []
    for h in holdings:
        # Build simplified FinancialData (3-point interpolation)
        sales = [h.get("sales_y10", 0), h.get("sales_y5", 0), h.get("sales_y1", 0)]
        pat_avg = h.get("pat_total", 0) / 10
        cfo_avg = h.get("cfo_total", 0) / 10
        capex_avg = h.get("capex_total", 0) / 10
        div_avg = h.get("dividends_total", 0) / 10
        npm_frac = h.get("npm_avg", 0) / 100
        nfa = h.get("nfa_current", 1)
        nfat = sales[-1] / nfa if nfa > 0 else 0

        fcf_total = h.get("cfo_total", 0) - h.get("capex_total", 0)
        ccfo_cpat = h.get("cfo_total", 0) / h.get("pat_total", 1) if h.get("pat_total", 0) > 0 else 0
        de_ratio = h.get("debt_current", 0) / h.get("equity_current", 1) if h.get("equity_current", 0) > 0 else 0
        recv_days = (h.get("receivables_current", 0) / h.get("sales_y1", 1)) * 365 if h.get("sales_y1", 0) > 0 else 0

        # SSGR
        dpr = div_avg / pat_avg if pat_avg > 0 else 0
        dep_rate = 0.08  # approximate
        ssgr = (nfat * npm_frac * (1 - dpr) - dep_rate) * 100

        # Growth
        import math
        growth = (math.pow(sales[-1] / max(sales[0], 1), 1/9) - 1) * 100 if sales[0] > 0 else 0

        # Scoring
        red_flags = 0
        flag_details = []
        if ccfo_cpat < 0.8:
            red_flags += 2
            flag_details.append(f"Poor cash conversion (cCFO/cPAT={ccfo_cpat:.2f})")
        if fcf_total < 0:
            red_flags += 2
            flag_details.append(f"Negative FCF ({fcf_total:.0f} Cr)")
        if fcf_total < 0 and h.get("dividends_total", 0) > 0:
            red_flags += 2
            flag_details.append("Dividends from debt")
        if h.get("opm_avg", 0) < 5:
            red_flags += 1
            flag_details.append(f"Low OPM ({h['opm_avg']:.1f}%)")
        if ssgr < growth * 0.5 and growth > 5:
            red_flags += 2
            flag_details.append(f"SSGR ({ssgr:.1f}%) << Growth ({growth:.1f}%)")
        if de_ratio > 1.5:
            red_flags += 1
            flag_details.append(f"High D/E ({de_ratio:.2f})")
        if h.get("promoter_salary_avg", 0) > 10:
            red_flags += 1
            flag_details.append(f"High promoter salary ({h['promoter_salary_avg']:.1f}% of PAT)")
        if recv_days > 90:
            red_flags += 1
            flag_details.append(f"High receivables ({recv_days:.0f} days)")

        risk_score = min(50, red_flags * 4)
        risk_level = "Low" if risk_score <= 10 else "Medium" if risk_score <= 20 else "High" if risk_score <= 35 else "Critical"

        results.append({
            "Company": h["company_name"],
            "Weight %": h.get("weight_pct", 0),
            "Risk Score": risk_score,
            "Risk Level": risk_level,
            "Red Flags": red_flags,
            "NFAT": round(nfat, 2),
            "cCFO/cPAT": round(ccfo_cpat, 2),
            "FCF (Cr)": round(fcf_total, 0),
            "SSGR %": round(ssgr, 1),
            "Growth %": round(growth, 1),
            "D/E": round(de_ratio, 2),
            "P/E": h.get("pe_ratio", 0),
            "OPM %": h.get("opm_avg", 0),
            "NPM %": h.get("npm_avg", 0),
            "Flag Details": "; ".join(flag_details) if flag_details else "None",
        })

    df_results = pd.DataFrame(results)

    # Portfolio-level metrics
    st.subheader("Portfolio Risk Summary")
    weighted_risk = sum(r["Risk Score"] * r["Weight %"] for r in results) / max(sum(r["Weight %"] for r in results), 1)
    portfolio_risk = "Low" if weighted_risk <= 10 else "Medium" if weighted_risk <= 20 else "High" if weighted_risk <= 35 else "Critical"
    pr_color = {"Low": "green", "Medium": "orange", "High": "red", "Critical": "red"}[portfolio_risk]

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Weighted Risk Score", f"{weighted_risk:.1f}/50")
    col2.metric("Portfolio Risk Level", portfolio_risk)
    col3.metric("Holdings Analyzed", len(results))
    col4.metric("High Risk Holdings", len([r for r in results if r["Risk Level"] in ("High", "Critical")]))

    st.divider()

    # Risk heatmap
    col1, col2 = st.columns(2)
    with col1:
        fig = px.bar(
            df_results.sort_values("Risk Score", ascending=True),
            x="Risk Score", y="Company", orientation="h",
            color="Risk Level",
            color_discrete_map={"Low": "#2ecc71", "Medium": "#f39c12", "High": "#e74c3c", "Critical": "#c0392b"},
            title="Risk Score by Company"
        )
        fig.update_layout(height=400, template="plotly_white")
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        fig = px.scatter(
            df_results, x="SSGR %", y="Growth %",
            size="Weight %", color="Risk Level",
            color_discrete_map={"Low": "#2ecc71", "Medium": "#f39c12", "High": "#e74c3c", "Critical": "#c0392b"},
            hover_name="Company", title="SSGR vs Growth (Sustainability Map)",
            text="Company",
        )
        fig.add_shape(type="line", x0=-20, y0=-20, x1=60, y1=60, line=dict(dash="dash", color="gray"))
        fig.update_layout(height=400, template="plotly_white")
        fig.update_traces(textposition="top center")
        st.plotly_chart(fig, use_container_width=True)

    # Detailed table
    st.subheader("Detailed Results")
    st.dataframe(
        df_results.style.applymap(
            lambda v: "background-color: #ffcccc" if v in ("High", "Critical") else
                      "background-color: #fff3cd" if v == "Medium" else
                      "background-color: #d4edda" if v == "Low" else "",
            subset=["Risk Level"]
        ),
        use_container_width=True,
    )

    # Per-holding details
    st.subheader("Per-Holding Flag Details")
    for r in results:
        if r["Flag Details"] != "None":
            color = "red" if r["Risk Level"] in ("High", "Critical") else "orange" if r["Risk Level"] == "Medium" else "green"
            st.markdown(f"**:{color}[{r['Company']}]** ({r['Risk Level']}, Score: {r['Risk Score']}): {r['Flag Details']}")
        else:
            st.markdown(f"**:green[{r['Company']}]** (Low, Score: {r['Risk Score']}): No flags detected")

    # Export
    csv = df_results.to_csv(index=False)
    st.download_button("Download Audit Report (CSV)", csv, "portfolio_audit.csv", "text/csv")
