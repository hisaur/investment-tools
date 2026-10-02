#!/usr/bin/env python3
"""
Portfolio Manager & Allocation Diagnostic
Loads, updates, and analyzes the user's persistent portfolio (default: ~/.gemini/config/portfolio.md).
Supports multi-currency conversion, FX normalization, cross-exchange ticker matching,
asset weights, sector exposures, cash reserves, and concentration risks.
"""

import argparse
import csv
import math
import os
import re
import subprocess
import sys
import urllib.error
import urllib.request
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple

try:
    import yfinance as yf
except ImportError:
    yf = None

DEFAULT_PORTFOLIO_PATH = os.path.expanduser("~/.gemini/config/portfolio.md")
DEFAULT_SYNCED_CSV_PATH = os.getenv("LOCAL_CSV_PATH", r"G:\My Drive\portfolio_docker_sync.csv")
GHOSTFOLIO_HEALTH_URL = os.getenv("GHOSTFOLIO_URL", "http://localhost:3333").rstrip("/") + "/api/v1/health"
PORTFOLIO_TRACKER_CTL = os.getenv("PORTFOLIO_TRACKER_CTL", os.path.expanduser("~/.gemini/config/skills/portfolio-tracker/scripts/portfolio_ctl.py"))


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

# Static fallback FX rates relative to USD if offline
FALLBACK_FX_RATES_TO_USD = {
    "USD": 1.000,
    "EUR": 1.085,
    "GBP": 1.285,
    "GBp": 0.01285,
    "CAD": 0.735,
    "AUD": 0.655,
    "CHF": 1.135,
    "JPY": 0.0067,
    "HKD": 0.128,
    "SEK": 0.095,
    "NOK": 0.092,
    "DKK": 0.145,
}

# Suffix to Currency map
EXCHANGE_SUFFIX_CURRENCY = {
    ".PA": "EUR",  # Paris
    ".AS": "EUR",  # Amsterdam
    ".DE": "EUR",  # XETRA Frankfurt
    ".MI": "EUR",  # Milan
    ".MC": "EUR",  # Madrid
    ".BR": "EUR",  # Brussels
    ".L":  "GBP",  # London
    ".TO": "CAD",  # Toronto
    ".V":  "CAD",  # TSX Venture
    ".AX": "AUD",  # Australia
    ".SW": "CHF",  # Swiss
    ".T":  "JPY",  # Tokyo
    ".HK": "HKD",  # Hong Kong
    ".ST": "SEK",  # Stockholm
}


def get_currency_symbol(curr: str) -> str:
    return CURRENCY_SYMBOLS.get((curr or "USD").upper(), f"{curr} ")


def infer_ticker_currency(ticker: str) -> str:
    """Infer the currency of a ticker from its exchange suffix."""
    ticker = ticker.upper()
    for suffix, curr in EXCHANGE_SUFFIX_CURRENCY.items():
        if ticker.endswith(suffix):
            return curr
    return "USD"


def get_fx_rate_to_usd(from_curr: str) -> float:
    """Get the conversion rate from `from_curr` to USD."""
    from_curr = (from_curr or "USD").upper()
    if from_curr == "USD":
        return 1.0

    # Try live yfinance rate
    if yf is not None:
        try:
            pair = f"{from_curr}USD=X"
            t = yf.Ticker(pair)
            price = t.fast_info.get("lastPrice") or t.info.get("regularMarketPrice")
            if price and price > 0:
                return float(price)
        except Exception:
            pass

    return FALLBACK_FX_RATES_TO_USD.get(from_curr, 1.0)


def convert_currency(amount: float, from_curr: str, to_curr: str) -> float:
    """Convert an amount from one currency to another."""
    from_curr = (from_curr or "USD").upper()
    to_curr = (to_curr or "USD").upper()
    if from_curr == to_curr:
        return amount

    # Convert to USD first, then to target currency
    rate_from_usd = get_fx_rate_to_usd(from_curr)
    rate_to_usd = get_fx_rate_to_usd(to_curr)
    
    amount_in_usd = amount * rate_from_usd
    return amount_in_usd / rate_to_usd if rate_to_usd > 0 else amount_in_usd


def match_ticker(query: str, target: str) -> bool:
    """Cross-match tickers (e.g. VIE.PA <-> VIE, ASML.AS <-> ASML, BRK.B <-> BRK-B)."""
    q = query.upper().replace("-", ".")
    t = target.upper().replace("-", ".")
    if q == t:
        return True
    # Strip suffixes
    q_base = q.split(".")[0]
    t_base = t.split(".")[0]
    return q_base == t_base


DEFAULT_PORTFOLIO_CONTENT = """---
updated_at: 2026-01-01
currency: USD
cash: 25000.0
strategy_hurdle_rate_annual_pct: 10.0
max_position_size_pct: 10.0
max_sector_size_pct: 25.0
---

## Holdings

| Ticker | Shares | Avg Cost | Current Price | Sector | Thesis | Currency |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| BRK-B | 50.0 | 360.00 | 504.03 | Financial Services | High-quality compounder with fortress balance sheet | USD |
| GOOGL | 80.0 | 150.00 | 345.90 | Communication Services | GARP AI leader with strong advertising moat and high ROIC | USD |

## Watchlist

| Ticker | Target Buy Price | Reason |
| :--- | :--- | :--- |
| TXN | 160.00 | Wait for semiconductor cyclical bottom and FCF normalization |
"""


def parse_markdown_content(content: str) -> Dict[str, Any]:
    """Parse string content of portfolio.md"""
    data = {
        "cash": 0.0,
        "currency": "USD",
        "strategy_hurdle_rate_annual_pct": 10.0,
        "max_position_size_pct": 10.0,
        "max_sector_size_pct": 25.0,
        "holdings": [],
        "watchlist": []
    }
    
    # 1. Parse YAML Frontmatter
    frontmatter_match = re.search(r"^---\s*\n(.*?)\n---", content, re.DOTALL)
    if frontmatter_match:
        for line in frontmatter_match.group(1).split("\n"):
            line = line.strip()
            if ":" in line:
                key, val = [x.strip() for x in line.split(":", 1)]
                try:
                    data[key] = float(val) if "." in val or val.isdigit() else val
                except ValueError:
                    data[key] = val

    # 2. Parse Holdings Table
    holdings_section = re.search(r"## Holdings\s*\n(.*?)(?=\n##|$)", content, re.DOTALL)
    if holdings_section:
        lines = holdings_section.group(1).strip().split("\n")
        if len(lines) > 2:  # Skip header and separator
            for line in lines[2:]:
                cols = [c.strip() for c in line.split("|")[1:-1]]
                if len(cols) >= 6:
                    holding_curr = cols[6] if len(cols) >= 7 and cols[6] else infer_ticker_currency(cols[0])
                    data["holdings"].append({
                        "ticker": cols[0],
                        "shares": float(cols[1]) if cols[1] else 0.0,
                        "avg_cost": float(cols[2]) if cols[2] else 0.0,
                        "current_price": float(cols[3]) if cols[3] else 0.0,
                        "sector": cols[4],
                        "thesis": cols[5],
                        "currency": holding_curr
                    })

    # 3. Parse Watchlist Table
    watchlist_section = re.search(r"## Watchlist\s*\n(.*?)(?=\n##|$)", content, re.DOTALL)
    if watchlist_section:
        lines = watchlist_section.group(1).strip().split("\n")
        if len(lines) > 2:
            for line in lines[2:]:
                cols = [c.strip() for c in line.split("|")[1:-1]]
                if len(cols) >= 3:
                    data["watchlist"].append({
                        "ticker": cols[0],
                        "target_buy_price": float(cols[1]) if cols[1] else 0.0,
                        "reason": cols[2]
                    })
                    
    return data


def check_ghostfolio_health(url: str = GHOSTFOLIO_HEALTH_URL, timeout: float = 2.0) -> bool:
    """Check if the Ghostfolio container stack is running and healthy."""
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Antigravity/1.0"})
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.status == 200
    except Exception:
        return False


def ensure_ghostfolio_running() -> bool:
    """
    Preparation step: Delegates to portfolio-tracker skill controller.
    """
    if check_ghostfolio_health():
        print("[OK] Ghostfolio container stack is ALREADY RUNNING and healthy at http://localhost:3333.")
        return True

    ctl = Path(PORTFOLIO_TRACKER_CTL)
    if ctl.exists():
        proc = subprocess.run([sys.executable, str(ctl), "ensure"], check=False)
        return proc.returncode == 0

    print(f"[WARNING] Could not find portfolio-tracker controller at {ctl}.")
    return False


def parse_synced_csv_holdings(csv_path: str = DEFAULT_SYNCED_CSV_PATH) -> List[Dict[str, Any]]:
    """Parse Google Drive synced trades CSV into current net holdings."""
    path = Path(csv_path)
    if not path.exists():
        return []

    holdings_dict: Dict[str, Dict[str, Any]] = {}
    try:
        with open(path, "r", encoding="utf-8", errors="replace") as f:
            reader = csv.DictReader(f)
            for row in reader:
                symbol = (row.get("Symbol") or "").strip().upper()
                trade_type = (row.get("Type") or "BUY").strip().upper()
                if not symbol:
                    continue
                try:
                    qty = float(row.get("Quantity") or 0.0)
                    price = float(row.get("UnitPrice") or 0.0)
                except ValueError:
                    continue
                curr = (row.get("Currency") or infer_ticker_currency(symbol)).strip().upper()

                if symbol not in holdings_dict:
                    holdings_dict[symbol] = {
                        "ticker": symbol,
                        "shares": 0.0,
                        "total_cost": 0.0,
                        "currency": curr,
                        "sector": "Other",
                        "thesis": "Synced from Google Drive"
                    }

                if trade_type == "BUY":
                    holdings_dict[symbol]["shares"] += qty
                    holdings_dict[symbol]["total_cost"] += (qty * price)
                elif trade_type == "SELL":
                    holdings_dict[symbol]["shares"] -= qty
                    holdings_dict[symbol]["total_cost"] = max(0.0, holdings_dict[symbol]["total_cost"] - (qty * price))

        results = []
        for symbol, data in holdings_dict.items():
            if data["shares"] > 0:
                avg_cost = data["total_cost"] / data["shares"] if data["shares"] > 0 else 0.0
                results.append({
                    "ticker": symbol,
                    "shares": data["shares"],
                    "avg_cost": round(avg_cost, 2),
                    "current_price": round(avg_cost, 2),
                    "currency": data["currency"],
                    "sector": data["sector"],
                    "thesis": data["thesis"]
                })
        return results
    except Exception as e:
        print(f"[WARNING] Error reading synced CSV at {csv_path}: {e}")
        return []


def parse_markdown_portfolio(filepath: str) -> Dict[str, Any]:
    """Parse YAML frontmatter and Markdown tables into a dictionary."""
    path = Path(filepath)
    if not path.exists():
        return parse_markdown_content(DEFAULT_PORTFOLIO_CONTENT)

    with open(path, "r", encoding="utf-8") as f:
        content = f.read()
    
    return parse_markdown_content(content)


def save_portfolio(data: Dict[str, Any], filepath: str = DEFAULT_PORTFOLIO_PATH) -> None:
    """Save dictionary to portfolio.md format."""
    path = Path(filepath)
    path.parent.mkdir(parents=True, exist_ok=True)
    
    lines = []
    lines.append("---")
    lines.append(f"updated_at: {datetime.now().strftime('%Y-%m-%d')}")
    lines.append(f"currency: {data.get('currency', 'USD')}")
    lines.append(f"cash: {data.get('cash', 0.0)}")
    lines.append(f"strategy_hurdle_rate_annual_pct: {data.get('strategy_hurdle_rate_annual_pct', 10.0)}")
    lines.append(f"max_position_size_pct: {data.get('max_position_size_pct', 10.0)}")
    lines.append(f"max_sector_size_pct: {data.get('max_sector_size_pct', 25.0)}")
    lines.append("---\n")
    
    lines.append("## Holdings\n")
    lines.append("| Ticker | Shares | Avg Cost | Current Price | Sector | Thesis | Currency |")
    lines.append("| :--- | :--- | :--- | :--- | :--- | :--- | :--- |")
    for h in data.get("holdings", []):
        lines.append(f"| {h.get('ticker')} | {h.get('shares')} | {h.get('avg_cost')} | {h.get('current_price')} | {h.get('sector')} | {h.get('thesis')} | {h.get('currency', 'USD')} |")
    
    lines.append("\n## Watchlist\n")
    lines.append("| Ticker | Target Buy Price | Reason |")
    lines.append("| :--- | :--- | :--- |")
    for w in data.get("watchlist", []):
        lines.append(f"| {w.get('ticker')} | {w.get('target_buy_price')} | {w.get('reason')} |")
        
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    print(f"[+] Saved portfolio to: {filepath}")


def analyze_portfolio(portfolio_data: Dict[str, Any]) -> Dict[str, Any]:
    """Calculate current market valuation and sector breakdown with FX normalization."""
    holdings = portfolio_data.get("holdings", [])
    base_currency = (portfolio_data.get("currency") or "USD").upper()
    cash = float(portfolio_data.get("cash", 0.0))
    
    evaluated_holdings = []
    total_equities_value = 0.0
    sector_values = {}

    for h in holdings:
        ticker = h.get("ticker", "").upper()
        shares = float(h.get("shares", 0.0))
        avg_cost = float(h.get("avg_cost", 0.0))
        current_price = float(h.get("current_price", avg_cost))
        sector = h.get("sector", "Other")
        holding_curr = (h.get("currency") or infer_ticker_currency(ticker)).upper()

        # Convert to base portfolio currency
        cost_basis_orig = shares * avg_cost
        cost_basis_base = convert_currency(cost_basis_orig, holding_curr, base_currency)

        mkt_val_orig = shares * current_price
        mkt_val_base = convert_currency(mkt_val_orig, holding_curr, base_currency)
        
        pnl = mkt_val_base - cost_basis_base
        pnl_pct = (pnl / cost_basis_base * 100) if cost_basis_base > 0 else 0.0

        total_equities_value += mkt_val_base
        sector_values[sector] = sector_values.get(sector, 0.0) + mkt_val_base

        evaluated_holdings.append({
            "ticker": ticker,
            "shares": shares,
            "avg_cost": avg_cost,
            "current_price": round(current_price, 2),
            "currency": holding_curr,
            "cost_basis_base": round(cost_basis_base, 2),
            "market_value_base": round(mkt_val_base, 2),
            "unrealized_pnl_base": round(pnl, 2),
            "pnl_pct": round(pnl_pct, 2),
            "sector": sector,
            "thesis": h.get("thesis", "")
        })

    total_portfolio_value = total_equities_value + cash

    for eh in evaluated_holdings:
        eh["weight_pct"] = round((eh["market_value_base"] / total_portfolio_value * 100), 2) if total_portfolio_value > 0 else 0.0

    sector_weights = {}
    for sec, val in sector_values.items():
        sector_weights[sec] = {
            "value": round(val, 2),
            "weight_pct": round((val / total_portfolio_value * 100), 2) if total_portfolio_value > 0 else 0.0
        }

    cash_weight_pct = round((cash / total_portfolio_value * 100), 2) if total_portfolio_value > 0 else 100.0

    return {
        "base_currency": base_currency,
        "base_currency_symbol": get_currency_symbol(base_currency),
        "total_portfolio_value": round(total_portfolio_value, 2),
        "total_equities_value": round(total_equities_value, 2),
        "cash_reserve": round(cash, 2),
        "cash_weight_pct": cash_weight_pct,
        "max_position_size_pct": float(portfolio_data.get("max_position_size_pct", 10.0)),
        "max_sector_size_pct": float(portfolio_data.get("max_sector_size_pct", 25.0)),
        "hurdle_rate_pct": float(portfolio_data.get("strategy_hurdle_rate_annual_pct", 10.0)),
        "holdings": evaluated_holdings,
        "sector_breakdown": sector_weights,
        "watchlist": portfolio_data.get("watchlist", [])
    }


def render_portfolio_markdown(summary: Dict[str, Any]) -> str:
    """Render a clean markdown table of portfolio metrics with currency tags."""
    sym = summary.get("base_currency_symbol", "$")
    curr = summary.get("base_currency", "USD")
    gf_online = check_ghostfolio_health()
    gf_status = "Online (http://localhost:3333)" if gf_online else "Offline (Container stack idle)"
    
    out = []
    out.append("### Current Portfolio Structure")
    out.append(f"- **Ghostfolio Container Status**: `{gf_status}`")
    out.append(f"- **Base Portfolio Currency**: `{curr}` ({sym})")
    out.append(f"- **Total Portfolio Value**: {sym}{summary['total_portfolio_value']:,.2f}")
    out.append(f"- **Cash Reserves**: {sym}{summary['cash_reserve']:,.2f} ({summary['cash_weight_pct']}%)")
    out.append(f"- **Max Position Limit**: {summary['max_position_size_pct']}% | **Max Sector Limit**: {summary['max_sector_size_pct']}%")
    out.append(f"- **Target Annual Hurdle Rate**: {summary['hurdle_rate_pct']}%\n")

    out.append("| Ticker | Sector | Shares | Avg Cost | Price | Market Val (Base) | Weight % | P&L % | Curr |")
    out.append("| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |")
    for h in summary["holdings"]:
        pnl_sign = "+" if h["pnl_pct"] >= 0 else ""
        h_sym = get_currency_symbol(h.get("currency", curr))
        out.append(f"| **{h['ticker']}** | {h['sector']} | {h['shares']} | {h_sym}{h['avg_cost']:.2f} | {h_sym}{h['current_price']:.2f} | {sym}{h['market_value_base']:,.2f} | {h['weight_pct']}% | {pnl_sign}{h['pnl_pct']}% | {h.get('currency', curr)} |")
    
    out.append("\n**Sector Distribution**:")
    for sec, data in summary["sector_breakdown"].items():
        out.append(f"- **{sec}**: {sym}{data['value']:,.2f} ({data['weight_pct']}%)")

    return "\n".join(out)


def check_candidate_fit(portfolio_data: Dict[str, Any], candidate_ticker: str, candidate_price: float, candidate_curr: str) -> str:
    """Analyze currency parity and whether candidate stock already exists in portfolio."""
    summary = analyze_portfolio(portfolio_data)
    base_curr = summary["base_currency"]
    base_sym = summary["base_currency_symbol"]
    
    price_in_base = convert_currency(candidate_price, candidate_curr, base_curr)
    
    matched_holding = None
    for h in summary["holdings"]:
        if match_ticker(candidate_ticker, h["ticker"]):
            matched_holding = h
            break
            
    out = []
    out.append("### Candidate Stock Portfolio Cross-Reference")
    out.append(f"- **Candidate Ticker**: `{candidate_ticker.upper()}` (Quoted: {get_currency_symbol(candidate_curr)}{candidate_price:.2f} {candidate_curr})")
    out.append(f"- **Normalized in Portfolio Currency ({base_curr})**: `{base_sym}{price_in_base:.2f}`")
    if matched_holding:
        out.append(f"- **Existing Portfolio Match**: Found existing position `{matched_holding['ticker']}` ({matched_holding['shares']} shares, {matched_holding['weight_pct']}% weight)")
    else:
        out.append("- **Existing Portfolio Match**: Not currently held in portfolio")
        
    return "\n".join(out)


def main():
    parser = argparse.ArgumentParser(description="Portfolio Manager for Stock Deep Dive")
    parser.add_argument("--path", "-p", default=DEFAULT_PORTFOLIO_PATH, help="Path to portfolio file")
    parser.add_argument("--list", "-l", action="store_true", help="Display current portfolio summary")
    parser.add_argument("--markdown", "-m", action="store_true", help="Output summary in markdown format")
    parser.add_argument("--check-ticker", help="Check candidate ticker fit and currency conversion (e.g. VIE.PA)")
    parser.add_argument("--price", type=float, default=0.0, help="Candidate ticker price")
    parser.add_argument("--curr", default="USD", help="Candidate ticker currency code (e.g. EUR, USD, GBP)")
    parser.add_argument("--ensure-ghostfolio", action="store_true", help="Preparation step: ensure Ghostfolio containers are running (spin up only if offline)")
    parser.add_argument("--ghostfolio-status", action="store_true", help="Check if Ghostfolio container stack is healthy")
    parser.add_argument("--csv", nargs="?", const=DEFAULT_SYNCED_CSV_PATH, help="Load holdings from synced CSV file (default: G:/My Drive/portfolio_docker_sync.csv)")
    args = parser.parse_args()

    if args.ghostfolio_status:
        is_healthy = check_ghostfolio_health()
        print(f"Ghostfolio Container Status: {'ONLINE' if is_healthy else 'OFFLINE'}")
        sys.exit(0)

    if args.ensure_ghostfolio:
        ensure_ghostfolio_running()

    # Load from synced CSV if specified
    if args.csv:
        csv_path = args.csv
        csv_holdings = parse_synced_csv_holdings(csv_path)
        if csv_holdings:
            port = {
                "currency": "USD",
                "cash": 0.0,
                "strategy_hurdle_rate_annual_pct": 10.0,
                "max_position_size_pct": 10.0,
                "max_sector_size_pct": 25.0,
                "holdings": csv_holdings,
                "watchlist": []
            }
        else:
            port = parse_markdown_portfolio(args.path)
    else:
        # Initialize default if it doesn't exist
        if not Path(args.path).exists():
            Path(args.path).parent.mkdir(parents=True, exist_ok=True)
            with open(args.path, "w", encoding="utf-8") as f:
                f.write(DEFAULT_PORTFOLIO_CONTENT)
            print(f"[*] Initialized starter portfolio at: {args.path}")
        port = parse_markdown_portfolio(args.path)

    if args.check_ticker:
        print(check_candidate_fit(port, args.check_ticker, args.price, args.curr))
        print()

    if args.list or args.markdown or (not args.check_ticker and len(sys.argv) == 1):
        summary = analyze_portfolio(port)
        if args.markdown:
            print(render_portfolio_markdown(summary))
        else:
            print(summary)


if __name__ == "__main__":
    main()
