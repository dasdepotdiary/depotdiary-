"""Zwei weitere Feed-Posts im Finanzhafen-Stil (Logo-Raster, Foto-Titelfolie):
Software & Cloud, Medien & Streaming. Nur bauen+stagen, NICHT automatisch queuen.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
sys.path.insert(0, str(Path(__file__).parent))
from format_wochenlogos import build

ROOT = Path(__file__).parent.parent


def logo(t):
    return ROOT / "assets" / f"{t}_logo_icon.png"


SOFTWARE = [
    {"name": "Microsoft", "ticker": "MSFT", "logo_path": logo("msft")},
    {"name": "Oracle", "ticker": "ORCL", "logo_path": logo("orcl")},
    {"name": "Adobe", "ticker": "ADBE", "logo_path": logo("adbe")},
    {"name": "SAP", "ticker": "SAP", "logo_path": logo("sap")},
    {"name": "ServiceNow", "ticker": "NOW", "logo_path": logo("servicenow")},
    {"name": "Palantir", "ticker": "PLTR", "logo_path": logo("pltr")},
    {"name": "Zeta Global", "ticker": "ZETA", "logo_path": logo("zeta")},
    {"name": "Alphabet", "ticker": "GOOGL", "logo_path": logo("googl")},
]

MEDIEN = [
    {"name": "Netflix", "ticker": "NFLX", "logo_path": logo("nflx")},
    {"name": "Warner Bros. Discovery", "ticker": "WBD", "logo_path": logo("wbd")},
    {"name": "AT&T", "ticker": "T", "logo_path": logo("t")},
    {"name": "Meta", "ticker": "META", "logo_path": logo("meta")},
    {"name": "Alphabet", "ticker": "GOOGL", "logo_path": logo("googl")},
    {"name": "Amazon", "ticker": "AMZN", "logo_path": logo("amzn")},
]


def main():
    build("format_software_cloud", "", SOFTWARE, hook_label="SEKTOR-CHECK",
          headline_lines=["SOFTWARE &", "CLOUD."],
          sub_text=f"{len(SOFTWARE)} Werte aus Software und Cloud -- auf einen Blick.",
          grid_label="DIE AKTIEN", cta_question_lines=["WELCHE HAST DU", "SELBST IM DEPOT?"])
    build("format_medien_streaming", "", MEDIEN, hook_label="SEKTOR-CHECK",
          headline_lines=["MEDIEN &", "STREAMING."],
          sub_text=f"{len(MEDIEN)} Werte aus Streaming, Werbung und Telekom -- auf einen Blick.",
          grid_label="DIE AKTIEN", cta_question_lines=["WELCHE HAST DU", "SELBST IM DEPOT?"])


if __name__ == "__main__":
    main()
