"""Rotierender Hashtag-Pool -- 3-5 pro Post statt immer derselben 5, damit der
Account nicht dauerhaft im gleichen kleinen Hashtag-Segment haengt.

Nutzung:
  import hashtags
  tags = hashtags.pick("erklaerstueck")  # oder "marktupdate", "quartalszahlen", "persoenlich"
"""

import random

# Feste Basis -- immer dabei, Markenwiedererkennung
BASE = ["#depotdiary"]

# Themen-Pools, grosszuegig genug fuer Rotation (nicht jedes Mal dieselben)
POOLS = {
    "erklaerstueck": [
        "#finanzbildung", "#boerse", "#investieren", "#geldanlage", "#finanzen",
        "#aktien", "#etf", "#persoenlichefinanzen", "#geldwissen", "#finanztipps",
    ],
    "marktupdate": [
        "#boerse", "#aktienmarkt", "#wirtschaft", "#finanznews", "#quartalszahlen",
        "#markttrends", "#investieren", "#wallstreet", "#finanzen",
    ],
    "quartalszahlen": [
        "#quartalszahlen", "#boerse", "#aktien", "#earnings", "#investieren",
        "#wallstreet", "#finanznews",
    ],
    "persoenlich": [
        "#depot", "#investieren", "#geldanlage", "#finanzjourney", "#sparen",
        "#persoenlichefinanzen", "#geldtagebuch",
    ],
}


def pick(category: str, n: int = 4) -> str:
    """Gibt n zufaellig rotierte Hashtags aus dem passenden Pool zurueck,
    als fertigen String zum Anhaengen an eine Caption (inkl. fester Basis)."""
    pool = POOLS.get(category, POOLS["erklaerstueck"])
    chosen = random.sample(pool, min(n, len(pool)))
    return " ".join(BASE + chosen)
