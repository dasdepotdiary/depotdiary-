"""Design-Alternative A fuer "Wochenrueckblick -- Mein Depot" (2026-09-20,
Nutzer-Feedback zur ersten Einzelbild-Version: "Design gefaellt mir gar
nicht... auf mehreren Slides und mach es ein bisschen besser"): mehrseitige
Fassung ueber die bewaehrte render.Post-Engine (gleiche cream/dunkelgruene
Erklaerstueck-Optik wie marktupdate.py/depot_update.py).

Design-Alternative B (Kassenbon-Optik) liegt in
posts/format_wochenrueckblick_depot_kassenbon.py -- beide werden dem Nutzer
als Vorschau geschickt, bevor eine davon gequeued wird.

Aufruf (Prototyp/Test):
  python posts/format_wochenrueckblick_depot_v2.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from render import Post
import brand as B

EYEBROW = "DEPOT-UPDATE"


def main(date_label, performance_pct, buys, sells):
    n = 5
    post = Post("format_wochenrueckblick_depot_v2", total_slides=n)

    post.slide_hook(
        EYEBROW,
        "Mein Depot diese *Woche*.",
        f"Performance, Käufe und Verkäufe -- Stand {date_label}.",
    )

    sign = "+" if performance_pct >= 0 else ""
    post.slide_card(
        EYEBROW,
        "Die Performance dieser *Woche*.",
        f"{sign}{performance_pct}%".replace(".", ","),
        "Veränderung meines Depots",
        "Reine Prozentangabe -- keine Kursziele, keine Bewertung.",
    )

    rows = [(b["label"], b["value"], B.INK) for b in buys]
    post.slide_rows(
        EYEBROW,
        "Meine *Käufe* diese Woche.",
        rows,
        "Preise jeweils zum Kaufzeitpunkt.",
    )

    if sells:
        post.slide_text(EYEBROW, "*Verkäufe* diese Woche.", ", ".join(sells))
    else:
        post.slide_text(EYEBROW, "*Verkäufe*: keine.", "Diese Woche keine Position verkauft.")

    post.slide_cta(
        EYEBROW,
        "Nächste Woche *mehr*.",
        "Ich zeig dir wieder, was sich bei mir getan hat.",
    )

    ig_dir, tt_dir = post.export()
    print("Instagram 4:5:", ig_dir)
    print("Kontaktabzug:", ig_dir.parent / "uebersicht.png")


if __name__ == "__main__":
    buys = [
        {"label": "Sparplan", "value": "regulär"},
        {"label": "Broadcom (AVGO)", "value": "297 USD"},
        {"label": "Vistra (VST)", "value": "301 USD"},
        {"label": "Uber (UBER)*", "value": "400 USD"},
    ]
    main("20.09.2026", 1.61, buys, sells=[])
