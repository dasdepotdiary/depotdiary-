"""Baut zwei weitere Feed-Posts im format_wochenlogos-Stil (Finanzhafen-
inspiriertes Logo-Raster) als Vorproduktion -- Themen statt Wochenrueckblick:
Tech-Giganten im Vergleich, Dividenden-Aktien im Check. Reine Uebersicht,
keine Bewertung/Empfehlung.

Aufruf:
  python posts/build_finanzhafen_style_extra.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
sys.path.insert(0, str(Path(__file__).parent))
from format_wochenlogos import build

ROOT = Path(__file__).parent.parent


def logo(ticker):
    return ROOT / "assets" / f"{ticker.lower()}_logo_icon.png"


TECH_GIGANTEN = [
    {"name": "Apple", "ticker": "AAPL", "logo_path": logo("aapl")},
    {"name": "Microsoft", "ticker": "MSFT", "logo_path": logo("msft")},
    {"name": "Alphabet", "ticker": "GOOGL", "logo_path": logo("googl")},
    {"name": "Amazon", "ticker": "AMZN", "logo_path": logo("amzn")},
    {"name": "Meta", "ticker": "META", "logo_path": logo("meta")},
    {"name": "Nvidia", "ticker": "NVDA", "logo_path": logo("nvda")},
    {"name": "Adobe", "ticker": "ADBE", "logo_path": logo("adbe")},
    {"name": "ServiceNow", "ticker": "NOW", "logo_path": logo("servicenow")},
    {"name": "Oracle", "ticker": "ORCL", "logo_path": logo("orcl")},
    {"name": "TSMC", "ticker": "TSM", "logo_path": logo("tsmc")},
]

DIVIDENDEN_AKTIEN = [
    {"name": "JPMorgan Chase", "ticker": "JPM", "logo_path": logo("jpm")},
    {"name": "McDonald's", "ticker": "MCD", "logo_path": logo("mcd")},
    {"name": "Coca-Cola", "ticker": "KO", "logo_path": logo("coca_cola")},
    {"name": "Procter & Gamble", "ticker": "PG", "logo_path": logo("pg")},
    {"name": "PepsiCo", "ticker": "PEP", "logo_path": logo("pep")},
    {"name": "Bank of America", "ticker": "BAC", "logo_path": logo("bac")},
    {"name": "RTX", "ticker": "RTX", "logo_path": logo("rtx")},
    {"name": "AT&T", "ticker": "T", "logo_path": logo("t")},
]


def main():
    build(
        "format_sektor_tech",
        "",
        TECH_GIGANTEN,
        hook_label="SEKTOR-CHECK",
        headline_lines=["TECH-GIGANTEN", "IM VERGLEICH."],
        sub_text="10 grosse Tech-Werte, die in vielen Depots stecken -- auf einen Blick.",
        grid_label="DIE AKTIEN",
        cta_question_lines=["WELCHE HAST DU", "SELBST IM DEPOT?"],
        cta_text="Schreib's in die Kommentare.",
    )
    build(
        "format_dividenden_check",
        "",
        DIVIDENDEN_AKTIEN,
        hook_label="PASSIVES EINKOMMEN",
        headline_lines=["DIVIDENDEN-", "AKTIEN."],
        sub_text="Bekannte Dividendenzahler aus verschiedenen Branchen -- auf einen Blick.",
        grid_label="DIE AKTIEN",
        cta_question_lines=["WELCHE DIVIDENDE", "GEFAELLT DIR AM BESTEN?"],
        cta_text="Schreib's in die Kommentare.",
    )


if __name__ == "__main__":
    main()
