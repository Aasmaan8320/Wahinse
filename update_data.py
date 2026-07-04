#!/usr/bin/env python3
"""
WahinSe daily updater v2 — computes Indian billionaire net worths from
promoter stakes x live market caps, now supporting multi-company empires.

  net worth = sum over holdings( stake % x market cap )

Usage:
  python3 update_data.py             # live via yfinance
  python3 update_data.py --offline   # fallback market caps, no network

Stakes from BSE/NSE shareholding filings (as of Q1 FY27 disclosures) and
Bloomberg Billionaires methodology for the Adani family attribution.
Update stakes quarterly when new filings drop.
"""
import json, sys, datetime

OFFLINE = "--offline" in sys.argv
USD_INR_FALLBACK = 87.0

def H(t, s, fb): return dict(ticker=t, stake=s, fb_mcap_cr=fb)

ENGINE = [
 dict(key="Mukesh Ambani & family", holdings=[H("RELIANCE.NS", 50.07, 17_63_966)]),
 dict(key="Gautam Adani & family", holdings=[
    H("ADANIENT.NS",   74.0, 2_80_000), H("ADANIPORTS.NS", 68.0, 3_00_000),
    H("ADANIPOWER.NS", 75.0, 2_30_000), H("ADANIGREEN.NS", 62.0, 1_60_000),
    H("ADANIENSOL.NS", 73.0, 1_10_000), H("ATGL.NS",       37.0,   70_000)]),
 dict(key="Sunil Mittal & family",   holdings=[H("BHARTIARTL.NS", 23.00, 11_42_490)]),
 dict(key="Dilip Shanghvi & family", holdings=[H("SUNPHARMA.NS",  54.48,  4_47_764)]),
 dict(key="RK Damani & family",      holdings=[H("DMART.NS",      74.50,  2_73_095)]),
 dict(key="Shiv Nadar family",       holdings=[H("HCLTECH.NS",    60.81,  3_12_913)]),
 dict(key="Uday Kotak",              holdings=[H("KOTAKBANK.NS",  25.88,  3_94_636)]),
 dict(key="Ravi Jaipuria",           holdings=[H("VBL.NS",        59.44,  1_74_468)]),
 dict(key="KP Singh & family",       holdings=[H("DLF.NS",        74.10,  1_63_482)]),
 dict(key="Pankaj Patel & family",   holdings=[H("ZYDUSLIFE.NS",  75.00,  1_10_701)]),
 dict(key="Falguni Nayar & family",  holdings=[H("NYKAA.NS",      52.10,    89_022)]),
]


# World engine: stakes verified Jul-2026 (SEC/AMF filings via press).
# ccy = listing currency; fb_mcap in $bn (USD), €bn (EUR), or Rs crore (INR).
def W(t, s, ccy, fb): return dict(ticker=t, stake=s, ccy=ccy, fb=fb)

WORLD_ENGINE = [
 dict(key="Elon Musk", holdings=[W("TSLA",13.0,"USD",1450), W("SPCX",42.0,"USD",2150)],
      note="TSLA excl. options; SPCX post-IPO economic stake"),
 dict(key="Mark Zuckerberg", holdings=[W("META",13.5,"USD",1500)]),
 dict(key="Jeff Bezos",      holdings=[W("AMZN", 8.8,"USD",2900)]),
 dict(key="Jensen Huang",    holdings=[W("NVDA", 3.5,"USD",4600)]),
 dict(key="Larry Ellison",   holdings=[W("ORCL",41.0,"USD", 450)]),
 dict(key="Bernard Arnault", holdings=[W("MC.PA",50.01,"EUR", 280)],
      note="family stake incl. Dior/Agache holdings"),
 dict(key="Mukesh Ambani",   holdings=[W("RELIANCE.NS",50.07,"INR",17_63_966)]),
 dict(key="Gautam Adani",    holdings=[
      W("ADANIENT.NS",74.0,"INR",2_80_000), W("ADANIPORTS.NS",68.0,"INR",3_00_000),
      W("ADANIPOWER.NS",75.0,"INR",2_30_000), W("ADANIGREEN.NS",62.0,"INR",1_60_000),
      W("ADANIENSOL.NS",73.0,"INR",1_10_000), W("ATGL.NS",37.0,"INR",70_000)]),
]
EURUSD_FALLBACK = 1.18

HINDI_MONTHS = ["जनवरी","फ़रवरी","मार्च","अप्रैल","मई","जून",
                "जुलाई","अगस्त","सितंबर","अक्टूबर","नवंबर","दिसंबर"]


def fetch_live(engine):
    import yfinance as yf
    caps, misses = {}, []
    for e in engine:
        for h in e["holdings"]:
            t = h["ticker"]
            try:
                caps[t] = yf.Ticker(t).fast_info["market_cap"] / 1e7   # rupees -> crore
            except Exception:
                caps[t] = h["fb_mcap_cr"]; misses.append(t)
    try:
        fx = float(yf.Ticker("USDINR=X").fast_info["last_price"])
    except Exception:
        fx = USD_INR_FALLBACK; misses.append("USDINR=X")
    if misses:
        print(f"[warn] fallback used for: {', '.join(misses)}", file=sys.stderr)
    return caps, fx


def main():
    if OFFLINE:
        caps = {h["ticker"]: h["fb_mcap_cr"] for e in ENGINE for h in e["holdings"]}
        fx, mode = USD_INR_FALLBACK, "offline"
    else:
        caps, fx = fetch_live(ENGINE); mode = "live (per-ticker fallback on misses)"

    india = {}
    for e in ENGINE:
        worth_cr = sum(caps[h["ticker"]] * h["stake"] / 100.0 for h in e["holdings"])
        india[e["key"]] = {"lcr": round(worth_cr / 1e5, 2),
                           "usd": round(worth_cr * 1e7 / (fx * 1e9), 1)}

    now = datetime.date.today()
    out = {"updated_iso": now.isoformat(),
           "updated_hi": f"{now.day} {HINDI_MONTHS[now.month-1]} {now.year} को अपडेट",
           "updated_en": f"Updated {now.day} {now.strftime('%B')} {now.year}",
           "usd_inr": round(fx, 2), "mode": mode, "india": india}
    # world engine (USD bn)
    wtickers = [h["ticker"] for e in WORLD_ENGINE for h in e["holdings"]]
    if OFFLINE:
        wcaps = {h["ticker"]: h["fb"] for e in WORLD_ENGINE for h in e["holdings"]}
        eurusd = EURUSD_FALLBACK
    else:
        import yfinance as yf
        wcaps, wmiss = {}, []
        for e in WORLD_ENGINE:
            for h in e["holdings"]:
                if h["ticker"] in wcaps: continue
                try:
                    mc = yf.Ticker(h["ticker"]).fast_info["market_cap"]
                    wcaps[h["ticker"]] = mc/1e7 if h["ccy"]=="INR" else mc/1e9
                except Exception:
                    wcaps[h["ticker"]] = h["fb"]; wmiss.append(h["ticker"])
        try:
            eurusd = float(yf.Ticker("EURUSD=X").fast_info["last_price"])
        except Exception:
            eurusd = EURUSD_FALLBACK; wmiss.append("EURUSD=X")
        if wmiss:
            print(f"[warn] world fallback used for: {', '.join(wmiss)}", file=sys.stderr)
    world = {}
    for e in WORLD_ENGINE:
        usd_bn = 0.0
        for h in e["holdings"]:
            cap = wcaps[h["ticker"]]
            if h["ccy"] == "USD": usd_bn += cap * h["stake"]/100
            elif h["ccy"] == "EUR": usd_bn += cap * eurusd * h["stake"]/100
            else: usd_bn += cap * 1e7 / (fx*1e9) * h["stake"]/100
        world[e["key"]] = {"usd": round(usd_bn, 1)}
    out["world"] = world

    with open("data.json", "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)

    print(f"world: " + ", ".join(f"{k} ${v['usd']}bn" for k,v in sorted(world.items(), key=lambda x:-x[1]['usd'])))
    print(f"data.json written ({mode}, USD/INR {fx:.2f}, {len(india)} live entries)")
    for k, v in sorted(india.items(), key=lambda x: -x[1]["lcr"]):
        print(f"  {k:26s} Rs {v['lcr']:6.2f} lakh crore  (~${v['usd']} bn)")


if __name__ == "__main__":
    main()
