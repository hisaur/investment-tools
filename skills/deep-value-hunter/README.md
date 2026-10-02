# Deep Value Hunter

A two-stage Claude Code skill for finding **genuinely overlooked** pockets of value in public equity markets. Not a monolithic DD checklist — an actual discovery pipeline.

## What it does

- **Stage 1 (Discovery)**: Narrows the ~10,000 US-listed ticker universe to ~20 finalists using quantitative filters (Piotroski F-score, Altman Z, Greenblatt Magic Formula, EV/EBIT, FCF yield, insider buying) and "overlooked pocket" heuristics (spinoffs, post-bankruptcy emergers, mega/large-cap fallen angels, 13D clusters).
- **Stage 2 (Deep Dive)**: Applies a Buffett / Munger / Fisher / Pabrai / Damodaran framework **only to survivors**, not to every stock the user has ever heard of.

## Philosophy

Most "value investing" prompts in the wild are 2,000-word monolithic checklists that assume you already picked the ticker. That's backwards. Real deep value is 80% searching, 20% analyzing — you spend most of your time rejecting candidates, not writing essays about them.

This skill flips the ratio.

## Why it's grounded

Built on the academic consensus of what actually works:

| Finding                                                                    | Citation                   |
| -------------------------------------------------------------------------- | -------------------------- |
| ~82% of 452 published anomalies fail the `t > 3.0` bar                     | Hou, Xue, Zhang (2020) RFS |
| Anomaly returns decay ~58% post-publication                                | McLean & Pontiff (2016) JF |
| Use `t > 3.0` not `t > 2.0` after multiple-testing correction              | Harvey, Liu, Zhu (2016) RFS|
| Four survivor premia: Value, Momentum, Carry, Defensive                    | AQR working papers (various)|
| Piotroski F-score adds ~7.5% annualized to a simple B/M screen             | Piotroski (2000) JAR       |
| Greenblatt Magic Formula ~30% CAGR 1988-2004 backtest (degraded since)     | Greenblatt (2006)          |

These aren't the only things that work, but they're the things that have survived replication, cost modeling, and multiple-testing correction. Everything else is suspect.

## Install as a Claude Code skill

```bash
# Clone to your skills directory
git clone https://github.com/Neyt/deep-value-hunter.git ~/.claude/skills/deep-value-hunter

# Or link from this repo
ln -s "$(pwd)" ~/.claude/skills/deep-value-hunter
```

Then in Claude Code, invoke with:

```
Find me overlooked value stocks in US mega-caps, Pabrai style, 5 names
```

## Usage

Three entry points:

1. **Full pipeline** — `find overlooked value in [universe]`
2. **Stage 1 only (screen)** — `screen for [Piotroski / spinoffs / net-nets / etc.]`
3. **Stage 2 only (deep dive)** — `deep dive on $TICKER`

## Output

- Markdown report by default
- `.docx` auto-generated via pandoc
- Cites SEC EDGAR primary sources for every number
- Explicit bull / base / bear scenarios with probability weights
- Explicit rejection criteria (value trap red flags)

## License

MIT. Do whatever you want with it. Nothing here is investment advice.

## Not investment advice

This is a research tool. It does not know your tax situation, risk tolerance, time horizon, or liquidity needs. Every number it produces is a starting point for your own independent verification against primary sources. Past replication does not guarantee future returns. Anomaly returns decay. Value traps exist. You can and will lose money if you blindly trust an LLM with your portfolio.
