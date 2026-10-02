# Deep Dive Report Template — [TICKER]

> Use this exact structure for Stage 2 output. Fill every section. Empty sections are not allowed — if data is unavailable, write "DATA UNAVAILABLE: [source tried]" explicitly.

**Ticker**: [TICKER]
**Company**: [Legal name]
**Report date**: [YYYY-MM-DD]
**Analyst**: Deep Value Hunter v0.1
**Verdict**: [Buy / Watch / Pass / Too Hard]
**Probability-weighted fair value**: $[X.XX] per share (fully diluted)
**Current price**: $[X.XX]
**Margin of safety**: [X]%

---

## 1. TL;DR (3 sentences)

[Sentence 1: what the company does in 8 words]
[Sentence 2: why it's overlooked in 12 words]
[Sentence 3: verdict + target upside at base case in 8 words]

---

## 2. Business in Plain English (≤120 words)

**What they sell**: [products/services]
**To whom**: [customer types]
**How they make money**: [unit economics, transaction type]
**Revenue mix**: [segment %, geography %]
**In your circle of competence?**: [Yes / Borderline / No — justify]

**Primary source**: [SEC 10-K URL]

---

## 3. The Overlooked Thesis (≤200 words)

**Why is this cheap?** (pick one)
- [ ] Spin-off orphan
- [ ] Post-bankruptcy emerger
- [ ] Mega/Large-cap temporary dislocation / fallen angel
- [ ] Post-dividend-cut overreaction
- [ ] Sum-of-parts discount
- [ ] Index-exclusion forced selling
- [ ] Activist entry point
- [ ] Industry out-of-favor
- [ ] Other: _______

**Why won't other value investors see this?**
[Articulate the specific edge. If you can't, downgrade the verdict.]

**What has to happen for the market to notice?**
1. [Catalyst 1 — expected timeline]
2. [Catalyst 2 — expected timeline]
3. [Catalyst 3 — expected timeline]

**Primary source**: [SEC filing URL demonstrating the "overlooked" characteristic — e.g., 10-12B for spin-off, Form 4 cluster for insider buying]

---

## 4. Quantitative Snapshot

| Metric                        | Value | Peer median | 5yr own median | Source |
|-------------------------------|-------|-------------|----------------|--------|
| Price (as of date)            |       |             |                |        |
| Market cap                    |       |             |                |        |
| Enterprise value              |       |             |                |        |
| EV/EBIT (TTM)                 |       |             |                |        |
| P/TBV                         |       |             |                |        |
| FCF yield (LTM)               |       |             |                |        |
| ROIC (3yr avg)                |       |             |                |        |
| Gross margin (LTM)            |       |             |                |        |
| Operating margin (LTM)        |       |             |                |        |
| Net debt / EBITDA             |       |             |                |        |
| Interest coverage             |       |             |                |        |
| **Altman Z-score**            |       |     —       |                |        |
| **Piotroski F-score**         |  /9   |     —       |                |        |
| Shares out (fully diluted)    |       |             |                |        |
| Insider ownership %           |       |             |                |        |
| Short interest (% float)      |       |             |                |        |
| Days to cover                 |       |             |                |        |
| Avg daily $ volume (90 day)   |       |             |                |        |

**Filings cited**: [list 10-K, 10-Q URLs with page numbers]

---

## 5. Moat & Competitive Position (≤300 words)

### Porter's Five Forces (one sentence each)
- **Rivalry**:
- **New entrants**:
- **Suppliers**:
- **Buyers**:
- **Substitutes**:

### Moat assessment
- **Moat type**: [brand / network / switching / cost / regulatory / none]
- **Moat trend**: [widening / stable / narrowing]
- **Evidence for trend**: [market share, pricing power, churn, gross margin direction]
- **Best-in-class peer**: [ticker + why they're better]

---

## 6. Management & Capital Allocation (≤250 words)

**CEO**: [name], tenure [X years], prior role: [company]
**Insider ownership**: [X]% ($[Y]M)
**Recent insider buying** (last 12 months): [aggregated from Form 4]

### Capital allocation — last 5 years (% of cumulative FCF)
- Dividends: [X]%
- Buybacks: [X]% — average price $[Y] vs. avg market price $[Z] → [accretive / dilutive]
- Acquisitions: [X]% — [successful / failed — cite goodwill impairments]
- Reinvestment: [X]%
- Debt paydown: [X]%

**CEO candor score** (read last 3 shareholder letters): [X/10]
[One-line justification]

**DEF 14A red flags**: [none / list]

---

## 7. Three-Scenario Valuation

### Bull case — P = [X]%
**Story**: [2 sentences — what goes right]
- Asset value per share (fully diluted): $[X]
- EPV (10x adjusted EBIT): $[X]
- DCF (10yr, 10% disc, 3% terminal): $[X]
- **Scenario fair value** (simple avg): $[X]

### Base case — P = [X]%
**Story**: [2 sentences — trend continuation]
- Asset value: $[X]
- EPV: $[X]
- DCF: $[X]
- **Scenario fair value**: $[X]

### Bear case — P = [X]%
**Story**: [2 sentences — what goes wrong]
- Liquidation value: $[X]
- EPV at 6x: $[X]
- DCF with 0% terminal: $[X]
- **Scenario fair value**: $[X]

### Weighted fair value
```
FV = P_bull × $bull + P_base × $base + P_bear × $bear
FV = [X]   × $[X]  + [X]   × $[X]  + [X]   × $[X]
FV = $[X]
```

**Current price**: $[X]
**Margin of safety**: [(FV - Price) / Price × 100]%
**Upside at base case**: [(Base FV - Price) / Price × 100]%

---

## 8. Value Trap Red Flags Checklist

From `references/value-trap-red-flags.md`:

| # | Flag                                | Status          | Note                   |
|---|-------------------------------------|-----------------|------------------------|
| 1 | Secular decline                     | ✅ / ⚠️ / ❌     |                        |
| 2 | Value-destroying management         | ✅ / ⚠️ / ❌     |                        |
| 3 | Accounting red flags                | ✅ / ⚠️ / ❌     |                        |
| 4 | Dilution creeper                    | ✅ / ⚠️ / ❌     |                        |
| 5 | Debt wall (next 24 months)          | ✅ / ⚠️ / ❌     |                        |
| 6 | Regulatory overhang                 | ✅ / ⚠️ / ❌     |                        |
| 7 | Customer concentration              | ✅ / ⚠️ / ❌     |                        |
| 8 | Margin decline trajectory           | ✅ / ⚠️ / ❌     |                        |
| 9 | Cyclical earnings at peak           | ✅ / ⚠️ / ❌     |                        |
|10 | Hedge-fund hotel                    | ✅ / ⚠️ / ❌     |                        |
|11 | Commodity dependence                | ✅ / ⚠️ / ❌     |                        |
|12 | Binary outcome dependence           | ✅ / ⚠️ / ❌     |                        |

**Triggered (❌)**: [count]
**Warnings (⚠️)**: [count]

**Rule**: If ≥ 2 triggered OR ≥ 3 warnings → verdict MUST be Pass unless specifically argued against.

---

## 9. Buffett/Munger Gates (from references/buffett-munger-gates.md)

| # | Gate                              | Pass? | Notes |
|---|-----------------------------------|-------|-------|
| 1 | Circle of competence              | ✅/❌ |       |
| 2 | Durable moat identified           | ✅/❌ |       |
| 3 | Honest/competent management       | ✅/❌ |       |
| 4 | Favorable business economics      | ✅/❌ |       |
| 5 | Price right (MoS ≥ 30%)           | ✅/❌ |       |
| 6 | Free from binary risks            | ✅/❌ |       |
| 7 | Realistic 18-36 month horizon     | ✅/❌ |       |

**Passes**: [X/7]
**Rule**: 5/7 = starter position. 7/7 = full-size. < 5/7 = Pass.

---

## 10. Catalyst Watch

### Near-term (next 1-2 quarters)
- [Catalyst + date + probability]

### Medium-term (1-3 years)
- [Catalyst + range]

### Long-term (3+ years)
- [Terminal / strategic]

---

## 11. Position Sizing Recommendation

**If Buy**: ~[X]% of portfolio
**Justification**: [Kelly-lite: edge × odds, capped at 5%]

**Sector & Factor Correlation Check**:
- **Primary Sector**: [Sector name]
- **Key Macro / Factor Sensitivities**: [e.g., Interest rates, Oil prices, USD strength, Consumer spending]
- **Portfolio Overlap Warning**: [Flag if candidate correlates heavily with existing holdings or sector clusters]

**Stop conditions** — sell if:
1. [Specific event]
2. [Specific event]
3. [Specific event]

**Re-evaluation triggers** — revisit the thesis on:
- [Next 10-Q filing date]
- [Next 10-K filing date]
- [Specific catalyst]

---

## 12. Sources (complete list)

**EDGAR filings referenced**:
- [10-K URL, filing date, pages cited]
- [10-Q URL, filing date, pages cited]
- [8-K URL, filing date, item number]
- [Form 4 URLs, dates]
- [13D/13G URLs if applicable]
- [DEF 14A URL, filing date, pages]

**Datasets / research cited**:
- [Chen-Zimmermann signal name if used]
- [Academic paper citations]

**Secondary sources (if any)**:
- [only for commentary, not numbers]

---

## 13. Appendix: What You're Trusting

Three specific assumptions that, if wrong, kill this thesis. For each, state how to verify cheaply.

1. **Assumption**: [claim]
   **If wrong**: [impact on fair value]
   **Cheap verification**: [specific check]

2. **Assumption**: [claim]
   **If wrong**: [impact]
   **Cheap verification**: [check]

3. **Assumption**: [claim]
   **If wrong**: [impact]
   **Cheap verification**: [check]

---

## 14. Analyst confidence

- **Data quality**: [High / Medium / Low] — [reason]
- **Model applicability**: [High / Medium / Low] — [reason]
- **Overall confidence**: [High / Medium / Low]
- **What would raise confidence**: [specific additional data]

---

*This report is not investment advice. Anomaly returns decay post-publication (McLean-Pontiff 2016). Value traps are real. Do your own verification against primary sources before putting real money at risk.*
