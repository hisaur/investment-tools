# Stage 0 — Intake

## Preparation Step: Ghostfolio Portfolio Check (Conditional Launch)
Before screening or position sizing, check whether the local Ghostfolio container pipeline is active using the `portfolio-tracker` skill:
```bash
python C:/Users/aleks/.gemini/config/skills/portfolio-tracker/scripts/portfolio_ctl.py ensure
```
- **If ALREADY ONLINE (HTTP 200)**: Ghostfolio is running. Does NOT restart. Proceed immediately.
- **If OFFLINE / DOWN**: Automatically executes container startup and ingests `G:\My Drive\portfolio_docker_sync.csv` so Stage 1 screening and Stage 2 position sizing have live portfolio holdings and cash balances.

---

Before running any screen or deep dive, Claude must collect three pieces of information from the user. These constrain the search space enough to make Stage 1 tractable. **Do not proceed without answers to all three.**

## Questions to ask

### 1. Universe
> "What's the fishing ground? Pick one or combine:
> - US only (all listings, ~6000 tickers) or include international (ADRs, Canada, UK)?
> - Market-cap band: small ($300M–$2B), mid ($2B–$10B), large ($10B–$200B), mega ($200B+), all ($300M+)? (Note: microcaps <$300M excluded)
> - Exclusions: financials? REITs? biotech? Chinese ADRs? SPACs?

**Default if user says "just pick"**: US only, all market caps $300M+ including large/mega-caps (exclude microcaps <$300M), exclude biotech and SPACs (too speculative/binary), include financials and REITs.

### 2. Style
> "Which deep-value lineage? Pick one or blend:
> - **Classic Graham** — net-nets, low P/B, balance-sheet bargains
> - **Buffett/Munger** — quality businesses at fair prices, durable moats
> - **Greenblatt** — Magic Formula (high ROIC × high earnings yield), spin-offs, special situations
> - **Pabrai / Dhandho** — low-risk, high-uncertainty, concentrated
> - **Damodaran / story-driven** — narrative + numbers, scenario-weighted
> - **Fisher scuttlebutt** — qualitative growth at reasonable price"

**Default**: Greenblatt + Pabrai (best combination of quantitative rigor and qualitative judgment for retail investors).

### 3. Output shape
> "How many finalists, and how deep?
> - Screen 20 candidates (1-sentence thesis per stock + sector breakdown for user selection)
> - Stage 3 Quick Verdicts (300-word fast checks on selected candidates)
> - Stage 2 Deep Dives (full structured report on user-selected winners)
> Also: concentrated portfolio (3-5 positions) or diversified (15-30)?"

**Default**: Screen 20 (1-sentence thesis per stock) → User selects candidates → Stage 3 Quick Verdicts or Stage 2 Deep Dives on user-selected names.

### 4. Model Tiering & Override
> "Model execution preference:
> - **Default Hybrid**: Fast **Flash** model for screening + **Pro (Thinking)** subagent for Stage 2 Deep Dives.
> - **Custom Override**: Override Stage 2 deep dive model (e.g. `pro`, `flash`, `inherit`, or specify external provider/model)."

**Default**: Flash for Stage 0/1/3; Stage 2 automatically dispatches a `pro` (Thinking) subagent.

## Output of Stage 0

A compact YAML block capturing the user's answers, passed to Stage 1:

```yaml
universe:
  geography: [US, Canada, UK]
  market_cap_band: [small, mid, large, mega]
  exclusions: [biotech, SPACs, chinese_adrs, microcaps]
style:
  primary: greenblatt_magic_formula
  secondary: pabrai_dhandho
  weight_qualitative: 0.4
output:
  shortlist_size: 20
  deep_dives: user_selected
  portfolio_type: concentrated
  target_positions: 5
execution:
  screening_model: flash
  deep_dive_model: pro    # Options: pro (thinking), flash, inherit, or custom model override
constraints:
  min_daily_volume_usd: 500000    # liquidity floor
  max_share_price: 200             # bias toward odd-lot-friendly
  min_years_public: 3              # survivorship filter
  min_altman_z: 1.8                # not about to go bankrupt
```

Confirm the YAML back to the user in one sentence ("Searching US stocks $300M+ including mega-caps, Greenblatt + Pabrai style, Stage 2 model: Pro (Thinking) — proceeding?") and only move to Stage 1 on acknowledgement.
