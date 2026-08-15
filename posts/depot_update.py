"""Erzeugt den 6-Slide Depot-Update-Post aus data/depot_<JJJJ-MM>.json.

Enthaelt ausschliesslich Prozentwerte (siehe scripts/update_depot.py) --
keine absoluten Eurobetraege werden je auf eine Slide geschrieben.

Aufruf:
  python posts/depot_update.py 2026-08
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from render import Post
import brand as B
import voiceover
import site_sync

DATA_DIR = Path(__file__).parent.parent / "data"

CATEGORY_COLOR = {
    "einzelaktien": B.INK,
    "etf": B.INK,
    "bitcoin": B.GREEN,
    "gold_silber": B.OCHRE,
    "cash": B.GREY,
}


def load_depot(month: str) -> dict:
    path = DATA_DIR / f"depot_{month}.json"
    if not path.exists():
        sys.exit(f"Nicht gefunden: {path}. Erst 'python scripts/update_depot.py {month}' laufen lassen.")
    return json.loads(path.read_text(encoding="utf-8"))


def rows_from_categories(categories):
    return [(c["label"], f"{c['percent']}%", CATEGORY_COLOR.get(c["key"], B.INK)) for c in categories]


def main():
    if len(sys.argv) != 2:
        sys.exit("Aufruf: python posts/depot_update.py <JJJJ-MM>")
    month = sys.argv[1]
    depot = load_depot(month)

    post = Post(f"depot_update_{month}", total_slides=6)

    post.slide_hook(
        "DEPOT-UPDATE",
        f"Mein Depot in *Zahlen*.",
        f"Stand {depot['updated']}, {depot['position_count']} Positionen, alles in Prozent.",
    )

    post.slide_rows(
        "DEPOT-UPDATE",
        "Meine *Allokation* ohne Cash.",
        rows_from_categories(depot["categories_ohne_cash"]),
        "Bezogen auf den investierten Betrag, ohne Cash-Anteil.",
    )

    post.slide_rows(
        "DEPOT-UPDATE",
        "Und *inklusive* Cash.",
        rows_from_categories(depot["categories_mit_cash"]),
        "Gleiche Aufteilung, jetzt mit Cash-Quote sichtbar.",
    )

    top_rows = [(p["name"], f"{p['percent']}%", B.INK) for p in depot["top_positions"]]
    post.slide_rows(
        "DEPOT-UPDATE",
        "Die *größten* Positionen.",
        top_rows,
        "Anteil am investierten Betrag, absteigend sortiert.",
    )

    diffs = depot.get("diff_vs_last_month") or []
    if diffs:
        biggest = max(diffs, key=lambda d: abs(d["delta"]))
        sign = "+" if biggest["delta"] > 0 else ""
        post.slide_card(
            "DEPOT-UPDATE",
            "Veränderung zum *Vormonat*.",
            f"{sign}{biggest['delta']}%",
            biggest["label"],
            "Die größte Verschiebung diesen Monat, gerundet auf Prozentpunkte.",
        )
    else:
        post.slide_text(
            "DEPOT-UPDATE",
            "Der *erste* Monat in diesem System.",
            "Ab jetzt vergleiche ich jeden Monat automatisch mit dem vorherigen Stand.",
        )

    post.slide_cta(
        "DEPOT-UPDATE",
        "Nächsten Monat *mehr*.",
        "Ich vergleiche dann automatisch mit diesem Stand hier.",
    )

    ig_dir, tt_dir = post.export()
    print("Instagram 4:5:", ig_dir)
    print("TikTok 9:16:", tt_dir)
    print("Kontaktabzug:", ig_dir.parent / "uebersicht.png")

    top = depot["categories_ohne_cash"]
    cash_pct = next((c["percent"] for c in depot["categories_mit_cash"] if c["key"] == "cash"), 0)
    top1, top2, top3 = depot["top_positions"][:3]
    if diffs:
        biggest = max(diffs, key=lambda d: abs(d["delta"]))
        change_sentence = (
            f"Auffaelligste Verschiebung zum Vormonat: {biggest['label']} "
            f"{'plus' if biggest['delta'] > 0 else 'minus'} {abs(biggest['delta'])} Prozentpunkte."
        )
    else:
        change_sentence = "Das ist der erste Monat, den ich so systematisch festhalte."

    sentences = [
        "Mein Depot in Zahlen -- heute zeig ich dir ganz genau, wie's bei mir gerade aussieht, Slide fuer Slide.",
        f"Ohne Cash gerechnet sind {top[0]['percent']}% in {top[0]['label']}, "
        f"der Rest verteilt sich auf {top[1]['label']}, {top[2]['label']} und {top[3]['label']}.",
        f"Rechne ich die Cash-Quote mit rein, liegen gerade {cash_pct}% als Cash da.",
        f"Meine groessten Positionen: {top1['name']}, dann {top2['name']}, dann {top3['name']}.",
        change_sentence,
        "Naechsten Monat zeig ich dir wieder, was sich bei mir veraendert hat -- folg mir gerne, wenn du das mitverfolgen willst.",
    ]
    voiceover.write(post.name, sentences)
    print("Voiceover-Skript:", (Path(__file__).parent.parent / "output" / post.name / "script.md"))

    cover = site_sync.stage_cover(post.name)
    site_sync.add_post(
        post_id=post.name,
        title="Mein Depot in Zahlen",
        category="depot-update",
        date_str=depot["updated"],
        excerpt=f"Allokation diesen Monat: {top[0]['label']} {top[0]['percent']}%, "
                f"{top[1]['label']} {top[1]['percent']}%, {top[2]['label']} {top[2]['percent']}%.",
        cover_relpath=cover,
    )
    print("Website-Eintrag aktualisiert (docs/content/posts.json)")


if __name__ == "__main__":
    main()
