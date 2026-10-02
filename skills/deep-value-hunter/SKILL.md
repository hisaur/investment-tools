---
name: deep-value-hunter
description: Two-stage deep value stock discovery and analysis pipeline. ONLY activate when the user explicitly requests the /deep-value-hunter command or mentions "deep-value-hunter". Do not trigger on general stock screening or value investing queries.
when_to_use:
  - "deep-value-hunter"
  - "/deep-value-hunter"
license: MIT
author: "Neyt (htlin222/meta-pipe-inspired architecture)"
version: 0.1.0
---

# Deep Value Hunter

> A two-stage pipeline for finding genuinely overlooked pockets of value in public equity markets — not yet-another monolithic due-diligence template.

## Why this exists

Most "value investing" prompts assume you already know which ticker to analyze. They produce 5000-word Buffett-style reports on stocks you picked from a headline. **That's not how real deep value works.** Klarman, Greenblatt, Pabrai, and Watsa spend the majority of their time **searching** — sifting through neglected corners of the market — and only the minority actually valuing individual names.

This skill flips the ratio:

- **Stage 1 — Discovery & Screening**: narrow ~10,000 US-listed tickers to ~20 finalists using quantitative filters (Piotroski, Altman, Graham, EV/EBIT, FCF yield) layered with "overlooked pocket" heuristics (spinoffs, post-bankruptcy emergers, mega/large-cap fallen angels, insider clusters, 13D filings, etc.).
- **Stage 2 — Deep Dive**: apply the Buffett/Munger/Fisher/Pabrai/Damodaran framework to the survivors, not to every stock you've ever heard of.

If you already have a ticker and just want a DD report, use `prompts/stage3-deep-dive.md` directly. Otherwise, run the full pipeline.

---

## How to invoke

The skill activates when the user says anything like:
- "find me overlooked value stocks"
- "run the deep value hunter"
- "screen for net-nets / Piotroski / spinoffs"
- "deep dive on $TICKER"

When activated, Claude should:

0. **Preparation Step — Ghostfolio Portfolio Sync (Conditional Launch)**:
   Before screening or deep-dive sizing, check whether the local ephemeral Ghostfolio stack is running to provide live portfolio holdings, trade history, and cash context using the dedicated `portfolio-tracker` skill:
   - **Check & Ensure Running (Idempotent 1-Command)**:
     ```bash
     python C:/Users/aleks/.gemini/config/skills/portfolio-tracker/scripts/portfolio_ctl.py ensure
     ```
     - **If ALREADY ONLINE**: Skips launch and outputs `[OK] Ghostfolio stack is ALREADY RUNNING`.
     - **If OFFLINE / DOWN**: Automatically starts containers, ingests Google Drive synced trades (`G:\My Drive\portfolio_docker_sync.csv`), and opens `http://localhost:3333`.
   - **Why This Matters**:
     - **Stage 1 (Screening)**: Cross-references candidates against current holdings and sector weightings in Ghostfolio (via `python scripts/screen.py --check-portfolio`) to prevent recommending overconcentrated sectors (>25% cap) or duplicate positions.
     - **Stage 2 (Deep Dive)**: Uses actual portfolio total value and available cash reserves to compute exact dollar position sizing and share counts alongside Kelly-lite %.
   - **Optional Teardown**: Stop and clean up containers when finished:
     ```bash
     python C:/Users/aleks/.gemini/config/skills/portfolio-tracker/scripts/portfolio_ctl.py cleanup
     ```

1. **Ask three clarifying questions** (from `prompts/stage0-intake.md`):
   a. Universe — US only, or include international? Market-cap band?
   b. Style — classic Graham net-nets, Greenblatt spin-offs, Pabrai Dhandho, Damodaran "story-driven," or a blend?
   c. Position sizing — concentrated (3-5 names) or diversified (20-30 names)?

2. **Run Stage 1** (`prompts/stage1-screen.md`) — emit a ranked shortlist of 20 candidates with a **ONE-SENTENCE thesis each**, key quantitative metrics, and a **Sector & Factor Overlap breakdown** (cross-referenced with Ghostfolio holdings).

3. **Present shortlist & await user selection**: Present the shortlist and ask the user which 3-5 candidates to advance to Stage 3 Quick Verdicts (or Stage 2 Deep Dives). **Stop and wait for user choice.**

4. **Run Stage 3 (Quick Verdict)** on Flash or **Stage 2 (Deep Dive)** by automatically spawning a **Pro (Thinking)** subagent (`invoke_subagent` with `Model: 'pro'` or user model override from Stage 0) to execute deep diligence on user-selected winners (including exact dollar & Kelly-lite position sizing against Ghostfolio cash reserves).

5. **Always cite primary sources** — EDGAR 10-K/10-Q/8-K/Form 4/13D/13G with direct URLs — before secondary (yfinance, GuruFocus, Seeking Alpha).

6. **Always produce a `.docx`** of the final report (user preference — convert markdown → docx via pandoc).

---

## Lazy-Loading Protocol (Token Optimization)

To conserve context window and minimize token overhead, **DO NOT load all reference files upfront**. Load reference files on-demand using `view_file` strictly according to the active stage:

- **Stage 0 (Intake)**: Read ONLY `prompts/stage0-intake.md`. Do NOT load any reference files.
- **Stage 1 (Discovery & Screening)**: Read ONLY `prompts/stage1-screen.md`, `references/quantitative-filters.md`, and `references/overlooked-pockets.md`.
- **Stage 2 (Deep Dive)**: Read ONLY `prompts/stage2-deep-dive.md`, `references/valuation-methods.md`, `references/buffett-munger-gates.md`, `references/value-trap-red-flags.md`, and `templates/deep-dive-report.md`.
- **Stage 3 (Quick Verdict)**: Read ONLY `prompts/stage3-quick-verdict.md` and `references/value-trap-red-flags.md`.
- **On-Demand Only**: Load `references/data-sources.md` or `references/academic-evidence.md` ONLY if specifically needed for EDGAR endpoints or when questioned on academic replication.

## Context Pruning & State Isolation Protocol

1. **No Dropped Stock Memory Leak**: Dropped/rejected stocks are logged to `scratch/screening_results.json` during screening. Do NOT output long reject list blocks into the chat context.
2. **Subagent Prompt Isolation**: When spawning Stage 2 subagents via `invoke_subagent`, pass ONLY the user-selected ticker(s) and Stage 0 YAML. Do NOT pass unselected shortlist stocks or past conversational transcripts into the subagent context.

---

## Files in this skill

```
deep-value-hunter/
├── SKILL.md                                    # <- you are here
├── README.md                                   # Public-facing intro
├── LICENSE                                     # MIT
├── prompts/
│   ├── stage0-intake.md                        # Clarifying questions
│   ├── stage1-screen.md                        # Discovery engine
│   ├── stage2-deep-dive.md                     # Full due-diligence framework
│   └── stage3-quick-verdict.md                 # Lightweight "is this worth more time?" check
├── scripts/
│   └── screen.py                               # Automated quantitative screener
├── references/
│   ├── overlooked-pockets.md                   # Where to fish (spinoffs, microcaps, etc.)
│   ├── quantitative-filters.md                 # Piotroski, Altman, Graham, Greenblatt Magic Formula
│   ├── buffett-munger-gates.md                 # Qualitative pass/fail gates
│   ├── valuation-methods.md                    # Asset/Earnings/FCF/SOTP/DCF with formulas
│   ├── value-trap-red-flags.md                 # How to REJECT, not just accept
│   ├── data-sources.md                         # EDGAR, 13F, Form 4, etc. with direct URLs
│   └── academic-evidence.md                    # What actually works (Hou-Xue-Zhang, Chen-Zimmermann)
└── templates/
    └── deep-dive-report.md                     # Structured output schema
```

## Design principles

1. **Reject fast** — most stocks are not worth analyzing. Stage 1 should kill ~99% of the universe. The worst failure mode is spending 3000 tokens on a DD report for a mediocre name.
2. **Primary sources first** — SEC EDGAR is free and authoritative. Claude should fetch 10-K / 10-Q / 8-K / Form 4 / 13D / 13G directly via `https://www.sec.gov/cgi-bin/browse-edgar` before touching secondary aggregators.
3. **Quantitative gates, qualitative judgment** — use hard numeric thresholds (Piotroski ≥ 7, Altman > 3, FCF yield > 8%) to filter, then apply Buffett/Munger narrative judgment to survivors.
4. **Explicit "too hard" pile** — when a stock triggers ≥2 red flags from `value-trap-red-flags.md`, reject immediately and move on. Don't burn tokens on "but maybe..." rationalizations.
5. **Track the base rate** — cite Hou-Xue-Zhang (2020) ~18% replication rate at t>3.0 and McLean-Pontiff (2016) ~58% post-publication decay whenever the user asks "does this strategy work?" Intellectual honesty over optimism.
6. **One citation per claim** — every number in the final report must cite an EDGAR filing, a Chen-Zimmermann dataset, or a peer-reviewed paper. "According to Seeking Alpha" is not acceptable.

## Anti-patterns this skill explicitly avoids

- ❌ Ten-thousand-word reports on every ticker ("monolithic DD dumps")
- ❌ Using GuruFocus/Seeking Alpha as primary sources
- ❌ Claiming margin of safety without showing the calculation
- ❌ Ignoring the base rate of anomaly decay
- ❌ No bear case ("every stock is a buy")
- ❌ Using P/E as the only valuation metric
- ❌ Forgetting dilution (fully diluted vs. current shares)
- ❌ Treating the Buffett/Munger checklist as boxes to tick rather than a forcing function for rejection
