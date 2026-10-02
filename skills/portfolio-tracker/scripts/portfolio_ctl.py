#!/usr/bin/env python3
"""
Portfolio Tracker CLI Controller
--------------------------------
Unified controller for the Ghostfolio ephemeral Docker pipeline and Google Drive sync.
Provides status checks, idempotent container spin-up (preparation step),
clean teardown, and portfolio holdings extraction.
"""

import argparse
import csv
import json
import os
import platform
import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

# Ensure console handles UTF-8 on Windows
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

DEFAULT_GHOSTFOLIO_URL = os.getenv("GHOSTFOLIO_URL", "http://localhost:3333").rstrip("/")
DEFAULT_CSV_PATH = os.getenv("LOCAL_CSV_PATH", r"G:\My Drive\portfolio_docker_sync.csv")


def find_repo_root() -> Path:
    """Dynamically locate the portfolio-tracker repository or subfolder root."""
    current = Path(__file__).resolve()
    for parent in [current] + list(current.parents):
        # Monorepo layout: check if 'portfolio-tracker' subdirectory exists
        pt_dir = parent / "portfolio-tracker"
        if pt_dir.is_dir() and (pt_dir / "docker-compose.yml").exists() and (
            (pt_dir / "start.ps1").exists() or (pt_dir / "start.sh").exists()
        ):
            return pt_dir
        # Standalone layout: docker-compose.yml at root
        if (parent / "docker-compose.yml").exists() and (
            (parent / "start.ps1").exists() or (parent / "start.sh").exists()
        ):
            return parent
    # Fallback to 3 levels up from scripts/
    return Path(__file__).resolve().parents[2]


def check_ghostfolio_health(url: str = DEFAULT_GHOSTFOLIO_URL, timeout: float = 2.0) -> bool:
    """Return True if Ghostfolio API responds with HTTP 200 on /api/v1/health."""
    health_url = f"{url}/api/v1/health"
    try:
        req = urllib.request.Request(health_url, headers={"User-Agent": "Antigravity-PortfolioTracker/1.0"})
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.status == 200
    except Exception:
        return False


def run_start(repo_root: Optional[Path] = None, watch: bool = False) -> int:
    """Run the platform-appropriate startup script."""
    root = repo_root or find_repo_root()
    is_windows = platform.system() == "Windows"

    if is_windows:
        script = root / "start.ps1"
        if not script.exists():
            print(f"[ERROR] Could not find start.ps1 at {script}", file=sys.stderr)
            return 1
        cmd = ["powershell", "-ExecutionPolicy", "Bypass", "-File", str(script)]
        if watch:
            cmd.append("-Watch")
    else:
        script = root / "start.sh"
        if not script.exists():
            print(f"[ERROR] Could not find start.sh at {script}", file=sys.stderr)
            return 1
        cmd = ["bash", str(script)]
        if watch:
            cmd.append("--watch")

    print(f"[*] Starting Ghostfolio stack via {script.name}...")
    proc = subprocess.run(cmd, cwd=str(root))
    return proc.returncode


def run_cleanup(repo_root: Optional[Path] = None) -> int:
    """Run the platform-appropriate cleanup script."""
    root = repo_root or find_repo_root()
    is_windows = platform.system() == "Windows"

    if is_windows:
        script = root / "cleanup.ps1"
        if not script.exists():
            print(f"[ERROR] Could not find cleanup.ps1 at {script}", file=sys.stderr)
            return 1
        cmd = ["powershell", "-ExecutionPolicy", "Bypass", "-File", str(script)]
    else:
        script = root / "cleanup.sh"
        if not script.exists():
            print(f"[ERROR] Could not find cleanup.sh at {script}", file=sys.stderr)
            return 1
        cmd = ["bash", str(script)]

    print(f"[*] Stopping and cleaning Ghostfolio stack via {script.name}...")
    proc = subprocess.run(cmd, cwd=str(root))
    return proc.returncode


def ensure_running(repo_root: Optional[Path] = None, url: str = DEFAULT_GHOSTFOLIO_URL) -> bool:
    """
    Preparation step:
    Checks if Ghostfolio is healthy on http://localhost:3333.
    If already running -> skips launch and returns True.
    If offline -> starts containers and waits for healthcheck.
    """
    if check_ghostfolio_health(url):
        print(f"[OK] Ghostfolio stack is ALREADY RUNNING and healthy at {url}.")
        return True

    print(f"[*] Ghostfolio is OFFLINE. Executing container preparation step...")
    code = run_start(repo_root)
    if code != 0:
        print(f"[WARNING] Startup script finished with exit code {code}.")
    
    # Verify health
    healthy = check_ghostfolio_health(url, timeout=5.0)
    if healthy:
        print(f"[OK] Ghostfolio stack successfully spun up and healthy at {url}!")
    else:
        print(f"[ERROR] Ghostfolio failed to respond healthy at {url}.", file=sys.stderr)
    return healthy


def parse_csv_holdings(csv_path: str = DEFAULT_CSV_PATH) -> List[Dict[str, Any]]:
    """Parse transactions from the Google Drive synced CSV into current aggregated holdings."""
    path = Path(csv_path)
    if not path.exists():
        return []

    trades_by_symbol: Dict[str, Dict[str, Any]] = {}
    try:
        with open(path, "r", encoding="utf-8", errors="replace") as f:
            reader = csv.DictReader(f)
            for row in reader:
                raw_sym = (row.get("Symbol") or "").strip().upper()
                sym = raw_sym
                if sym == "ANTM":
                    sym = "ELV"
                elif sym in ("013CD_EQ", "013C.DE", "013C", "GF_013C_DE"):
                    sym = "013C.F"
                elif sym in ("HOP_EQ", "HOP.PA", "HOP"):
                    sym = "HO.PA"
                elif sym in ("ETH", "ETH-USD", "ETH/USD"):
                    sym = "ETHUSD"
                elif sym in ("USDE", "USDE-USD", "USDE/USD"):
                    sym = "USDE29470USD"
                elif sym in ("SUSDE", "SUSDE-USD", "SUSDE/USD"):
                    sym = "SUSDEUSD"
                elif sym in ("BTC", "BTC-USD", "BTC/USD"):
                    sym = "BTCUSD"
                elif sym in ("SOL", "SOL-USD", "SOL/USD"):
                    sym = "SOLUSD"
                ttype = (row.get("Type") or "BUY").strip().upper()
                if not sym:
                    continue
                try:
                    qty = float(row.get("Quantity") or 0.0)
                    price = float(row.get("UnitPrice") or 0.0)
                except ValueError:
                    continue
                curr = (row.get("Currency") or "").strip().upper()
                if any(k in sym for k in ("CASH", "HYSA", "SAVINGS")):
                    curr = curr or "AUD"
                elif (
                    sym.endswith(".DE")
                    or sym.endswith(".AS")
                    or sym.endswith(".PA")
                    or sym.endswith(".F")
                    or sym.endswith("D_EQ")
                    or sym.endswith("A_EQ")
                    or sym.endswith("P_EQ")
                    or sym in ("HO.PA", "013C.F")
                ):
                    curr = "EUR"
                elif sym.endswith(".L") or sym.endswith("L_EQ"):
                    curr = "GBP"
                elif curr == "AUD" or not curr:
                    curr = "USD"

                if sym not in trades_by_symbol:
                    trades_by_symbol[sym] = {
                        "ticker": sym,
                        "shares": 0.0,
                        "total_cost": 0.0,
                        "currency": curr,
                        "buy_count": 0,
                        "sell_count": 0,
                        "brokers": set()
                    }

                raw_broker = (row.get("Broker") or "").strip()
                if raw_broker:
                    trades_by_symbol[sym]["brokers"].add(raw_broker)

                if ttype == "BUY":
                    trades_by_symbol[sym]["shares"] += qty
                    trades_by_symbol[sym]["total_cost"] += (qty * price)
                    trades_by_symbol[sym]["buy_count"] += 1
                elif ttype == "SELL":
                    trades_by_symbol[sym]["shares"] -= qty
                    trades_by_symbol[sym]["total_cost"] = max(0.0, trades_by_symbol[sym]["total_cost"] - (qty * price))
                    trades_by_symbol[sym]["sell_count"] += 1

        holdings = []
        for sym, d in trades_by_symbol.items():
            if d["shares"] > 0:
                avg_cost = d["total_cost"] / d["shares"] if d["shares"] > 0 else 0.0
                holdings.append({
                    "ticker": sym,
                    "shares": round(d["shares"], 4),
                    "avg_cost": round(avg_cost, 2),
                    "current_price": round(avg_cost, 2),
                    "market_value": round(d["shares"] * avg_cost, 2),
                    "currency": d["currency"],
                    "buy_count": d["buy_count"],
                    "sell_count": d["sell_count"],
                    "brokers": sorted(list(d["brokers"])) if d["brokers"] else ["Manual"]
                })
        return holdings
    except Exception as e:
        print(f"[WARNING] Error reading synced CSV at {csv_path}: {e}", file=sys.stderr)
        return []


def format_holdings_markdown(holdings: List[Dict[str, Any]], is_online: bool, url: str) -> str:
    """Format holdings into clean markdown table."""
    status_str = f"Online ({url})" if is_online else "Offline (Container stack idle)"
    total_val = sum(h["market_value"] for h in holdings)

    lines = []
    lines.append("### Portfolio Holdings Overview")
    lines.append(f"- **Ghostfolio Container Status**: `{status_str}`")
    lines.append(f"- **Data Source**: `{DEFAULT_CSV_PATH}`")
    lines.append(f"- **Total Asset Holdings**: {len(holdings)} positions")
    lines.append(f"- **Estimated Book Value**: ${total_val:,.2f}\n")

    if not holdings:
        lines.append("*No active holdings found in synced CSV.*")
        return "\n".join(lines)

    has_brokers = any(h.get("brokers") and h["brokers"] != ["Manual"] for h in holdings)
    if has_brokers:
        lines.append("| Ticker | Shares | Avg Cost | Est. Market Value | Currency | Broker(s) |")
        lines.append("| :--- | :---: | :---: | :---: | :---: | :--- |")
        for h in holdings:
            weight = (h["market_value"] / total_val * 100) if total_val > 0 else 0.0
            brk_str = ", ".join(h.get("brokers", []))
            lines.append(f"| **{h['ticker']}** | {h['shares']} | ${h['avg_cost']:.2f} | ${h['market_value']:,.2f} ({weight:.1f}%) | {h['currency']} | {brk_str} |")
    else:
        lines.append("| Ticker | Shares | Avg Cost | Est. Market Value | Currency |")
        lines.append("| :--- | :---: | :---: | :---: | :---: |")
        for h in holdings:
            weight = (h["market_value"] / total_val * 100) if total_val > 0 else 0.0
            lines.append(f"| **{h['ticker']}** | {h['shares']} | ${h['avg_cost']:.2f} | ${h['market_value']:,.2f} ({weight:.1f}%) | {h['currency']} |")

    return "\n".join(lines)


def install_skill() -> int:
    """Register skill suite globally into Antigravity."""
    root = find_repo_root()
    monorepo_root = root.parent if (root.parent / "install.ps1").exists() else root
    is_windows = platform.system() == "Windows"
    installer = monorepo_root / ("install.ps1" if is_windows else "install.sh")
    if installer.exists():
        if is_windows:
            cmd = ["powershell", "-ExecutionPolicy", "Bypass", "-File", str(installer)]
        else:
            cmd = ["bash", str(installer)]
        proc = subprocess.run(cmd, check=False)
        return proc.returncode

    skill_src = root / "skills" / "portfolio-tracker"
    global_dir = Path.home() / ".gemini" / "config" / "skills"
    global_dir.mkdir(parents=True, exist_ok=True)
    target = global_dir / "portfolio-tracker"

    if target.exists() or target.is_symlink():
        print(f"[OK] Skill is already installed globally at: {target}")
        return 0

    print(f"[*] Installing skill: {skill_src} -> {target}")
    if is_windows:
        cmd = ["powershell", "-Command", f'New-Item -ItemType Junction -Path "{target}" -Target "{skill_src}"']
        proc = subprocess.run(cmd, check=False)
        if proc.returncode == 0:
            print("[OK] Skill installed successfully globally via NTFS directory junction!")
            return 0
        return proc.returncode
    else:
        try:
            target.symlink_to(skill_src, target_is_directory=True)
            print("[OK] Skill installed successfully globally via symlink!")
            return 0
        except Exception as e:
            print(f"[ERROR] Failed to create symlink: {e}", file=sys.stderr)
            return 1


def uninstall_skill() -> int:
    """Remove global skill link from ~/.gemini/config/skills/portfolio-tracker."""
    target = Path.home() / ".gemini" / "config" / "skills" / "portfolio-tracker"
    if not (target.exists() or target.is_symlink()):
        print(f"[INFO] Skill is not currently installed at: {target}")
        return 0

    print(f"[*] Removing global skill link: {target}")
    if platform.system() == "Windows":
        cmd = ["powershell", "-Command", f'Remove-Item -Force "{target}"']
        proc = subprocess.run(cmd, check=False)
        if proc.returncode == 0:
            print("[OK] Skill link removed successfully!")
            return 0
        return proc.returncode
    else:
        try:
            target.unlink()
            print("[OK] Skill symlink removed successfully!")
            return 0
        except Exception as e:
            print(f"[ERROR] Failed to unlink: {e}", file=sys.stderr)
            return 1


def main():
    parser = argparse.ArgumentParser(description="Portfolio Tracker CLI Controller")
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")

    # install & uninstall
    subparsers.add_parser("install", help="Register skill globally in ~/.gemini/config/skills/portfolio-tracker")
    subparsers.add_parser("uninstall", help="Unregister skill from ~/.gemini/config/skills/portfolio-tracker")

    # status
    p_status = subparsers.add_parser("status", help="Check if Ghostfolio container stack is running and healthy")
    p_status.add_argument("--url", default=DEFAULT_GHOSTFOLIO_URL, help="Ghostfolio base URL")

    # ensure
    p_ensure = subparsers.add_parser("ensure", help="Preparation step: launch containers only if not already running")
    p_ensure.add_argument("--url", default=DEFAULT_GHOSTFOLIO_URL, help="Ghostfolio base URL")

    # start
    p_start = subparsers.add_parser("start", help="Spin up Ghostfolio containers and trigger sync sidecar")
    p_start.add_argument("--watch", action="store_true", help="Start sidecar in continuous watch mode")

    # cleanup / stop
    subparsers.add_parser("cleanup", help="Stop Ghostfolio containers and clean up ephemeral data")
    subparsers.add_parser("stop", help="Alias for cleanup")

    # holdings
    p_holdings = subparsers.add_parser("holdings", help="Get current portfolio holdings from synced CSV / Ghostfolio")
    p_holdings.add_argument("--csv", default=DEFAULT_CSV_PATH, help="Path to synced CSV file")
    p_holdings.add_argument("--json", action="store_true", help="Output raw JSON")
    p_holdings.add_argument("--symbols-only", action="store_true", help="Output comma-separated symbol list")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(0)

    if args.command == "install":
        code = install_skill()
        sys.exit(code)

    elif args.command == "uninstall":
        code = uninstall_skill()
        sys.exit(code)

    elif args.command == "status":
        healthy = check_ghostfolio_health(args.url)
        print(f"Ghostfolio Container Status: {'ONLINE' if healthy else 'OFFLINE'} ({args.url})")
        sys.exit(0 if healthy else 1)

    elif args.command == "ensure":
        healthy = ensure_running(url=args.url)
        sys.exit(0 if healthy else 1)

    elif args.command == "start":
        code = run_start(watch=args.watch)
        sys.exit(code)

    elif args.command in ("cleanup", "stop"):
        code = run_cleanup()
        sys.exit(code)

    elif args.command == "holdings":
        is_online = check_ghostfolio_health()
        holdings = parse_csv_holdings(args.csv)

        if args.symbols_only:
            symbols = [h["ticker"] for h in holdings]
            print(",".join(symbols))
            sys.exit(0)

        if args.json:
            out = {
                "ghostfolio_online": is_online,
                "url": DEFAULT_GHOSTFOLIO_URL,
                "csv_path": args.csv,
                "holdings_count": len(holdings),
                "holdings": holdings
            }
            print(json.dumps(out, indent=2))
        else:
            print(format_holdings_markdown(holdings, is_online, DEFAULT_GHOSTFOLIO_URL))
        sys.exit(0)


if __name__ == "__main__":
    main()
