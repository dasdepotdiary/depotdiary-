"""Taegliches Sprech-Skript "What happened to the stock market?" (~30-40 s) fuer
Voiceover-Reels. Zieht Schlusskurse des letzten Handelstags (Yahoo) und schreibt
output/voice_scripts/skript_<datum>.md. Nur Fakten, keine Empfehlung (BaFin/MAR).

Aufruf: python posts/daily_voice_script.py
"""
import datetime as dt
from pathlib import Path

import requests

H = {"User-Agent": "Mozilla/5.0"}
ROOT = Path(__file__).parent.parent
ITEMS = [("S&P 500", "^GSPC", "idx"), ("Nasdaq", "^IXIC", "idx"), ("Dow Jones", "^DJI", "idx"),
         ("DAX", "^GDAXI", "idx"), ("Gold", "GC=F", "usd"), ("Oel (WTI)", "CL=F", "usd"),
         ("Bitcoin", "BTC-USD", "usd")]


def fetch(sym):
    r = requests.get(f"https://query1.finance.yahoo.com/v8/finance/chart/{sym}?range=10d&interval=1d",
                     headers=H, timeout=20).json()["chart"]["result"][0]
    rows = [(t, c) for t, c in zip(r["timestamp"], r["indicators"]["quote"][0]["close"]) if c]
    today = dt.date.today()
    rows = [x for x in rows if dt.datetime.fromtimestamp(x[0]).date() < today]  # nur abgeschlossene Handelstage
    return rows[-1][0], rows[-1][1], rows[-2][1]


def de(x, d=0):
    return f"{x:,.{d}f}".replace(",", "X").replace(".", ",").replace("X", ".")


def word(p):
    a = abs(p)
    if a < 0.15: return "praktisch unveraendert"
    s = "stark " if a >= 1.5 else ""
    return f"{s}{'im Plus' if p > 0 else 'im Minus'}, {de(a, 1)} Prozent"


def main():
    data = {}
    for n, s, k in ITEMS:
        ts, last, prev = fetch(s)
        data[n] = (ts, last, (last / prev - 1) * 100, k)
    day = dt.datetime.fromtimestamp(max(v[0] for v in data.values())).strftime("%d.%m.%Y")
    wd = ["Montag", "Dienstag", "Mittwoch", "Donnerstag", "Freitag", "Samstag", "Sonntag"][
        dt.datetime.strptime(day, "%d.%m.%Y").weekday()]
    ups = sum(1 for v in data.values() if v[2] > 0)
    mood = "ein gruener Tag" if ups >= 5 else "ein roter Tag" if ups <= 2 else "ein gemischter Tag"
    g = lambda n: data[n][2]
    lines = [
        f"HOOK: Was ist am {wd} an der Boerse passiert? Kurz und ehrlich -- {mood}.",
        f"US-Markt: Der S&P 500 schliesst {word(g('S&P 500'))}, der Nasdaq {word(g('Nasdaq'))}, der Dow {word(g('Dow Jones'))}.",
        f"Europa: Der DAX endet {word(g('DAX'))} bei {de(data['DAX'][1])} Punkten.",
        f"Rohstoffe: Gold {word(g('Gold'))}, Oel {word(g('Oel (WTI)'))}.",
        f"Krypto: Bitcoin {word(g('Bitcoin'))}, aktuell bei {de(data['Bitcoin'][1])} Dollar.",
        "[EIGENER SATZ, 1 Thema des Tages: Warum? -- kurz in Schlagzeilen nachsehen und in 1 Satz sagen; nur Fakten, kein Kursziel]",
        "OUTRO: Das war's. Ich schreib dir morgen wieder, was an der Boerse los war -- folg mir, wenn du's nicht verpassen willst. Keine Anlageberatung.",
    ]
    out = ROOT / "output" / "voice_scripts"
    out.mkdir(parents=True, exist_ok=True)
    p = out / f"skript_{dt.datetime.strptime(day, '%d.%m.%Y').strftime('%Y-%m-%d')}.md"
    p.write_text(f"# Skript fuer {wd}, {day} (ca. 35 s)\n\n" + "\n\n".join(lines) + "\n", encoding="utf-8")
    print(p.read_text(encoding="utf-8"))


if __name__ == "__main__":
    main()
