# Value Trap Red Flags — How to Reject

A value trap is a stock that looks statistically cheap but is cheap for a reason that won't reverse. Most of the edge in deep value comes from **avoiding** traps, not from finding the next multi-bagger. If you eliminate value traps, a mechanical quantitative strategy will do the rest.

Use this checklist in Stage 2. **Two or more triggered flags = Pass, unless you have a specific argument for why each one doesn't apply.** Silence is not an argument.

## The 12 Flags

### Flag 1: Secularly declining business
**Signal**: Revenue down ≥ 3 of the last 5 years AND industry shrinking (not cyclical downturn).

**Examples**: Newspapers 2005-2020, yellow-pages, DVD rental, film cameras, shopping malls, brick-and-mortar retail pre-internet-winners.

**Why it's a trap**: Terminal value is zero. Every year the optionality shrinks. Management buybacks just delay the zero.

**How to distinguish from a cyclical dip**: Look at industry units shipped, not revenue. If units are falling too, it's secular. If only dollars are falling (price deflation), it might be cyclical.

### Flag 2: Management with a history of value destruction
**Signal**: CEO tenure > 5 years AND stock has underperformed sector by > 30% cumulative AND cap allocation was heavy on bad acquisitions.

**Where to check**: Proxy statements (DEF 14A) for CEO tenure + total comp vs. stock performance. Past 10-K "Business" sections for acquisition history.

**Why it's a trap**: Same management will keep destroying value. Management changes almost never happen without an activist. Even then, it takes 2-3 years.

### Flag 3: Accounting red flags
**Signal ANY of**:
- Going-concern language in auditor's opinion
- Auditor changed recently (especially if new auditor is smaller)
- Restatements of prior-year financials
- Frequent "one-time" charges (3+ years of non-recurring items)
- Accounts receivable growing faster than revenue
- Inventory growing faster than revenue
- Goodwill impairment in 2+ of last 5 years

**Where to check**: 10-K Notes to Financial Statements, especially "Critical Accounting Policies" and "Subsequent Events"; 8-K filings for auditor changes (Item 4.01).

**Why it's a trap**: Statistical cheapness is computed from reported numbers. If the numbers are fiction, the cheapness is fiction.

### Flag 4: Dilution creeper
**Signal**: Fully diluted share count growing > 5%/year AND management compensation > 50% in stock AND SBC / revenue > 10%.

**Where to check**: 10-K Notes on Stock-Based Compensation, DEF 14A compensation tables.

**Why it's a trap**: Per-share metrics look stable while shareholders are being silently diluted. The "cheap" stock isn't cheap per dollar of existing equity — it's cheap per continuously-expanding equity.

### Flag 5: Debt wall in next 24 months
**Signal**: Current portion of long-term debt + debt maturing in next 24 months > 50% of trailing 12-month FCF AND interest coverage (EBIT/Interest) < 4x.

**Where to check**: 10-K debt maturity schedule (Notes to FS, usually Note 7-9).

**Why it's a trap**: If refinancing terms tighten, the company is forced into a dilutive equity raise or worse. The cheap multiple won't save equity holders if the debt gets restructured.

### Flag 6: Regulatory overhang
**Signal**: Ongoing SEC investigation, DOJ inquiry, FDA warning letter, EPA consent order, or pending class-action with settlement estimate > 20% of market cap.

**Where to check**: 10-K "Legal Proceedings" section and "Risk Factors"; 8-K material events.

**Why it's a trap**: Regulatory risks have fat tails. Small probability of catastrophic outcomes. Statistical valuations don't capture this.

### Flag 7: Customer concentration
**Signal**: Top 3 customers > 30% of revenue AND contracts renewable within 2 years AND no long-term supply agreements.

**Where to check**: 10-K "Customers" section, usually in Item 1 Business description.

**Why it's a trap**: One lost customer = 10-20% revenue hit. Hard to recover in competitive industries.

### Flag 8: Negative operating leverage trajectory
**Signal**: Gross margin AND operating margin BOTH declining for 3+ consecutive years.

**Where to check**: 5-year income statement comparison (Bloomberg, yfinance, or compute from 10-K/10-Qs).

**Why it's a trap**: The business is losing pricing power, cost discipline, or both. Statistical cheapness computed from past earnings is stale. Future earnings will be lower.

### Flag 9: Cyclical earnings at peak (The Low P/E & Low EV/EBIT Trap)
**Signal**: Current TTM EBIT or TTM EPS > 1.5 × 5-year median AND industry is cyclical (shipping, semiconductors, housing, auto, airlines, steel, chemicals, energy) AND no structural moat expansion justifying the margin.

**Where to check**: 10-K 5-year financial summary; TTM EBIT vs 5-year average EBIT; TTM EPS vs 5-year average EPS.

**Why it's a trap**: At cyclical peaks, massive temporary profits create illusionary low P/E ratios (e.g. 3x–4x P/E) and low EV/EBIT ratios (e.g. 2x–3x EV/EBIT). Unwary value investors mistake peak earnings for permanent cheapness, buying right before earnings collapse 70-90% and multiples explode. **Always value cyclicals on mid-cycle normalized earnings (5-year average EBIT/EPS), never peak TTM earnings.**

### Flag 10: Activist trap / hedge fund hotel
**Signal**: ≥ 3 famous value investors in 13F AND stock has been stuck in a range for 2+ years AND no catalyst in sight.

**Examples**: Valeant 2014-2016, Bed Bath & Beyond 2018-2020, Weight Watchers 2019-2020.

**Why it's a trap**: When everyone smart is long and the thesis isn't working, someone is going to capitulate. Big funds unwinding creates the final leg down. "The consensus trade is the crowded trade."

### Flag 11: Commodity dependence with weak differentiation
**Signal**: Revenue tied to a commodity price AND company is a price-taker (not producer of differentiated specialty product).

**Where to check**: 10-K "Risk Factors" and segment discussion.

**Why it's a trap**: You're making a commodity bet, not a company bet. Valuation is spurious — you'd be better off buying the commodity directly.

### Flag 12: Binary outcome dependence
**Signal**: Thesis depends on a single event: FDA approval, court ruling, acquisition closing, regulatory change, debt restructuring outcome.

**Where to check**: 8-K filings, 10-K "Risk Factors," news.

**Why it's a trap**: Not a value investment — it's an options trade. Either price it as an option (probability-weighted payoff) or skip. Don't treat it as "cheap" — it's not.

## How to use the checklist

1. Go through all 12 flags for your candidate.
2. For each, answer ✅ clear / ⚠️ warning / ❌ triggered.
3. **If ≥ 2 are ❌ triggered, the verdict MUST be Pass** unless you can argue each one is wrong with specific evidence.
4. If 1 is ❌ triggered, the position size should be cut in half.
5. If 3+ are ⚠️ warnings, treat as one ❌ (warnings compound).

## Priors — how often each flag fires

Rough frequencies observed in practice (my rough calibration, not peer-reviewed):

| Flag                              | % of screened candidates |
|-----------------------------------|-------------------------:|
| 1. Secular decline                |                    ~20% |
| 2. Value-destroying management    |                    ~15% |
| 3. Accounting red flags           |                     ~8% |
| 4. Dilution creeper               |                    ~25% |
| 5. Debt wall                      |                    ~12% |
| 6. Regulatory overhang            |                     ~6% |
| 7. Customer concentration         |                    ~10% |
| 8. Margin decline                 |                    ~30% |
| 9. Cyclical peak                  |                    ~18% |
| 10. Hedge fund hotel              |                     ~5% |
| 11. Commodity dependence          |                     ~8% |
| 12. Binary outcome                |                     ~7% |

So a typical "statistically cheap" stock has 1-2 flags just by default. You're looking for the ~10% with zero or 1 easy-to-dismiss flag.

## Survivorship tax

Running this checklist rigorously will reject ~80% of screening hits. This feels wasteful. It isn't. The 80% you rejected were value traps. Your hit rate on the remaining 20% will be dramatically higher, and your Sharpe ratio will be higher than a mechanical strategy even though your gross return looks lower. Trust the process.
