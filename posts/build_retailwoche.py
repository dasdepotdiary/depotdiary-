"""Finanzhafen-Stil-Carousel "Retail-Woche": Logo-Raster mit Berichtstag + Konsens-EPS
(Nasdaq-Terminkalender). Rein beschreibend, keine Bewertung."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from format_wochenlogos import build
ROOT = Path(__file__).parent.parent
data = [("Home Depot","HD","Di","3,87"),("JD.com","JD","Di","0,88"),("Lowe's","LOW","Mi","2,86"),("Target","TGT","Mi","2,03"),
        ("TJX","TJX","Mi","1,33"),("Walmart","WMT","Do","0,64"),("Alibaba","BABA","Do","1,56"),("Ross Stores","ROST","Do","1,82")]
stocks = [{"name": n, "ticker": t, "logo_path": ROOT/"assets"/f"{t.lower()}_logo_icon.png",
           "sub": f"{d} · {e} $", "sub_color": "#F5F3EE"} for n, t, d, e in data]
build("format_retailwoche", "", stocks, hook_label="RETAIL-WOCHE",
      headline_lines=["8 HAENDLER", "BERICHTEN."],
      sub_text="Wer diese Woche Quartalszahlen vorlegt -- mit Berichtstag und Konsens-EPS.",
      grid_label="DIE TERMINE", cta_question_lines=["WELCHEN HAENDLER", "HAST DU IM DEPOT?"])
