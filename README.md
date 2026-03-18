# Forensic Accounting Intelligence Platform

A comprehensive forensic accounting analysis platform built from **Dr. Vijay Malik's "Peaceful Investing" methodology** — distilled from 2,774 pages of forensic analysis covering 80+ Indian companies.

## Features

| Module | Description |
|--------|-------------|
| **Forensic Q&A** | RAG-powered semantic search over the complete knowledge base |
| **Company Screener** | Input financial data, get automated forensic analysis with risk scoring |
| **Annual Report Analyzer** | Upload PDF annual reports for instant red flag scanning |
| **Portfolio Audit** | Analyze entire portfolios with aggregate risk scoring |
| **Knowledge Explorer** | Browse 74 red flags, 20+ manipulation techniques, 80+ case studies |
| **Prompt Generator** | Generate ready-to-use forensic prompts for any LLM |

## Knowledge Base

| File | Contents |
|------|----------|
| `01_FRAMEWORK.md` | Complete 5-pillar forensic methodology |
| `02_RED_FLAGS_TAXONOMY.md` | 74 categorized red flags with real examples |
| `03_GREEN_FLAGS.md` | Positive indicators and ideal company profile |
| `04_COMPANY_CASE_STUDIES.md` | All 80+ companies indexed by outcome |
| `05_CHECKLIST.md` | 18-step analysis protocol with decision gates |
| `06_PROMPT_TEMPLATES.md` | 10+ LLM prompts for company analysis |
| `07_MANIPULATION_TECHNIQUES.md` | 20+ manipulation techniques encyclopedia |
| `08_LLM_TRAINING_GUIDE.md` | RAG, fine-tuning, and agentic workflow designs |
| `09_ADDITIONAL_USE_CASES.md` | 10 additional use cases |
| `10_KEY_CONCEPTS_GLOSSARY.md` | 50+ terms and Dr. Malik's principles |

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Run the app
cd app
streamlit run Forensics_Home.py
```

## Core Forensic Framework

**5 Pillars of Analysis:**
1. **Financial & Business** — Sales growth, OPM stability, cCFO vs cPAT, FCF
2. **Operating Efficiency** — NFAT, ITR, Receivables Days
3. **Business Margin of Safety** — SSGR vs actual growth
4. **Price Margin of Safety** — P/E ratio, earnings yield vs G-Sec rate
5. **Management Quality** — Promoter salary, related party transactions, governance

**Key Formulas:**
```
SSGR = NFAT x NPM x (1-DPR) - Depreciation Rate
FCF = CFO - Capex
NFAT = Sales / Net Fixed Assets
Earnings Yield = 1 / PE Ratio
```

## Tech Stack

- **Frontend**: Streamlit (multi-page app)
- **RAG Engine**: ChromaDB + sentence-transformers (all-MiniLM-L6-v2)
- **Analysis Engine**: Custom Python forensic analyzer
- **PDF Parsing**: PyPDF2 + pdfplumber
- **Visualization**: Plotly

## Source Material

Built from Dr. Vijay Malik's published forensic accounting analyses:
- Case Studies Ebook (178 pages, 20 companies)
- Company Analysis Volumes 1-6, 8-9 (2,596 pages, 60+ companies)

## License

For educational and research purposes.
