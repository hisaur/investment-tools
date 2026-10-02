# Academic Evidence — What Actually Works

This file exists to keep the skill honest. The trading strategies below are the only ones with robust peer-reviewed evidence for long-term out-of-sample outperformance. Everything else — technical indicators, pattern trading, astrology, most newsletter picks — has failed replication or has no credible academic track record.

Anomaly returns decay. Be humble.

## The four survivor premia

Across thousands of published anomalies, AQR's researchers (Asness, Frazzini, Moskowitz, Pedersen, and others) argue that only four premia have survived:
1. **Value** — price < fundamentals (B/M, E/P, CF/P composite)
2. **Momentum** — recent winners continue winning (12-1 month)
3. **Carry** — high yield > low yield (FX, commodities, bonds)
4. **Defensive** — low volatility / high quality

Source: Asness, Moskowitz, Pedersen (2013) "Value and Momentum Everywhere" *J. Finance* 68.
Follow-up: Koijen, Moskowitz, Pedersen, Vrugt (2018) "Carry" *JFE* 127.

**Realistic post-cost Sharpe for diversified factor portfolios**: 0.5 – 0.7 (not the 1.0+ seen in-sample).

## The meta-finding: most anomalies are fake

### Hou-Xue-Zhang (2020) "Replicating Anomalies" *RFS*

Re-tested 452 published anomalies with strict replication rules (microcap filters, value-weighted portfolios):
- **64% failed** at the `t > 1.96` bar
- **82% failed** at the `t > 3.0` bar (the new multiple-testing-corrected standard)
- Surviving categories: profitability, momentum, investment, value (weakening)
- Dying: accruals, most sentiment, calendar effects, most technical indicators

### McLean & Pontiff (2016) "Does Academic Research Destroy Stock Return Predictability?" *J. Finance*

Tracked 97 anomalies before and after publication:
- Average post-publication return **drop of 58%**
- Best explanation: crowding from funds implementing the strategy
- Implication: if you're going to trade an anomaly, either find one that hasn't been published yet, or accept that your realistic return is half the paper's number

### Harvey, Liu, Zhu (2016) "… and the Cross-Section of Expected Returns" *RFS*

Reviewed ~300 factors in the finance literature:
- After Bonferroni / BHY multiple-testing correction, the significance threshold should be `t > 3.0`, not `t > 2.0`
- Recommended: new factors should clear `t ≥ 3.0` to be taken seriously
- Implication: maybe half the published anomaly zoo is statistical noise

### Bailey, Borwein, López de Prado, Zhu (2014) "Pseudo-Mathematics and Financial Charlatanism" *Notices AMS*

Demonstrated that with 5 years of daily data you can data-mine any target Sharpe you want:
- Derived the "probability of backtest overfitting" (PBO) metric
- Showed most published strategies had PBO > 50%
- Practical implication: don't trust single-sample backtests

## Individual findings to keep

### Value (Graham / Fama-French)

- **Citation**: Fama, French (1993, 2015); Piotroski (2000); Asness et al. (2013)
- **Surviving t-stat**: ~3 in long samples, weakening since 2000
- **Realistic Sharpe**: 0.4 – 0.6 standalone, 0.7+ combined with quality screen
- **Warning**: 2015-2020 had the worst value drawdown in history. Even real factors have multi-year pain periods.

### Momentum (Jegadeesh-Titman)

- **Citation**: Jegadeesh, Titman (1993) *J. Finance* 48
- **Signal**: 12-month return, skip last month
- **Surviving t-stat**: ~4-5
- **Realistic Sharpe**: 0.6 – 0.8 standalone
- **Warning**: Momentum "crashes" exist — 2009 and 2020 both had -30% drawdowns in one month

### Time-series momentum / trend-following in futures (Moskowitz-Ooi-Pedersen)

- **Citation**: Moskowitz, Ooi, Pedersen (2012) *JFE* 104; Hurst, Ooi, Pedersen (2017) "A Century of Evidence" *JPM* 44
- **Signal**: 12-month return of the asset itself; go long if positive, short if negative
- **Markets tested**: 59 liquid futures (equities, FX, rates, commodities)
- **Time span**: 120+ years (Hurst et al. use Global Financial Data back to 1880s)
- **Surviving t-stat**: ~5
- **Realistic Sharpe**: 0.8-1.0 for diversified CTA implementation
- **Comment**: This is the single most robust standalone systematic strategy in the literature. It's the backbone of the CTA industry.

### Betting Against Beta (Frazzini-Pedersen)

- **Citation**: Frazzini, Pedersen (2014) "Betting Against Beta" *JFE* 111
- **Signal**: Long low-beta stocks, short high-beta stocks, leveraged to match market beta
- **Surviving t-stat**: ~3.5
- **Warning**: Requires leverage. Works in most markets but not all periods.

### Post-Earnings Announcement Drift (PEAD)

- **Citation**: Bernard, Thomas (1989) *JAE* 13 and follow-ups
- **Signal**: After a large earnings surprise, stock continues drifting in same direction for 60 days
- **Capacity**: Limited — ~$1-5B before alpha decays
- **Warning**: Earnings quality matters; "adjusted" beats are softer signal than GAAP beats

### Low-risk / low-volatility anomaly

- **Citation**: Haugen, Heins (1975); Ang, Hodrick, Xing, Zhang (2006, 2009)
- **Signal**: Sort on trailing-1-year volatility, long low-vol
- **Warning**: Often becomes a crowded momentum trade (popular ETFs)
- **Realistic Sharpe**: 0.4-0.5 standalone

### Piotroski F-Score

- **Citation**: Piotroski (2000) *J. Accounting Research* 38
- **Evidence**: High B/M stocks with F≥8 beat F≤2 by 7.5%/year (1976-1996)
- **Out-of-sample**: Replicated in Piotroski, So (2012); continues to work with degradation
- **Use**: As a quality filter on value screens, not standalone

## Things NOT supported by evidence

- **RSI, MACD, Bollinger Bands, moving average crossovers** on stocks (individual names): virtually no peer-reviewed evidence for out-of-sample outperformance after costs
- **Elliot Wave / Gann angles / harmonic patterns**: no evidence, not testable
- **January effect**: disappeared post-1980
- **Monday effect / turn-of-month effect**: mostly disappeared
- **P/E as a standalone factor**: weak compared to EV/EBIT and composite value
- **Dividend yield as a standalone factor**: weak after controlling for value
- **Most "sentiment" indicators**: mostly noise, some modest evidence (VIX)
- **Technical divergences / chart patterns**: no academic survival evidence
- **Most AI/ML "alpha" claims**: majority are overfitting

## How to use this file in Stage 2

When the user asks "does this strategy work?" or "what's the backtested Sharpe?", cite:
1. The original paper
2. The out-of-sample replication (Hou-Xue-Zhang if applicable)
3. The post-publication decay estimate (McLean-Pontiff)
4. A realistic post-cost Sharpe given crowding

Example answer: "The Piotroski F-score anomaly has strong in-sample evidence (Piotroski 2000, 7.5% annualized alpha). Hou-Xue-Zhang (2020) confirms it at t>3.0 out of sample, and McLean-Pontiff (2016) suggests ~58% decay post-publication, so realistic standalone Sharpe is probably 0.4 rather than the 0.7 in the paper. It's more useful as a quality filter on top of a value screen than as a standalone strategy."

## Reading list (ordered by practical value)

**Start here**:
1. Greenblatt (2006) *The Little Book That Still Beats the Market* — Magic Formula, accessible
2. Piotroski (2000) *J. Accounting Research* — read the original, it's short and clear
3. Chen & Zimmermann (2022) open-source anomaly library — working code

**Then**:
4. Harvey, Liu, Zhu (2016) — the sobering dose of skepticism
5. McLean & Pontiff (2016) — post-publication decay
6. Hou, Xue, Zhang (2020) — replication reality check
7. Asness, Moskowitz, Pedersen (2013) — the four survivor premia

**Deep end**:
8. Damodaran, *Investment Valuation* — the valuation bible
9. Klarman, *Margin of Safety* — philosophy, out of print but findable
10. Graham, *Security Analysis* — the canon, slow going but foundational
