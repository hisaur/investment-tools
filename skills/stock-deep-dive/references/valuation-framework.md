# Valuation Framework & Target Buy Price Calculation

This reference provides the formal valuation models and hurdle rate formulas used in **Step 2 (Deep Thinking Valuation Agent)**.

---

## 1. Core Principles & The 10% Annual Hurdle Rate

1. **Absolute Return Hurdle**: Every prospective investment must offer an expected annual compound return (CAGR / IRR) of **at least 10% per annum** over a 3-to-5 year horizon.
2. **Margin of Safety**: We demand a margin of safety proportional to business uncertainty:
   - **Wide-Moat / Stable Compounders**: Minimum **15–20% Margin of Safety**.
   - **Moderate-Moat / Cyclical Leaders**: Minimum **25–30% Margin of Safety**.
   - **Turnaround / Asset Plays**: Minimum **35–40% Margin of Safety**.
3. **Data-Driven Multi-Model Triangulation**: Never rely on a single metric (like P/E). Triangulate value using:
   - Discounted Cash Flow (DCF)
   - Earnings Power Value (EPV)
   - Tangible Asset / Reproduction Value

---

## 2. Valuation Methodologies

### A. Three-Scenario DCF (Discounted Cash Flow)
Model normalized Free Cash Flow over a 5–10 year horizon discounted at **10.0%** (our minimum required cost of equity hurdle):

$$\text{PV} = \sum_{t=1}^{n} \frac{\text{FCF}_t}{(1 + r)^t} + \frac{\text{FCF}_n \times (1 + g)}{(r - g) \times (1 + r)^n}$$

- **Discount Rate ($r$)**: Default to **10.0%** (enforces our minimum hurdle).
- **Terminal Growth Rate ($g$)**: Conservative **2.0% – 3.0%** (cannot exceed GDP growth).
- **Normalized FCF**: Use 3-year average FCF or adjust for one-time CapEx / working capital swings.

### B. Earnings Power Value (EPV - Bruce Greenwald)
Assumes zero growth and evaluates the sustainability of current normalized operating earnings:

$$\text{Adjusted NOPAT} = \text{Normalized EBIT} \times (1 - \text{Effective Tax Rate})$$
$$\text{EPV of Operations} = \frac{\text{Adjusted NOPAT}}{\text{Cost of Capital (10\%)}}$$
$$\text{EPV Equity Value} = \text{EPV of Operations} + \text{Excess Cash} - \text{Total Debt}$$

### C. Tangible Asset & Net-Net Value
Establishes the firm liquidation or replacement floor:

$$\text{Tangible Book Value per Share} = \frac{\text{Total Stockholders' Equity} - \text{Goodwill} - \text{Intangibles}}{\text{Fully Diluted Shares}}$$
$$\text{NCAV (Net Current Asset Value)} = \frac{\text{Current Assets} - \text{Total Liabilities} - \text{Preferred Stock}}{\text{Fully Diluted Shares}}$$

---

## 3. Three-Scenario Synthesis & Probability Weighting

For every stock, establish three clear, justified scenarios:

| Scenario | Growth & Margin Assumptions | Primary Valuation Anchor | Probability (Weight) |
| :--- | :--- | :--- | :---: |
| **Bull Case** | High-end organic growth + margin expansion + market multiple re-rating | 10-yr DCF + Multiple Expansion | 20% – 30% |
| **Base Case** | Historical normalized growth + stable margins + steady capital returns | 5-yr DCF + EPV blend | 50% – 60% |
| **Bear Case** | Revenue stagnation/decline + margin compression + multiple contraction | EPV / Tangible Book Value | 20% – 30% |

$$\text{Probability-Weighted Fair Value} = (P_{\text{Bull}} \times V_{\text{Bull}}) + (P_{\text{Base}} \times V_{\text{Base}}) + (P_{\text{Bear}} \times V_{\text{Bear}})$$

---

## 4. Margin of Safety & Expected Return (CAGR)

$$\text{Margin of Safety (\%)} = \frac{\text{Probability-Weighted Fair Value} - \text{Current Price}}{\text{Probability-Weighted Fair Value}} \times 100\%$$

$$\text{Expected 5-Year CAGR} = \left( \frac{\text{Target Base Value}}{\text{Current Price}} \right)^{1/5} - 1 + \text{Dividend Yield}$$

---

## 5. Recommendation Decision Tree & Target Buy Alert Price

```mermaid
graph TD
    A[Evaluate Margin of Safety & 5Y CAGR] --> B{5Y CAGR >= 10% AND MoS >= Required Threshold?}
    B -->|Yes| C[Verdict: BUY]
    B -->|No| D{Business Quality High & MoS > 0% but < Threshold?}
    D -->|Yes| E[Verdict: HOLD / WATCHLIST]
    D -->|No (Overvalued or Thesis Broken)| F[Verdict: PASS / SELL]
    E --> G[Calculate Target Buy Alert Price]
    F --> G
```

### Actionable Buy Alert Price Formula
When a stock is NOT a Buy (e.g. trading at fair value or slight premium), calculate the **Target Buy Alert Price** that gives the user the required entry point to lock in a 10%+ CAGR and the minimum margin of safety:

$$\text{Target Buy Alert Price} = \min \left( \text{Fair Value} \times (1 - \text{Required MoS}), \; \frac{\text{Target 5Y Value}}{(1.10)^5} \right)$$

This exact price is passed into Step 3 to configure alerts in the user's watchlist.
