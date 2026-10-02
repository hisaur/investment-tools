# Valuation Methods

Every deep dive in Stage 2 must produce three independent valuations and weight them. No single method is trustworthy alone. Disagreement between methods is information — investigate it, don't average it away.

## 1. Asset-Based Valuation (the balance-sheet floor)

**When to use**: Asset plays — companies whose primary value is the balance sheet, not the income statement. Real estate, natural resources, holding companies, post-bankruptcy emergers, distressed names.

### A. Book Value (starting point, not ending point)

```
Book Value = Total Assets - Total Liabilities
Tangible Book = Book Value - Goodwill - Intangibles
```

Use Tangible Book, never Book Value. Goodwill is just a memory of prior bad acquisitions.

### B. Net Current Asset Value (Graham)

```
NCAV = Current Assets - Total Liabilities
```

Deep-value floor for distressed names. Graham's rule: buy at ≤ 2/3 NCAV for a ~30% margin of safety.

### C. Liquidation Value (most conservative)

```
Liquidation Value =
    Cash × 1.00
  + Accounts Receivable × 0.80
  + Inventory × 0.50
  + PP&E × (real-estate-adjusted)
  + Intangibles × 0.00
  - Total Liabilities
  - Severance/shutdown costs
```

Use when the business is arguably worth more dead than alive.

### D. Replacement Cost

What would it cost a new entrant to rebuild the assets from scratch?
- For PP&E: current construction costs × remaining useful life
- For real estate: appraised value (check last 10-K Notes on PP&E)
- For licenses/quotas: recent transaction comps
- For inventory: replacement cost, not historical cost

**When replacement > market**: genuine asset play.
**When replacement < market**: the assets are obsolete or misvalued up.

### E. Sum-of-the-Parts (SOTP)

For holding companies and conglomerates. Value each segment separately, sum, subtract net debt and holdco expenses.

```
SOTP = Σ (Segment EBIT × Segment Multiple)  +  Real Estate  +  Investments  -  Net Debt  -  HoldCo Discount
```

HoldCo discount: typically 15-25% because of double taxation, management fees, limited flexibility.

## 2. Earnings-Based Valuation (Earnings Power Value, Greenblatt/Graham)

**When to use**: Stable or declining businesses with a consistent operating record. The question is "what are normalized earnings worth?"

```
Adjusted EBIT = Trailing 5-Year Average EBIT
                × (1 + long-term sustainable growth rate)
                − one-time items
                − normalized maintenance capex (from 10-K Notes or estimate as 5% of revenue)

NOPAT = Adjusted EBIT × (1 - effective tax rate)   # use 21% federal as baseline
EPV   = NOPAT × 10                                  # 10x multiple = 10% cap rate
EPV per Share = EPV / Fully Diluted Shares Outstanding
```

**Why 10x**: Corresponds to a ~10% required return, consistent with long-term equity cost of capital. It's a prior, not a law.

**Adjustments**:
- For low-capex businesses (software, services): 12-14x
- For high-capex or commoditized (steel, airlines): 6-8x
- For cyclical companies: use MID-CYCLE EBIT, not peak or trough

## 3. Discounted Cash Flow (Damodaran school)

**When to use**: Growth businesses with visible cash flow trajectory. Has more assumptions than EPV, so use it as a sanity check, not the primary method.

### Basic two-stage model

```
Years 1-10: FCFF growing at g₁
Terminal:   Gordon growth at g_t forever

DCF Value = Σ [FCFF_t / (1+r)^t] + TV / (1+r)^10

TV = FCFF_11 / (r - g_t)

where:
  FCFF = Operating Cash Flow - Capex     # free cash flow to the firm
  r    = WACC = 0.10 as a default         # adjust if capital structure unusual
  g₁   = 3-6% based on realistic growth prospects
  g_t  = 2.5% (long-term GDP growth nominal)
```

### Key constraints to keep yourself honest

- **g₁ ≤ industry growth rate** — don't assume the company outgrows its industry forever
- **g_t ≤ long-term GDP** — literally impossible for a company to grow faster than the economy forever
- **r ≥ 9%** — don't use discount rates below historical equity premium
- **Terminal value ≤ 70% of DCF value** — if > 70%, you're not valuing the business, you're betting on the distant future

### Damodaran's story-to-numbers method

1. Write the business story in 3 sentences
2. Map story elements to DCF inputs:
   - "Market share gains" → higher revenue growth
   - "Operating leverage" → margin expansion
   - "Capital discipline" → lower reinvestment rate
3. Run DCF with those inputs
4. Check if implied valuation is consistent with the story ("if I buy at this price, I'm betting on X")

If you can't articulate the story in 3 sentences, you don't understand the business.

## 4. Relative Valuation (peer multiples)

Use as a cross-check, not a primary method. Always suspect.

### Methodology

1. Define peer set (4-6 names, similar size, similar business model, similar profitability)
2. Compute median and interquartile range of: EV/EBIT, EV/EBITDA, P/E, P/B, EV/Revenue
3. Apply peer median × company's current number → implied price
4. Compare to market price

### Traps

- Peer multiples are polluted by each peer's own mispricing
- "Cheap vs. peers" is not the same as "cheap in absolute terms" — an entire sector can be expensive or cheap
- Peer quality differences blow up simple multiple comparisons (a higher-quality business deserves a higher multiple)
- Avoid EV/Sales — doesn't capture profitability differences
- Avoid P/B for non-financials — book value is often meaningless for asset-light businesses

**Better use**: Historical multiples. Is the company trading at a discount to its OWN 5-year average multiple? This is more informative than peer comparisons.

## 5. Probability-Weighted Fair Value

Run all three methods (Asset, EPV, DCF) under three scenarios (Bull, Base, Bear). Assign probabilities. Weight.

```
Weighted FV = Σ (scenario_probability × scenario_value)
           = p_bull × bull_fv + p_base × base_fv + p_bear × bear_fv

Margin of Safety = (Weighted FV - Current Price) / Current Price
```

### Scenario design

| Scenario | Assumption | Probability (default) |
|----------|-----------|----------------------:|
| Bull     | Everything goes right: growth tailwind, margin expansion, multiple re-rating | 20-25% |
| Base     | Trend continuation: historical averages for growth/margins | 50-60% |
| Bear     | Thesis fails: margin compression, dilution, or cyclical bust | 20-30% |

**Critical**: The probability of the bear case should be ≥ probability of the bull case. If you find yourself assigning bull 50% and bear 10%, check your biases.

### Probability-weighted margin of safety thresholds

- MoS ≥ 50%: Strong buy candidate (rare)
- MoS 30-50%: Buy
- MoS 15-30%: Small starter position
- MoS 0-15%: Watchlist
- MoS < 0%: Pass
- MoS < -15%: Short candidate (if borrow is cheap)

## 6. Per-Share Discipline

Always use **fully diluted shares outstanding**, including:
- Stock options (in-the-money and near-money)
- Warrants
- Convertible preferred / debt at conversion ratio
- Restricted stock units vesting in next 12 months

Formula:
```
Fully Diluted Shares = Basic Shares + In-the-Money Options + Warrants + Convertibles at Conversion
```

From the 10-K: look at "Earnings per share" computation and Notes on Stock-Based Compensation.

## 7. Presenting valuations

Always show a horizontal bar chart (or equivalent table):

```
Method                      Per-share value     Margin vs. price
----------------------------------------------------------------
Current market price        $10.00              —
Liquidation value           $ 7.20              -28%
Tangible book value         $ 9.50              -5%
NCAV                        $ 4.10              -59%
EPV (10x adjusted EBIT)     $14.00              +40%
DCF base case               $16.50              +65%
DCF bull case               $23.00              +130%
DCF bear case               $ 9.80              -2%
Probability-weighted FV     $15.20              +52%
```

Disagreement between methods is the interesting part. If EPV says $14 and liquidation says $7.20, the market is pricing it below EPV but above liquidation — you're being paid to bet on the business being a going concern. Articulate that bet explicitly.

## 8. What to ignore

- **PEG ratio**: garbage metric, ratio of two ratios
- **Dividend discount model** for non-dividend-paying stocks
- **Graham number** (√(22.5 × EPS × BVPS)): historical curiosity, not useful
- **Price-to-sales**: ignores profitability, used by people who don't understand EV
- **Forward P/E**: relies on sell-side estimates which are systematically biased
- **Technical indicators**: have no academic survival evidence for deep-value horizons (1-3 years)
