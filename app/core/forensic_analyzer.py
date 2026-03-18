"""Core forensic analysis engine implementing Dr. Vijay Malik's framework."""

import math
from dataclasses import dataclass, field


@dataclass
class FinancialData:
    """10-year financial data for a company."""
    company_name: str = ""
    years: list[str] = field(default_factory=list)
    sales: list[float] = field(default_factory=list)
    operating_profit: list[float] = field(default_factory=list)
    net_profit: list[float] = field(default_factory=list)
    tax: list[float] = field(default_factory=list)
    pbt: list[float] = field(default_factory=list)
    cfo: list[float] = field(default_factory=list)
    capex: list[float] = field(default_factory=list)
    net_fixed_assets: list[float] = field(default_factory=list)
    inventory: list[float] = field(default_factory=list)
    trade_receivables: list[float] = field(default_factory=list)
    total_debt: list[float] = field(default_factory=list)
    equity: list[float] = field(default_factory=list)
    dividends_paid: list[float] = field(default_factory=list)
    interest_expense: list[float] = field(default_factory=list)
    depreciation: list[float] = field(default_factory=list)
    promoter_salary: list[float] = field(default_factory=list)
    promoter_holding_pct: list[float] = field(default_factory=list)
    pe_ratio: float = 0.0
    current_market_cap: float = 0.0
    gsec_rate: float = 7.0


@dataclass
class RedFlag:
    category: str
    severity: int  # 1-5
    title: str
    detail: str
    evidence: str


@dataclass
class GreenFlag:
    category: str
    title: str
    detail: str


@dataclass
class ForensicReport:
    company_name: str
    red_flags: list[RedFlag] = field(default_factory=list)
    green_flags: list[GreenFlag] = field(default_factory=list)
    ratios: dict = field(default_factory=dict)
    risk_score: int = 0
    risk_level: str = "Unknown"
    verdict: str = ""
    summary: str = ""


def _safe_div(a, b):
    if b == 0 or b is None:
        return None
    return a / b


def _pct_change(old, new):
    if old == 0:
        return None
    return ((new - old) / abs(old)) * 100


def calculate_ratios(data: FinancialData) -> dict:
    """Calculate all forensic ratios from financial data."""
    n = len(data.years)
    if n == 0:
        return {}

    ratios = {}

    # OPM
    ratios["opm"] = [round(_safe_div(op, s) * 100, 1) if s else None
                     for op, s in zip(data.operating_profit, data.sales)]

    # NPM
    ratios["npm"] = [round(_safe_div(np, s) * 100, 1) if s else None
                     for np, s in zip(data.net_profit, data.sales)]

    # Tax Payout Ratio
    ratios["tax_payout"] = [round(_safe_div(t, p) * 100, 1) if p and p > 0 else None
                            for t, p in zip(data.tax, data.pbt)]

    # NFAT
    ratios["nfat"] = []
    for i in range(n):
        if i == 0:
            nfat = _safe_div(data.sales[i], data.net_fixed_assets[i])
        else:
            avg_nfa = (data.net_fixed_assets[i] + data.net_fixed_assets[i - 1]) / 2
            nfat = _safe_div(data.sales[i], avg_nfa)
        ratios["nfat"].append(round(nfat, 2) if nfat else None)

    # ITR
    ratios["itr"] = []
    for i in range(n):
        if i == 0:
            itr = _safe_div(data.sales[i], data.inventory[i]) if data.inventory[i] else None
        else:
            avg_inv = (data.inventory[i] + data.inventory[i - 1]) / 2
            itr = _safe_div(data.sales[i], avg_inv) if avg_inv else None
        ratios["itr"].append(round(itr, 1) if itr else None)

    # Receivables Days
    ratios["receivables_days"] = [
        round((_safe_div(r, s) or 0) * 365, 0) if s else None
        for r, s in zip(data.trade_receivables, data.sales)
    ]

    # Cumulative PAT and CFO
    ratios["cumulative_pat"] = []
    ratios["cumulative_cfo"] = []
    cum_pat, cum_cfo = 0, 0
    for pat, cfo in zip(data.net_profit, data.cfo):
        cum_pat += pat
        cum_cfo += cfo
        ratios["cumulative_pat"].append(round(cum_pat, 1))
        ratios["cumulative_cfo"].append(round(cum_cfo, 1))

    ratios["total_cpat"] = round(cum_pat, 1)
    ratios["total_ccfo"] = round(cum_cfo, 1)
    ratios["ccfo_cpat_ratio"] = round(_safe_div(cum_cfo, cum_pat), 2) if cum_pat > 0 else None

    # FCF
    ratios["fcf"] = [round(cfo - capex, 1) for cfo, capex in zip(data.cfo, data.capex)]
    ratios["total_fcf"] = round(sum(ratios["fcf"]), 1)
    ratios["total_dividends"] = round(sum(data.dividends_paid), 1)

    # Debt to Equity
    ratios["debt_equity"] = [round(_safe_div(d, e), 2) if e else None
                             for d, e in zip(data.total_debt, data.equity)]

    # Sales Growth
    ratios["sales_growth"] = [None]
    for i in range(1, n):
        g = _pct_change(data.sales[i - 1], data.sales[i])
        ratios["sales_growth"].append(round(g, 1) if g is not None else None)

    # Sales CAGR
    if n >= 2 and data.sales[0] > 0 and data.sales[-1] > 0:
        ratios["sales_cagr"] = round(
            (math.pow(data.sales[-1] / data.sales[0], 1 / (n - 1)) - 1) * 100, 1
        )
    else:
        ratios["sales_cagr"] = None

    # SSGR (simplified)
    ratios["ssgr"] = []
    for i in range(n):
        nfat_val = ratios["nfat"][i]
        npm_val = ratios["npm"][i]
        if nfat_val is None or npm_val is None:
            ratios["ssgr"].append(None)
            continue
        npm_frac = npm_val / 100
        dpr = _safe_div(data.dividends_paid[i], data.net_profit[i]) if data.net_profit[i] > 0 else 0
        dpr = min(max(dpr or 0, 0), 1)
        dep_rate = _safe_div(data.depreciation[i], data.net_fixed_assets[i]) if data.net_fixed_assets[i] else 0
        dep_rate = dep_rate or 0
        ssgr = (nfat_val * npm_frac * (1 - dpr) - dep_rate) * 100
        ratios["ssgr"].append(round(ssgr, 1))

    # Promoter salary as % of PAT
    ratios["promoter_salary_pct"] = [
        round(_safe_div(ps, pat) * 100, 1) if pat and pat > 0 else None
        for ps, pat in zip(data.promoter_salary, data.net_profit)
    ]

    # PBT/NFA ratio
    ratios["pbt_nfa"] = [round(_safe_div(p, nfa) * 100, 1) if nfa else None
                         for p, nfa in zip(data.pbt, data.net_fixed_assets)]

    # Earnings yield
    if data.pe_ratio and data.pe_ratio > 0:
        ratios["earnings_yield"] = round(100 / data.pe_ratio, 1)
    else:
        ratios["earnings_yield"] = None

    return ratios


def analyze(data: FinancialData) -> ForensicReport:
    """Run full forensic analysis and generate report."""
    report = ForensicReport(company_name=data.company_name)
    ratios = calculate_ratios(data)
    report.ratios = ratios
    n = len(data.years)
    if n == 0:
        report.summary = "Insufficient data for analysis."
        return report

    # --- RED FLAG CHECKS ---

    # 1. cCFO vs cPAT
    r = ratios.get("ccfo_cpat_ratio")
    if r is not None and r < 0.8:
        report.red_flags.append(RedFlag(
            "Financial", 4,
            "Poor cash conversion",
            f"cCFO/cPAT ratio is {r}. Only {r*100:.0f}% of profits converted to cash.",
            f"Cumulative PAT: {ratios['total_cpat']}, Cumulative CFO: {ratios['total_ccfo']}"
        ))
    elif r is not None and r >= 1.0:
        report.green_flags.append(GreenFlag(
            "Financial", "Strong cash conversion",
            f"cCFO/cPAT ratio is {r}. Profits fully converting to cash."
        ))

    # 2. Negative FCF
    total_fcf = ratios.get("total_fcf", 0)
    if total_fcf < 0:
        report.red_flags.append(RedFlag(
            "Financial", 4,
            "Negative cumulative FCF",
            f"Total FCF over {n} years is {total_fcf}. Company cannot self-fund growth.",
            f"Total CFO: {ratios['total_ccfo']}, Total Capex: {sum(data.capex):.1f}"
        ))
    elif total_fcf > 0:
        report.green_flags.append(GreenFlag(
            "Financial", "Positive FCF",
            f"Cumulative FCF of {total_fcf} over {n} years."
        ))

    # 3. Dividends from debt
    if total_fcf < 0 and ratios["total_dividends"] > 0:
        report.red_flags.append(RedFlag(
            "Financial", 5,
            "Dividends funded by debt",
            f"FCF is negative ({total_fcf}) but dividends of {ratios['total_dividends']} were paid.",
            "Dividends are effectively being paid from borrowed money."
        ))

    # 4. OPM stability
    opm_values = [v for v in ratios.get("opm", []) if v is not None]
    if opm_values:
        opm_range = max(opm_values) - min(opm_values)
        if opm_range > 15:
            report.red_flags.append(RedFlag(
                "Business", 3,
                "Highly volatile OPM",
                f"OPM range: {min(opm_values):.1f}% to {max(opm_values):.1f}% ({opm_range:.1f} pp spread).",
                "Indicates commodity business with no pricing power."
            ))
        elif opm_range < 5:
            report.green_flags.append(GreenFlag(
                "Business", "Stable OPM",
                f"OPM stable in {min(opm_values):.1f}%-{max(opm_values):.1f}% range. Indicates pricing power."
            ))

    # 5. SSGR vs actual growth
    ssgr_values = [v for v in ratios.get("ssgr", []) if v is not None]
    growth_values = [v for v in ratios.get("sales_growth", []) if v is not None]
    if ssgr_values and growth_values:
        avg_ssgr = sum(ssgr_values) / len(ssgr_values)
        avg_growth = sum(growth_values) / len(growth_values)
        if avg_ssgr < avg_growth * 0.5 and avg_growth > 5:
            report.red_flags.append(RedFlag(
                "Financial", 4,
                "Growth exceeds SSGR",
                f"Avg SSGR ({avg_ssgr:.1f}%) << Avg Growth ({avg_growth:.1f}%). Unsustainable.",
                "Company must continuously raise external capital to sustain growth."
            ))
        elif avg_ssgr > avg_growth:
            report.green_flags.append(GreenFlag(
                "Financial", "SSGR exceeds growth",
                f"Avg SSGR ({avg_ssgr:.1f}%) > Avg Growth ({avg_growth:.1f}%). Self-sustaining."
            ))

    # 6. Rising debt
    if n >= 2 and data.total_debt[0] > 0:
        debt_change = _pct_change(data.total_debt[0], data.total_debt[-1])
        if debt_change is not None and debt_change > 100:
            report.red_flags.append(RedFlag(
                "Financial", 3,
                "Debt more than doubled",
                f"Debt changed from {data.total_debt[0]:.0f} to {data.total_debt[-1]:.0f} ({debt_change:.0f}% increase).",
                "Continuously increasing debt is a structural risk."
            ))
    if data.total_debt[-1] == 0 or (n >= 2 and data.total_debt[-1] < data.total_debt[0] * 0.5):
        report.green_flags.append(GreenFlag(
            "Financial", "Debt-free or declining debt",
            f"Debt reduced from {data.total_debt[0]:.0f} to {data.total_debt[-1]:.0f}."
        ))

    # 7. Receivables days trend
    rd = [v for v in ratios.get("receivables_days", []) if v is not None]
    if len(rd) >= 3:
        if rd[-1] > rd[0] * 1.5 and rd[-1] > 60:
            report.red_flags.append(RedFlag(
                "Efficiency", 3,
                "Receivables days deteriorating",
                f"Receivables days went from {rd[0]:.0f} to {rd[-1]:.0f}.",
                "Declining bargaining power or customers delaying payments."
            ))
        elif rd[-1] < 30:
            report.green_flags.append(GreenFlag(
                "Efficiency", "Excellent receivables management",
                f"Receivables days at {rd[-1]:.0f}. Near cash-and-carry model."
            ))

    # 8. NFAT trend
    nfat_vals = [v for v in ratios.get("nfat", []) if v is not None]
    if nfat_vals:
        if nfat_vals[-1] is not None and nfat_vals[-1] < 1:
            report.red_flags.append(RedFlag(
                "Efficiency", 3,
                "Very low NFAT (capital-intensive)",
                f"NFAT is {nfat_vals[-1]:.2f}. Each Rs 1 of additional sales needs > Rs 1 of new assets.",
                "Capital-intensive business prone to debt trap."
            ))

    # 9. Promoter salary
    ps_pct = [v for v in ratios.get("promoter_salary_pct", []) if v is not None]
    if ps_pct:
        avg_ps = sum(ps_pct) / len(ps_pct)
        if avg_ps > 10:
            report.red_flags.append(RedFlag(
                "Management", 3,
                "High promoter remuneration",
                f"Average promoter salary is {avg_ps:.1f}% of PAT (threshold: 10%).",
                "Promoters extracting excessive value."
            ))
        elif avg_ps < 4 and avg_ps > 0:
            report.green_flags.append(GreenFlag(
                "Management", "Reasonable promoter compensation",
                f"Promoter salary at {avg_ps:.1f}% of PAT. Well aligned with shareholders."
            ))

    # 10. Promoter holding
    if data.promoter_holding_pct and len(data.promoter_holding_pct) >= 2:
        first_ph = data.promoter_holding_pct[0]
        last_ph = data.promoter_holding_pct[-1]
        if first_ph > 0 and last_ph < first_ph - 5:
            report.red_flags.append(RedFlag(
                "Management", 3,
                "Declining promoter holding",
                f"Promoter holding declined from {first_ph:.1f}% to {last_ph:.1f}%.",
                "Promoters reducing stake -- why?"
            ))

    # 11. P/E margin of safety
    ey = ratios.get("earnings_yield")
    if ey is not None:
        if ey < data.gsec_rate:
            report.red_flags.append(RedFlag(
                "Valuation", 2,
                "No margin of safety in valuation",
                f"Earnings yield ({ey:.1f}%) < G-Sec rate ({data.gsec_rate}%). P/E of {data.pe_ratio:.1f} is expensive.",
                "Per Benjamin Graham, earnings yield should exceed risk-free rate."
            ))

    # 12. PBT/NFA vs FD rate
    pbt_nfa = [v for v in ratios.get("pbt_nfa", []) if v is not None]
    if pbt_nfa:
        recent_pbt_nfa = pbt_nfa[-1]
        if recent_pbt_nfa < 7:
            report.red_flags.append(RedFlag(
                "Business", 3,
                "Business earning less than bank FD",
                f"PBT/NFA ratio is {recent_pbt_nfa:.1f}% vs ~7% bank FD rate.",
                "Capital would earn more in a simple fixed deposit."
            ))

    # --- SCORING ---
    total_severity = sum(rf.severity for rf in report.red_flags)
    green_offset = len(report.green_flags) * 2
    report.risk_score = max(0, min(50, total_severity - green_offset))

    if report.risk_score <= 10:
        report.risk_level = "Low Risk"
        report.verdict = "Potentially Investment-Worthy"
    elif report.risk_score <= 20:
        report.risk_level = "Moderate Risk"
        report.verdict = "Requires Deeper Investigation"
    elif report.risk_score <= 35:
        report.risk_level = "High Risk"
        report.verdict = "Likely Avoid"
    else:
        report.risk_level = "Critical Risk"
        report.verdict = "Avoid"

    report.summary = (
        f"{data.company_name}: {len(report.red_flags)} red flags, "
        f"{len(report.green_flags)} green flags. "
        f"Risk Score: {report.risk_score}/50 ({report.risk_level}). "
        f"Verdict: {report.verdict}."
    )

    return report
