# वहीं से · WahinSe — self-updating rich list

## What's in this folder
- `index.html` — the complete site (Top 20 India, Top 25 world, चप्पल से जहाज़ stories, आपकी बारी resources). Works standalone.
- `update_data.py` — recomputes engine-tracked net worths (promoter stake × live market cap via yfinance) and writes `data.json`.
- `data.json` — daily numbers the site loads at runtime. If missing, the site silently uses its embedded values.
- `.github/workflows/daily-update.yml` — runs the updater automatically every weekday after NSE close and commits the result.

## One-time setup (~20 minutes)
1. Create a GitHub account and a new repository (e.g. `wahinse`).
2. Upload everything in this folder to the repo (keep the `.github/workflows/` path intact).
3. Enable GitHub Pages: repo → Settings → Pages → Source: `main` branch, root. Your site is now live at `https://<user>.github.io/wahinse/`.
4. Point your domain: at your registrar, add a CNAME record for `wahinse.in` → `<user>.github.io`, and add the custom domain in the Pages settings.
5. Done. Every weekday at ~4:15 PM IST the workflow fetches prices, recomputes, commits `data.json`, and Pages redeploys automatically. Laptop off, site fresh.

Test locally any time: `pip install yfinance && python3 update_data.py` (or `--offline` without internet).

## New in this version
- `og.png` — the preview card shown when wahinse.com is shared on WhatsApp/social. Upload it to the repo root alongside index.html.
- Story deep links — every story now has its own URL, e.g. `https://wahinse.com/#story=jindal`. Use these as the reel-specific "link in bio" so viewers land directly on the story the reel promoted. Keys: dhirubhai, damani, nadar, shanghvi, mittal, karsanbhai, adani, jindal, nayar, kotak, yusuffali.
- WhatsApp share button on every story — pre-filled message with the deep link.
- Analytics — the site includes a GoatCounter snippet (free, privacy-friendly, no cookies). One-time setup: go to goatcounter.com → sign up → choose the code `wahinse` (so your dashboard is wahinse.goatcounter.com). If that code is taken, pick another and update the `data-goatcounter` URL in index.html to match. Your visitor dashboard then works automatically.

## Your recurring maintenance
- **Quarterly (~15 min):** when BSE/NSE shareholding filings drop, update `stake` values in `update_data.py`.
- **As you verify:** the 15 entries marked `est.` in `index.html` carry seed figures — verify each against Hurun India / Forbes India, and move listed-company families into `ENGINE` (add ticker + stake) so they update live too.
- **Occasionally:** refresh `fallback_mcap_cr` values so offline/fallback mode stays reasonable.

## Honest limits (keep these on the site)
- Estimates = listed promoter stake × market cap. Private assets, debt, and pledged shares are not included.
- The world list is reference data (Forbes, July 2026) and is not auto-updated in v1 — refresh it manually or extend the updater later.
- Yahoo Finance data is convenient but unofficial; for a serious launch, review its terms and consider a licensed market-data API.
