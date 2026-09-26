"""Baut zwei weitere Feed-Posts im format_wochenlogos-Stil (Finanzhafen-
inspiriertes Logo-Raster) als Vorproduktion -- Themen statt Wochenrueckblick:
Tech-Giganten im Vergleich, Dividenden-Aktien im Check. Reine Uebersicht,
keine Bewertung/Empfehlung.

v2 (2026-09-26, Nutzer-Feedback: "mehr Tech-Titel und kurze Infos, moderner"):
Tech-Liste auf 15 Titel erweitert, layout="info_rows" (Logo+Name+1-Zeile-Fakt
statt reiner Logo-Kreise) fuer mehr Kontext pro Aktie.

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
    {"name": "Apple", "ticker": "AAPL", "logo_path": logo("aapl"),
     "info": "iPhone, Mac, Services -- nach Marktkap. einer der groessten Konzerne der Welt."},
    {"name": "Microsoft", "ticker": "MSFT", "logo_path": logo("msft"),
     "info": "Windows, Office, Azure-Cloud -- einer der grossen Cloud-Anbieter."},
    {"name": "Alphabet", "ticker": "GOOGL", "logo_path": logo("googl"),
     "info": "Google-Mutterkonzern: Suche, YouTube, Google Cloud."},
    {"name": "Amazon", "ticker": "AMZN", "logo_path": logo("amzn"),
     "info": "E-Commerce weltweit + AWS, einer der groessten Cloud-Anbieter."},
    {"name": "Meta", "ticker": "META", "logo_path": logo("meta"),
     "info": "Facebook, Instagram, WhatsApp -- Werbeerloese als Haupteinnahmequelle."},
    {"name": "Nvidia", "ticker": "NVDA", "logo_path": logo("nvda"),
     "info": "Grafikchips (GPUs), stark nachgefragt fuer KI-Rechenzentren."},
    {"name": "Adobe", "ticker": "ADBE", "logo_path": logo("adbe"),
     "info": "Kreativ-Software wie Photoshop, ueber Creative-Cloud-Abo vertrieben."},
    {"name": "ServiceNow", "ticker": "NOW", "logo_path": logo("servicenow"),
     "info": "Cloud-Software fuer Workflows und IT-Prozesse in Unternehmen."},
    {"name": "Oracle", "ticker": "ORCL", "logo_path": logo("orcl"),
     "info": "Datenbanken und zunehmend auch Cloud-Infrastruktur."},
    {"name": "TSMC", "ticker": "TSM", "logo_path": logo("tsmc"),
     "info": "Groesster Chip-Auftragsfertiger weltweit, u.a. fuer Apple und Nvidia."},
    {"name": "Netflix", "ticker": "NFLX", "logo_path": logo("nflx"),
     "info": "Groesster Streaming-Anbieter nach Abonnentenzahl."},
    {"name": "Palantir", "ticker": "PLTR", "logo_path": logo("pltr"),
     "info": "Datenanalyse-Software fuer Behoerden und Unternehmen."},
    {"name": "Micron", "ticker": "MU", "logo_path": logo("mu"),
     "info": "Speicherchips (DRAM/NAND) fuer Computer und Server."},
    {"name": "Uber", "ticker": "UBER", "logo_path": logo("uber"),
     "info": "Fahrdienst- und Lieferplattform, in vielen Laendern aktiv."},
    {"name": "CoreWeave", "ticker": "CRWV", "logo_path": logo("coreweave"),
     "info": "Cloud-Infrastruktur spezialisiert auf KI-Rechenleistung."},
]

DIVIDENDEN_AKTIEN = [
    {"name": "JPMorgan Chase", "ticker": "JPM", "logo_path": logo("jpm"),
     "info": "Groesste US-Bank nach Bilanzsumme, zahlt seit Jahrzehnten Dividende."},
    {"name": "McDonald's", "ticker": "MCD", "logo_path": logo("mcd"),
     "info": "Groesste Fast-Food-Kette der Welt, seit ueber 45 Jahren steigende Dividende."},
    {"name": "Coca-Cola", "ticker": "KO", "logo_path": logo("coca_cola"),
     "info": "Getraenkekonzern, gilt als klassischer 'Dividendenaristokrat'."},
    {"name": "Procter & Gamble", "ticker": "PG", "logo_path": logo("pg"),
     "info": "Konsumguetermarken wie Gillette, Pampers -- ebenfalls Dividendenaristokrat."},
    {"name": "PepsiCo", "ticker": "PEP", "logo_path": logo("pep"),
     "info": "Getraenke und Snacks (u.a. Lays, Doritos), lange Dividendenhistorie."},
    {"name": "Bank of America", "ticker": "BAC", "logo_path": logo("bac"),
     "info": "Eine der groessten US-Banken nach Kundenzahl."},
    {"name": "RTX", "ticker": "RTX", "logo_path": logo("rtx"),
     "info": "Luft- und Raumfahrt sowie Ruestungstechnik (u.a. Raytheon, Collins)."},
    {"name": "AT&T", "ticker": "T", "logo_path": logo("t"),
     "info": "US-Telekomkonzern, bekannt fuer hohe Dividendenrendite."},
]


def main():
    build(
        "format_sektor_tech",
        "",
        TECH_GIGANTEN,
        hook_label="SEKTOR-CHECK",
        headline_lines=["TECH-GIGANTEN", "IM VERGLEICH."],
        sub_text="15 grosse Tech-Werte, die in vielen Depots stecken -- auf einen Blick.",
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
