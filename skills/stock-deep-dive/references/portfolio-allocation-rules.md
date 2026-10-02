# Portfolio Allocation & Position Sizing Rules

This reference outlines the portfolio fit evaluation criteria and position sizing mechanics applied in **Step 3 (Portfolio Strategy Agent)**.

---

## 1. Portfolio Construction Philosophy

1. **Focused Diversification**: High conviction value investing requires concentrating capital in top opportunities (typically 12–25 holdings), while preventing single-stock catastrophe risk.
2. **Hard Concentration Limits**:
   - **Maximum Single Stock Weight**: **10.0%** at initial purchase (can run to 15.0% on capital appreciation).
   - **Maximum Single Sector Weight**: **25.0%** of total portfolio value.
   - **Minimum Cash Reserve**: Maintain **5.0% – 15.0%** in cash / short-term instruments to exploit market panics and buy alert triggers.

---

## 2. Position Sizing Framework (Modified Kelly Criterion)

We use a conservative, fractional Kelly-lite framework to map conviction, moat durability, and margin of safety directly into portfolio weight:

$$f^* = \text{Base Weight} \times \text{Quality Factor} \times \text{Margin of Safety Multiplier}$$

### Conviction & Allocation Tiers

| Tier | Category | Criteria | Initial Position Sizing |
| :---: | :--- | :--- | :---: |
| **Tier 1** | **Core Compounder** | Wide moat + High ROIC (>15%) + Low leverage + Margin of Safety $\ge$ 20% + 5Y CAGR $\ge$ 12% | **6.0% – 10.0%** |
| **Tier 2** | **GARP / Quality Value** | Stable moat + Moderate ROIC (10–15%) + Margin of Safety $\ge$ 20% + 5Y CAGR $\ge$ 10% | **3.5% – 5.5%** |
| **Tier 3** | **Opportunistic / Starter** | Cyclical turnaround / Deep value / High upside with higher volatility | **1.5% – 3.0%** |
| **Tier 4** | **Watchlist / Alert Queue** | High quality but currently overvalued / MoS $< 15\%$ | **0.0%** (Queue Buy Alert) |

---

## 3. Portfolio Fit Diagnostic Questions

When evaluating whether to add a candidate stock, the agent analyzes:

1. **Sector / Industry Overlap**:
   - Does adding this stock cause the sector to exceed the 25% ceiling?
   - If yes, recommend trimming an existing lower-conviction peer or reducing the new position size.
2. **Factor & Correlation Risk**:
   - What is the existing balance between Cyclical vs. Defensive, Growth vs. Deep Value?
   - Does this stock improve portfolio resilience or concentrate existing risks?
3. **Capital Sourcing & Opportunity Cost**:
   - Can this position be funded from existing cash reserves?
   - If cash is limited, does this stock offer higher expected return (IRR) than the lowest-ranked existing holding? If so, recommend a capital swap.
4. **Action Verdict**:
   - **Immediate Allocation**: Execute buy order and specify target shares / dollars.
   - **Tranche Allocation**: Initiate a 50% starter position now, with a 50% tranche placed at the Target Buy Alert Price.
   - **Queue Buy Alert**: Add to watchlist at the calculated Target Buy Price.
   - **Pass**: Reject due to sector overconcentration or superior alternative opportunities.
