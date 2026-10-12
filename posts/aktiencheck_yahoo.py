"""Aktien-Check mit Yahoo-Daten (Alpha-Vantage-Key aktuell ungueltig/limitiert).
Aufruf: python posts/aktiencheck_yahoo.py <ISO-Datum> TICKER:Name:Zusatzsatz ...
Rendert 3 Slides nach docs/assets/posts_9x16/aktiencheck_<datum>/ (Fakten, keine Wertung).
"""
import csv, datetime as dt, sys
from pathlib import Path
import requests
sys.path.insert(0, str(Path(__file__).parent))
import story_aktiencheck as A

ROOT = Path(__file__).parent.parent
s = requests.Session(); s.headers["User-Agent"] = "Mozilla/5.0"
s.get("https://fc.yahoo.com", timeout=15)
crumb = s.get("https://query1.finance.yahoo.com/v1/test/getcrumb", timeout=15).text


def de(x, d=1): return f"{x:,.{d}f}".replace(",", "X").replace(".", ",").replace("X", ".")


def main(iso, specs):
    out = []
    accents = [A.OCHRE, A.CAT_TEAL, A.GREEN]
    for i, spec in enumerate(specs):
        t, name, extra = (spec.split(":", 2) + [""])[:3]
        r = s.get(f"https://query1.finance.yahoo.com/v8/finance/chart/{t}?range=1y&interval=1d", timeout=20).json()["chart"]["result"][0]
        q = r["indicators"]["quote"][0]
        rows = [(dt.datetime.fromtimestamp(a).strftime("%Y-%m-%d"), c, v) for a, c, v in zip(r["timestamp"], q["close"], q["volume"]) if c and dt.datetime.fromtimestamp(a).strftime("%Y-%m-%d") < iso]
        last, prev = rows[-1][1], rows[-2][1]; lo = min(x[1] for x in rows); hi = max(x[1] for x in rows)
        with open(A.DATA_DIR / f"{t}.csv", "w", newline="") as fh:
            w = csv.writer(fh); w.writerow(["timestamp", "close"]); [w.writerow(x[:2]) for x in rows[-70:]]
        d = s.get(f"https://query1.finance.yahoo.com/v10/finance/quoteSummary/{t}?modules=summaryDetail,defaultKeyStatistics,price&crumb={crumb}", timeout=20).json()["quoteSummary"]["result"][0]
        g = lambda m, k: (d[m].get(k) or {}).get("raw")
        cap = g("price", "marketCap")
        note = f"Rund {(1 - last / hi) * 100:.0f}% unter dem 52-Wochen-Hoch ({de(hi, 2)} USD), {(last / lo - 1) * 100:.0f}% ueber dem Tief ({de(lo, 2)} USD)." + (" " + extra if extra else "")
        dy = g("summaryDetail", "dividendYield"); eg = g("defaultKeyStatistics", "earningsQuarterlyGrowth")
        out.append(dict(name=name, ticker=t, price=round(last, 2), change_pct=round((last / prev - 1) * 100, 2), as_of=rows[-1][0][8:] + "." + rows[-1][0][5:7] + ".",
            pe=g("summaryDetail", "trailingPE"), forward_pe=g("summaryDetail", "forwardPE"), peg=g("defaultKeyStatistics", "pegRatio"), div_yield=(dy or 0) * 100,
            earnings_growth=(eg * 100 if eg is not None else None), beta=g("summaryDetail", "beta"),
            market_cap=(de(cap / 1e9, 1) + " Mrd. USD") if cap < 1e12 else (de(cap / 1e12, 2) + " Bio. USD"),
            volume=de(rows[-1][2] / 1e6, 1) + " Mio.", week52_low=round(lo, 2), week52_high=round(hi, 2), csv_path=A.DATA_DIR / f"{t}.csv", accent=accents[i % 3], note=note))
    dst = ROOT / "docs" / "assets" / "posts_9x16" / f"aktiencheck_{iso}"; dst.mkdir(parents=True, exist_ok=True)
    for i, st in enumerate(out, 1):
        A.slide_stock(st, i, len(out)).save(dst / f"slide_{i}.png")
    for st in out: print(st["ticker"], st["price"], st["change_pct"], st["note"])


if __name__ == "__main__":
    iso = sys.argv[1]
    A.DATE_LABEL = dt.date.fromisoformat(iso).strftime("%d.%m.%Y")
    main(iso, sys.argv[2:])
