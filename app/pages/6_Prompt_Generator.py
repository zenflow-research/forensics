"""Prompt Generator: Generate ready-to-use forensic analysis prompts for any LLM."""

import streamlit as st
from pathlib import Path

st.set_page_config(page_title="Prompt Generator", page_icon="🤖", layout="wide")
st.title("Forensic Prompt Generator")
st.caption("Generate customized forensic analysis prompts for any LLM. Copy and paste into ChatGPT, Claude, Gemini, or local models.")

company_name = st.text_input("Company Name", "Company XYZ", help="The company you want to analyze")

# Prompt templates
PROMPTS = {
    "Full Forensic Analysis": {
        "desc": "Comprehensive 5-pillar forensic analysis covering financials, efficiency, management, business model, and valuation.",
        "template": """You are an expert forensic accountant trained in Dr. Vijay Malik's "Peaceful Investing" methodology. Analyze {company} using this framework:

**FINANCIAL ANALYSIS:**
1. Calculate 10-year sales CAGR and growth trajectory
2. Analyze OPM stability (is the range within 5 pp or wildly fluctuating?)
3. Calculate NPM trend
4. Compare tax payout ratio to standard 25-30% corporate tax rate
5. Calculate Cumulative PAT vs Cumulative CFO over 10 years (cCFO >= cPAT?)
6. Calculate Free Cash Flow (FCF = CFO - Capex) for each year and cumulative
7. Determine if dividends are funded from FCF or borrowed money

**OPERATING EFFICIENCY:**
8. NFAT (Sales/Net Fixed Assets) trend -- sweet spot is 2-5
9. ITR (Sales/Inventory) trend -- declining is bad
10. Receivables Days trend -- check for > 6 month old receivables

**MARGIN OF SAFETY:**
11. SSGR = NFAT x NPM x (1-DPR) - Depreciation Rate
12. Compare SSGR to actual sales growth (SSGR > growth = self-sustaining)
13. P/E margin of safety (earnings yield > G-Sec rate?)

**MANAGEMENT QUALITY:**
14. Promoter remuneration as % of PAT (threshold: <4% good, >10% red flag)
15. Promoter shareholding changes and pledging
16. Related party transactions -- identify self-dealing patterns
17. Independent director independence verification
18. Succession planning assessment

**BUSINESS MODEL:**
19. Customer/supplier concentration risks
20. Barriers to entry and pricing power
21. Regulatory/policy dependency

Output: Red flags (categorized by severity 1-5), Green flags, Risk Score (0-50), Verdict (Invest/Avoid/Monitor)."""
    },
    "Cash Flow Forensics": {
        "desc": "Deep dive into cash flow statement to detect manipulation and assess quality.",
        "template": """Perform a detailed cash flow forensic analysis of {company}:

1. For each of the last 10 years, extract: PAT, CFO, Capex, FCF, Interest paid, Dividends
2. Calculate cumulative figures for all metrics
3. Check if interest expense is correctly classified under CFF (not CFO)
4. Check if any loan proceeds are misclassified under CFO
5. Check if asset sale proceeds are correctly under CFI
6. Reconcile CFO working capital adjustments with actual balance sheet changes
7. Identify "exceptional items" that appear repeatedly (not truly exceptional)
8. Calculate: Are dividends covered by FCF? If not, dividends are debt-funded

Known manipulation patterns to check:
- Sreeleathers: Loan shown as CFO inflow (Rs 11.5 cr misclassified)
- PIX Transmissions: Asset sale proceeds under CFO instead of CFI (Rs 134 cr)
- Supreme Industries: Interest shown under CFO instead of CFF
- HEG: Rs 55.5 cr CFO calculation error in annual report

Provide a cash flow quality score: Genuine / Suspect / Manipulated"""
    },
    "Related Party Deep Dive": {
        "desc": "Forensic analysis of all related party transactions to detect self-dealing.",
        "template": """Analyze all related party transactions of {company} for the last 5 years:

1. List every related party and their relationship to promoters
2. For each transaction (sales, purchases, loans, guarantees, rent, commission):
   - Amount and trend over 5 years
   - Is pricing at arm's length? (compare to market rates)
   - Who benefits -- company or promoter?
3. Check for specific patterns:
   - Loans TO related parties at below-market rates (should earn FD rate minimum)
   - Loans FROM promoters at above-market rates (should not exceed bank borrowing rate)
   - Corporate guarantees for non-subsidiary group companies
   - Property transactions with promoter family
   - Undisclosed related parties (cross-reference DIN database)
4. Check for the "Vicious Cycle": High promoter salary -> Cash shortfall -> Promoter loans at high interest
   - PIX Transmissions: 12% interest on promoter loans
   - Bharat Rasayan: 10% vs 6% FD rate
   - KNR Constructions: 10.3% on promoter loans to A+ rated company
5. Check for circular shareholding (Sreeleathers/Shoeline pattern)

Rate: Clean / Minor Concerns / Significant Self-Dealing / Potential Fraud"""
    },
    "Fraud Pattern Matching": {
        "desc": "Compare company against 7 known fraud/manipulation patterns from Dr. Malik's case studies.",
        "template": """Compare {company}'s financial patterns against these known forensic patterns:

**Pattern 1: The Trinity** (Omkar Speciality)
- Rising sales + Rising receivables + Rising debt simultaneously
- Raw material consumption declining while product sales increasing

**Pattern 2: Credit Rating Shopping** (Omkar, Granules, Albert David)
- Company switches rating agencies after negative outlook/downgrade

**Pattern 3: Circular Shareholding** (Sreeleathers, Dynemic Products)
- Company invests in promoter entity that buys company shares

**Pattern 4: The Vicious Cycle** (PIX Transmissions, Bharat Rasayan)
- High promoter salary -> Cash shortfall -> Promoter lends back at high interest

**Pattern 5: Pre-Event Extraction** (Quick Heal, Kokuyo Camlin)
- Large dividends before IPO; selling subsidiaries to promoters before revival

**Pattern 6: Accounting Gymnastics** (Indo Count, HEG, Bodal)
- Asset revaluation to inflate profits
- Capitalizing expenses to hide costs
- Changing depreciation methods to alter ratios

**Pattern 7: Unsustainable Growth** (Omkar, Nandan Denim, Minda)
- Actual growth far exceeding SSGR, funded by increasingly expensive debt

For each pattern, provide specific evidence if found. Score each pattern match 0-10."""
    },
    "Peer Comparison": {
        "desc": "Compare company against industry peers on all forensic parameters.",
        "template": """Compare {company} with its top 3-4 industry peers on these forensic parameters:

| Parameter | {company} | Peer 1 | Peer 2 | Peer 3 |
|-----------|-----------|--------|--------|--------|
| OPM (10-yr range) | | | | |
| NPM trend | | | | |
| NFAT | | | | |
| ITR | | | | |
| Receivables Days | | | | |
| Debt/Equity | | | | |
| cCFO/cPAT ratio | | | | |
| SSGR vs actual growth | | | | |
| FCF (10-yr cumulative) | | | | |
| Promoter salary % of PAT | | | | |
| Related party txn intensity | | | | |

Critical questions:
1. Is {company}'s claimed performance genuinely superior to peers?
2. Are peer companies citing same macro challenges while performing differently? (Verify management truthfulness)
3. Which company has the best forensic profile and why?
4. Is {company}'s OPM advantage structural or temporary?"""
    },
    "Annual Report Reading Guide": {
        "desc": "Structured guide for reading an annual report with forensic intent.",
        "template": """Read {company}'s annual report with forensic intent. Extract and analyze:

1. **INCONSISTENCIES:**
   - Do numbers match across Director's Report, financial statements, and MD&A?
   - Any calculation errors in indebtedness tables, capacity data?
   - Copy-pasted sections from previous years without updating?

2. **DISCLOSURE GAPS:**
   - What is NOT disclosed that should be? (Contingent liabilities, related party details)
   - Are "Others" categories unusually large without breakdown?
   - Are subsidiary/JV financials provided or just management-prepared summaries?

3. **LANGUAGE ANALYSIS:**
   - Is management blaming only external factors for poor performance?
   - Compare macro claims with peer company performance
   - Do tone and promises match actual results from previous years?

4. **NOTES TO ACCOUNTS:**
   - Revenue recognition policy (aggressive or conservative?)
   - Accounting policy changes and their impact
   - Depreciation method and any changes
   - Treatment of forex gains/losses

5. **AUDITOR'S REPORT:**
   - Any qualifications or emphasis of matter?
   - CARO observations on statutory dues, related party loans
   - Are prior year qualifications resolved?

Output: Trust Score (1-10) with specific evidence for each deduction.

Key principle from Dr. Malik: "Focus on disclosure standards, not amounts. Even small undisclosed items reveal management attitude toward transparency." """
    },
    "Quick Red Flag Scan": {
        "desc": "Rapid 10-point red flag check with scoring.",
        "template": """Perform a rapid forensic red flag scan of {company}:

1. Is cCFO < cPAT over 10 years? (Profit quality)
2. Is FCF negative? Are dividends paid from debt?
3. Is SSGR < actual growth rate? (Unsustainable)
4. Is promoter salary > 10% of PAT?
5. Loans to/from promoters at non-market rates?
6. Credit rating agency changes? (Shopping)
7. Is NFAT declining? PBT/NFA < bank FD rate?
8. Receivables days increasing?
9. Corporate guarantees for group companies?
10. Promoter holding declining or pledged?

Score each flag 0-5. Total Score interpretation:
- 0-10: Low Risk
- 11-20: Moderate Risk
- 21-35: High Risk
- 36-50: Critical Risk"""
    },
}

# UI
st.subheader("Select Analysis Type")
prompt_type = st.selectbox(
    "Prompt Type",
    list(PROMPTS.keys()),
    format_func=lambda x: f"{x} -- {PROMPTS[x]['desc'][:60]}...",
)

selected_prompt = PROMPTS[prompt_type]

st.divider()

# Custom additions
with st.expander("Customize Prompt"):
    additional_context = st.text_area(
        "Additional context or specific concerns",
        placeholder="e.g., Focus on pharma sector risks, check for USFDA issues, compare to Divi's Labs...",
        height=100,
    )
    include_examples = st.checkbox("Include example companies from knowledge base", value=True)
    output_format = st.selectbox("Output Format", ["Structured Report", "Table Format", "Bullet Points", "JSON"])

# Generate final prompt
final_prompt = selected_prompt["template"].format(company=company_name)

if additional_context:
    final_prompt += f"\n\nADDITIONAL CONTEXT:\n{additional_context}"

if output_format != "Structured Report":
    final_prompt += f"\n\nPlease format the output as: {output_format}"

st.subheader("Generated Prompt")
st.code(final_prompt, language="text")

col1, col2 = st.columns(2)
col1.download_button(
    "Download Prompt",
    final_prompt,
    f"forensic_prompt_{company_name.replace(' ', '_').lower()}.txt",
    "text/plain",
    use_container_width=True,
)

# Count tokens (approximate)
token_count = len(final_prompt.split()) * 1.3
col2.metric("Approximate Tokens", f"{int(token_count)}")

st.divider()

# All prompts overview
with st.expander("View All Available Prompt Types"):
    for name, data in PROMPTS.items():
        st.markdown(f"**{name}**: {data['desc']}")
