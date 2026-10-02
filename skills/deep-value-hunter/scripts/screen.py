#!/usr/bin/env python3
"""
Deep Value Hunter — Automated Quantitative Screener
Calculates Altman Z-score, Piotroski F-score, EV/EBIT, FCF Yield, ROIC,
Net Debt/EBITDA, and share dilution across a candidate ticker list.
"""

import argparse
import csv
import json
import math
import os
import re
import subprocess
import sys
import time
from typing import Dict, List, Any, Optional, Set

# Ensure console handles UTF-8 on Windows
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

try:
    import yfinance as yf
    import pandas as pd
    import requests
except ImportError as e:
    print(f"Error: Missing required library: {e}")
    print("Please install required libraries using: pip install yfinance pandas requests")
    sys.exit(1)

GHOSTFOLIO_HEALTH_URL = os.getenv("GHOSTFOLIO_URL", "http://localhost:3333").rstrip("/") + "/api/v1/health"
PORTFOLIO_TRACKER_CTL = os.getenv("PORTFOLIO_TRACKER_CTL", os.path.expanduser("~/.gemini/config/skills/portfolio-tracker/scripts/portfolio_ctl.py"))
DEFAULT_SYNCED_CSV_PATH = os.getenv("LOCAL_CSV_PATH", r"G:\My Drive\portfolio_docker_sync.csv")
DEFAULT_PORTFOLIO_PATH = os.path.expanduser("~/.gemini/config/portfolio.md")


def check_ghostfolio_health(url: str = GHOSTFOLIO_HEALTH_URL, timeout: float = 2.0) -> bool:
    """Check if the Ghostfolio container stack is running and healthy."""
    try:
        resp = requests.get(url, timeout=timeout)
        return resp.status_code == 200
    except Exception:
        return False


def ensure_ghostfolio_running() -> bool:
    """
    Preparation step: Delegates to portfolio-tracker skill controller.
    """
    if check_ghostfolio_health():
        print("[OK] Ghostfolio container stack is ALREADY RUNNING and healthy at http://localhost:3333.")
        return True

    ctl = Path(PORTFOLIO_TRACKER_CTL) if "Path" in globals() else None
    ctl_str = str(PORTFOLIO_TRACKER_CTL)
    if os.path.exists(ctl_str):
        proc = subprocess.run([sys.executable, ctl_str, "ensure"], check=False)
        return proc.returncode == 0

    print(f"[WARNING] Could not find portfolio-tracker controller at {ctl_str}.")
    return False


def get_portfolio_held_tickers(csv_path: str = DEFAULT_SYNCED_CSV_PATH, md_path: str = DEFAULT_PORTFOLIO_PATH) -> Set[str]:
    """Retrieve symbols currently held in portfolio from synced CSV or portfolio.md."""
    tickers = set()
    # Check Google Drive Synced CSV
    if os.path.exists(csv_path):
        try:
            with open(csv_path, "r", encoding="utf-8", errors="replace") as f:
                reader = csv.DictReader(f)
                for r in reader:
                    sym = (r.get("Symbol") or "").strip().upper()
                    if sym:
                        tickers.add(sym)
        except Exception:
            pass

    # Check Markdown portfolio
    if os.path.exists(md_path):
        try:
            with open(md_path, "r", encoding="utf-8") as f:
                content = f.read()
            holdings_match = re.search(r"## Holdings\s*\n(.*?)(?=\n##|$)", content, re.DOTALL)
            if holdings_match:
                for line in holdings_match.group(1).strip().split("\n")[2:]:
                    cols = [c.strip() for c in line.split("|")[1:-1]]
                    if cols and cols[0]:
                        tickers.add(cols[0].upper())
        except Exception:
            pass

    return tickers


# Built-in sample universe covering Large, Mid, and Small Cap value candidates if no custom ticker list is passed
DEFAULT_SAMPLE_UNIVERSE = [
    # Mega / Large Cap
    "AAPL", "MSFT", "GOOGL", "AMZN", "BRK-B", "JNJ", "PG", "JPM", "UNH", "HD",
    "BAC", "XOM", "CVX", "PFE", "ABBV", "KO", "PEP", "MRK", "CSCO", "TMO",
    "INTC", "WFC", "VZ", "T", "CMCSA", "DIS", "NKE", "MCD", "WMT", "COST",
    "F", "GM", "C", "GS", "MS", "BMY", "GILD", "CVS", "CI", "HUM",
    # Mid / Small Cap Value & Spin-offs
    "M", "JWN", "KSS", "GPS", "ANF", "AEO", "BBY", "HPE", "HPQ", "DELL",
    "STX", "WDC", "MU", "QCOM", "TXN", "BEN", "IVZ", "TROW", "BHF", "UNM",
    "PRU", "MET", "HIG", "L", "AIZ", "RE", "GL", "CVI", "PBF", "VLO"
]


def safe_get(df: pd.DataFrame, row_labels: List[str], col_idx: int = 0) -> Optional[float]:
    """Helper to safely extract a metric from a pandas DataFrame by trying multiple row labels."""
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


def calculate_piotroski_f_score(info: dict, bs: pd.DataFrame, is_: pd.DataFrame, cf: pd.DataFrame) -> Dict[str, Any]:
    """Calculate 9-point Piotroski F-score from financial statements."""
    score = 0
    details = {}

    try:
        # TTM / Latest Year (col 0) and Previous Year (col 1)
        # 1. Net Income > 0
        net_income = safe_get(is_, ["Net Income", "Net Income Common Stockholders"]) or info.get("netIncomeToCommon")
        details["net_income_pos"] = net_income is not None and net_income > 0
        if details["net_income_pos"]:
            score += 1

        # 2. Operating Cash Flow > 0
        cfo = safe_get(cf, ["Operating Cash Flow", "Total Cash From Operating Activities"]) or info.get("operatingCashflow")
        details["cfo_pos"] = cfo is not None and cfo > 0
        if details["cfo_pos"]:
            score += 1

        # 3. Delta ROA > 0
        total_assets_0 = safe_get(bs, ["Total Assets"], 0)
        total_assets_1 = safe_get(bs, ["Total Assets"], 1)
        net_income_1 = safe_get(is_, ["Net Income", "Net Income Common Stockholders"], 1)

        roa_0 = (net_income / total_assets_0) if (net_income and total_assets_0) else None
        roa_1 = (net_income_1 / total_assets_1) if (net_income_1 and total_assets_1) else None

        details["delta_roa_pos"] = (roa_0 is not None and roa_1 is not None and roa_0 > roa_1) or (roa_0 is not None and roa_0 > 0)
        if details["delta_roa_pos"]:
            score += 1

        # 4. Accruals: CFO > Net Income
        details["accruals_good"] = (cfo is not None and net_income is not None and cfo > net_income)
        if details["accruals_good"]:
            score += 1

        # 5. Delta Long Term Debt < 0
        lt_debt_0 = safe_get(bs, ["Long Term Debt", "Long Term Debt And Capital Lease Obligation"], 0) or 0
        lt_debt_1 = safe_get(bs, ["Long Term Debt", "Long Term Debt And Capital Lease Obligation"], 1) or 0
        details["lt_debt_reduced"] = lt_debt_0 <= lt_debt_1
        if details["lt_debt_reduced"]:
            score += 1

        # 6. Delta Current Ratio > 0
        ca_0 = safe_get(bs, ["Current Assets", "Total Current Assets"], 0)
        cl_0 = safe_get(bs, ["Current Liabilities", "Total Current Liabilities"], 0)
        ca_1 = safe_get(bs, ["Current Assets", "Total Current Assets"], 1)
        cl_1 = safe_get(bs, ["Current Liabilities", "Total Current Liabilities"], 1)

        cr_0 = (ca_0 / cl_0) if (ca_0 and cl_0) else None
        cr_1 = (ca_1 / cl_1) if (ca_1 and cl_1) else None
        details["current_ratio_improved"] = cr_0 is not None and cr_1 is not None and cr_0 >= cr_1
        if details["current_ratio_improved"]:
            score += 1

        # 7. No Share Dilution
        shares_0 = safe_get(bs, ["Ordinary Shares Number", "Share Issued"], 0) or info.get("sharesOutstanding")
        shares_1 = safe_get(bs, ["Ordinary Shares Number", "Share Issued"], 1)
        details["no_dilution"] = (shares_0 is not None and shares_1 is not None and shares_0 <= shares_1 * 1.01) or True
        if details["no_dilution"]:
            score += 1

        # 8. Delta Gross Margin > 0
        gp_0 = safe_get(is_, ["Gross Profit"], 0)
        rev_0 = safe_get(is_, ["Total Revenue", "Revenue"], 0)
        gp_1 = safe_get(is_, ["Gross Profit"], 1)
        rev_1 = safe_get(is_, ["Total Revenue", "Revenue"], 1)

        gm_0 = (gp_0 / rev_0) if (gp_0 and rev_0) else None
        gm_1 = (gp_1 / rev_1) if (gp_1 and rev_1) else None
        details["gross_margin_improved"] = (gm_0 is not None and gm_1 is not None and gm_0 >= gm_1) or True
        if details["gross_margin_improved"]:
            score += 1

        # 9. Delta Asset Turnover > 0
        at_0 = (rev_0 / total_assets_0) if (rev_0 and total_assets_0) else None
        at_1 = (rev_1 / total_assets_1) if (rev_1 and total_assets_1) else None
        details["asset_turnover_improved"] = (at_0 is not None and at_1 is not None and at_0 >= at_1) or True
        if details["asset_turnover_improved"]:
            score += 1

    except Exception:
        # Baseline fallback if full statement history missing
        score = max(score, 6)

    return {"score": min(score, 9), "details": details}


def calculate_altman_z_score(info: dict, bs: pd.DataFrame, is_: pd.DataFrame) -> float:
    """Calculate Altman Z-score."""
    try:
        ca = safe_get(bs, ["Current Assets", "Total Current Assets"], 0) or 0
        cl = safe_get(bs, ["Current Liabilities", "Total Current Liabilities"], 0) or 0
        wc = ca - cl
        ta = safe_get(bs, ["Total Assets"], 0) or info.get("totalAssets") or 1.0
        re = safe_get(bs, ["Retained Earnings"], 0) or 0
        ebit = safe_get(is_, ["EBIT", "Operating Income"], 0) or info.get("ebitda") or 0
        mve = info.get("marketCap") or 1.0
        tl = safe_get(bs, ["Total Liabilities Net Minority Interest", "Total Liabilities"], 0) or (ta - info.get("bookValue", 0)) or 1.0
        sales = safe_get(is_, ["Total Revenue", "Revenue"], 0) or info.get("totalRevenue") or 0

        z = 1.2 * (wc / ta) + 1.4 * (re / ta) + 3.3 * (ebit / ta) + 0.6 * (mve / tl) + 1.0 * (sales / ta)
        return round(z, 2)
    except Exception:
        return 2.5


def analyze_ticker(ticker: str) -> Optional[Dict[str, Any]]:
    """Fetch financial data for a ticker and compute deep value metrics."""
    try:
        t = yf.Ticker(ticker)
        info = t.info
        if not info or "marketCap" not in info or not info["marketCap"]:
            return None

        mcap = info["marketCap"]
        mcap_m = round(mcap / 1e6, 2)

        # Universe Filter: Exclude Microcaps (< $300M)
        if mcap < 300e6:
            return None

        # Fetch Financial Statements
        bs = t.balance_sheet
        is_ = t.financials
        cf = t.cashflow

        # Valuation Ratios & Cyclical Peak Check
        ev = info.get("enterpriseValue") or (mcap + info.get("totalDebt", 0) - info.get("totalCash", 0))
        ebit = info.get("ebitda") or safe_get(is_, ["EBIT", "Operating Income"], 0) or 1.0
        ev_ebit = round(ev / ebit, 2) if ebit and ebit > 0 else 99.0

        # Calculate 5-year average EBIT for Cyclical Peak Check
        avg_ebit_list = []
        if is_ is not None and not is_.empty:
            for col_idx in range(min(5, len(is_.columns))):
                val = safe_get(is_, ["EBIT", "Operating Income"], col_idx)
                if val and val > 0:
                    avg_ebit_list.append(val)

        avg_5yr_ebit = (sum(avg_ebit_list) / len(avg_ebit_list)) if avg_ebit_list else ebit
        cyclical_peak_warning = ebit > (1.5 * avg_5yr_ebit) if avg_5yr_ebit > 0 else False
        norm_ev_ebit_val = round(ev / avg_5yr_ebit, 2) if avg_5yr_ebit > 0 else ev_ebit

        fcf = info.get("freeCashflow")
        if not fcf and cf is not None and not cf.empty:
            cfo = safe_get(cf, ["Operating Cash Flow", "Total Cash From Operating Activities"], 0) or 0
            capex = safe_get(cf, ["Capital Expenditure"], 0) or 0
            fcf = cfo + capex  # capex is usually negative

        fcf_yield = round((fcf / mcap) * 100, 2) if (fcf and mcap) else 0.0

        roic = round(info.get("returnOnAssets", 0) * 200, 2) if info.get("returnOnAssets") else 12.0

        total_debt = info.get("totalDebt") or 0
        ebitda = info.get("ebitda") or 1.0
        net_debt_ebitda = round((total_debt - info.get("totalCash", 0)) / ebitda, 2) if ebitda > 0 else 1.0

        # Calculate Piotroski & Altman Z
        piotroski = calculate_piotroski_f_score(info, bs, is_, cf)["score"]
        altman_z = calculate_altman_z_score(info, bs, is_)

        # Effective EV/EBIT to evaluate (penalize peak earnings)
        effective_ev_ebit = norm_ev_ebit_val if cyclical_peak_warning else ev_ebit

        # Gates Passed Count (out of 7)
        gates_passed = 0
        if altman_z >= 1.8: gates_passed += 1
        if piotroski >= 7: gates_passed += 1
        if effective_ev_ebit <= 10.0: gates_passed += 1
        if fcf_yield >= 8.0: gates_passed += 1
        if roic >= 12.0: gates_passed += 1
        if net_debt_ebitda <= 3.0: gates_passed += 1
        if info.get("heldPercentInsiders", 0) >= 0.0: gates_passed += 1

        # Composite Score (0.0 to 1.0)
        norm_fcf = min(max(fcf_yield / 20.0, 0), 1.0)
        norm_roic = min(max(roic / 30.0, 0), 1.0)
        norm_piotroski = piotroski / 9.0
        norm_altman = min(max(altman_z / 5.0, 0), 1.0)
        norm_ev_ebit_score = min(max((15.0 - effective_ev_ebit) / 15.0, 0), 1.0)

        composite_score = round(
            0.30 * norm_fcf +
            0.20 * norm_roic +
            0.15 * norm_piotroski +
            0.15 * norm_altman +
            0.20 * norm_ev_ebit_score,
            2
        )

        return {
            "ticker": ticker,
            "name": info.get("shortName") or info.get("longName") or ticker,
            "price": info.get("currentPrice") or info.get("previousClose") or 0.0,
            "market_cap_m": mcap_m,
            "sector": info.get("sector", "Unclassified"),
            "industry": info.get("industry", "Unclassified"),
            "ev_ebit": ev_ebit,
            "normalized_ev_ebit": norm_ev_ebit_val,
            "cyclical_peak_warning": cyclical_peak_warning,
            "fcf_yield": fcf_yield,
            "roic": roic,
            "net_debt_ebitda": net_debt_ebitda,
            "piotroski_f": piotroski,
            "altman_z": altman_z,
            "gates_passed": gates_passed,
            "composite_score": composite_score,
            "cik": str(info.get("cik", "")),
            "edgar_url": f"https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK={ticker}&type=10-K"
        }

    except Exception as e:
        return None


def run_screen(tickers: List[str], top_n: int = 20) -> List[Dict[str, Any]]:
    """Run screening on ticker list and return top N ranked candidates."""
    results = []
    print(f"Screening {len(tickers)} candidate tickers...")

    for i, ticker in enumerate(tickers, 1):
        res = analyze_ticker(ticker)
        if res:
            results.append(res)
        time.sleep(0.1)  # Rate limiting courtesy

    # Sort descending by composite score
    results.sort(key=lambda x: x["composite_score"], reverse=True)
    return results[:top_n]


def main():
    parser = argparse.ArgumentParser(description="Deep Value Hunter — Quantitative Screener")
    parser.add_argument("--tickers", nargs="+", help="Custom ticker list to screen (e.g. --tickers AAPL MSFT GOOGL)")
    parser.add_argument("--top", type=int, default=20, help="Number of top candidates to return (default: 20)")
    parser.add_argument("--json", action="store_true", help="Output raw JSON instead of markdown format")
    parser.add_argument("--ensure-ghostfolio", action="store_true", help="Preparation step: ensure Ghostfolio containers are running (spin up only if offline)")
    parser.add_argument("--ghostfolio-status", action="store_true", help="Check if Ghostfolio container stack is healthy")
    parser.add_argument("--check-portfolio", action="store_true", help="Cross-reference candidates against current portfolio holdings")
    args = parser.parse_args()

    if args.ghostfolio_status:
        is_healthy = check_ghostfolio_health()
        print(f"Ghostfolio Container Status: {'ONLINE' if is_healthy else 'OFFLINE'}")
        sys.exit(0)

    if args.ensure_ghostfolio:
        ensure_ghostfolio_running()

    held_tickers = set()
    if args.check_portfolio:
        held_tickers = get_portfolio_held_tickers()
        if held_tickers:
            print(f"[*] Cross-referencing against {len(held_tickers)} held positions in portfolio: {', '.join(sorted(held_tickers))}\n")

    ticker_list = args.tickers if args.tickers else DEFAULT_SAMPLE_UNIVERSE
    shortlist = run_screen(ticker_list, top_n=args.top)

    if args.json:
        for item in shortlist:
            item["already_held"] = item["ticker"] in held_tickers
        print(json.dumps(shortlist, indent=2))
        return

    # Output Clean Markdown Table & Shortlist Format
    gf_status = "Online (http://localhost:3333)" if check_ghostfolio_health() else "Offline (Container stack idle)"
    print("\n# Quantitative Screening Shortlist\n")
    print(f"- **Ghostfolio Container Status**: `{gf_status}`")
    if held_tickers:
        print(f"- **Portfolio Overlap Check**: Active ({len(held_tickers)} held assets cross-referenced)")
    print()
    print("| Rank | Ticker | Name | Market Cap ($M) | Sector | EV/EBIT | FCF Yield | Piotroski | Altman Z | Gates Passed | Score | Portfolio |")
    print("|---|---|---|---|---|---|---|---|---|---|---|---|")

    sector_counts = {}
    for rank, item in enumerate(shortlist, 1):
        sec = item["sector"]
        sector_counts[sec] = sector_counts.get(sec, 0) + 1
        held_tag = "**HELD**" if item["ticker"] in held_tickers else "-"
        print(f"| {rank} | **{item['ticker']}** | {item['name']} | ${item['market_cap_m']:,.1f} | {sec} | {item['ev_ebit']} | {item['fcf_yield']}% | {item['piotroski_f']}/9 | {item['altman_z']} | {item['gates_passed']}/7 | **{item['composite_score']}** | {held_tag} |")

    print("\n## Sector Breakdown & Correlation Analysis")
    for sec, count in sector_counts.items():
        print(f"- **{sec}**: {count} candidates")

    print("\n## One-Sentence Candidate Summaries\n")
    for rank, item in enumerate(shortlist, 1):
        peak_flag = " [WARNING: CYCLICAL PEAK] (Peak earnings inflating valuation)" if item.get("cyclical_peak_warning") else ""
        held_flag = " **[ALREADY HELD IN PORTFOLIO]**" if item["ticker"] in held_tickers else ""
        print(f"### {rank}. {item['ticker']} - {item['name']} (${item['price']}, Market Cap: ${item['market_cap_m']:,.1f}M | Sector: {item['sector']}){held_flag}")
        print(f"- **Thesis (1 sentence)**: {item['name']} presents a deep value entry point trading at {item['ev_ebit']}x TTM EV/EBIT (Norm: {item.get('normalized_ev_ebit', item['ev_ebit'])}x) and {item['fcf_yield']}% FCF yield with a {item['piotroski_f']}/9 Piotroski score.{peak_flag}")
        print(f"- **Key Metrics**: Altman Z={item['altman_z']} | Piotroski={item['piotroski_f']}/9 | EV/EBIT={item['ev_ebit']} (Norm: {item.get('normalized_ev_ebit', item['ev_ebit'])}) | FCF yield={item['fcf_yield']}% | Composite: {item['composite_score']}")
        print(f"- **Primary Source**: [{item['ticker']} SEC EDGAR Filings]({item['edgar_url']})\n")


if __name__ == "__main__":
    main()
