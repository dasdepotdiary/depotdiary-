"""Beispielpost zum Testen der Render-Engine (Bootstrap-Check, Prompt 1)."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from render import Post
import brand as B

post = Post("beispiel", total_slides=6)

post.slide_hook(
    "ERKLAERSTUECK",
    "Was eine *Position* im Depot wirklich bedeutet.",
    "Eine kurze Einordnung, bevor wir ins Detail gehen.",
)

post.slide_text(
    "ERKLAERSTUECK",
    "Eine Position ist einfach ein *gehaltener* Posten.",
    "Wenn ich zehn Anteile eines ETFs halte, ist das eine Position. "
    "Der Wert schwankt mit dem Kurs, die Stueckzahl bleibt gleich, "
    "solange ich nicht kaufe oder verkaufe.",
)

post.slide_rows(
    "DEPOT-UPDATE",
    "Meine *Allokation* diesen Monat.",
    [
        ("Einzelaktien", "42%", B.INK),
        ("ETFs & Fonds", "31%", B.INK),
        ("Bitcoin & BTC-Treasuries", "18%", B.GREEN),
        ("Gold & Silber", "9%", B.OCHRE),
    ],
    "Ohne Cash gerechnet, gerundet auf ganze Prozent.",
)

post.slide_card(
    "DEPOT-UPDATE",
    "Veraenderung zum *Vormonat*.",
    "+3%",
    "Aktienquote gestiegen",
    "Kein Verkauf, nur ein neuer Kauf hat die Gewichtung verschoben.",
)

post.slide_text(
    "FEHLER",
    "Was ich *falsch* eingeschaetzt habe.",
    "Ich bin zu frueh in eine Position eingestiegen, ohne auf die "
    "Bewertung zu schauen. Das war ein Lerngeld, kein Drama.",
)

post.slide_cta(
    "ERKLAERSTUECK",
    "Naechste *Woche* mehr davon.",
    "Wenn du das nachvollziehen willst, bleib dran.",
)

ig_dir, tt_dir = post.export()
print("Instagram 4:5:", ig_dir)
print("TikTok 9:16:", tt_dir)
print("Kontaktabzug:", ig_dir.parent / "uebersicht.png")
