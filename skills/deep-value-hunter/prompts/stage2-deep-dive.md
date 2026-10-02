# Stage 2 — Deep Dive

> **Lazy-Load Protocol**: View ONLY `references/valuation-methods.md`, `references/buffett-munger-gates.md`, `references/value-trap-red-flags.md`, and `templates/deep-dive-report.md` for this stage. Do NOT load screening or academic files into context.

Run this only on the 3-5 finalists the user picked from Stage 1's shortlist. Full structured report per name. Target length: 1500-2500 words. Use `templates/deep-dive-report.md` as the output skeleton.

## Subagent & Model Selection Protocol

For Stage 2 Deep Dives, automatically invoke a dedicated subagent using `invoke_subagent`:
- **TypeName**: `self`
- **Role**: `Deep Value Analyst`
- **Model**: `pro` (Thinking tier) — or the custom model specified in Stage 0 YAML under `execution.deep_dive_model`.
- **Context Pruning Rule**: Include ONLY the specific selected ticker symbol(s) and Stage 0 YAML in the subagent `Prompt`. Do NOT pass unselected shortlist stocks, dropped ticker logs, or past conversational transcript text into the subagent prompt.

This isolates the 2,500-word due-diligence report inside a high-reasoning thinking subagent context, maximizing forensic accounting quality while preserving primary session tokens.

## Pre-flight

Before writing anything, fetch these files directly from EDGAR:

1. **Most recent 10-K** (annual report)
2. **Last two 10-Q** (quarterly)
3. **Last 5 Form 4** (insider trades)
4. **Any 13D/13G filed against this CIK in last 24 months**
5. **Any 8-K in last 12 months** (material events)
6. **Most recent proxy (DEF 14A)** — for compensation

Direct URL pattern:
```
https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK=[ticker-or-cik]&type=10-K&dateb=&owner=include&count=40
```

If you can't access EDGAR, stop and tell the user the deep dive is blocked on data access — do not proceed with guessed numbers.

## Required sections (use exact headings)

### 1. TL;DR (top of report, 3 sentences max)
- What the company does (8 words)
- Why it's overlooked (12 words)
- Your verdict: Buy / Watch / Pass + target upside % (8 words)

### 2. Business in Plain English (120 words)
- What it sells, to whom, how it makes money
- Revenue mix (segment %, geography %)
- Within your circle of competence? If not, say so — "too hard pile" is a valid verdict

### 3. The Overlooked Thesis (200 words)
- **Why is this cheap?** (pick exactly one primary reason)
  - Spin-off orphan
  - Post-bankruptcy emerger
  - Microcap below coverage
  - Post-dividend-cut overreaction
  - Sum-of-parts discount
  - Index-exclusion forced selling
  - Activist entry point
  - Industry out-of-favor
- **What has to happen for the market to notice?** (named catalysts with timelines)
- **Why won't every other value investor see this?** (articulate the edge — if you can't, it's not really overlooked)

### 4. Quantitative Snapshot (table)

| Metric                        | Value | Peer median | 5yr own median | Source (filing + page)  |
|-------------------------------|-------|-------------|----------------|-------------------------|
| Price                         |       |             |                |                         |
| Market cap                    |       |             |                |                         |
| Enterprise value              |       |             |                |                         |
| EV / EBIT (TTM)               |       |             |                |                         |
| P / TBV                       |       |             |                |                         |
| FCF yield (LTM)               |       |             |                |                         |
| ROIC (3yr avg)                |       |             |                |                         |
| Gross margin                  |       |             |                |                         |
| Net debt / EBITDA             |       |             |                |                         |
| Altman Z                      |       |             |                |                         |
| Piotroski F-score             |       |             |                |                         |
| Shares out (fully diluted)    |       |             |                |                         |
| Insider ownership %           |       |             |                |                         |

### 5. Moat & Competitive Position (300 words)
- Porter's Five Forces — one sentence each, be ruthless
- Moat type (brand / cost / network / switching / regulatory) or "none"
- Moat trend — widening, stable, or narrowing — with evidence (market share, pricing power, churn)
- Best-in-class comparison in the same industry

### 6. Management & Capital Allocation (250 words)
- CEO track record — how long, prior jobs, compensation structure from DEF 14A
- Insider buying pattern — names, amounts, dates (Form 4)
- Cap allocation over last 5 years — what share of FCF went to dividends / buybacks / acquisitions / reinvestment / debt paydown?
- Buyback discipline — did they buy high or low? (show average buyback price vs. avg price that year)
- Owner-orientation test — read the last 3 CEO letters, score 1-10 for candor

### 7. Three-Scenario Valuation (use ALL three methods per scenario)

**Bull case (P=??%)** — growth tailwind + margin expansion
- Asset value per share (fully diluted): $
- Earnings Power Value (10x adjusted EBIT): $
- DCF (10yr, 10% discount, 3% terminal): $
- **Weighted fair value**: $

**Base case (P=??%)** — trend continuation
- Asset value: $
- EPV: $
- DCF: $
- **Weighted fair value**: $

**Bear case (P=??%)** — margin compression or dilution
- Liquidation value: $
- EPV at 6x: $
- DCF with zero terminal growth: $
- **Weighted fair value**: $

**Probability-weighted fair value**: $  (× bull + × base + × bear)
**Current price**: $
**Margin of safety**: __%
**Target upside at base case**: __%

> Assign probabilities explicitly and justify each in one sentence. "It could happen" is not a probability.

### 8. Value Trap Red Flags Checklist (from references/value-trap-red-flags.md)
For each of the 12 red flags, mark ✅ clear / ⚠️ warning / ❌ triggered. If 2+ are triggered, the verdict MUST be Pass unless you have a specific argument for why they don't apply.

### 9. Catalyst Watch (100 words)
- Near-term (next 1-2 quarters): earnings, spin-off completion, asset sale, contract, regulatory decision
- Medium-term (1-3 years): margin normalization, debt paydown, industry cycle
- Long-term (3+ years): terminal valuation, strategic optionality

### 10. Position Sizing Recommendation
- **Conviction Tier & Sizing**: If Buy, assign allocation % using Kelly-lite (`f* = (edge / odds)` capped at 5.0%–10.0% max per position).
- **Exact Dollar & Share Target**: Convert the sizing % into exact capital allocation ($ amount) and share count using the user's live portfolio value and cash balance from Ghostfolio (`http://localhost:3333` / `portfolio_manager.py` / `G:\My Drive\portfolio_docker_sync.csv`).
- **Sector Limit Check**: Verify that adding this position will not exceed the 25.0% maximum sector concentration ceiling.
- **Stop conditions**: What price / news / filing would invalidate the thesis and force an immediate exit?
- **Re-evaluation triggers**: Next 10-K, upcoming earnings call, or specific catalyst milestone.

### 11. Sources
- List every EDGAR filing URL referenced
- List every dataset / paper referenced
- No bare claims without citations

### 12. Appendix: What You're Trusting
- 3 specific assumptions that, if wrong, kill the thesis
- For each, state how to verify cheaply before putting real money in

## After the report

1. **Save as markdown** at `reports/[TICKER]-[YYYY-MM-DD].md`
2. **Convert to .docx** via `pandoc [file].md -o [file].docx`
3. **Report the .docx path** to the user

## Anti-patterns

- ❌ Writing a report to justify the Stage 1 ranking — if the deep dive finds problems, lower the rating
- ❌ Target prices without a scenario-weighted average
- ❌ Using LTM data and ignoring 5-year history
- ❌ "Strong moat" as a claim without evidence
- ❌ Ignoring dilution (always use fully diluted share count)
- ❌ Skipping the value-trap checklist because "it looks good"
