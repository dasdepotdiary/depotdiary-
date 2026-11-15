"""Finanzhafen-Stil-Carousel "Chip-Woche": Logo-Raster mit echten Wochen-Prozenten
(Schlusskurs Fr 13.11. vs. Fr 6.11., Yahoo-Chart-Daten). Rein beschreibend."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from format_wochenlogos import build
ROOT = Path(__file__).parent.parent
GREEN, RED = "#5FD9A6", "#FF6B6B"
data = [("AMD","AMD",18.9),("Broadcom","AVGO",18.2),("Micron","MU",12.8),("Applied Materials","AMAT",11.4),
        ("TSMC","TSM",6.2),("Intel","INTC",6.0),("ASML","ASML",4.9),("Qualcomm","QCOM",4.3),("Nvidia","NVDA",-12.7)]
stocks = [{"name": n, "ticker": t, "logo_path": ROOT/"assets"/f"{t.lower()}_logo_icon.png",
           "sub": f"{v:+.1f} %".replace(".", ","), "sub_color": GREEN if v >= 0 else RED} for n, t, v in data]
build("format_chipwoche", "", stocks, hook_label="CHIP-WOCHE",
      headline_lines=["8 VON 9 CHIPWERTEN", "IM PLUS."],
      sub_text="Wochenveraenderung 6.-13.11. -- nur Nvidia fiel, nach dem Ruecktritt von CEO Jensen Huang.",
      grid_label="DIE WOCHENBILANZ", cta_question_lines=["WELCHEN CHIPWERT", "HAST DU IM BLICK?"])
