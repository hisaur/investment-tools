# Quantitative Filters — Formulas and Thresholds

Every filter in this file has a peer-reviewed citation behind it. Use these as hard gates in Stage 1. Do not lower the thresholds to "let more stocks through" — the point is ruthless rejection.

## 1. Piotroski F-Score (9-point fundamental quality)

**Citation**: Piotroski, J. (2000). "Value Investing: The Use of Historical Financial Statement Information to Separate Winners from Losers from Losers." *J. Accounting Research* 38.

**Purpose**: Separates high-B/M stocks that are actually improving from those that are value traps.

**Computation** — one point for each "yes":

### Profitability (4 points)
1. Net income > 0 (last fiscal year)
2. Operating cash flow > 0 (last fiscal year)
3. ΔROA > 0 (this year's ROA > last year's ROA)
4. Accruals: CFO > Net income (cash earnings quality check)

### Leverage, liquidity, source of funds (3 points)
5. ΔLong-term debt ratio < 0 (debt decreased)
6. ΔCurrent ratio > 0 (liquidity improved)
7. No new share issuance this year (or share count decreased)

### Operating efficiency (2 points)
8. ΔGross margin > 0
9. ΔAsset turnover > 0

**Thresholds**:
- F ≥ 8: Strong buy candidate
- F = 7: Passes gate
- F ≤ 6: Reject at screening
- F ≤ 3: Short candidate

**Edge**: Piotroski's original study showed an F≥8 basket beat an F≤2 basket by 7.5%/year over 1976-1996, and the strategy has continued to work (with decay) in out-of-sample tests through 2020.

## 2. Altman Z-Score (bankruptcy risk)

**Citation**: Altman, E. (1968). "Financial Ratios, Discriminant Analysis and the Prediction of Corporate Bankruptcy." *J. Finance* 23.

**Formula** (for public manufacturers — Z):
```
Z = 1.2·(WC/TA) + 1.4·(RE/TA) + 3.3·(EBIT/TA) + 0.6·(MVE/TL) + 1.0·(S/TA)

where:
  WC  = working capital (current assets - current liabilities)
  TA  = total assets
  RE  = retained earnings
  EBIT = earnings before interest and taxes
  MVE = market value of equity (market cap)
  TL  = total liabilities
  S   = sales
```

**Z''-Score** (for private or non-manufacturers — more commonly used today):
```
Z'' = 6.56·(WC/TA) + 3.26·(RE/TA) + 6.72·(EBIT/TA) + 1.05·(BE/TL)

where BE = book value of equity
```

**Thresholds**:
- Z > 2.99 (Z'' > 2.60): "Safe zone" — distress unlikely
- 1.81 < Z < 2.99 (1.1 < Z'' < 2.60): "Grey zone" — caution
- Z < 1.81 (Z'' < 1.1): "Distress zone" — REJECT

**Accuracy**: ~82% accurate at predicting bankruptcy 1 year out; ~72% at 2 years.

## 3. Greenblatt Magic Formula (ROIC × Earnings Yield)

**Citation**: Greenblatt, J. (2006). *The Little Book That Beats the Market*.

**Formula**:
```
Earnings Yield = EBIT / Enterprise Value
ROIC           = EBIT / (Net Working Capital + Net Fixed Assets)
```

**Method**: Rank all stocks by Earnings Yield (high = good) and by ROIC (high = good). Sum the two ranks. Buy the top 30.

**Thresholds for screening**:
- EBIT / EV ≥ 10% (EV/EBIT ≤ 10)
- ROIC ≥ 15% for non-asset-plays

**Backtest**: Greenblatt's original 1988-2004 backtest showed ~30% CAGR. Out-of-sample has degraded substantially — ~13-15% in 2005-2015 — but still beats S&P 500 by ~4-5%/year.

**Known failure mode**: Magic Formula picks up financially engineered names (heavy buybacks on borrowed money). Cross-check with Piotroski and Altman.

## 4. Graham's NCAV (Net Current Asset Value)

**Citation**: Graham, B. (1934). *Security Analysis*. Also Oppenheimer (1986) FAJ replication.

**Formula**:
```
NCAV = Current Assets - Total Liabilities
NCAV/Share = NCAV / Shares Outstanding (fully diluted)
```

**Threshold**: Market Cap ≤ NCAV × 2/3 (Graham's "margin of safety" rule).

**Additional filters** (critical — naive NCAV catches cash-burning husks):
- Positive operating cash flow in 2 of last 3 years
- No going-concern language in auditor's report (10-K)
- Not in a declining industry with permanent impairment risk
- Inventory turnover not collapsing (inventory not rotting)

**Backtest**: Oppenheimer (1986) found a naive NCAV basket returned 29.4% annualized 1970-1983. Montier (2008, GMO) replicated globally with similar results. Almost no NCAV candidates exist in US large/mid caps anymore — but 10-30 always exist in microcaps and emerging markets.

## 5. FCF Yield and EV/EBIT

**Formulas**:
```
FCF Yield  = FCF (TTM) / Market Cap
FCF        = Operating Cash Flow - Capex
EV         = Market Cap + Debt - Cash
EV/EBIT    = Enterprise Value / EBIT (TTM)
```

**Thresholds**:
- FCF Yield ≥ 8% for buy candidate
- FCF Yield ≥ 12% for "screaming cheap"
- EV/EBIT ≤ 10 for Greenblatt-style
- EV/EBIT ≤ 6 for deep value

**Why EV/EBIT, not P/E**:
- P/E ignores debt — a leveraged company can have low P/E and be terrifying
- EV/EBIT captures the whole capital structure
- EBIT is less manipulable than net income (no tax tricks, no one-time items)

## 5b. Cyclical Peak Warning (Low P/E & Low EV/EBIT Trough Trap)

**The Trap**: At the peak of an economic or commodity cycle (e.g. shipping, semiconductors, steel, chemicals, energy), earnings explode. This produces artificially low P/E ratios (e.g. P/E = 3x–4x) and low EV/EBIT ratios (e.g. EV/EBIT = 2x–3x). Naive screeners mistake peak earnings for permanent cheapness, buying right before earnings collapse 70-90%.

**Formula & Threshold**:
```
EBIT_Ratio = EBIT (TTM) / 5-Year Average EBIT
EPS_Ratio  = EPS (TTM)  / 5-Year Average EPS
```

**Trigger Condition**:
- If `EBIT_Ratio > 1.5` OR `EPS_Ratio > 1.5` → Flag **CYCLICAL PEAK WARNING**.

**Required Action**:
1. Do NOT use TTM P/E or TTM EV/EBIT for valuation.
2. Substitute TTM EBIT with **5-Year Average Normalized EBIT**.
3. Calculate **Normalized EV/EBIT** = `EV / (5-Year Avg EBIT)`.
4. Calculate **Normalized P/E** = `Price / (5-Year Avg EPS)`.
5. Require Normalized EV/EBIT ≤ 10 (reject if peak earnings mask a true normalized multiple > 10x).

## 6. ROIC (Return on Invested Capital)

**Formula**:
```
NOPAT = EBIT × (1 - effective tax rate)
Invested Capital = Total Debt + Book Equity - Cash - Non-operating Assets
ROIC = NOPAT / Invested Capital
```

Use the Damodaran "clean" definition — subtract cash because it earns money-market rates, not business rates.

**Thresholds**:
- ROIC > 15% (3-year average): Strong business economics
- ROIC > WACC + 5%: Creating value
- ROIC < WACC: Destroying value (AVOID even if cheap)

**Why 3-year average**: Single-year ROIC can be inflated by one-time gains or depressed by one-time charges.

## 7. Debt / EBITDA

**Formula**: Total Debt / EBITDA (TTM)

**Thresholds**:
- < 2.0: Conservative
- 2.0 – 3.0: Normal
- 3.0 – 4.0: Caution
- > 4.0: Reject (unless the asset play thesis requires leverage, e.g., REITs)
- > 6.0: Reject always

## 8. Dilution Filter

**Formula**: Δ (Fully Diluted Shares Outstanding, 5-year CAGR)

**Threshold**: Shares should not grow by more than 3%/year on average. Preferably flat or shrinking.

**Watch for**:
- Convertible debt dilution (check 10-K Notes to Financial Statements)
- Stock-based compensation creep (SBC / revenue > 5% is a yellow flag, > 10% is red)
- Warrants outstanding (especially in post-SPAC, post-IPO names)

## 9. Accruals Quality (Sloan accrual anomaly)

**Citation**: Sloan, R. (1996). "Do Stock Prices Fully Reflect Information in Accruals and Cash Flows About Future Earnings?" *Accounting Review*.

**Formula**:
```
Accruals = (Net Income - CFO) / Total Assets
```

**Thresholds**:
- Accruals < 0: Cash earnings exceed reported earnings (good)
- Accruals > 10% of assets: Earnings quality red flag
- Accruals > 15% of assets: Reject

Sloan's original study showed that low-accruals portfolios outperform high-accruals portfolios by ~10%/year over 1962-1991. The effect has degraded but remains in out-of-sample tests (Chen-Zimmermann dataset).

## 10. Liquidity Filter

Not a quality filter — a practical filter.

**Thresholds**:
- Average daily dollar volume ≥ $500,000 (for positions up to $20k)
- Average daily dollar volume ≥ $5,000,000 (for positions up to $200k)
- Bid-ask spread < 2% of price (otherwise trading costs will kill the trade)

## Composite scoring (for Stage 1 ranking)

```python
# Normalize each metric to [0, 1] across the candidate pool
def normalize(x, p_low=10, p_high=90):
    low = percentile(universe, p_low)
    high = percentile(universe, p_high)
    return clip((x - low) / (high - low), 0, 1)

composite_score = (
    0.30 * normalize(fcf_yield) +                 # cash generation
    0.20 * normalize(roic) +                      # business quality
    0.15 * (piotroski_f_score / 9) +              # fundamental momentum
    0.15 * normalize(altman_z) +                  # bankruptcy distance
    0.10 * (1 - normalize(ev_to_ebit)) +          # valuation (inverted)
    0.10 * (overlooked_pocket_boosts / 10)        # overlooked-pocket heuristics
)
```

Sort descending. Top 20 go to the shortlist. The rest get discarded without further analysis.

## Calibration check

If your shortlist contains ANY of the following, something is wrong with the filters:
- Micro-caps (market cap < $300M) — excluded per search settings
- Pre-revenue biotech — Piotroski/Altman don't apply, reject at universe level
- SPACs pre-deSPAC — no operating history, reject
- Chinese ADRs with VIE structures — governance risk swamps any numerical edge

*(Note: Mega-caps with market cap > $200B are explicitly allowed if they meet deep-value criteria such as cyclical drawdowns or sentiment overreactions.)*

Re-run with stricter universe filters if any appear.
