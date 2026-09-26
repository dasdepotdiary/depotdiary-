"""Zwei weitere Feed-Posts im format_wochenlogos-Stil (Finanzhafen-
inspiriertes Logo-Raster, Foto-Titelfolie): KI-Infrastruktur, E-Commerce &
Zahlungen. Reine Uebersicht, keine Bewertung/Empfehlung. Wie die anderen
Themen dieser Familie NUR gebaut+gestaged, nicht automatisch gequeued.

Aufruf:
  python posts/build_finanzhafen_style_extra2.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
sys.path.insert(0, str(Path(__file__).parent))
from format_wochenlogos import build

ROOT = Path(__file__).parent.parent


def logo(ticker):
    return ROOT / "assets" / f"{ticker.lower()}_logo_icon.png"


KI_INFRASTRUKTUR = [
    {"name": "Nvidia", "ticker": "NVDA", "logo_path": logo("nvda")},
    {"name": "TSMC", "ticker": "TSM", "logo_path": logo("tsmc")},
    {"name": "ASML", "ticker": "ASML", "logo_path": logo("asml")},
    {"name": "Broadcom", "ticker": "AVGO", "logo_path": logo("avgo")},
    {"name": "Micron", "ticker": "MU", "logo_path": logo("mu")},
    {"name": "Intel", "ticker": "INTC", "logo_path": logo("intc")},
    {"name": "CoreWeave", "ticker": "CRWV", "logo_path": logo("coreweave")},
    {"name": "Oracle", "ticker": "ORCL", "logo_path": logo("orcl")},
    {"name": "ServiceNow", "ticker": "NOW", "logo_path": logo("servicenow")},
]

ECOMMERCE_ZAHLUNGEN = [
    {"name": "Amazon", "ticker": "AMZN", "logo_path": logo("amzn")},
    {"name": "MercadoLibre", "ticker": "MELI", "logo_path": logo("mercadolibre")},
    {"name": "PayPal", "ticker": "PYPL", "logo_path": logo("pypl")},
    {"name": "Visa", "ticker": "V", "logo_path": logo("v")},
    {"name": "Uber", "ticker": "UBER", "logo_path": logo("uber")},
    {"name": "Costco", "ticker": "COST", "logo_path": logo("cost")},
    {"name": "Home Depot", "ticker": "HD", "logo_path": logo("hd")},
]


def main():
    build(
        "format_ki_infrastruktur",
        "",
        KI_INFRASTRUKTUR,
        hook_label="SEKTOR-CHECK",
        headline_lines=["KI-INFRASTRUKTUR", "IM CHECK."],
        sub_text=f"{len(KI_INFRASTRUKTUR)} Werte, die vom KI-Rechenzentrums-Boom profitieren -- auf einen Blick.",
        grid_label="DIE AKTIEN",
        cta_question_lines=["WELCHE HAST DU", "SELBST IM DEPOT?"],
    )
    build(
        "format_ecommerce_zahlungen",
        "",
        ECOMMERCE_ZAHLUNGEN,
        hook_label="SEKTOR-CHECK",
        headline_lines=["E-COMMERCE &", "ZAHLUNGEN."],
        sub_text=f"{len(ECOMMERCE_ZAHLUNGEN)} Werte aus Online-Handel und digitalen Zahlungen -- auf einen Blick.",
        grid_label="DIE AKTIEN",
        cta_question_lines=["WELCHE HAST DU", "SELBST IM DEPOT?"],
    )


if __name__ == "__main__":
    main()
