"""Konstanten aus CLAUDE.md: Farben, Schriftpfade, Maße."""

from pathlib import Path

ROOT = Path(__file__).parent
FONT_DIR = ROOT / "assets" / "fonts"

# --- Farben ---
BG = "#F2F0EA"
INK = "#16181C"
GREEN = "#1A4D3C"
GREEN_MID = "#4E8C6E"
OCHRE = "#B08A2E"
GREY = "#B7B1A4"
RED = "#C0392B"
SUBTEXT = "#6E6A62"
CARD = "#E7E3D9"
DIVIDER = "#D3CDC0"
BODY_TEXT = "#33352F"

# --- Schriften ---
SERIF_BOLD = str(FONT_DIR / "DejaVuSerif-Bold.ttf")
SERIF_BOLD_ITALIC = str(FONT_DIR / "DejaVuSerif-BoldItalic.ttf")
SERIF_REGULAR = str(FONT_DIR / "DejaVuSerif.ttf")
SANS_BOLD = str(FONT_DIR / "LiberationSans-Bold.ttf")

# --- Maße ---
FEED_SIZE = (1080, 1350)   # 4:5 Feed-Karussell
STORY_SIZE = (1080, 1920)  # 9:16 Story/Reel/TikTok

BAR_WIDTH = 16              # schwarzer Vertikalbalken links
MARGIN_LEFT = BAR_WIDTH + 64
MARGIN_RIGHT = 64
CONTENT_MAX_Y_RATIO = 0.88  # nichts unterhalb von 88% der Höhe

ACCENT_LINE_WIDTH = 200
ACCENT_LINE_HEIGHT = 5

EYEBROW_TRACKING = 5        # Sperrung in px
EYEBROW_SIZE = 26
HEADLINE_SIZE = 64
BODY_SIZE = 34
FOOTER_SIZE = 22
DISCLAIMER_SIZE = 20

WORDMARK = "DEPOT DIARY"
DISCLAIMER = "Keine Anlageberatung. Nur mein eigenes Depot."
