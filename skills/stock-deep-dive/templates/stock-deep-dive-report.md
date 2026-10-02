# Stock Deep Dive & Portfolio Allocation Report: {TICKER}

**Date**: {DATE}  
**Company**: {COMPANY_NAME} (`{TICKER}`)  
**Sector / Industry**: {SECTOR} / {INDUSTRY}  
**Current Price**: {NATIVE_CURR_SYM}{CURRENT_PRICE} {NATIVE_CURR} ({BASE_CURR_SYM}{NORMALIZED_PRICE} {BASE_CURR}) | **Market Cap**: {NATIVE_CURR_SYM}{MARKET_CAP} | **Enterprise Value**: {NATIVE_CURR_SYM}{ENTERPRISE_VALUE}  

---

## 1. Executive Verdict & Sizing Summary

| Metric | Evaluation | Target / Benchmark | Status |
| :--- | :---: | :---: | :---: |
| **Valuation Recommendation** | **{BUY / HOLD / SELL}** | Value Entry Gates | {✅ / ⚠️ / ❌} |
| **Probability-Weighted Fair Value** | **{NATIVE_CURR_SYM}{FAIR_VALUE}** ({BASE_CURR_SYM}{BASE_FAIR_VALUE}) | Intrinsic Value Base | — |
| **Current Margin of Safety** | **{MOS_PCT}%** | $\ge 20\%$ Target | {Status} |
| **Expected 5-Year CAGR** | **{CAGR_PCT}%** | $\ge 10\%$ Hurdle | {Status} |
| **Target Buy Alert Price** | **{NATIVE_CURR_SYM}{BUY_ALERT_PRICE}** ({BASE_CURR_SYM}{BASE_BUY_ALERT_PRICE}) | Setup Notification | 🔔 |
| **Portfolio Allocation Decision** | **{ALLOCATION_VERDICT}** | Max {MAX_POS}% Pos | {Status} |
| **Target Weight / Allocation (on Trigger)** | **{WEIGHT_PCT}%** ({BASE_CURR_SYM}{ALLOCATION_DOLLARS}) | ~{SHARES} shares | — |

---

## 2. Business Model & Economic Moat

- **What the Company Does**: {BUSINESS_SUMMARY}
- **Circle of Competence**: {CIRCLE_ASSESSMENT}
- **Moat Type & Durability**: {MOAT_DESCRIPTION} (Score: {MOAT_SCORE}/10)
- **ROIC & Reinvestment Runway**: {ROIC_ASSESSMENT}
- **Capital Allocation & Management Discipline**: {CAPITAL_ALLOCATION_ASSESSMENT}

---

## 3. Quantitative & Health Diagnostics

- **Piotroski F-Score**: **{PIOTROSKI_SCORE}/9** ({PIOTROSKI_RATIONALE})
- **Altman Z-Score**: **{ALTMAN_Z}** ({ALTMAN_CATEGORY})
- **Free Cash Flow Quality**: {FCF_QUALITY_NOTE}
- **Capital Structure & Debt Coverage**: Net Debt/EBITDA: {NET_DEBT_EBITDA}x | Interest Coverage: {INTEREST_COVERAGE}x
- **Share Dilution / Buyback Trend**: {DILUTION_TREND}

---

## 4. Three-Scenario Valuation Model

All valuation models enforce our **10.0% Minimum Cost of Equity Hurdle Rate ($r = 10.0\%$)** and conservative terminal growth rates ($g \le 2.5\%$).

| Scenario | Weight % | Key Drivers / Growth & Margin Assumptions | Value / Share | Implied Upside % |
| :--- | :---: | :--- | :---: | :---: |
| **🟢 Bull Case** | {BULL_WT}% | {BULL_ASSUMPTIONS} | {NATIVE_CURR_SYM}{BULL_VAL} | {BULL_UPSIDE}% |
| **🟡 Base Case** | {BASE_WT}% | {BASE_ASSUMPTIONS} | {NATIVE_CURR_SYM}{BASE_VAL} | {BASE_UPSIDE}% |
| **🔴 Bear Case** | {BEAR_WT}% | {BEAR_ASSUMPTIONS} | {NATIVE_CURR_SYM}{BEAR_VAL} | {BEAR_UPSIDE}% |
| **Weighted Fair Value** | **100%** | **Expected Intrinsic Value** | **{NATIVE_CURR_SYM}{FAIR_VALUE}** | **{WEIGHTED_UPSIDE}%** |

### Valuation Key Takeaways & Buy Alert Derivation
- **Margin of Safety**: {MOS_EXPLANATION}
- **Expected Return (CAGR)**: Modeled expected compound annual growth rate of **{CAGR_PCT}%** against the 10% strategy hurdle.
- **Target Buy Alert Price ({NATIVE_CURR_SYM}{BUY_ALERT_PRICE} / {BASE_CURR_SYM}{BASE_BUY_ALERT_PRICE})**: {BUY_PRICE_RATIONALE}

---

## 5. Relative Peer Valuation & Sector Cost of Capital

- **Sector WACC Benchmark**: `{SECTOR_WACC_RANGE}` ({SECTOR_WACC_TYPE})
- **Strategy Required Hurdle Rate**: `10.0%` (Cost of Equity minimum)

| Peer Ticker | Name | Market Cap | Fwd P/E | EV/EBITDA | FCF Yield | Div Yield |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| **{PEER_1_TICKER}** | {PEER_1_NAME} | {PEER_1_MCAP} | {PEER_1_PE} | {PEER_1_EV_EBITDA} | {PEER_1_FCF_YIELD} | {PEER_1_DIV} |
| **{PEER_2_TICKER}** | {PEER_2_NAME} | {PEER_2_MCAP} | {PEER_2_PE} | {PEER_2_EV_EBITDA} | {PEER_2_FCF_YIELD} | {PEER_2_DIV} |
| **{PEER_3_TICKER}** | {PEER_3_NAME} | {PEER_3_MCAP} | {PEER_3_PE} | {PEER_3_EV_EBITDA} | {PEER_3_FCF_YIELD} | {PEER_3_DIV} |

---

## 6. Value Trap Diagnostic Checklist

| Red Flag | Status | Finding / Analysis |
| :--- | :---: | :--- |
| **1. Secular Decline** | {✅/⚠️/❌} | {Note} |
| **2. Debt Wall / Solvency** | {✅/⚠️/❌} | {Note} |
| **3. Chronic Dilution** | {✅/⚠️/❌} | {Note} |
| **4. Unfunded CapEx / Fake FCF** | {✅/⚠️/❌} | {Note} |
| **5. Customer Concentration** | {✅/⚠️/❌} | {Note} |
| **6. Unsupportable Dividend** | {✅/⚠️/❌} | {Note} |
| **7. Piotroski Deterioration** | {✅/⚠️/❌} | {Note} |
| **8. Channel Stuffing / A-R Divergence** | {✅/⚠️/❌} | {Note} |
| **9. Destructive M&A / Goodwill** | {✅/⚠️/❌} | {Note} |
| **10. Net Insider Offloading** | {✅/⚠️/❌} | {Note} |

---

## 7. Portfolio Integration & Allocation Strategy (Step 3 Results)

- **Portfolio Baseline**: Base Currency: `{BASE_CURR}` ({BASE_CURR_SYM}) | Total Value: {BASE_CURR_SYM}{TOTAL_PORTFOLIO_VAL} | Cash: {BASE_CURR_SYM}{CASH_RESERVES} ({CASH_PCT}%)
- **Sector Impact**: Current Sector Weight: {CURR_SECTOR_WT}% $\rightarrow$ Projected: {PROJ_SECTOR_WT}% (Limit: 25.0%)
- **Allocation Directive**:
  - **Action**: **{PORTFOLIO_DIRECTIVE}**
  - **Size**: **{RECOMMENDED_WEIGHT_PCT}%** ({BASE_CURR_SYM}{RECOMMENDED_DOLLARS} / ~{RECOMMENDED_SHARES} shares)
  - **Execution Plan**: {EXECUTION_PLAN}
  - **Notification Trigger**: {WATCHLIST_ALERT_INSTRUCTION}

---

## 8. Thesis Invalidation & Exit Triggers

1. **Trigger 1**: {TRIGGER_1}
2. **Trigger 2**: {TRIGGER_2}
3. **Trigger 3**: {TRIGGER_3}
