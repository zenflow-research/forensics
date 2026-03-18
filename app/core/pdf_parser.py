"""PDF parser for annual reports -- extracts text and tables."""

import re
from pathlib import Path
from io import BytesIO

import pdfplumber
import PyPDF2


def extract_text_pypdf2(file_or_path) -> str:
    """Fast text extraction using PyPDF2."""
    if isinstance(file_or_path, (str, Path)):
        reader = PyPDF2.PdfReader(str(file_or_path))
    else:
        reader = PyPDF2.PdfReader(file_or_path)

    text_parts = []
    for i, page in enumerate(reader.pages):
        t = page.extract_text()
        if t:
            text_parts.append(f"\n--- PAGE {i+1} ---\n{t}")
    return "\n".join(text_parts)


def extract_tables(file_or_path, pages: list[int] | None = None) -> list[dict]:
    """Extract tables from PDF using pdfplumber."""
    if isinstance(file_or_path, (str, Path)):
        pdf = pdfplumber.open(str(file_or_path))
    else:
        pdf = pdfplumber.open(file_or_path)

    tables = []
    target_pages = pages if pages else range(len(pdf.pages))

    for page_num in target_pages:
        if page_num >= len(pdf.pages):
            continue
        page = pdf.pages[page_num]
        page_tables = page.extract_tables()
        for table in page_tables:
            if table and len(table) > 1:
                tables.append({
                    "page": page_num + 1,
                    "headers": table[0],
                    "rows": table[1:],
                })
    pdf.close()
    return tables


def extract_sections(text: str) -> dict:
    """Extract key sections from annual report text."""
    sections = {}
    section_patterns = {
        "directors_report": r"(?i)(director.?s?.?\s*report)",
        "mda": r"(?i)(management\s*discussion|md\s*&?\s*a)",
        "auditors_report": r"(?i)(independent\s*auditor|auditor.?s?.?\s*report)",
        "related_party": r"(?i)(related\s*party\s*(?:transaction|disclosure))",
        "contingent_liabilities": r"(?i)(contingent\s*liabilit)",
        "cash_flow": r"(?i)(cash\s*flow\s*statement|statement\s*of\s*cash\s*flow)",
        "notes_to_accounts": r"(?i)(notes\s*(?:to|forming\s*part)\s*(?:the\s*)?(?:financial|account))",
        "corporate_governance": r"(?i)(corporate\s*governance)",
        "shareholding_pattern": r"(?i)(shareholding\s*pattern)",
        "remuneration": r"(?i)(remuneration|managerial\s*remuneration)",
        "csr": r"(?i)(corporate\s*social\s*responsibility|csr)",
    }

    for name, pattern in section_patterns.items():
        matches = list(re.finditer(pattern, text))
        if matches:
            start = matches[0].start()
            # Take ~5000 chars from section start
            sections[name] = text[start : start + 5000]

    return sections


def search_for_red_flags(text: str) -> list[dict]:
    """Search annual report text for common red flag keywords."""
    red_flag_patterns = [
        (r"(?i)pledge[d]?\s*(?:of\s*)?shares?", "Share Pledging", 3),
        (r"(?i)credit\s*rating\s*(?:downgrad|withdrawn|suspended)", "Credit Rating Issue", 4),
        (r"(?i)(?:auditor|statutory)\s*(?:qualification|emphasis\s*of\s*matter)", "Auditor Qualification", 3),
        (r"(?i)related\s*party\s*(?:transaction|loan|advance)", "Related Party Transaction", 2),
        (r"(?i)corporate\s*guarantee", "Corporate Guarantee", 3),
        (r"(?i)contingent\s*liabilit", "Contingent Liability", 2),
        (r"(?i)(?:delay|default)\s*(?:in\s*)?(?:payment|deposit|statutory\s*dues)", "Payment Delays", 4),
        (r"(?i)exceptional\s*(?:item|loss|expense)", "Exceptional Items", 2),
        (r"(?i)write[\s-]*off", "Write-off", 2),
        (r"(?i)revaluation\s*(?:of\s*)?(?:asset|reserve)", "Asset Revaluation", 3),
        (r"(?i)scheme\s*of\s*arrangement", "Scheme of Arrangement", 2),
        (r"(?i)(?:sebi|regulatory)\s*(?:order|penalty|investigation)", "Regulatory Action", 4),
        (r"(?i)whistle[\s-]*blow", "Whistleblower Complaint", 3),
        (r"(?i)fraud", "Fraud Mention", 4),
        (r"(?i)non[\s-]*comply|non[\s-]*compliance", "Non-Compliance", 3),
        (r"(?i)(?:company\s*secretary|cs)\s*(?:resign|vacancy)", "CS Resignation", 3),
        (r"(?i)warrant[s]?\s*(?:issued|allot)", "Warrant Issuance", 2),
        (r"(?i)inter[\s-]*corporate\s*(?:deposit|loan)", "Inter-Corporate Deposit", 3),
        (r"(?i)derivative\s*(?:loss|contract|instrument)", "Derivative Position", 2),
    ]

    flags = []
    for pattern, label, severity in red_flag_patterns:
        matches = list(re.finditer(pattern, text))
        if matches:
            contexts = []
            for m in matches[:3]:  # Max 3 context snippets per flag
                start = max(0, m.start() - 100)
                end = min(len(text), m.end() + 100)
                contexts.append(text[start:end].strip().replace("\n", " "))
            flags.append({
                "label": label,
                "severity": severity,
                "count": len(matches),
                "contexts": contexts,
            })

    return sorted(flags, key=lambda x: x["severity"], reverse=True)
