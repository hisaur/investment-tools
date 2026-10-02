# Data Sources — Where the Real Numbers Live

**Rule**: Primary sources first. Never cite a secondary aggregator if the primary source is accessible.

## Tier 1 — Primary (free, authoritative)

### SEC EDGAR (US companies)

The canonical source for all US-listed companies. Everything else is a re-packaging of this.

- **Base URL**: https://www.sec.gov/
- **Full-text search**: https://efts.sec.gov/LATEST/search-index?q=&forms=10-K
- **Company filings by ticker**: `https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK=TICKER&type=10-K&dateb=&owner=include&count=40`
- **XBRL financial data**: https://www.sec.gov/cgi-bin/viewer?action=view&cik=[cik]&type=10-K (machine-readable)
- **Python SDK**: `pip install sec-edgar-downloader` — scrape filings programmatically

**Key filings**:
| Form      | Contents                                    | Frequency   |
|-----------|---------------------------------------------|-------------|
| 10-K      | Annual report                               | Once/year   |
| 10-Q      | Quarterly report                            | 3x/year     |
| 8-K       | Material events (M&A, debt, exec changes)   | As needed   |
| DEF 14A   | Proxy statement (compensation, governance)  | Once/year   |
| Form 4    | Insider transaction                         | Per transaction |
| SC 13D    | Activist 5%+ stake                          | Within 10 days |
| SC 13G    | Passive 5%+ stake                           | Within 45 days  |
| 13F       | Institutional holdings > $100M              | Quarterly   |
| S-1/S-3   | New securities issuance                     | Per offering |
| 10-12B    | Spin-off registration                       | Per spin    |

### Non-US regulatory sites

| Country | Body       | URL                                     |
|---------|------------|-----------------------------------------|
| Canada  | SEDAR+     | https://www.sedarplus.ca/               |
| UK      | FCA / LSE  | https://www.londonstockexchange.com/    |
| EU      | ESMA       | https://www.esma.europa.eu/             |
| Japan   | EDINET     | https://disclosure.edinet-fsa.go.jp/    |
| HK      | HKEx       | https://www.hkexnews.hk/                |
| Aus     | ASX        | https://www.asx.com.au/                 |

Quality falls sharply outside North America and Europe. Outside these regions, treat filings as necessary but not sufficient.

### FRED (macroeconomic)

- **Base URL**: https://fred.stlouisfed.org/
- Free time-series for ~800k economic indicators
- Use for: interest rates, inflation, industry indices, commodity prices, exchange rates
- Python: `pip install fredapi` (requires free API key)

### FRB / Shiller / Damodaran datasets

- **Robert Shiller data**: http://www.econ.yale.edu/~shiller/data.htm — S&P 500 with earnings back to 1871
- **Aswath Damodaran data**: https://pages.stern.nyu.edu/~adamodar/ — free updated industry multiples, betas, ERP, country risk
- **Kenneth French data library**: https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/data_library.html — Fama-French factors, size, value portfolios

## Tier 2 — Academic / research (free, niche)

### Chen & Zimmermann Open Source Cross-Section

**The single most valuable free resource** for systematic deep value.

- **GitHub**: https://github.com/OpenSourceAP/CrossSection
- **Paper**: Chen & Zimmermann (2022) "Open Source Cross-Sectional Asset Pricing" CFR
- **What it contains**:
  - 210+ published anomalies, re-implemented from scratch
  - CSV of each anomaly's signal for every US stock, every month, 1926–present
  - Portfolio returns for each anomaly
  - Replication status flags (which ones actually work out-of-sample)
- **How to use for this skill**:
  1. Clone: `git clone https://github.com/OpenSourceAP/CrossSection.git`
  2. Read `README.md` for signal file layout
  3. Filter the universe in Stage 1 by top quintile on 3-5 complementary anomalies (e.g., Piotroski + AltmanZ + insider buying + post-spin)

### Papers with Code (finance)

- https://paperswithcode.com/area/machine-learning → search for "cross-section of stock returns"
- Many recent papers include code and data

## Tier 3 — Commercial (APIs, some paid)

### yfinance (Python, free but scraped — can break)

```python
import yfinance as yf
ticker = yf.Ticker("AAPL")
ticker.info             # price, market cap, ratios
ticker.financials       # income statement
ticker.balance_sheet    # balance sheet
ticker.cashflow         # cash flow statement
ticker.history("10y")   # price history
ticker.insider_transactions  # Form 4 aggregation
```

**Caveats**: yfinance scrapes Yahoo Finance HTML; breaks when Yahoo changes layout. Use for prototyping, not production. Cross-check numbers against EDGAR.

### Alpha Vantage (free tier)

- https://www.alphavantage.co/
- 5 calls/minute, 500/day on free tier
- Has fundamentals, technical indicators, crypto, FX

### IEX Cloud (paid, but cheap)

- https://iexcloud.io/
- ~$50/month for a decent plan
- Clean APIs for fundamentals, real-time price, corporate actions

### Financial Modeling Prep

- https://financialmodelingprep.com/
- Free tier has basic fundamentals; paid tiers include screeners, ratios, DCF templates

### Quandl / Nasdaq Data Link

- https://data.nasdaq.com/
- Premium datasets (Sharadar, Zacks, etc.) — paid but institutional-quality

## Tier 4 — Screeners (for Stage 1 candidate generation)

### Free and decent

| Tool | URL | Strengths | Weaknesses |
|------|-----|-----------|------------|
| Stockanalysis.com | https://stockanalysis.com/stocks/screener/ | Clean UI, free, Piotroski/Altman built in | No custom metrics |
| Finviz | https://finviz.com/screener.ashx | Fast, many filters, free | Data quality ok but not great |
| Simply Wall St | https://simplywall.st/ | Visual, beginner-friendly | Limited custom screens on free tier |
| Koyfin | https://www.koyfin.com/ | Bloomberg-lite, decent free tier | Paid for full features |
| StockRover | https://www.stockrover.com/ | Deep screening, custom formulas | Paid tiers start ~$8/mo |

### Paid but worth it (at scale)

- **Bloomberg Terminal** ($25k/year — probably not for retail)
- **FactSet** ($15k/year — institutional)
- **Sharadar SF1 via Nasdaq Data Link** ($50-200/month — good retail choice)
- **GuruFocus** ($50/month — fine for deep dives, NOT a primary source)
- **Seeking Alpha Premium** ($240/year — commentary, not data)

## Tier 5 — Insider & institutional flow

| Source | URL | What |
|--------|-----|------|
| OpenInsider | http://openinsider.com/ | Free aggregation of SEC Form 4 |
| Fintel | https://fintel.io/ | Form 4 + 13D + 13F + short interest |
| Dataroma | https://www.dataroma.com/ | Famous investor 13F holdings |
| WhaleWisdom | https://whalewisdom.com/ | Institutional 13F tracking |

## Tier 6 — News / sentiment (use cautiously)

- Reuters, Bloomberg: decent for hard news
- WSJ: paywalled but often has company-specific scoops
- SEC 8-K filings: everything material shows up here eventually, free
- X/Twitter (use a list of vetted accounts — @JesseFelder, @Citron, @HindenburgRes, @modestproposal1, etc.)

## Anti-recommendations (things to NOT use as primary)

- ❌ Seeking Alpha article thesis as primary source → it's commentary on the filings, not the filings
- ❌ GuruFocus DCF "fair value" → black box, methodology unclear, cross-check everything
- ❌ Yahoo Finance "Key Statistics" → occasional stale numbers, cross-check with EDGAR
- ❌ Investopedia → tutorial quality, not research quality
- ❌ Motley Fool → entertainment, not analysis
- ❌ Reddit / WSB → sentiment source only, never a data source
- ❌ ChatGPT / any LLM without tool use → training cutoff, hallucinations

## Recommended stack for this skill

For a retail user with zero budget:
```
Discovery:  Stockanalysis.com screener + Chen-Zimmermann CSV + OpenInsider
Primary:    SEC EDGAR direct fetch (Python requests + BeautifulSoup or sec-edgar-downloader)
Pricing:    yfinance
Macro:      FRED + Damodaran datasets
Sentiment:  Curated X/Twitter list
Deep dive:  SEC EDGAR (10-K, 10-Q, 8-K, DEF 14A, Form 4) + company IR website
```

For a retail user with ~$100/month budget, add:
```
+ Koyfin or StockRover for screening
+ Alpha Vantage or Financial Modeling Prep for fundamentals API
```

For a small fund or serious retail with ~$500/month budget, add:
```
+ Sharadar SF1 (via Nasdaq Data Link) — institutional-quality fundamentals
+ Fintel for institutional and insider flow
```

Beyond that, you need Bloomberg or FactSet and you're no longer retail.
