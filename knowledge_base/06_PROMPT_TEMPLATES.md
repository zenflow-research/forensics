# Prompt Templates for LLM-Based Forensic Analysis
## Ready-to-Use Prompts for Analyzing Companies

---

## PROMPT SET 1: COMPREHENSIVE COMPANY ANALYSIS

### Prompt 1A: Full Forensic Screening
```
You are an expert forensic accountant trained in Dr. Vijay Malik's "Peaceful Investing" methodology. Analyze [COMPANY NAME] using the following framework:

**FINANCIAL ANALYSIS:**
1. Calculate 10-year sales CAGR and identify growth trajectory
2. Analyze Operating Profit Margin (OPM) stability -- is it within a 5 percentage point range or wildly fluctuating?
3. Calculate Net Profit Margin (NPM) trend
4. Compare tax payout ratio to standard corporate tax rate (25-30%)
5. Calculate Cumulative PAT vs Cumulative CFO over 10 years -- is cCFO >= cPAT?
6. Calculate Free Cash Flow (FCF = CFO - Capex) for each year and cumulative
7. Determine if dividends are funded from FCF or borrowed money

**OPERATING EFFICIENCY:**
8. Calculate Net Fixed Asset Turnover (NFAT = Sales/Net Fixed Assets) trend
9. Calculate Inventory Turnover Ratio (ITR) trend
10. Calculate Receivables Days trend -- are receivables > 6 months old?

**MARGIN OF SAFETY:**
11. Calculate Self-Sustainable Growth Rate (SSGR = NFAT x NPM x (1-DPR) - Depreciation Rate)
12. Compare SSGR to actual sales growth rate
13. Assess P/E ratio margin of safety (earnings yield vs G-Sec rate)

**MANAGEMENT QUALITY:**
14. Calculate promoter remuneration as % of PAT
15. Track promoter shareholding changes and any pledging
16. List all related party transactions -- identify potential self-dealing
17. Check for independent director independence
18. Assess succession planning

**BUSINESS MODEL:**
19. Identify customer/supplier concentration risks
20. Assess barriers to entry and pricing power
21. Check regulatory/policy dependency

Output a structured report with:
- Red flags found (categorized by severity)
- Green flags found
- Overall forensic risk score (Low/Medium/High/Critical)
- Key concerns requiring further investigation
- Verdict: Invest / Avoid / Monitor
```

### Prompt 1B: Quick Red Flag Scan
```
Perform a rapid forensic red flag scan of [COMPANY NAME] checking for these specific patterns:

1. Is cCFO < cPAT over the last 10 years? (Profit quality issue)
2. Is FCF negative? Are dividends being paid from borrowed money?
3. Is SSGR < actual sales growth rate? (Unsustainable growth)
4. Is promoter salary > 10% of PAT?
5. Are there loans to/from promoters at non-market interest rates?
6. Has the company changed credit rating agencies? (Credit rating shopping)
7. Is NFAT declining? Is PBT/NFA lower than bank FD rate?
8. Are receivables days increasing?
9. Are there corporate guarantees for group companies?
10. Is promoter shareholding declining or pledged?

For each flag found, provide:
- The specific data/evidence
- Severity rating (1-5)
- Historical precedent from known fraud cases

Calculate an overall Red Flag Score (0-50) and classify as:
- 0-10: Low Risk
- 11-20: Moderate Risk
- 21-35: High Risk
- 36-50: Critical Risk
```

---

## PROMPT SET 2: SPECIFIC ANALYSIS AREAS

### Prompt 2A: Cash Flow Forensics
```
Perform a detailed cash flow forensic analysis of [COMPANY NAME]:

1. For each of the last 10 years, extract: PAT, CFO, Capex, FCF, Interest paid, Dividends paid
2. Calculate cumulative figures for all metrics
3. Check if interest expense is correctly classified under CFF (not CFO)
4. Check if any loan proceeds are misclassified under CFO
5. Check if asset sale proceeds are correctly under CFI
6. Reconcile CFO working capital adjustments with actual balance sheet changes
7. Identify any "exceptional items" that appear repeatedly (not truly exceptional)
8. Calculate: Are dividends covered by FCF? If not, company is paying dividends from debt.

Flag any discrepancies between stated cash flows and balance sheet movements.
Provide a cash flow quality score: Genuine / Suspect / Manipulated
```

### Prompt 2B: Related Party Transaction Analysis
```
Analyze all related party transactions of [COMPANY NAME] for the last 5 years:

1. List every related party and their relationship to the promoter
2. For each transaction type (sales, purchases, loans, guarantees, rent, commission):
   - What is the amount and trend?
   - Is the pricing at arm's length? (compare to market rates)
   - Who benefits -- the company or the promoter?
3. Check for these specific patterns:
   - Loans TO related parties at below-market rates (should earn bank FD rate minimum)
   - Loans FROM promoters at above-market rates (should not exceed company's bank borrowing rate)
   - Corporate guarantees for non-subsidiary group entities
   - Property transactions with promoter family
   - Undisclosed related parties (cross-reference director other directorships)
4. Check if related party receivables are growing (money stuck with promoters)
5. Identify the "vicious cycle" pattern: High promoter salary -> Cash shortfall -> Promoter loans at high interest

Rate the risk: Clean / Minor Concerns / Significant Self-Dealing / Potential Fraud
```

### Prompt 2C: Promoter Integrity Assessment
```
Assess the integrity and alignment of [COMPANY NAME]'s promoters with minority shareholders:

1. **Remuneration analysis:**
   - Total promoter family remuneration vs PAT (should be < 4%)
   - Are all family members paid equally regardless of role/qualification?
   - Has remuneration exceeded statutory limits?

2. **Shareholding pattern:**
   - 10-year promoter holding trend (increasing = good, decreasing = concern)
   - Any share pledging? Current and historical levels
   - Warrants/preferential allotments: at what discount to market?
   - Did promoters sell shortly after warrant conversion?
   - Any circular shareholding structures (company -> promoter entity -> buys company shares)?

3. **Commitment track record:**
   - List management's stated targets/plans from past annual reports
   - Compare to actual outcomes
   - Any broken promises on pledge release, capex timelines, etc.?

4. **Red flags from other entities:**
   - SEBI orders against promoters or their other companies
   - Criminal cases pending
   - Promoter running competing businesses

5. **Positive signals:**
   - Promoter buying shares in open market
   - Reasonable/low salary with high dividends
   - Family members working in junior positions before elevation

Verdict: Trustworthy / Acceptable / Concerning / Avoid
```

### Prompt 2D: Annual Report Deep Reading
```
I am providing [COMPANY NAME]'s annual report. Read it with forensic intent and extract:

1. **Inconsistencies:**
   - Do numbers in different sections match? (Director's report vs financial statements vs MD&A)
   - Are there calculation errors? (Check indebtedness tables, capacity data)
   - Any copy-pasted sections from previous years without updating?

2. **Disclosure gaps:**
   - What is NOT disclosed that should be? (Contingent liabilities, related party details)
   - Are "Others" categories unusually large without breakdown?
   - Are subsidiary/JV financials provided or just management-prepared summaries?

3. **Language analysis:**
   - Are management explanations for poor performance citing only external factors?
   - Compare the company's macro claims with peer company performance
   - Do tone and promises match actual results from previous years?

4. **Notes to Accounts forensics:**
   - Revenue recognition policy (aggressive or conservative?)
   - Accounting policy changes and their impact
   - Depreciation method and any changes
   - Inventory valuation method
   - Treatment of forex gains/losses

5. **Auditor's report analysis:**
   - Any qualifications or emphasis of matter?
   - CARO observations -- especially on statutory dues, related party loans
   - Are prior year qualifications resolved?

Output: A "Trust Score" for the annual report (1-10) with specific evidence for each deduction.
```

---

## PROMPT SET 3: COMPARATIVE & SECTOR ANALYSIS

### Prompt 3A: Peer Comparison
```
Compare [COMPANY NAME] with its industry peers on these forensic parameters:

| Parameter | Company | Peer 1 | Peer 2 | Peer 3 |
|-----------|---------|--------|--------|--------|
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
| Related party txns | | | | |

Identify:
1. Is the company's claimed performance genuinely superior to peers?
2. Are peer companies citing same macro challenges while performing differently?
3. Which company in the peer group has the best forensic profile?
```

### Prompt 3B: Industry Red Flag Patterns
```
For the [INDUSTRY/SECTOR], identify common forensic red flags based on Dr. Vijay Malik's analysis:

Known patterns by sector:
- **Pharma**: High promoter salaries, parallel competing businesses, USFDA risks
- **Chemicals**: Cyclicality, Chinese policy dependency, environmental risks, CDR history
- **Infrastructure/EPC**: POCM manipulation, unbilled revenue, partner default risk
- **Textiles**: Derivative losses, export incentive dependency, fluctuating margins
- **Auto Components**: OEM pricing power extraction, cyclicality, complex structures
- **FMCG/Consumer**: Reserve manipulation, brand purchases from parent, derivative losses
- **IT Services**: Declining margins, acquisition failures, speculative hedging
- **Contract Manufacturing**: Razor-thin margins, no customer commitment, pricing pressure

Apply the sector-specific lens to analyze [COMPANY NAME].
```

---

## PROMPT SET 4: DATA EXTRACTION FROM ANNUAL REPORTS

### Prompt 4A: Financial Data Extraction
```
Extract the following data points from [COMPANY NAME]'s annual report for [YEAR]:

**Income Statement:**
- Revenue from operations (net)
- Other income (break down components)
- Raw material cost and % of revenue
- Employee cost and % of revenue
- Other expenses (identify largest items)
- Operating profit and OPM
- Interest expense
- Depreciation
- Exceptional items (detail each)
- PBT, Tax, PAT
- Tax payout ratio

**Balance Sheet:**
- Net fixed assets and gross block
- CWIP (Capital Work in Progress)
- Non-current investments (list entities and amounts)
- Trade receivables (total and > 6 months)
- Inventory
- Cash and bank balances
- Current investments
- Loans and advances (to related parties separately)
- Total debt (short-term + long-term)
- Trade payables

**Cash Flow:**
- CFO (and key working capital adjustments)
- CFI (capex, investments, acquisitions)
- CFF (debt raised/repaid, equity raised, dividends)
- Verify: Interest classification, loan classification

**Governance:**
- Promoter remuneration (each member)
- Related party transactions (each party, each type)
- Contingent liabilities
- Auditor observations/qualifications
- Promoter shareholding and pledge status
```

### Prompt 4B: Web Data Extraction for Forensic Analysis
```
For [COMPANY NAME], gather the following from web sources:

1. **Screener.in**: Export 10-year financial data
2. **BSE/NSE**: Latest shareholding pattern, corporate announcements, regulatory orders
3. **Credit Rating Reports**: Latest and historical ratings from all agencies
4. **MCA/RoC**: Director DIN details, other company directorships, charge documents
5. **SEBI**: Any orders or investigations involving the company or promoters
6. **Industry Reports**: Market share data, competitive landscape
7. **News**: Any fraud allegations, regulatory actions, whistleblower complaints
8. **Court Cases**: NCLT, High Court, Supreme Court cases involving the company
9. **Glassdoor/AmbitionBox**: Employee reviews (indicator of internal culture)
10. **Google Scholar/SSRN**: Any academic research on the company or sector

Cross-reference promoter names with:
- Other company directorships (MCA data)
- Political contributions (election commission data)
- Charitable trust involvements
- Criminal cases (if any)
```

---

## PROMPT SET 5: PATTERN RECOGNITION

### Prompt 5A: Known Fraud Pattern Matching
```
Compare [COMPANY NAME]'s financial patterns against these known fraud indicators from Dr. Vijay Malik's case studies:

**Pattern 1: The "Trinity"** (Omkar Speciality)
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

Does [COMPANY NAME] exhibit any of these patterns? Provide specific evidence.
```
