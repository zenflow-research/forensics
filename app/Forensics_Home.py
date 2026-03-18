"""
Forensic Accounting Intelligence Platform
Built from Dr. Vijay Malik's 'Peaceful Investing' methodology (2,774 pages, 80+ company analyses)
"""

import streamlit as st
from pathlib import Path

st.set_page_config(
    page_title="Forensic Accounting Intelligence",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0;
    }
    .sub-header {
        font-size: 1.1rem;
        color: #666;
        margin-top: -10px;
    }
    .metric-card {
        background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
        border-radius: 12px;
        padding: 20px;
        border-left: 4px solid;
        margin-bottom: 10px;
    }
    .red-card { border-left-color: #e74c3c; }
    .green-card { border-left-color: #2ecc71; }
    .blue-card { border-left-color: #3498db; }
    .gold-card { border-left-color: #f39c12; }
    .feature-box {
        background: #ffffff;
        border: 1px solid #e0e0e0;
        border-radius: 12px;
        padding: 24px;
        margin-bottom: 16px;
        transition: box-shadow 0.3s;
    }
    .feature-box:hover {
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    }
    .stMetric label { font-size: 0.9rem !important; }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown('<p class="main-header">Forensic Accounting Intelligence</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">Built from Dr. Vijay Malik\'s "Peaceful Investing" methodology | 2,774 pages | 80+ company analyses</p>', unsafe_allow_html=True)

st.divider()

# Dashboard metrics
kb_dir = Path(__file__).parent.parent / "knowledge_base"
kb_files = list(kb_dir.glob("*.md")) if kb_dir.exists() else []

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Red Flags Catalogued", "74", help="Categorized across 5 categories: Financial, Management, Business, Capital Allocation, Derivatives")
with col2:
    st.metric("Companies Analyzed", "80+", help="From Dr. Vijay Malik's Case Studies and Company Analysis volumes")
with col3:
    st.metric("Manipulation Techniques", "20+", help="Documented with real examples and detection methods")
with col4:
    st.metric("Analysis Checklist Steps", "18", help="Step-by-step protocol with 4 decision gates")

st.divider()

# Features grid
st.subheader("Platform Modules")

col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    <div class="feature-box">
        <h3>1. Forensic Q&A (RAG)</h3>
        <p>Ask any question about forensic accounting. Powered by the complete knowledge base with semantic search.</p>
        <p><b>Examples:</b> "What is SSGR?", "How to detect dividend stripping?", "Red flags in pharma sector"</p>
    </div>
    """, unsafe_allow_html=True)
    if st.button("Open Q&A Engine", key="qa", use_container_width=True):
        st.switch_page("pages/1_Forensic_QA.py")

    st.markdown("""
    <div class="feature-box">
        <h3>3. Annual Report Analyzer</h3>
        <p>Upload any annual report PDF. Get instant red flag scan, section extraction, and forensic scoring.</p>
        <p><b>Features:</b> Keyword detection, section parsing, red flag scoring, context extraction</p>
    </div>
    """, unsafe_allow_html=True)
    if st.button("Open Report Analyzer", key="ar", use_container_width=True):
        st.switch_page("pages/3_Report_Analyzer.py")

    st.markdown("""
    <div class="feature-box">
        <h3>5. Knowledge Explorer</h3>
        <p>Browse the complete knowledge base. Search red flags, manipulation techniques, and case studies.</p>
        <p><b>Features:</b> Full-text search, category filtering, company case study browser</p>
    </div>
    """, unsafe_allow_html=True)
    if st.button("Open Explorer", key="ke", use_container_width=True):
        st.switch_page("pages/5_Knowledge_Explorer.py")

with col2:
    st.markdown("""
    <div class="feature-box">
        <h3>2. Company Screener</h3>
        <p>Input financial data for any company. Get automated forensic analysis with risk scoring using Dr. Malik's framework.</p>
        <p><b>Calculates:</b> SSGR, FCF, NFAT, cCFO/cPAT, and 12+ forensic checks</p>
    </div>
    """, unsafe_allow_html=True)
    if st.button("Open Screener", key="cs", use_container_width=True):
        st.switch_page("pages/2_Company_Screener.py")

    st.markdown("""
    <div class="feature-box">
        <h3>4. Portfolio Audit</h3>
        <p>Analyze your entire portfolio at once. Get aggregate risk scores and per-holding forensic reports.</p>
        <p><b>Features:</b> Multi-company analysis, portfolio risk heatmap, concentration checks</p>
    </div>
    """, unsafe_allow_html=True)
    if st.button("Open Portfolio Audit", key="pa", use_container_width=True):
        st.switch_page("pages/4_Portfolio_Audit.py")

    st.markdown("""
    <div class="feature-box">
        <h3>6. Prompt Generator</h3>
        <p>Generate ready-to-use forensic analysis prompts for any LLM. Customizable by analysis type.</p>
        <p><b>Types:</b> Full analysis, cash flow forensics, related party, pattern matching, peer comparison</p>
    </div>
    """, unsafe_allow_html=True)
    if st.button("Open Prompt Generator", key="pg", use_container_width=True):
        st.switch_page("pages/6_Prompt_Generator.py")

st.markdown("""
<div class="feature-box" style="border: 2px solid #0f3460;">
    <h3>7. AI Forensic Generator (NEW)</h3>
    <p><b>Hybrid AI:</b> Claude CLI + Ollama | Say a company name, get full forensic analysis with pattern matching.</p>
    <p><b>Features:</b> Pulls from extracted annual reports (D:\\Annual_report_extract), RAG knowledge base, PDF red flag scan, 7 fraud pattern checks, risk scoring.</p>
</div>
""", unsafe_allow_html=True)
if st.button("Open AI Forensic Generator", key="aifg", use_container_width=True, type="primary"):
    st.switch_page("pages/7_AI_Forensic_Generator.py")

st.divider()

# Quick reference
with st.expander("Quick Reference: Dr. Malik's Key Principles"):
    st.markdown("""
    1. **Read annual reports for at least 10 years** -- they unfold like a storybook
    2. **Focus on disclosure standards, not amounts** -- small undisclosed items reveal management attitude
    3. **Any growth > 30-35% is highly unstable** -- usually driven by external factors
    4. **One company a year is enough** -- quality over quantity
    5. **cCFO must >= cPAT** -- profits must convert to cash
    6. **SSGR > Actual Growth = Self-sustaining** -- no need for external capital
    7. **Positive FCF = Real value creation** -- company can fund growth + dividends internally
    8. **Compare company claims with peer performance** -- to verify truthfulness
    9. **High ROE needs decomposition** -- prefer high NPM + high NFAT + LOW leverage
    10. **Credit rating reports** provide info not in annual reports (capacity, key risks)
    """)

with st.expander("Core Formulas"):
    col1, col2 = st.columns(2)
    with col1:
        st.code("""
SSGR = NFAT x NPM x (1-DPR) - Dep Rate
FCF = CFO - Capex
NFAT = Sales / Net Fixed Assets
ITR = Sales / Avg Inventory
        """, language="text")
    with col2:
        st.code("""
Receivables Days = (Receivables/Sales) x 365
Earnings Yield = 1 / PE Ratio
cCFO/cPAT Ratio (target >= 1.0)
PBT/NFA Ratio (compare to FD rate ~7%)
        """, language="text")

st.caption("Built from Dr. Vijay Malik's forensic accounting corpus | Knowledge base at `knowledge_base/`")
