# Stage 1 — Discovery & Screen

> **Lazy-Load Protocol**: View ONLY `references/quantitative-filters.md` and `references/overlooked-pockets.md` for this stage. Do NOT load valuation, academic, or report template files into context.

Your job in this stage is to **narrow the universe to exactly 20 candidates** and rank them. Do NOT write long due-diligence reports. Keep each candidate thesis to **EXACTLY ONE SENTENCE** for token efficiency so the user can easily review and select candidates.

## Workflow (follow in order)

### A. Load the user's Stage 0 YAML

Read the constraints YAML from Stage 0. Everything below is filtered by those constraints.

### B. Apply quantitative screens (hard gates)

*(Note: You can run `python scripts/screen.py --tickers T1 T2 T3...` or `python scripts/screen.py` to automatically fetch metrics, calculate Piotroski & Altman Z scores, and compute candidate rank scores).*

Pull from `references/quantitative-filters.md`. In order of priority:

1. **Altman Z-score** ≥ `min_altman_z` (reject bankruptcy risk)
2. **Piotroski F-score** ≥ 7 out of 9 (reject declining fundamentals)
3. **EV/EBIT** ≤ 10 (Greenblatt earnings yield floor) OR **P/TBV** ≤ 1.2 (Graham bargain floor)
4. **FCF yield** ≥ 8% on last twelve months (cash generation check)
5. **ROIC** ≥ 12% on last three years (quality filter, skip if pure asset play)
6. **Net debt / EBITDA** ≤ 3 (leverage ceiling)
7. **Share count** not increasing >3%/year over last 5 years (dilution filter)

**A ticker must pass at least 5 of the 7 gates to advance.** The only exception is classic Graham net-nets where only gate 1 + a NCAV test matter.

### C. Apply "overlooked pocket" heuristics (soft boosts)

Pull from `references/overlooked-pockets.md`. Add +1 to a candidate's rank score for each of these that applies:

- Spun off in the last 24 months (Greenblatt edge)
- Emerged from bankruptcy in the last 36 months
- Not covered by any major sell-side analyst (≤ 2 ratings published this year)
- Insider buying cluster: ≥ 2 insiders buying ≥ $50k each in the last 6 months (Form 4)
- 13D/13G filed by a credible activist in last 12 months (Icahn, Einhorn, Burry, Pabrai, Ackman, etc.)
- Index exclusion / forced selling event in the last 6 months
- Dual-class or holding-company structure creating a sum-of-parts discount
- Foreign listing with US investor neglect (e.g., Hong Kong, Tokyo secondary)
- Post-dividend-cut drop (>20% price decline in past 6 months with intact FCF)
- Mega-cap / Large-cap cyclical drawdown or sentiment overreaction (Fallen Angel)
- 52-week low within last 30 days

### D. Rank and produce shortlist

For each of ~20 survivors, compute composite_score and sort descending. Pick top 20.

### E. Sector & Factor Overlap Check (with Ghostfolio Cross-Reference)

Analyze sector & factor correlation across the top 20, cross-referencing the user's live portfolio from Ghostfolio (`http://localhost:3333`), synced trades (`G:\My Drive\portfolio_docker_sync.csv`), or `portfolio.md`:
- **Existing Position Flag**: Flag if any candidate is already held in the user's portfolio (`[ALREADY HELD IN PORTFOLIO]`).
- **Sector Concentration Guard**: Check existing portfolio sector exposures. Reject or de-prioritize candidate clusters that would push an already heavy sector past the 25% maximum sector limit.
- **Factor Risk Clustering**: Group candidates by sector (e.g. Technology, Industrials, Energy, Financials, Healthcare, Consumer) and identify high-correlation factor risks (interest rate sensitivity, cyclical commodities).
- **Suggested Diversified Basket**: Highlight a recommended multi-sector basket of 3–5 candidates that maximizes diversification against the user's existing holdings.

### F. Output format (STRICT — ONE SENTENCE THESIS per name)

```markdown
# Shortlist — [Date] — [Universe: e.g., US stocks $300M+ including mega-caps]

## Pre-screen stats
- Universe size before gates: [N]
- After Altman/Piotroski: [N]
- After valuation gates: [N]
- Final shortlist: 20 names

## Ranked candidates

### 1. TICKER — Company Name ($X.XX, Market Cap: $Y.YB | Sector: [Sector])
- **Thesis (1 sentence)**: [One precise sentence stating the overlooked catalyst, valuation edge, and rough upside.]
- **Key Metrics**: Altman Z=X.X | Piotroski=X/9 | EV/EBIT=X.X | FCF yield=X% | ROIC=X% | Net Debt/EBITDA=X.X | Composite: 0.XX
- **Catalyst / Tailwind**: [Spin-off / 13D / Form 4 cluster / Fallen angel]
- **Primary Source**: https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK=[cik]&type=10-K

### 2. TICKER — ...
[same concise format for all 20 candidates]

## Sector & Factor Overlap Analysis
- **Sector breakdown**: [e.g., Tech: 4, Energy: 3, Industrials: 5, Financials: 3, Healthcare: 3, Consumer: 2]
- **Factor correlation note**: [Flag any heavy industry or macro risk cluster]
- **Suggested Diversified Basket (3-5 names)**: [Suggest 3-5 candidates spanning different sectors]

*(Note: Full screening data & dropped ticker audit logs are automatically saved to `scratch/screening_results.json` to keep chat context memory clean.)*
```

### G. Stop & Await User Selection

**DO NOT proceed automatically to Stage 2 or Stage 3.** Present the shortlist and ask the user:
> "Which 3-5 candidates would you like to run Stage 3 Quick Verdicts on (or proceed directly to Stage 2 Deep Dives)?"

## Data sources (priority order)

1. **SEC EDGAR full-text search**: `https://efts.sec.gov/LATEST/search-index?q=&dateRange=custom&forms=10-K`
2. **SEC EDGAR company filings**: `https://www.sec.gov/cgi-bin/browse-edgar`
3. **OpenSourceAP / CrossSection** (Chen-Zimmermann): already-replicated anomaly data at https://github.com/OpenSourceAP/CrossSection
4. **yfinance** via Python: for price, shares outstanding, basic ratios
5. **Fintel.io** or **OpenInsider**: Form 4 aggregation
6. **StockAnalysis.com** / **Stockanalysis.io**: screener with free filters
7. **WSJ markets** / **Bloomberg**: only as last resort, and only for data not in EDGAR

Never use Seeking Alpha or GuruFocus as a **source of facts**. They are commentary aggregators — fine for sentiment, not for numbers.

## Performance note

If the user has access to the Chen-Zimmermann open-source anomaly dataset at `D:\projects\meta-pipe\` or similar, use it to pre-filter candidates by anomaly score before running the gates. This is the single biggest leverage — ~210 pre-computed anomalies for the entire US universe going back to 1926.
