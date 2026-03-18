# Forensic Accounting Checklist
## Step-by-Step Company Analysis Protocol

---

## PHASE 1: INITIAL SCREENING (30 minutes)

### Step 1: Gather 10-Year Financial Data
- [ ] Download financial data from Screener.in (Export to Excel)
- [ ] Collect annual reports for last 10 years from company website / BSE / NSE
- [ ] Download credit rating reports (CRISIL, CARE, ICRA, India Ratings, Brickwork)
- [ ] Note any rating agency changes over the years (potential credit rating shopping)

### Step 2: Quick Financial Health Check
- [ ] **Sales Growth**: Calculate 10-year CAGR and YoY growth rates
  - Alert if growth > 30-35% (unstable)
  - Alert if growth is declining
- [ ] **OPM Trend**: Plot 10-year OPM
  - Alert if range > 10 percentage points (commodity/cyclical)
  - Green if stable or improving
- [ ] **Debt Trajectory**: Is debt increasing or decreasing over 10 years?
  - Alert if continuously increasing
- [ ] **P/E Ratio**: Calculate earnings yield (1/PE) vs G-Sec rate
  - Green if P/E < 10-11

### Decision Gate 1: Proceed only if sales growth, OPM, and debt trends are acceptable

---

## PHASE 2: DEEP FINANCIAL ANALYSIS (2-3 hours)

### Step 3: Cash Conversion Test
- [ ] Calculate **Cumulative PAT (cPAT)** over 10 years
- [ ] Calculate **Cumulative CFO (cCFO)** over 10 years
- [ ] **cCFO / cPAT ratio**: Should be >= 1.0
  - If < 0.8: Major red flag -- profits not converting to cash
- [ ] Cross-check: Do CFO working capital adjustments reconcile with balance sheet changes?

### Step 4: Free Cash Flow Analysis
- [ ] **FCF = CFO - Capex** for each year and cumulative
- [ ] **Net FCF = FCF + Non-operating income - Interest**
- [ ] Are dividends covered by FCF? If not, dividends are debt-funded
- [ ] Is the company raising debt/equity despite positive FCF? Why?

### Step 5: SSGR Calculation
- [ ] Calculate **NFAT** = Sales / Net Fixed Assets (each year)
- [ ] Calculate **SSGR** = NFAT x NPM x (1 - DPR) - Depreciation Rate
- [ ] Compare SSGR to actual sales growth rate
  - Green if SSGR > Actual Growth
  - Alert if SSGR < Actual Growth (external capital dependent)
  - Danger if SSGR is negative

### Step 6: Operating Efficiency Ratios
- [ ] **NFAT trend**: Improving, stable, or declining?
  - Alert if declining (new projects less efficient)
  - Note: NFAT > 5 = low barriers to entry; NFAT < 1 = capital trap
- [ ] **ITR trend**: Calculate Sales/Inventory each year
  - Alert if declining (inventory buildup)
- [ ] **Receivables Days**: (Receivables/Sales) x 365
  - Alert if increasing
  - Check receivables > 6 months old (write-off risk)
  - Compare to stated credit period

### Step 7: Tax Analysis
- [ ] Calculate tax payout ratio = Tax / PBT each year
- [ ] Compare to standard corporate tax rate (25-30%)
- [ ] If significantly lower: identify the reason (tax holidays, export benefits)
- [ ] When do tax benefits expire? Impact on future profitability?

### Step 8: Cash Flow Statement Deep Dive
- [ ] Verify interest expense classification (should be CFF, not CFO)
- [ ] Verify no loans misclassified as CFO
- [ ] Verify asset sale proceeds under CFI, not CFO
- [ ] Check for "exceptional items" -- are they truly exceptional or recurring?
- [ ] Reconcile cash flow statement with balance sheet movements

### Decision Gate 2: Proceed only if cash conversion, FCF, and SSGR are satisfactory

---

## PHASE 3: MANAGEMENT QUALITY ASSESSMENT (3-4 hours)

### Step 9: Promoter Behaviour Analysis
- [ ] **Remuneration**: Calculate total promoter family salary as % of PAT
  - Alert if > 10% of PAT
  - Alert if all family members get identical salary regardless of role
  - Check if remuneration exceeds statutory limits
- [ ] **Shareholding**: Track promoter holding over 10 years
  - Alert if declining without valid reason
  - Green if increasing via market purchases
- [ ] **Pledging**: Check promoter share pledge history
  - Any pledging is a concern, especially > 20%
- [ ] **Warrants/Preferential Allotment**:
  - Calculate discount to market price at time of issue
  - Check if promoters sold shares shortly after warrant conversion

### Step 10: Related Party Transaction Forensics
- [ ] List ALL related party transactions from last 5 annual reports
- [ ] For each transaction:
  - [ ] Is the pricing at arm's length?
  - [ ] Does the company benefit or does the promoter benefit?
  - [ ] Are related party receivables growing (money stuck)?
  - [ ] Are loans to related parties at below-market rates?
  - [ ] Are loans from related parties at above-market rates?
- [ ] Check for undisclosed related parties (compare director list with Companies Act filings)
- [ ] Check corporate guarantees for group companies

### Step 11: Board & Governance Quality
- [ ] Are "independent" directors truly independent? Cross-check their other directorships
- [ ] Has the auditor been changed? Why?
- [ ] Are auditor qualifications/observations recurring?
- [ ] Has the Company Secretary resigned?
- [ ] Check for SEBI orders, regulatory penalties
- [ ] Review compliance with Companies Act requirements
- [ ] Check contingent liabilities (disputed taxes, lawsuits, guarantees)

### Step 12: Annual Report Reading (THE MOST IMPORTANT STEP)
- [ ] Read Director's Report for all 10 years
- [ ] Read Management Discussion & Analysis (MD&A) for all 10 years
- [ ] Compare management promises vs actual outcomes
- [ ] Note management commitments -- were they kept?
- [ ] Check for copy-pasted sections across years
- [ ] Look for spelling mistakes and data inconsistencies
- [ ] Read the fine print in notes to accounts

### Step 13: Succession Planning
- [ ] Is the next generation identified and being groomed?
- [ ] Key man risk: What happens if the founder leaves?
- [ ] Are professional managers in place?
- [ ] Check ages of all board members

### Decision Gate 3: Proceed only if management passes integrity test

---

## PHASE 4: BUSINESS ANALYSIS (1-2 hours)

### Step 14: Competitive Position
- [ ] Barriers to entry assessment
- [ ] Customer concentration (top 5 customers as % of revenue)
- [ ] Supplier concentration and dependency
- [ ] Pricing power: Can company pass on cost increases?
- [ ] Compare OPM with industry peers to verify claims

### Step 15: Industry & Regulatory Risk
- [ ] Government policy dependency
- [ ] Anti-dumping duty dependency (check expiry dates)
- [ ] Environmental compliance risk
- [ ] Technology disruption risk
- [ ] Compare company's macro explanations with peer performance

### Step 16: Capital Allocation Track Record
- [ ] List all major investments/acquisitions in last 10 years
- [ ] Were projects completed on time and within budget?
- [ ] Did acquisitions create value or destroy it?
- [ ] Any write-offs of investments? What was the explanation?
- [ ] Is the company investing in non-core activities?

### Decision Gate 4: Proceed only if business model is sustainable

---

## PHASE 5: VALUATION (30 minutes)

### Step 17: Margin of Safety in Price
- [ ] P/E ratio: Calculate earnings yield vs G-Sec rate
- [ ] P/B ratio: Context of ROE quality (high NPM + high NFAT + low leverage preferred)
- [ ] Market cap increase vs retained earnings (10-year value creation)
- [ ] Dividend yield assessment
- [ ] Is this a value trap? (Low P/E but no growth/business quality)

---

## PHASE 6: MONITORING (Ongoing)

### Step 18: Post-Investment Quarterly Review
- [ ] Track receivables days for deterioration
- [ ] Track inventory turnover for deterioration
- [ ] Track debt levels
- [ ] Track NFAT and NPM trends
- [ ] Track promoter shareholding changes
- [ ] Track related party transaction changes
- [ ] Read every quarterly results announcement
- [ ] Read every annual report thoroughly
- [ ] Compare performance with industry peers

---

## RED FLAG SCORING SYSTEM

| Score | Meaning | Action |
|-------|---------|--------|
| 0-2 red flags | Low risk | Proceed with valuation |
| 3-5 red flags | Moderate risk | Deep dive into each flag |
| 6-10 red flags | High risk | Likely avoid unless compelling business |
| 10+ red flags | Very high risk | Avoid |

### Automatic Disqualifiers (Any ONE = Reject)
1. Negative SSGR with sales growth > 15%
2. cCFO < 50% of cPAT over 10 years
3. Credit rating downgrade to sub-investment grade
4. Evidence of promoter fraud/self-dealing
5. Management not sharing profits (no dividends despite positive FCF and cash)

---

## DATA SOURCES

| Source | What to Get |
|--------|-------------|
| Screener.in | Financial data export, peer comparison |
| Company website | Annual reports, investor presentations |
| BSE/NSE | Shareholding pattern, corporate announcements, annual reports |
| CRISIL/CARE/ICRA | Credit rating reports (include capacity data, risk factors) |
| MCA (Ministry of Corporate Affairs) | Director details, charge details, company filings |
| Tofler/Zauba Corp | Related party company information |
| Money Control / Tijori Finance | Industry comparison, historical data |
| SEBI website | Regulatory orders, penalties |
| RoC filings | Annual returns, charge documents |
