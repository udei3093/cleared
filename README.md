# Cleared

A readiness tool for small U.S. importers of record facing Executive Order 14411 ("Strengthening Customs Enforcement," signed June 3, 2026). CBP has until November 30, 2026 to require every importer of record to prove financial standing and disclose beneficial ownership — this project helps importers without a trade compliance desk figure out where they stand.

## What's in here

- `index.html` — landing page
- `assessment.html` — interactive 7-question readiness assessment with a scored, deadline-tagged action list
- `updates.html` — **Regulatory Radar**: a live feed of real CBP / Federal Register filings relevant to EO 14411, refreshed automatically
- `data/updates.json` — the data behind the radar, kept current by a scheduled job (see below)
- `scripts/fetch_updates.py` — pulls fresh documents from the free, public [Federal Register API](https://www.federalregister.gov/developers/documentation/api/v1) (no key required), filters for relevance, and merges them into `data/updates.json`
- `.github/workflows/update-feed.yml` — runs `fetch_updates.py` on a daily schedule (and on demand via `workflow_dispatch`) and commits any changes automatically

## Why it's self-updating without an AI subscription

The radar doesn't call any LLM API — it queries the Federal Register's own public REST API directly, matches results against a relevance filter (agency + keyword based), and commits the diff. That means the feed stays current for free, indefinitely, without needing a paid Claude/OpenAI plan wired into the pipeline.

## Deploying

This is a static site (plain HTML/CSS/JS, no build step) — deploy the repo root as-is to Vercel, Netlify, GitHub Pages, or any static host. When GitHub Actions pushes a new `data/updates.json`, a host connected via git integration (e.g. Vercel's GitHub integration) redeploys automatically, so the live site updates itself with no manual step.

## Not legal or brokerage advice

Cleared gives directional readiness guidance based on public sources. It is not a customs broker or law firm and does not file entries. For binding compliance decisions, consult a licensed customs broker or trade attorney.
