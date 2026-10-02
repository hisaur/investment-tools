#!/usr/bin/env python3
"""
Stock Deep Dive — Financial Statement & Valuation Data Extractor
Fetches live market data, 5-year financials, peer multiples, and sector cost of capital
via yfinance, computes Piotroski F-score, Altman Z-score, ROIC, and financial metrics,
and generates a token-efficient structured markdown document (stock_digest.md).
"""

import argparse
import math
import os
import sys
from datetime import datetime
from typing import Dict, List, Any, Optional

try:
    import yfinance as yf
    import pandas as pd
except ImportError as e:
    print(f"Error: Missing required library: {e}")
    print("Install required libraries: pip install yfinance pandas")
    sys.exit(1)


# Sector-level typical cost of capital / WACC benchmarks
SECTOR_COST_OF_CAPITAL_BENCHMARKS = {
    "Utilities": {"wacc_range": "6.0% – 7.5%", "beta_typical": "0.60 – 0.90", "type": "Regulated / Concession Infrastructure"},
    "Real Estate": {"wacc_range": "6.5% – 8.0%", "beta_typical": "0.70 – 1.00", "type": "Capital Intensive / Rate Sensitive"},
    "Consumer Defensive": {"wacc_range": "7.0% – 8.5%", "beta_typical": "0.65 – 0.85", "type": "Non-Cyclical Compounder"},
    "Healthcare": {"wacc_range": "7.5% – 9.0%", "beta_typical": "0.75 – 1.05", "type": "Defensive Growth / Regulated"},
    "Industrials": {"wacc_range": "8.0% – 9.5%", "beta_typical": "0.90 – 1.20", "type": "Cyclical / Capital Goods"},
    "Communication Services": {"wacc_range": "8.5% – 10.0%", "beta_typical": "0.95 – 1.25", "type": "Platform & Advertising"},
    "Financial Services": {"wacc_range": "8.5% – 10.5%", "beta_typical": "1.00 – 1.30", "type": "Financial Intermediation"},
    "Technology": {"wacc_range": "9.0% – 11.0%", "beta_typical": "1.10 – 1.40", "type": "High Reinvestment / Innovation"},
    "Consumer Cyclical": {"wacc_range": "8.5% – 10.5%", "beta_typical": "1.05 – 1.35", "type": "Discretionary / Macro Sensitive"},
    "Basic Materials": {"wacc_range": "8.5% – 10.5%", "beta_typical": "1.00 – 1.35", "type": "Commodity / Capital Intensive"},
    "Energy": {"wacc_range": "9.0% – 11.5%", "beta_typical": "1.05 – 1.45", "type": "Cyclical / Commodity Driven"},
}

# Representative sector / industry peer baskets for instant relative comparison
SECTOR_PEER_BASKETS = {
    "Utilities": ["WM", "RSG", "AWK", "ENGIE.PA"],
    "Waste Management": ["WM", "RSG", "CWST"],
    "Water Utilities": ["AWK", "AWR", "VIE.PA"],
    "Technology": ["MSFT", "GOOGL", "ORCL", "SAP"],
    "Semiconductors": ["NVDA", "ASML", "TSM", "AMD"],
    "Financial Services": ["MA", "V", "SPGI", "ADYEN.AS"],
    "Healthcare": ["UNH", "ELV", "CVS", "JNJ"],
    "Industrials": ["UBER", "CAT", "UNP", "GE"],
    "Communication Services": ["GOOGL", "META", "NFLX", "DIS"],
    "Consumer Cyclical": ["AMZN", "MELI", "COST", "HD"],
    "Consumer Defensive": ["PG", "KO", "PEP", "WMT"],
    "Energy": ["XOM", "CVX", "SHEL", "TTE"],
    "Basic Materials": ["LIN", "APD", "ECL", "SHW"],
}

CURRENCY_SYMBOLS = {
    "USD": "$",
    "EUR": "€",
    "GBP": "£",
    "GBp": "p",
    "CAD": "C$",
    "AUD": "A$",
    "CHF": "CHF ",
    "JPY": "¥",
    "HKD": "HK$",
    "SEK": "kr ",
    "NOK": "kr ",
    "DKK": "kr ",
}


def get_currency_symbol(curr_code: Optional[str]) -> str:
    """Return appropriate currency symbol for a 3-letter currency code."""
    if not curr_code:
        return "$"
    return CURRENCY_SYMBOLS.get(curr_code.upper(), f"{curr_code} ")


def format_num(val: Any, is_curr: bool = True, is_pct: bool = False, decimals: int = 2, curr_code: str = "USD") -> str:
    """Format large numbers into human-readable strings (e.g. $12.4B, €350.2M, 14.5%)."""
    if val is None or pd.isna(val) or val == "N/A" or val == "":
        return "—"
    try:
        fval = float(val)
        if math.isnan(fval) or math.isinf(fval):
            return "—"
        if is_pct:
            pct_val = fval * 100 if abs(fval) < 1.0 else fval
            return f"{pct_val:.{decimals}f}%"
        
        prefix = get_currency_symbol(curr_code) if is_curr else ""
        abs_val = abs(fval)
        sign = "-" if fval < 0 else ""
        
        if abs_val >= 1e12:
            return f"{sign}{prefix}{abs_val / 1e12:.{decimals}f}T"
        elif abs_val >= 1e9:
            return f"{sign}{prefix}{abs_val / 1e9:.{decimals}f}B"
        elif abs_val >= 1e6:
            return f"{sign}{prefix}{abs_val / 1e6:.{decimals}f}M"
        elif abs_val >= 1e3:
            return f"{sign}{prefix}{abs_val / 1e3:.{decimals}f}K"
        else:
            return f"{sign}{prefix}{abs_val:.{decimals}f}"
    except (ValueError, TypeError):
        return str(val)


def safe_get(df: pd.DataFrame, row_labels: List[str], col_idx: int = 0) -> Optional[float]:
    """Extract a metric from a DataFrame across multiple possible row labels."""
    if df is None or df.empty:
        return None
    for label in row_labels:
        if label in df.index:
            try:
                val = df.loc[label].iloc[col_idx]
                if pd.notna(val):
                    return float(val)
            except Exception:
                continue
    return None


def extract_robust_capex(cashflow: pd.DataFrame, info: dict, col_idx: int = 0) -> float:
    """
    Robust CapEx extractor supporting US GAAP and IFRS/European filing conventions.
    Checks PPE purchases, capital expenditures, investments in fixed assets,
    and cash flow from investing fallbacks.
    """
    if cashflow is None or cashflow.empty:
        # Fallback to info freeCashflow if available
        cfo_info = info.get("operatingCashflow") or 0
        fcf_info = info.get("freeCashflow") or 0
        if cfo_info and fcf_info and cfo_info > fcf_info:
            return abs(cfo_info - fcf_info)
        return 0.0

    # Primary US / Standard labels
    capex_labels = [
        "Capital Expenditure",
        "Capital Expenditures",
        "Capital Expenditure Reported",
        "Purchase Of Property Plant And Equipment",
        "Purchase Of PPE",
        "Investments In Property Plant And Equipment",
        "Net PPE Purchase And Sale",
    ]
    val = safe_get(cashflow, capex_labels, col_idx)
    if val is not None and val != 0.0:
        return abs(val)

    # IFRS / Concession / European filing fallbacks
    if "Purchase Of Investment" in cashflow.index:
        inv_val = safe_get(cashflow, ["Purchase Of Investment"], col_idx)
        if inv_val is not None and inv_val != 0.0:
            return abs(inv_val)

    # Investing Cash Flow fallback
    if "Investing Cash Flow" in cashflow.index:
        icf = safe_get(cashflow, ["Investing Cash Flow"], col_idx)
        if icf is not None and icf != 0.0:
            return abs(icf)

    # Cross-check with info
    if col_idx == 0:
        cfo_info = info.get("operatingCashflow") or safe_get(cashflow, ["Operating Cash Flow"], 0) or 0
        fcf_info = info.get("freeCashflow")
        if cfo_info and fcf_info is not None and cfo_info > fcf_info:
            return abs(cfo_info - fcf_info)

    return 0.0


def calculate_piotroski_f_score(info: dict, bs: pd.DataFrame, is_: pd.DataFrame, cf: pd.DataFrame) -> Dict[str, Any]:
    """Calculate 9-point Piotroski F-score."""
    score = 0
    breakdown = {}

    try:
        # 1. Net Income > 0
        net_income_0 = safe_get(is_, ["Net Income", "Net Income Common Stockholders", "Net Income Continuous Operations"], 0)
        if net_income_0 is None:
            net_income_0 = info.get("netIncomeToCommon")
        breakdown["Positive Net Income"] = net_income_0 is not None and net_income_0 > 0
        if breakdown["Positive Net Income"]:
            score += 1

        # 2. Operating Cash Flow > 0
        cfo_0 = safe_get(cf, ["Operating Cash Flow", "Total Cash From Operating Activities", "Cash Flows from Operating Activities"], 0)
        if cfo_0 is None:
            cfo_0 = info.get("operatingCashflow")
        breakdown["Positive Operating Cash Flow"] = cfo_0 is not None and cfo_0 > 0
        if breakdown["Positive Operating Cash Flow"]:
            score += 1

        # 3. Delta ROA > 0
        total_assets_0 = safe_get(bs, ["Total Assets"], 0)
        total_assets_1 = safe_get(bs, ["Total Assets"], 1)
        net_income_1 = safe_get(is_, ["Net Income", "Net Income Common Stockholders"], 1)
        roa_0 = (net_income_0 / total_assets_0) if (net_income_0 and total_assets_0) else None
        roa_1 = (net_income_1 / total_assets_1) if (net_income_1 and total_assets_1) else None
        breakdown["ROA Improvement"] = (roa_0 is not None and roa_1 is not None and roa_0 > roa_1) or (roa_0 is not None and roa_0 > 0)
        if breakdown["ROA Improvement"]:
            score += 1

        # 4. Accruals: CFO > Net Income
        breakdown["CFO > Net Income (Quality)"] = (cfo_0 is not None and net_income_0 is not None and cfo_0 > net_income_0)
        if breakdown["CFO > Net Income (Quality)"]:
            score += 1

        # 5. Delta Long Term Debt <= 0
        lt_debt_0 = safe_get(bs, ["Long Term Debt", "Long Term Debt And Capital Lease Obligation"], 0) or 0
        lt_debt_1 = safe_get(bs, ["Long Term Debt", "Long Term Debt And Capital Lease Obligation"], 1) or 0
        breakdown["Long Term Debt Reduced / Flat"] = lt_debt_0 <= lt_debt_1
        if breakdown["Long Term Debt Reduced / Flat"]:
            score += 1

        # 6. Delta Current Ratio > 0
        ca_0 = safe_get(bs, ["Current Assets", "Total Current Assets"], 0)
        cl_0 = safe_get(bs, ["Current Liabilities", "Total Current Liabilities"], 0)
        ca_1 = safe_get(bs, ["Current Assets", "Total Current Assets"], 1)
        cl_1 = safe_get(bs, ["Current Liabilities", "Total Current Liabilities"], 1)
        cr_0 = (ca_0 / cl_0) if (ca_0 and cl_0) else None
        cr_1 = (ca_1 / cl_1) if (ca_1 and cl_1) else None
        breakdown["Current Ratio Improved"] = (cr_0 is not None and cr_1 is not None and cr_0 >= cr_1)
        if breakdown["Current Ratio Improved"]:
            score += 1

        # 7. No New Shares Issued (Delta Shares <= 0)
        shares_0 = safe_get(bs, ["Common Stock Shares Issued", "Ordinary Shares Number", "Share Issued"], 0) or safe_get(is_, ["Diluted Average Shares", "Basic Average Shares"], 0)
        shares_1 = safe_get(bs, ["Common Stock Shares Issued", "Ordinary Shares Number", "Share Issued"], 1) or safe_get(is_, ["Diluted Average Shares", "Basic Average Shares"], 1)
        breakdown["No Dilution"] = (shares_0 is not None and shares_1 is not None and shares_0 <= shares_1 * 1.01)
        if breakdown["No Dilution"]:
            score += 1

        # 8. Delta Gross Margin > 0
        rev_0 = safe_get(is_, ["Total Revenue", "Operating Revenue"], 0)
        gp_0 = safe_get(is_, ["Gross Profit"], 0)
        rev_1 = safe_get(is_, ["Total Revenue", "Operating Revenue"], 1)
        gp_1 = safe_get(is_, ["Gross Profit"], 1)
        gm_0 = (gp_0 / rev_0) if (gp_0 and rev_0) else None
        gm_1 = (gp_1 / rev_1) if (gp_1 and rev_1) else None
        breakdown["Gross Margin Improved"] = (gm_0 is not None and gm_1 is not None and gm_0 >= gm_1)
        if breakdown["Gross Margin Improved"]:
            score += 1

        # 9. Delta Asset Turnover > 0
        at_0 = (rev_0 / total_assets_0) if (rev_0 and total_assets_0) else None
        at_1 = (rev_1 / total_assets_1) if (rev_1 and total_assets_1) else None
        breakdown["Asset Turnover Improved"] = (at_0 is not None and at_1 is not None and at_0 >= at_1)
        if breakdown["Asset Turnover Improved"]:
            score += 1

    except Exception as e:
        breakdown["error"] = str(e)

    return {"score": score, "max": 9, "breakdown": breakdown}


def calculate_altman_z_score(info: dict, bs: pd.DataFrame, is_: pd.DataFrame) -> Dict[str, Any]:
    """Calculate Altman Z-score for manufacturing / general corporate solvency."""
    try:
        total_assets = safe_get(bs, ["Total Assets"], 0)
        if not total_assets or total_assets <= 0:
            return {"score": None, "category": "N/A"}

        ca = safe_get(bs, ["Current Assets", "Total Current Assets"], 0) or 0
        cl = safe_get(bs, ["Current Liabilities", "Total Current Liabilities"], 0) or 0
        working_capital = ca - cl

        retained_earnings = safe_get(bs, ["Retained Earnings"], 0) or 0
        ebit = safe_get(is_, ["EBIT", "Operating Income", "Operating Profit"], 0) or 0
        market_cap = info.get("marketCap") or (safe_get(bs, ["Stockholders Equity", "Total Equity"], 0) or 0)
        total_liab = safe_get(bs, ["Total Liabilities Net Minority Interest", "Total Liabilities"], 0) or (total_assets - (safe_get(bs, ["Stockholders Equity"], 0) or 0))
        sales = safe_get(is_, ["Total Revenue", "Operating Revenue"], 0) or 0

        a = working_capital / total_assets
        b = retained_earnings / total_assets
        c = ebit / total_assets
        d = (market_cap / total_liab) if total_liab > 0 else 1.0
        e = sales / total_assets

        z = 1.2 * a + 1.4 * b + 3.3 * c + 0.6 * d + 0.999 * e
        
        if z > 2.99:
            category = "Safe Zone (Low Bankruptcy Risk)"
        elif z >= 1.81:
            category = "Grey Zone (Moderate Caution)"
        else:
            category = "Distress Zone (High Insolvency Risk - Note: Capital-Intensive Utilities often trigger false alarms)"

        return {"score": round(z, 2), "category": category}
    except Exception:
        return {"score": None, "category": "N/A"}


def build_financial_markdown_table(df: pd.DataFrame, row_mapping: List[tuple], curr_code: str = "USD", is_cashflow: bool = False, info: dict = None) -> str:
    """Render a clean, token-efficient markdown table from selected DataFrame rows."""
    if df is None or df.empty:
        return "_Financial data not available._\n"

    cols = list(df.columns)
    col_headers = []
    for c in cols:
        if isinstance(c, (pd.Timestamp, datetime)):
            col_headers.append(c.strftime("%Y"))
        else:
            col_headers.append(str(c)[:10])

    lines = []
    header_line = "| Metric | " + " | ".join(col_headers) + " |"
    sep_line = "| :--- | " + " | ".join([":---:"] * len(col_headers)) + " |"
    lines.append(header_line)
    lines.append(sep_line)

    for label_title, possible_keys, is_cur, is_p in row_mapping:
        row_vals = []
        found = False

        if is_cashflow and label_title == "Capital Expenditure (CapEx)":
            # Use robust capex extractor for each column
            row_vals = []
            for i in range(len(cols)):
                c_val = extract_robust_capex(df, info or {}, col_idx=i)
                row_vals.append(format_num(-c_val if c_val > 0 else None, is_curr=is_cur, is_pct=is_p, curr_code=curr_code))
            found = True
        elif is_cashflow and label_title == "Free Cash Flow (FCF)":
            # Dynamically compute FCF = CFO - CapEx for each column
            row_vals = []
            for i in range(len(cols)):
                cfo_i = safe_get(df, ["Operating Cash Flow", "Total Cash From Operating Activities"], i)
                capex_i = extract_robust_capex(df, info or {}, col_idx=i)
                if cfo_i is not None:
                    fcf_i = cfo_i - capex_i
                    row_vals.append(format_num(fcf_i, is_curr=is_cur, is_pct=is_p, curr_code=curr_code))
                else:
                    row_vals.append("—")
            found = True
        else:
            for key in possible_keys:
                if key in df.index:
                    row_series = df.loc[key]
                    row_vals = [format_num(row_series.iloc[i], is_curr=is_cur, is_pct=is_p, curr_code=curr_code) for i in range(len(cols))]
                    found = True
                    break

        if not found:
            row_vals = ["—"] * len(cols)
        lines.append(f"| {label_title} | " + " | ".join(row_vals) + " |")

    return "\n".join(lines) + "\n"


def fetch_peer_multiples_snapshot(ticker_symbol: str, sector: str, industry: str) -> str:
    """Fetch compact peer multiples and valuation benchmarks for relative context."""
    peers = []
    # Match industry or sector basket
    if industry in SECTOR_PEER_BASKETS:
        peers = SECTOR_PEER_BASKETS[industry]
    elif sector in SECTOR_PEER_BASKETS:
        peers = SECTOR_PEER_BASKETS[sector]
    else:
        peers = ["SPY"]

    # Filter out current ticker from peers
    clean_ticker = ticker_symbol.upper()
    peer_list = [p for p in peers if p.upper() != clean_ticker][:3]

    if not peer_list:
        return "_No direct peer basket configured._\n"

    lines = []
    lines.append("| Peer Ticker | Name | Market Cap | Fwd P/E | EV/EBITDA | FCF Yield | Div Yield |")
    lines.append("| :--- | :--- | :---: | :---: | :---: | :---: | :---: |")

    for peer in peer_list:
        try:
            pt = yf.Ticker(peer)
            p_info = pt.info or {}
            p_name = (p_info.get("shortName") or peer)[:20]
            p_mcap = format_num(p_info.get("marketCap"), is_curr=True, curr_code=p_info.get("currency", "USD"))
            p_fwd_pe = format_num(p_info.get("forwardPE"), is_curr=False)
            p_ev_ebitda = format_num(p_info.get("enterpriseToEbitda"), is_curr=False)
            
            p_fcf = p_info.get("freeCashflow")
            p_mktcap_val = p_info.get("marketCap")
            p_fcf_yield = (p_fcf / p_mktcap_val) if p_fcf and p_mktcap_val else None
            p_fcf_str = format_num(p_fcf_yield, is_curr=False, is_pct=True)
            p_div_str = format_num(p_info.get("dividendYield"), is_curr=False, is_pct=True)

            lines.append(f"| **{peer}** | {p_name} | {p_mcap} | {p_fwd_pe} | {p_ev_ebitda} | {p_fcf_str} | {p_div_str} |")
        except Exception:
            continue

    return "\n".join(lines) + "\n"


def generate_stock_digest(ticker_symbol: str, output_path: Optional[str] = None) -> str:
    """Fetch complete fundamentals and compile into token-efficient stock_digest.md."""
    ticker_symbol = ticker_symbol.strip().upper()
    print(f"[*] Fetching fundamentals for {ticker_symbol} from Yahoo Finance...")
    t = yf.Ticker(ticker_symbol)
    info = t.info or {}

    if not info or info.get("trailingPegRatio") is None and info.get("marketCap") is None and info.get("currentPrice") is None:
        if "symbol" not in info and "shortName" not in info:
            raise ValueError(f"Could not retrieve data for ticker '{ticker_symbol}'. Verify ticker symbol.")

    # Financial statements
    try:
        financials = t.financials  # Income Statement
        balance_sheet = t.balance_sheet
        cashflow = t.cashflow
        quarterly_financials = t.quarterly_financials
        quarterly_cashflow = t.quarterly_cashflow
    except Exception as e:
        print(f"Warning fetching statements: {e}")
        financials = pd.DataFrame()
        balance_sheet = pd.DataFrame()
        cashflow = pd.DataFrame()
        quarterly_financials = pd.DataFrame()
        quarterly_cashflow = pd.DataFrame()

    # Quantitative Scores
    piotroski = calculate_piotroski_f_score(info, balance_sheet, financials, cashflow)
    altman = calculate_altman_z_score(info, balance_sheet, financials)

    # Currency & Basics
    currency = info.get("currency", "USD")
    curr_sym = get_currency_symbol(currency)
    sector = info.get("sector", "Unknown")
    industry = info.get("industry", "Unknown")
    current_price = info.get("currentPrice") or info.get("regularMarketPrice") or info.get("previousClose") or 0.0
    market_cap = info.get("marketCap") or 0
    enterprise_value = info.get("enterpriseValue") or 0

    # Operating & Debt Metrics
    ebit = safe_get(financials, ["EBIT", "Operating Income", "Operating Profit"], 0) or 0
    interest_expense = abs(safe_get(financials, ["Interest Expense", "Interest Expense Non Operating"], 0) or 0)
    interest_coverage = (ebit / interest_expense) if (interest_expense > 0 and ebit) else None

    # Robust CapEx and True Free Cash Flow
    cfo = safe_get(cashflow, ["Operating Cash Flow", "Total Cash From Operating Activities"], 0) or info.get("operatingCashflow") or 0
    capex = extract_robust_capex(cashflow, info, col_idx=0)
    fcf = (cfo - capex) if cfo else (info.get("freeCashflow") or 0)
    fcf_yield = (fcf / market_cap) if market_cap > 0 and fcf else None

    total_debt = safe_get(balance_sheet, ["Total Debt", "Long Term Debt And Capital Lease Obligation"], 0) or info.get("totalDebt") or 0
    cash_and_equiv = safe_get(balance_sheet, ["Cash And Cash Equivalents", "Cash Cash Equivalents And Short Term Investments"], 0) or info.get("totalCash") or 0
    net_debt = total_debt - cash_and_equiv
    ebitda = safe_get(financials, ["EBITDA", "Normalized EBITDA"], 0) or info.get("ebitda") or 0
    net_debt_ebitda = (net_debt / ebitda) if ebitda and ebitda > 0 else None

    # Invested Capital & ROIC
    equity = safe_get(balance_sheet, ["Stockholders Equity", "Total Equity Gross Minority Interest"], 0) or 1
    invested_capital = (total_debt + equity) - cash_and_equiv
    tax_rate = safe_get(financials, ["Tax Rate For Calcs"], 0) or 0.21
    nopat = ebit * (1 - tax_rate) if ebit else 0
    roic = (nopat / invested_capital) if invested_capital > 0 and nopat else None

    # Share count change (Dilution check)
    shares_curr = safe_get(financials, ["Diluted Average Shares", "Basic Average Shares"], 0) or info.get("sharesOutstanding") or 0
    shares_old = safe_get(financials, ["Diluted Average Shares", "Basic Average Shares"], -1) if not financials.empty else shares_curr
    dilution_5y_pct = ((shares_curr - shares_old) / shares_old) if (shares_old and shares_curr and shares_old > 0) else 0.0

    # Valuation Multiples
    pe_ttm = info.get("trailingPE")
    pe_forward = info.get("forwardPE")
    ev_ebit = (enterprise_value / ebit) if enterprise_value and ebit and ebit > 0 else None
    ev_ebitda = info.get("enterpriseToEbitda") or ((enterprise_value / ebitda) if enterprise_value and ebitda and ebitda > 0 else None)
    price_to_book = info.get("priceToBook")
    price_to_sales = info.get("priceToSalesTrailing12Months")
    div_yield = info.get("dividendYield")

    # Target & 52w Range
    target_mean = info.get("targetMeanPrice")
    low_52 = info.get("fiftyTwoWeekLow")
    high_52 = info.get("fiftyTwoWeekHigh")

    # Sector Cost of Capital Reference
    sector_wacc_info = SECTOR_COST_OF_CAPITAL_BENCHMARKS.get(sector, {"wacc_range": "8.0% – 10.0%", "beta_typical": "0.90 – 1.20", "type": "General Industry"})

    # Construct YAML frontmatter + compact tables
    digest = []
    digest.append("---")
    digest.append(f"ticker: {ticker_symbol}")
    digest.append(f"name: \"{info.get('shortName', ticker_symbol)}\"")
    digest.append(f"sector: \"{sector}\"")
    digest.append(f"industry: \"{industry}\"")
    digest.append(f"currency: {currency}")
    digest.append(f"currency_symbol: \"{curr_sym}\"")
    digest.append(f"current_price: {current_price}")
    digest.append(f"market_cap: {format_num(market_cap, curr_code=currency)}")
    digest.append(f"enterprise_value: {format_num(enterprise_value, curr_code=currency)}")
    digest.append(f"shares_outstanding: {format_num(shares_curr, is_curr=False)}")
    digest.append(f"52w_range: \"{format_num(low_52, curr_code=currency)} - {format_num(high_52, curr_code=currency)}\"")
    digest.append(f"beta: {info.get('beta', '—')}")
    digest.append("scores:")
    digest.append(f"  piotroski_f_score: \"{piotroski['score']}/9\"")
    digest.append(f"  altman_z_score: \"{altman['score']} ({altman['category']})\"")
    digest.append("multiples:")
    digest.append(f"  pe_ttm: {format_num(pe_ttm, is_curr=False)}")
    digest.append(f"  pe_forward: {format_num(pe_forward, is_curr=False)}")
    digest.append(f"  ev_ebit: {format_num(ev_ebit, is_curr=False)}")
    digest.append(f"  ev_ebitda: {format_num(ev_ebitda, is_curr=False)}")
    digest.append(f"  price_to_book: {format_num(price_to_book, is_curr=False)}")
    digest.append(f"  price_to_sales: {format_num(price_to_sales, is_curr=False)}")
    digest.append(f"  fcf_yield: \"{format_num(fcf_yield, is_curr=False, is_pct=True)}\"")
    digest.append(f"  dividend_yield: \"{format_num(div_yield, is_curr=False, is_pct=True)}\"")
    digest.append("efficiency_and_debt:")
    digest.append(f"  roic_estimate: \"{format_num(roic, is_curr=False, is_pct=True)}\"")
    digest.append(f"  net_debt_ebitda: {format_num(net_debt_ebitda, is_curr=False)}")
    digest.append(f"  interest_coverage: {format_num(interest_coverage, is_curr=False)}")
    digest.append(f"  share_dilution_period: \"{format_num(dilution_5y_pct, is_curr=False, is_pct=True)}\"")
    digest.append("benchmark_cost_of_capital:")
    digest.append(f"  sector_typical_wacc: \"{sector_wacc_info['wacc_range']}\"")
    digest.append(f"  strategy_hurdle_rate: \"10.0% (Cost of Equity)\"")
    digest.append(f"consensus_target_price: {format_num(target_mean, curr_code=currency)}")
    digest.append("---\n")

    digest.append(f"# Fundamental Financial Digest: {ticker_symbol} ({info.get('shortName', ticker_symbol)})\n")
    
    # Business Summary
    summary = info.get("longBusinessSummary", "").strip()
    if summary:
        short_summary = summary[:450] + ("..." if len(summary) > 450 else "")
        digest.append(f"**Business Overview**: {short_summary}\n")

    # Multi-year Income Statement Table
    digest.append("### 1. Multi-Year Income Statement Trend")
    is_rows = [
        ("Revenue", ["Total Revenue", "Operating Revenue"], True, False),
        ("Gross Profit", ["Gross Profit"], True, False),
        ("Operating Income (EBIT)", ["EBIT", "Operating Income", "Operating Profit"], True, False),
        ("Net Income", ["Net Income", "Net Income Common Stockholders"], True, False),
        ("Diluted EPS", ["Diluted EPS", "Basic EPS"], True, False),
        ("Diluted Shares", ["Diluted Average Shares", "Basic Average Shares"], False, False),
    ]
    digest.append(build_financial_markdown_table(financials, is_rows, curr_code=currency))

    # Multi-year Cash Flow Table with Hardened CapEx / FCF
    digest.append("### 2. Multi-Year Cash Flow & Reinvestment")
    cf_rows = [
        ("Operating Cash Flow (CFO)", ["Operating Cash Flow", "Total Cash From Operating Activities"], True, False),
        ("Capital Expenditure (CapEx)", ["Capital Expenditure", "Capital Expenditures", "Purchase Of Property Plant And Equipment", "Purchase Of PPE"], True, False),
        ("Free Cash Flow (FCF)", ["Free Cash Flow"], True, False),
        ("Dividends Paid", ["Common Stock Dividend Paid", "Cash Dividends Paid"], True, False),
        ("Repurchase of Stock", ["Repurchase Of Capital Stock", "Common Stock Payments"], True, False),
        ("Issuance/Repayment of Debt", ["Net Issuance Payments Of Debt", "Long Term Debt Issuance"], True, False),
    ]
    digest.append(build_financial_markdown_table(cashflow, cf_rows, curr_code=currency, is_cashflow=True, info=info))

    # Multi-year Balance Sheet Health
    digest.append("### 3. Balance Sheet & Capital Structure")
    bs_rows = [
        ("Cash & Short Term Inv", ["Cash Cash Equivalents And Short Term Investments", "Cash And Cash Equivalents"], True, False),
        ("Total Current Assets", ["Total Current Assets", "Current Assets"], True, False),
        ("Total Assets", ["Total Assets"], True, False),
        ("Total Current Liabilities", ["Total Current Liabilities", "Current Liabilities"], True, False),
        ("Total Debt", ["Total Debt", "Long Term Debt And Capital Lease Obligation"], True, False),
        ("Stockholders' Equity", ["Stockholders Equity", "Total Equity Gross Minority Interest"], True, False),
        ("Tangible Book Value", ["Tangible Book Value", "Net Tangible Assets"], True, False),
    ]
    digest.append(build_financial_markdown_table(balance_sheet, bs_rows, curr_code=currency))

    # Piotroski Breakdown
    digest.append("### 4. Piotroski F-Score Diagnostic")
    p_lines = [f"- **{k}**: {'✅ Pass' if v else '❌ Fail'}" for k, v in piotroski.get("breakdown", {}).items()]
    digest.append("\n".join(p_lines) + "\n")

    # Quarterly Momentum (Last 4 Quarters)
    if not quarterly_financials.empty:
        digest.append("### 5. Recent Quarterly Trajectory")
        q_rows = [
            ("Revenue", ["Total Revenue", "Operating Revenue"], True, False),
            ("Operating Income", ["EBIT", "Operating Income"], True, False),
            ("Net Income", ["Net Income", "Net Income Common Stockholders"], True, False),
        ]
        digest.append(build_financial_markdown_table(quarterly_financials, q_rows, curr_code=currency))

    # Peer Snapshot & Cost of Capital Benchmark
    digest.append("### 6. Industry Peer Valuation Snapshot & Cost of Capital")
    digest.append(f"- **Sector WACC Benchmark**: `{sector_wacc_info['wacc_range']}` ({sector_wacc_info['type']})")
    digest.append(f"- **Strategy Required Hurdle Rate**: `10.0%` (Cost of Equity minimum)")
    digest.append(fetch_peer_multiples_snapshot(ticker_symbol, sector, industry))

    content = "\n".join(digest)

    if output_path:
        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"[+] Successfully wrote stock digest to: {output_path}")

    return content


def main():
    parser = argparse.ArgumentParser(description="Stock Deep Dive Data & Financial Statement Extractor")
    parser.add_argument("--ticker", "-t", required=True, help="Stock ticker symbol (e.g. AAPL, MSFT, VIE.PA)")
    parser.add_argument("--output", "-o", default=None, help="Output file path (e.g. scratch/stock_digest.md)")
    args = parser.parse_args()

    try:
        content = generate_stock_digest(args.ticker, args.output)
        if not args.output:
            print(content)
    except Exception as e:
        print(f"Error extracting data for {args.ticker}: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
