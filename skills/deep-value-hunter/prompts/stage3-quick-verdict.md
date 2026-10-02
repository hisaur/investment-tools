# Stage 3 — Quick Verdict (optional, lightweight)

> **Lazy-Load Protocol**: View ONLY `references/value-trap-red-flags.md` for this stage. Do NOT load full Stage 2 valuation files or templates unless proceeding to Stage 2.

Use this when the user asks "is $TICKER worth a deep dive?" — do NOT run the full Stage 2 framework. Target: under 400 words, under 60 seconds of reading.

## 5-point checklist

For the ticker the user named, answer exactly these five questions. Each must cite one primary source.

1. **Is it solvent?** (Altman Z > 1.8 and net debt/EBITDA < 4)
   → Cite latest 10-Q balance sheet (URL + page).

2. **Is it cheap on ANY normalized metric?** (EV/EBIT < 10, or P/TBV < 1.2, or FCF yield > 8%, or NCAV positive)
   → Cite the number you used and the filing.

3. **Is there ANY overlooked-pocket tailwind?** (spin-off, insider cluster, 13D, post-bankruptcy, microcap neglect, etc.)
   → Cite the evidence (EDGAR filing URL or Form 4 URL).

4. **Does it trigger 2+ value-trap flags?** (see `references/value-trap-red-flags.md`)
   → Yes / No with the specific flags named.

5. **Is the business within a normal circle of competence?** (a retail investor could explain it in 2 sentences)
   → Yes / No / Borderline.

## Verdict

Based on the 5 answers, pick ONE:

- **Worth a deep dive** — all 5 pass (solvent, cheap, has a tailwind, no trap flags, understandable)
- **Watchlist only** — 3-4 pass but one softer concern
- **Pass immediately** — 2+ value-trap flags, OR it's not cheap, OR outside circle of competence
- **Too hard pile** — data is inaccessible or the business can't be understood in 2 sentences

## Output format (strict)

```markdown
## [TICKER] Quick Verdict — [Date]

1. **Solvent?** ✅/⚠️/❌ [one-sentence evidence + URL]
2. **Cheap?** ✅/⚠️/❌ [metric + value + URL]
3. **Tailwind?** ✅/⚠️/❌ [pocket + evidence]
4. **Value trap flags?** ✅ clear / ⚠️ one / ❌ two+  [list them]
5. **Circle of competence?** ✅/⚠️/❌ [2-sentence business description]

**Verdict**: [one of the four above]
**Next step**: [concrete action — e.g., "run Stage 2 deep dive" / "skip" / "revisit after Q2 10-Q"]
```

That's the whole output. No more, no less. The user can request a full Stage 2 dive afterward if verdict is "Worth a deep dive."
