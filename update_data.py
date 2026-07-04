#!/usr/bin/env python3
"""
WahinSe daily updater — recomputes engine-tracked Indian net worths and
writes data.json, which the site loads at runtime.

  net worth = promoter stake % x live market cap

Usage:
  python3 update_data.py             # live: fetches prices via yfinance
  python3 update_data.py --offline   # uses fallback market caps (no network)

Production: runs daily via .github/workflows/daily-update.yml
Maintenance: update `stake` quarterly when BSE/NSE shareholding filings drop,
and refresh fallback_mcap_cr occasionally so offline mode stays sane.
"""
import json, sys, datetime

OFFLINE = "--offline" in sys.argv
USD_INR_FALLBACK = 87.0

# key = the exact English name used in the site's INDIA data (join key)
ENGINE = [
    dict(key="Mukesh Ambani & family",  ticker="RELIANCE.NS",   stake=50.07, fallback_mcap_cr=17_63_966),
    dict(key="Sunil Mittal & family",   ticker="BHARTIARTL.NS", stake=23.00, fallback_mcap_cr=11_42_490),
    dict(key="Dilip Shanghvi & family", ticker="SUNPHARMA.NS",  stake=54.48, fallback_mcap_cr=4_47_764),
    dict(key="RK Damani & family",      ticker="DMART.NS",      stake=74.50, fallback_mcap_cr=2_73_095),
    dict(key="Shiv Nadar family",       ticker="HCLTECH.NS",    stake=60.81, fallback_mcap_cr=3_12_913),
]

HINDI_MONTHS = ["जनवरी","फ़रवरी","मार्च","अप्रैल","मई","जून",
                "जुलाई","अगस्त","सितंबर","अक्टूबर","नवंबर","दिसंबर"]


def fetch_live():
    """Returns ({ticker: mcap_cr}, usd_inr). Raises on any failure."""
    import yfinance as yf
    caps = {}
    for e in ENGINE:
        info = yf.Ticker(e["ticker"]).fast_info
        mcap_rupees = info["market_cap"]          # in rupees
        caps[e["ticker"]] = mcap_rupees / 1e7      # rupees -> crore
    fx = yf.Ticker("USDINR=X").fast_info["last_price"]
    return caps, float(fx)


def main():
    if OFFLINE:
        caps = {e["ticker"]: e["fallback_mcap_cr"] for e in ENGINE}
        fx = USD_INR_FALLBACK
        mode = "offline (fallback caps)"
    else:
        try:
            caps, fx = fetch_live()
            mode = "live"
        except Exception as err:
            print(f"[warn] live fetch failed ({err}); using fallbacks", file=sys.stderr)
            caps = {e["ticker"]: e["fallback_mcap_cr"] for e in ENGINE}
            fx = USD_INR_FALLBACK
            mode = "fallback after error"

    india = {}
    for e in ENGINE:
        worth_cr = caps[e["ticker"]] * e["stake"] / 100.0
        india[e["key"]] = {
            "lcr": round(worth_cr / 1e5, 2),                       # Rs lakh crore
            "usd": round(worth_cr * 1e7 / (fx * 1e9), 1),          # $ bn
        }

    now = datetime.date.today()
    out = {
        "updated_iso": now.isoformat(),
        "updated_hi": f"{now.day} {HINDI_MONTHS[now.month-1]} {now.year} को अपडेट",
        "updated_en": f"Updated {now.day} {now.strftime('%B')} {now.year}",
        "usd_inr": round(fx, 2),
        "mode": mode,
        "india": india,
    }
    with open("data.json", "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)

    print(f"data.json written ({mode}, USD/INR {fx:.2f})")
    for k, v in india.items():
        print(f"  {k:28s} Rs {v['lcr']:.2f} lakh crore  (~${v['usd']} bn)")


if __name__ == "__main__":
    main()
