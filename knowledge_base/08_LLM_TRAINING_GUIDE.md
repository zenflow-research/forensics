# LLM Training & Fine-Tuning Guide
## Training a Local Model on Forensic Accounting Data

---

## OBJECTIVE
Train a local LLM that can:
1. Scrape and extract relevant data from annual reports and web sources
2. Apply Dr. Vijay Malik's "Peaceful Investing" forensic framework
3. Identify red flags and manipulation patterns
4. Generate forensic analysis reports for any Indian listed company

---

## APPROACH 1: RAG (Retrieval-Augmented Generation) -- RECOMMENDED START

### Why RAG First
- No fine-tuning needed (faster to deploy)
- Uses the knowledge base documents as retrieval corpus
- Works with any local LLM (Llama 3, Mistral, Qwen, etc.)
- Can be updated without retraining

### Architecture
```
[Annual Report PDF] --> [PDF Parser] --> [Text Chunks]
                                              |
                                              v
[Knowledge Base Docs] --> [Embedding Model] --> [Vector Store (ChromaDB/FAISS)]
                                              |
                                              v
[User Query] --> [Retriever] --> [Top-K Relevant Chunks] --> [LLM] --> [Analysis Report]
```

### Implementation Steps
1. **Chunk the knowledge base**: Split all 8 knowledge base files + extracted PDF texts into overlapping chunks (512-1024 tokens)
2. **Create embeddings**: Use a local embedding model (e.g., `all-MiniLM-L6-v2` or `bge-large-en`)
3. **Build vector store**: ChromaDB or FAISS for local storage
4. **Query pipeline**: User asks about a company -> retrieve relevant forensic patterns + examples -> LLM generates analysis
5. **Annual report ingestion**: Parse new annual reports -> extract key data -> compare against stored patterns

### Tools
- **LLM**: Llama 3.1 8B/70B, Mistral 7B, or Qwen 2.5 (via Ollama or llama.cpp)
- **Embedding**: `sentence-transformers/all-MiniLM-L6-v2`
- **Vector Store**: ChromaDB (easy) or FAISS (fast)
- **Framework**: LangChain or LlamaIndex
- **PDF Parsing**: PyPDF2, pdfplumber, or marker-pdf (for better table extraction)

---

## APPROACH 2: FINE-TUNING (Advanced)

### Training Data Format

#### Format 1: Instruction-Following (Alpaca Style)
```json
{
  "instruction": "Analyze the cash flow quality of a company with the following data: Cumulative PAT over 10 years is Rs 528 cr, Cumulative CFO is Rs 176 cr, Capex is Rs 1,062 cr, and debt increased from Rs 77 cr to Rs 1,402 cr.",
  "input": "",
  "output": "This company shows severe cash flow quality issues:\n\n1. **cCFO/cPAT Ratio**: Rs 176 cr / Rs 528 cr = 0.33. This means only 33% of reported profits converted to actual cash. The remaining 67% is stuck in working capital - a major red flag.\n\n2. **Free Cash Flow**: FCF = CFO (Rs 176 cr) - Capex (Rs 1,062 cr) = NEGATIVE Rs 886 cr. The company cannot fund its growth from operations.\n\n3. **Debt Dependency**: Debt increased 18x from Rs 77 cr to Rs 1,402 cr to fund the gap between CFO and Capex.\n\n4. **Pattern Match**: This matches the MBL Infrastructure pattern from Dr. Malik's analysis - a company showing accounting profits while being deeply cash-negative, funding growth entirely through debt.\n\n**Verdict**: Critical risk. The company's reported profits are largely paper profits not backed by cash. The massive debt buildup suggests potential financial distress ahead."
}
```

#### Format 2: Multi-Turn Chat
```json
{
  "conversations": [
    {"role": "user", "content": "What are the red flags if a company's promoter takes Rs 14.21 cr salary which is exactly the maximum allowed by Companies Act, and all three family members get exactly Rs 2.84 cr each?"},
    {"role": "assistant", "content": "This exhibits multiple red flags from Dr. Malik's framework:\n\n1. **Maximum statutory salary**: Taking remuneration 'down to the last rupee' of what's legally allowed signals a mindset of extracting maximum value rather than reasonable compensation. This was seen in Balaji Amines and Bharat Rasayan.\n\n2. **Identical family salaries**: When family members of vastly different ages, qualifications, and experience all receive the exact same salary, it suggests the remuneration is not performance-based but an entitlement-based extraction. Ruchira Papers showed this pattern with 8 relatives all getting Rs 36.2 lac regardless of role.\n\n3. **Combined impact**: Calculate total family remuneration as % of PAT. If it exceeds 10%, this is a significant concern. In PIX Transmissions, promoter family took 40-60% of PAT.\n\n4. **Watch for the Vicious Cycle**: High salaries can lead to cash shortfall, after which promoters 'helpfully' lend money back at above-market interest rates (10-12%), earning income on both salary and interest."}
  ]
}
```

#### Format 3: Structured Q&A for Specific Checks
```json
[
  {
    "question": "How do I check if a company is paying dividends from borrowed money?",
    "answer": "Calculate Free Cash Flow (FCF) = CFO - Capex for each year. If FCF is negative but dividends are being paid, the dividends are effectively funded by debt. Example: KRBL had negative FCF of Rs -300 cr over 10 years but paid Rs 133 cr in dividends. This means Rs 433 cr of debt was raised to cover both capex shortfall and dividend payments. Check: (1) Is cumulative FCF positive? (2) Are cumulative dividends < cumulative FCF? If either fails, dividends are debt-funded."
  },
  {
    "question": "What is the Self-Sustainable Growth Rate (SSGR) and how do I calculate it?",
    "answer": "SSGR is the maximum growth rate a company can sustain using only internally generated funds, without additional debt or equity. Formula: SSGR = NFAT x NPM x (1 - Dividend Payout Ratio) - Depreciation Rate. Where: NFAT = Sales/Net Fixed Assets, NPM = Net Profit Margin, DPR = Dividends/PAT. Interpretation: If SSGR > actual sales growth rate, the company can self-fund (GREEN). If SSGR < actual growth, external capital is needed (RED). If SSGR is negative, the business is destroying capital (DANGER). Limitation: SSGR doesn't account for working capital, so always cross-check with cCFO vs cPAT. Example: Finolex Cables had SSGR of 25-35% vs actual growth of 5-7% = massively self-sustaining. PIX Transmissions had SSGR of -5% = business destroying value."
  },
  {
    "question": "How do I detect credit rating shopping?",
    "answer": "Credit rating shopping occurs when a company switches rating agencies after receiving negative outlook or downgrade. Pattern: (1) Company has rating from Agency A, (2) Agency A downgrades or changes outlook to negative, (3) Company stops cooperating with Agency A, (4) Company gets rating from Agency B (usually a less reputed agency). Examples: Omkar Speciality switched from CRISIL to Brickwork after CRISIL downgraded to BB+. Granules India switched from CARE to ICRA to India Ratings. Albert David stopped cooperating with CRISIL after outlook changed from Positive to Stable. Detection: Check credit rating history across all agencies; note any gaps where an agency's rating was 'withdrawn' or 'suspended'; check if the company cooperated with all agencies or selectively stopped."
  }
]
```

### Training Data Categories to Generate

| Category | # of Examples | Source |
|----------|--------------|-------|
| Red flag identification | 200+ | 70 red flags x 3 variations each |
| Financial ratio calculation & interpretation | 100+ | 15 ratios x 7 interpretations |
| Cash flow forensics | 80+ | Real company examples + variations |
| Related party analysis | 60+ | From case studies |
| Management assessment | 50+ | From case studies |
| Annual report reading | 40+ | Specific extraction tasks |
| Pattern matching (fraud detection) | 50+ | 7 fraud patterns x 7 variations |
| Sector-specific analysis | 30+ | 8 sectors x 4 questions |
| Peer comparison | 20+ | Industry comparison templates |
| Valuation & margin of safety | 30+ | Graham framework applications |
| **Total** | **~660+** | |

---

## APPROACH 3: AGENTIC WORKFLOW (Most Powerful)

### Architecture
```
[User: "Analyze Company X"]
        |
        v
[Orchestrator Agent]
   |          |           |            |
   v          v           v            v
[Scraper   [Financial   [Annual      [News
 Agent]     Agent]       Report       Agent]
              |          Agent]         |
              v            |            v
           [Calculate    [Read &      [Search for
            ratios,      extract      regulatory
            SSGR,        red flags]   actions,
            FCF]                      fraud cases]
              |            |            |
              v            v            v
         [Forensic Analysis Synthesis Agent]
                        |
                        v
              [Final Report with Risk Score]
```

### Agent Capabilities

**Scraper Agent:**
- Fetch financial data from Screener.in, Trendlyne, Tijori
- Download annual reports from BSE/NSE
- Extract shareholding patterns
- Get credit rating reports

**Financial Analysis Agent:**
- Calculate all 15+ financial ratios
- Compute SSGR, FCF, cCFO/cPAT
- Perform 10-year trend analysis
- Compare to sector benchmarks

**Annual Report Agent:**
- Parse PDF annual reports
- Extract Notes to Accounts data
- Identify related party transactions
- Flag inconsistencies and errors
- Compare management promises vs outcomes

**News/Regulatory Agent:**
- Search for SEBI orders
- Check for court cases
- Find media reports on fraud/issues
- Verify promoter backgrounds

**Synthesis Agent:**
- Combine all inputs
- Match against known fraud patterns
- Generate forensic risk score
- Produce structured report

---

## DATA SOURCES FOR SCRAPING

### Structured Financial Data
| Source | Data Available | Access Method |
|--------|---------------|--------------|
| Screener.in | 10-year financials, peer comparison | Web scraping / API |
| Trendlyne | Ratios, technicals, fundamentals | Web scraping |
| Tijori Finance | Detailed financials, segments | Web scraping |
| BSE India | Annual reports, shareholding, announcements | Public API / scraping |
| NSE India | Same as BSE + corporate governance reports | Public API / scraping |

### Qualitative Data
| Source | Data Available | Access Method |
|--------|---------------|--------------|
| MCA (Ministry of Corporate Affairs) | Director details, charge documents, annual returns | Portal access |
| SEBI | Orders, circulars, investigation outcomes | Public website |
| CRISIL/CARE/ICRA | Credit rating reports with capacity data | Rating agency websites |
| Company websites | Annual reports, investor presentations, press releases | Direct download |
| Court databases | NCLT, High Court orders | Legal databases |

### Annual Report Key Sections to Extract
1. Director's Report (management promises, outlook)
2. Management Discussion & Analysis (business strategy, risks)
3. Notes to Financial Statements (accounting policies, related parties)
4. Auditor's Report (qualifications, emphasis of matter, CARO)
5. Corporate Governance Report (board details, remuneration, compliance)
6. Secretarial Audit Report (compliance issues)
7. Cash Flow Statement (verify classifications)
8. Shareholding Pattern (promoter changes, pledging)
9. Segment Reporting (business-wise performance)
10. Contingent Liabilities (hidden risks)

---

## RECOMMENDED MODEL CHOICES

### For RAG (No Fine-Tuning)
| Model | Size | Good For |
|-------|------|----------|
| Llama 3.1 8B | 8B | Quick analysis, runs on consumer GPU |
| Mistral 7B | 7B | Good reasoning, fast inference |
| Qwen 2.5 14B | 14B | Strong on financial analysis |
| Llama 3.1 70B | 70B | Best quality, needs server GPU |

### For Fine-Tuning
| Model | Method | Hardware Needed |
|-------|--------|-----------------|
| Llama 3.1 8B | QLoRA | 24GB VRAM (RTX 4090) |
| Mistral 7B | QLoRA | 24GB VRAM |
| Phi-3 Mini 3.8B | Full fine-tune | 16GB VRAM |
| Qwen 2.5 7B | QLoRA | 24GB VRAM |

### Fine-Tuning Tools
- **Unsloth**: Fastest QLoRA training
- **Axolotl**: Flexible, supports many formats
- **LLaMA-Factory**: GUI-based, easy to use
- **TRL (Transformers Reinforcement Learning)**: HuggingFace official

---

## EVALUATION METRICS

### Forensic Analysis Quality
1. **Red Flag Detection Rate**: % of known red flags correctly identified from test cases
2. **False Positive Rate**: % of clean companies flagged incorrectly
3. **Pattern Matching Accuracy**: Correct identification of manipulation techniques
4. **Ratio Calculation Accuracy**: Correct computation of SSGR, FCF, NFAT, etc.
5. **Report Quality**: Clarity, actionability, and accuracy of generated reports

### Test Set
Use 10 companies from the case studies as test set:
- 5 with known severe red flags (Omkar, MBL Infrastructure, PIX, Virat Crane, Nandan Denim)
- 5 with generally positive assessments (MRF, Divi's Labs, TVS Srichakra, Finolex Cables, AIA Engineering)
- Model should correctly classify 8/10 minimum
