#!/usr/bin/env python3
"""
Trading 212 API Diagnostic & Order Inspection Utility
------------------------------------------------------
Queries the Trading 212 Public API (Invest / Stocks ISA) for historical orders,
verifies API credentials, and outputs formatted orders for inspection or manual
copy-paste into Google Sheets.

Trading 212 uses HTTP Basic Authentication with:
- API Key ID (Username)
- Secret Key (Password)
Pass either via --api-key and --api-secret, or as --api-key "KEY_ID:SECRET".

NOTE: Do NOT write directly to 'portfolio_docker_sync.csv'!
Google Sheets is the single source of truth for the portfolio ledger.
"""

import argparse
import base64
import json
import os
import re
import sys
import urllib.error
import urllib.request
from datetime import datetime
from typing import Any, Dict, List, Optional

# Ensure console handles UTF-8 on Windows
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

LIVE_BASE_URL = "https://live.trading212.com/api/v0"
DEMO_BASE_URL = "https://demo.trading212.com/api/v0"


def clean_ticker_symbol(raw_ticker: str) -> str:
    """Normalize Trading 212 ticker (e.g. AAPL_US_EQ -> AAPL)."""
    if not raw_ticker:
        return ""
    # Strip common exchange suffixes like _US_EQ, _UK_EQ, _DE_EQ, _FR_EQ
    cleaned = re.sub(r"_[A-Z]{2}_EQ$", "", raw_ticker.strip(), flags=re.IGNORECASE)
    return cleaned.upper()


def build_auth_header(api_key: str, api_secret: Optional[str] = None) -> str:
    """Construct HTTP Basic Authentication header for Trading 212."""
    if api_secret:
        combined = f"{api_key.strip()}:{api_secret.strip()}"
        encoded = base64.b64encode(combined.encode("utf-8")).decode("utf-8")
        return f"Basic {encoded}"
    elif ":" in api_key:
        encoded = base64.b64encode(api_key.strip().encode("utf-8")).decode("utf-8")
        return f"Basic {encoded}"
    elif api_key.startswith("Basic "):
        return api_key.strip()
    return api_key.strip()


def fetch_account_currency(base_url: str, auth_header: str) -> str:
    """Query /equity/account/info to get the base account currency."""
    url = f"{base_url}/equity/account/info"
    req = urllib.request.Request(url, headers={
        "Authorization": auth_header,
        "Accept": "application/json",
        "User-Agent": "Antigravity-Trading212-Sync/1.0"
    })
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            if resp.status == 200:
                data = json.loads(resp.read().decode("utf-8"))
                return str(data.get("currencyCode") or data.get("currency") or "USD").upper()
    except Exception:
        pass
    return "USD"


def fetch_historical_orders(
    api_key: str,
    api_secret: Optional[str] = None,
    demo: bool = False,
    limit: int = 50,
    max_pages: int = 5,
    ticker: Optional[str] = None
) -> List[Dict[str, Any]]:
    """
    Fetch executed orders from Trading 212 API handling cursor pagination.
    Handles both nested schema ({order: ..., fill: ...}) and flat schema.
    """
    base_url = DEMO_BASE_URL if demo else LIVE_BASE_URL
    orders: List[Dict[str, Any]] = []
    next_path = f"/equity/history/orders?limit={min(50, limit)}"
    if ticker:
        next_path += f"&ticker={ticker}"

    auth_header = build_auth_header(api_key, api_secret)
    headers = {
        "Authorization": auth_header,
        "User-Agent": "Antigravity-Trading212-Sync/1.0",
        "Accept": "application/json"
    }

    default_currency = fetch_account_currency(base_url, auth_header)

    page = 0
    while next_path and page < max_pages:
        page += 1
        url = next_path if next_path.startswith("http") else f"{base_url}{next_path}"
        if url.startswith("http://"):
            url = "https://" + url[7:]
        req = urllib.request.Request(url, headers=headers)

        try:
            with urllib.request.urlopen(req, timeout=15) as resp:
                if resp.status != 200:
                    print(f"[ERROR] API returned HTTP {resp.status}", file=sys.stderr)
                    break
                data = json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            if e.code in (401, 403):
                print(f"[ERROR] Authentication failed (HTTP {e.code}). Verify API Key ID and Secret Key, and ensure 'History' permissions are checked.", file=sys.stderr)
            elif e.code == 429:
                print("[WARNING] Trading 212 rate limit reached (20 req/min for history). Backing off.", file=sys.stderr)
            else:
                print(f"[ERROR] HTTP Error {e.code}: {e.reason}", file=sys.stderr)
            break
        except Exception as e:
            print(f"[ERROR] Network connection failed: {e}", file=sys.stderr)
            break

        items = data.get("items", [])
        if not items:
            break

        for itm in items:
            # T212 Schema: support nested order/fill or flat
            order_obj = itm.get("order") if isinstance(itm.get("order"), dict) else itm
            fill_obj = itm.get("fill") if isinstance(itm.get("fill"), dict) else itm
            wallet_obj = fill_obj.get("walletImpact") if isinstance(fill_obj.get("walletImpact"), dict) else {}

            status = str(order_obj.get("status") or itm.get("status") or "").upper()
            if status not in ("FILLED", "EXECUTED", "PARTIALLY_FILLED") and not fill_obj.get("filledAt") and not order_obj.get("dateExecuted"):
                continue

            raw_qty = fill_obj.get("quantity") if fill_obj.get("quantity") is not None else (
                order_obj.get("filledQuantity") if order_obj.get("filledQuantity") is not None else (
                    order_obj.get("orderedQuantity") if order_obj.get("orderedQuantity") is not None else itm.get("quantity")
                )
            )
            try:
                num_qty = float(raw_qty or 0.0)
            except (ValueError, TypeError):
                num_qty = 0.0

            if num_qty == 0:
                continue

            side_str = str(order_obj.get("side") or fill_obj.get("side") or order_obj.get("type") or "").upper()
            is_sell = (num_qty < 0) or side_str == "SELL" or "SELL" in side_str
            is_buy = not is_sell
            abs_qty = abs(num_qty)

            price = 0.0
            raw_price = fill_obj.get("price") or order_obj.get("fillPrice") or itm.get("fillPrice")
            if raw_price:
                try:
                    price = float(raw_price)
                except (ValueError, TypeError):
                    price = 0.0

            if price == 0 and (order_obj.get("filledValue") or itm.get("filledValue")) and abs_qty > 0:
                try:
                    val = float(order_obj.get("filledValue") or itm.get("filledValue") or 0.0)
                    price = abs(val / abs_qty)
                except Exception:
                    pass

            raw_date = fill_obj.get("filledAt") or order_obj.get("dateExecuted") or order_obj.get("createdAt") or itm.get("dateExecuted") or itm.get("dateCreated") or ""
            date_str = ""
            if raw_date:
                try:
                    dt = datetime.fromisoformat(str(raw_date).replace("Z", "+00:00"))
                    date_str = dt.strftime("%Y-%m-%d")
                except Exception:
                    date_str = str(raw_date)[:10]

            raw_ticker = str(order_obj.get("ticker") or itm.get("ticker") or "")
            symbol = clean_ticker_symbol(raw_ticker)
            if not symbol:
                continue

            curr = str(order_obj.get("currency") or fill_obj.get("currency") or itm.get("currencyCode") or itm.get("currency") or default_currency).upper()

            fee = 0.0
            taxes = wallet_obj.get("taxes") or itm.get("taxes") or []
            if isinstance(taxes, list):
                for t in taxes:
                    if isinstance(t, dict):
                        fee += float(t.get("fillCost") or t.get("quantity") or 0.0)

            order_id = str(order_obj.get("id") or itm.get("id") or "")

            orders.append({
                "Date": date_str,
                "Type": "BUY" if is_buy else "SELL",
                "Symbol": symbol,
                "Quantity": abs_qty,
                "UnitPrice": round(price, 4),
                "Currency": curr,
                "Fee": round(fee, 2),
                "Broker": "Trading212",
                "OrderId": order_id
            })

        next_path = data.get("nextPagePath")

    return orders


def print_tsv(orders: List[Dict[str, Any]]):
    """Print orders in tab-separated format for easy copy-pasting into Google Sheets."""
    headers = ["Date", "Type", "Symbol", "Quantity", "UnitPrice", "Currency", "Fee", "Broker", "OrderId"]
    print("\t".join(headers))
    for o in orders:
        row = [
            str(o.get("Date", "")),
            str(o.get("Type", "")),
            str(o.get("Symbol", "")),
            str(o.get("Quantity", "")),
            str(o.get("UnitPrice", "")),
            str(o.get("Currency", "")),
            str(o.get("Fee", "")),
            str(o.get("Broker", "")),
            str(o.get("OrderId", ""))
        ]
        print("\t".join(row))


def print_table(orders: List[Dict[str, Any]]):
    """Print orders formatted as a human-readable table."""
    print(f"\n[OK] Retrieved {len(orders)} filled orders from Trading 212:\n")
    print(f"{'Date':<12} {'Type':<6} {'Symbol':<10} {'Shares':<10} {'UnitPrice':<12} {'Currency':<8} {'Broker':<12} {'OrderId'}")
    print("-" * 85)
    for o in orders:
        print(f"{o['Date']:<12} {o['Type']:<6} {o['Symbol']:<10} {o['Quantity']:<10} ${o['UnitPrice']:<11.2f} {o['Currency']:<8} {o['Broker']:<12} {o['OrderId']}")


def main():
    parser = argparse.ArgumentParser(
        description="Inspect and verify executed trades from Trading 212 API"
    )
    parser.add_argument("--api-key", default=os.getenv("TRADING212_API_KEY"), help="Trading 212 API Key ID (or KEY_ID:SECRET)")
    parser.add_argument("--api-secret", default=os.getenv("TRADING212_API_SECRET"), help="Trading 212 Secret Key")
    parser.add_argument("--demo", action="store_true", help="Use Trading 212 Practice / Demo environment")
    parser.add_argument("--limit", type=int, default=50, help="Max orders to fetch per request (default: 50)")
    parser.add_argument("--max-pages", type=int, default=5, help="Max pagination depth (default: 5)")
    parser.add_argument("--ticker", help="Filter by specific instrument ticker (e.g. AAPL)")
    parser.add_argument("--json", action="store_true", help="Output results as JSON")
    parser.add_argument("--tsv", action="store_true", help="Output results as TSV (Tab-Separated) to copy-paste into Google Sheets")

    args = parser.parse_args()

    if not args.api_key:
        print("[ERROR] Trading 212 API Key ID is required. Supply via --api-key or set TRADING212_API_KEY env.", file=sys.stderr)
        sys.exit(1)

    print(f"[*] Fetching historical orders from Trading 212 ({'DEMO' if args.demo else 'LIVE'})...", file=sys.stderr)
    orders = fetch_historical_orders(
        api_key=args.api_key,
        api_secret=args.api_secret,
        demo=args.demo,
        limit=args.limit,
        max_pages=args.max_pages,
        ticker=args.ticker
    )

    if args.json:
        print(json.dumps(orders, indent=2))
    elif args.tsv:
        print_tsv(orders)
    else:
        print_table(orders)


if __name__ == "__main__":
    main()
