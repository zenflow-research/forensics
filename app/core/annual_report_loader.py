"""
Loader for extracted annual report data from D:\\Annual_report_extract.

Reads structured JSON extractions and SQLite database to pull financial data
for any company by ID.
"""

import json
import sqlite3
from pathlib import Path
from dataclasses import dataclass, field

ANNUAL_REPORT_DIR = Path("D:/Annual_report_extract/output")
STOCK_DIR = Path("C:/Users/user/OneDrive/15_Financial_stack/3_Screener/stockDirectory")
DB_PATH = ANNUAL_REPORT_DIR / "extractions.db"


@dataclass
class ExtractedFinancials:
    company_id: str
    company_name: str = ""
    year: str = ""
    unit: str = "lakhs"
    currency: str = "INR"

    # P&L items
    revenue: float = 0
    other_income: float = 0
    total_income: float = 0
    raw_material_cost: float = 0
    employee_cost: float = 0
    finance_cost: float = 0
    depreciation: float = 0
    other_expenses: float = 0
    total_expenses: float = 0
    pbt: float = 0
    tax: float = 0
    pat: float = 0

    # Balance Sheet items
    net_fixed_assets: float = 0
    total_assets: float = 0
    inventory: float = 0
    trade_receivables: float = 0
    cash_and_equivalents: float = 0
    total_debt: float = 0
    equity: float = 0

    # Cash Flow items
    cfo: float = 0
    cfi: float = 0
    cff: float = 0

    # Raw data for deeper analysis
    pnl_raw: dict = field(default_factory=dict)
    bs_raw: dict = field(default_factory=dict)
    cf_raw: dict = field(default_factory=dict)


def list_available_companies() -> list[dict]:
    """List all companies with extracted data."""
    companies = []
    if not ANNUAL_REPORT_DIR.exists():
        return companies

    for company_dir in sorted(ANNUAL_REPORT_DIR.iterdir()):
        if not company_dir.is_dir():
            continue
        company_id = company_dir.name
        years = [y.name for y in company_dir.iterdir() if y.is_dir()]
        if years:
            # Try to get company name from any extraction
            name = _get_company_name(company_id, years[0])
            companies.append({
                "id": company_id,
                "name": name or f"Company {company_id}",
                "years": sorted(years),
            })

    return companies


def _get_company_name(company_id: str, year: str) -> str:
    """Try to extract company name from available data."""
    # Check DB first
    if DB_PATH.exists():
        try:
            conn = sqlite3.connect(str(DB_PATH))
            row = conn.execute(
                "SELECT name FROM companies WHERE company_id=?", (company_id,)
            ).fetchone()
            conn.close()
            if row and row[0]:
                return row[0]
        except Exception:
            pass

    # Check section_map
    section_map = ANNUAL_REPORT_DIR / company_id / year / "section_map.json"
    if section_map.exists():
        try:
            data = json.loads(section_map.read_text(encoding="utf-8"))
            if isinstance(data, dict) and "company_name" in data:
                return data["company_name"]
        except Exception:
            pass

    return ""


def _find_line_item(items: list[dict], keywords: list[str], is_total: bool = None) -> float:
    """Find a line item by keyword matching."""
    for item in items:
        label = (item.get("label") or "").lower()
        matches = any(kw.lower() in label for kw in keywords)
        if matches:
            if is_total is not None and item.get("is_total") != is_total:
                continue
            val = item.get("current_year") or item.get("amount_current") or 0
            return float(val) if val else 0
    return 0


def _find_cf_activity_total(items: list[dict], activity: str) -> float:
    """Find total for a cash flow activity."""
    for item in items:
        act = (item.get("activity") or "").lower()
        label = (item.get("label") or "").lower()
        if activity.lower() in act and ("net" in label or "total" in label or item.get("is_total")):
            val = item.get("amount_current") or 0
            return float(val) if val else 0
    return 0


def load_extractions(company_id: str, year: str = "2025", qualifier: str = "standalone") -> ExtractedFinancials:
    """Load extracted financial data for a company."""
    result = ExtractedFinancials(company_id=company_id, year=year)
    result.company_name = _get_company_name(company_id, year)

    base_dir = ANNUAL_REPORT_DIR / company_id / year / "extractions"
    if not base_dir.exists():
        # Try extractions_v2
        base_dir = ANNUAL_REPORT_DIR / company_id / year / "extractions_v2"
    if not base_dir.exists():
        return result

    # Load P&L
    pnl_file = base_dir / f"profit_and_loss_{qualifier}.json"
    if pnl_file.exists():
        try:
            pnl = json.loads(pnl_file.read_text(encoding="utf-8"))
            data = pnl.get("data", {})
            result.unit = data.get("unit", "lakhs")
            result.currency = data.get("currency", "INR")
            result.pnl_raw = data

            income_items = data.get("income", [])
            expense_items = data.get("expenses", [])
            tax_items = data.get("tax", data.get("tax_expense", []))
            if isinstance(tax_items, (int, float)):
                result.tax = float(tax_items)
                tax_items = []

            result.revenue = _find_line_item(income_items, ["revenue from operations", "net sales"], is_total=True)
            if result.revenue == 0:
                result.revenue = _find_line_item(income_items, ["revenue from operations", "net sales"])
            result.other_income = _find_line_item(income_items, ["other income"])
            result.total_income = _find_line_item(income_items, ["total income"], is_total=True)

            result.raw_material_cost = _find_line_item(expense_items, ["raw material", "material consumed", "cost of material"])
            result.employee_cost = _find_line_item(expense_items, ["employee benefit", "employee cost", "salaries"])
            result.finance_cost = _find_line_item(expense_items, ["finance cost", "interest"])
            result.depreciation = _find_line_item(expense_items, ["depreciation", "amortization"])
            result.other_expenses = _find_line_item(expense_items, ["other expense"])
            result.total_expenses = _find_line_item(expense_items, ["total expense"], is_total=True)

            # PBT/PAT
            bottom_items = data.get("profit_summary", data.get("bottom_line", []))
            if isinstance(bottom_items, list):
                result.pbt = _find_line_item(bottom_items, ["profit before tax", "pbt"])
                result.pat = _find_line_item(bottom_items, ["profit after tax", "pat", "profit for the"])
                if not result.tax and isinstance(tax_items, list):
                    result.tax = _find_line_item(tax_items, ["total tax", "tax expense"], is_total=True)
                    if result.tax == 0:
                        result.tax = _find_line_item(tax_items, ["current tax"])

            # Fallback: calculate if missing
            if result.pbt == 0 and result.total_income > 0 and result.total_expenses > 0:
                result.pbt = result.total_income - result.total_expenses
            if result.pat == 0 and result.pbt > 0:
                result.pat = result.pbt - result.tax

        except Exception as e:
            pass

    # Load Balance Sheet
    bs_file = base_dir / f"balance_sheet_{qualifier}.json"
    if bs_file.exists():
        try:
            bs = json.loads(bs_file.read_text(encoding="utf-8"))
            data = bs.get("data", {})
            result.bs_raw = data

            assets = data.get("assets", data.get("non_current_assets", []))
            if isinstance(assets, list):
                result.net_fixed_assets = _find_line_item(assets, ["property plant", "net fixed asset", "tangible asset"])
                result.inventory = _find_line_item(assets, ["inventor"])
                result.trade_receivables = _find_line_item(assets, ["trade receivable"])
                result.cash_and_equivalents = _find_line_item(assets, ["cash and cash equivalent", "cash and bank"])
                result.total_assets = _find_line_item(assets, ["total asset"], is_total=True)

            liabilities = data.get("liabilities", data.get("equity_and_liabilities", []))
            if isinstance(liabilities, list):
                borrowings = _find_line_item(liabilities, ["borrowing", "long term borrowing", "short term borrowing"])
                result.total_debt = borrowings
                result.equity = _find_line_item(liabilities, ["total equity", "shareholder", "equity attributable"])

        except Exception:
            pass

    # Load Cash Flow
    cf_file = base_dir / f"cash_flow_{qualifier}.json"
    if cf_file.exists():
        try:
            cf = json.loads(cf_file.read_text(encoding="utf-8"))
            data = cf.get("data", {})
            result.cf_raw = data

            items = data.get("items", data.get("operating", []) + data.get("investing", []) + data.get("financing", []))
            if isinstance(items, list):
                result.cfo = _find_cf_activity_total(items, "operating")
                result.cfi = _find_cf_activity_total(items, "investing")
                result.cff = _find_cf_activity_total(items, "financing")

        except Exception:
            pass

    return result


def load_annual_report_pdf_path(company_id: str, year: str = "2025") -> Path | None:
    """Find the annual report PDF path for a company."""
    ar_dir = STOCK_DIR / company_id / "annual_report"
    if not ar_dir.exists():
        return None
    pdfs = list(ar_dir.glob(f"*{year}*.pdf")) + list(ar_dir.glob("*.pdf"))
    return pdfs[0] if pdfs else None


def get_all_extracted_json(company_id: str, year: str = "2025") -> dict:
    """Load all available extracted JSONs for a company."""
    result = {}
    base = ANNUAL_REPORT_DIR / company_id / year

    for subdir in ["extractions", "extractions_v2"]:
        d = base / subdir
        if d.exists():
            for f in d.glob("*.json"):
                try:
                    result[f.stem] = json.loads(f.read_text(encoding="utf-8"))
                except Exception:
                    pass
    return result
