"""Monatliches Depot-Update (PROMPTS.md Prompt 3).

Liest data/holdings_<JJJJ-MM>.json (Rohwerte in Euro, bleibt lokal/gitignored),
rechnet Allokation in Prozent, vergleicht mit dem Vormonat falls vorhanden,
und schreibt AUSSCHLIESSLICH Prozentwerte nach:

  data/depot_<JJJJ-MM>.json     (lokales Archiv, fuer Monatsvergleich)
  site/content/depot.json       (fuer die Website)

Absolute Eurobetraege verlassen diese Datei nie in Richtung der Ausgabedateien.

Aufruf:
  python scripts/update_depot.py 2026-08
"""

import json
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).parent.parent
DATA_DIR = ROOT / "data"
SITE_DEPOT_JSON = ROOT / "site" / "content" / "depot.json"

CATEGORY_LABELS = {
    "einzelaktien": "Einzelaktien",
    "etf": "ETFs & Fonds",
    "bitcoin": "Bitcoin & BTC-Treasuries",
    "gold_silber": "Gold & Silber",
}
CATEGORY_ORDER = ["einzelaktien", "etf", "bitcoin", "gold_silber"]


def load_holdings(month: str) -> dict:
    path = DATA_DIR / f"holdings_{month}.json"
    if not path.exists():
        sys.exit(f"Nicht gefunden: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def previous_month_depot(month: str) -> dict | None:
    """Sucht die naechstaeltere data/depot_*.json vor <month>, falls vorhanden."""
    candidates = sorted(
        p for p in DATA_DIR.glob("depot_*.json") if p.stem.split("_", 1)[1] < month
    )
    if not candidates:
        return None
    return json.loads(candidates[-1].read_text(encoding="utf-8"))


def compute(holdings: dict) -> dict:
    positions = holdings["positions"]
    cash = holdings["cash"]
    invested = sum(p["value"] for p in positions)
    total = invested + cash

    cat_sums = {c: 0.0 for c in CATEGORY_ORDER}
    for p in positions:
        cat_sums[p["category"]] += p["value"]

    categories_ohne_cash = [
        {"key": c, "label": CATEGORY_LABELS[c], "percent": round(cat_sums[c] / invested * 100, 1)}
        for c in CATEGORY_ORDER
    ]
    categories_mit_cash = [
        {"key": c, "label": CATEGORY_LABELS[c], "percent": round(cat_sums[c] / total * 100, 1)}
        for c in CATEGORY_ORDER
    ] + [{"key": "cash", "label": "Cash", "percent": round(cash / total * 100, 1)}]

    top_positions = sorted(positions, key=lambda p: p["value"], reverse=True)[:8]
    top_positions_pct = [
        {"name": p["name"], "percent": round(p["value"] / invested * 100, 1)} for p in top_positions
    ]

    return {
        "month": holdings["month"],
        "updated": date.today().isoformat(),
        "position_count": len(positions),
        "categories_ohne_cash": categories_ohne_cash,
        "categories_mit_cash": categories_mit_cash,
        "top_positions": top_positions_pct,
    }


def diff_categories(current: dict, previous: dict | None) -> list[dict]:
    if previous is None:
        return []
    prev_by_key = {c["key"]: c["percent"] for c in previous["categories_ohne_cash"]}
    diffs = []
    for c in current["categories_ohne_cash"]:
        prev_pct = prev_by_key.get(c["key"])
        if prev_pct is None:
            continue
        diffs.append({"key": c["key"], "label": c["label"], "delta": round(c["percent"] - prev_pct, 1)})
    return diffs


def write_site_depot_json(result: dict, diffs: list[dict]):
    change_note = ""
    if diffs:
        biggest = max(diffs, key=lambda d: abs(d["delta"]))
        if abs(biggest["delta"]) >= 0.1:
            sign = "+" if biggest["delta"] > 0 else ""
            change_note = f"*{biggest['label']}* {sign}{biggest['delta']} Prozentpunkte zum Vormonat."

    payload = {
        "placeholder": False,
        "updated": result["updated"],
        "categories": [
            {"label": c["label"], "percent": c["percent"]} for c in result["categories_ohne_cash"]
        ],
        "change_note": change_note,
    }
    SITE_DEPOT_JSON.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def main():
    if len(sys.argv) != 2:
        sys.exit("Aufruf: python scripts/update_depot.py <JJJJ-MM>")
    month = sys.argv[1]

    holdings = load_holdings(month)
    previous = previous_month_depot(month)

    result = compute(holdings)
    result["diff_vs_last_month"] = diff_categories(result, previous)

    out_path = DATA_DIR / f"depot_{month}.json"
    out_path.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    write_site_depot_json(result, result["diff_vs_last_month"])

    print(f"Geschrieben: {out_path}")
    print(f"Geschrieben: {SITE_DEPOT_JSON}")
    print()
    print("Ohne Cash:")
    for c in result["categories_ohne_cash"]:
        print(f"  {c['label']:28s} {c['percent']:5.1f}%")
    print("\nMit Cash:")
    for c in result["categories_mit_cash"]:
        print(f"  {c['label']:28s} {c['percent']:5.1f}%")
    print("\nTop-8-Positionen:")
    for p in result["top_positions"]:
        print(f"  {p['name']:28s} {p['percent']:5.1f}%")
    if result["diff_vs_last_month"]:
        print("\nVeraenderung zum Vormonat:")
        for d in result["diff_vs_last_month"]:
            print(f"  {d['label']:28s} {d['delta']:+.1f} Prozentpunkte")


if __name__ == "__main__":
    main()
