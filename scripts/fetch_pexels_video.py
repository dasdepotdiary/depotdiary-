"""Sucht und laedt ein passendes Hintergrundvideo von Pexels (kostenlos, mit Attribution
laut Pexels-Lizenz nicht verpflichtend, aber fair).

Aufruf:
  python scripts/fetch_pexels_video.py "server room data center" output/marktupdate_speicherchips/pexels_bg.mp4
"""

import os
import sys
from pathlib import Path

import requests
from dotenv import load_dotenv

ROOT = Path(__file__).parent.parent
load_dotenv(ROOT / ".env")

API_KEY = os.environ.get("PEXELS_API_KEY")


def search(query: str, per_page: int = 5) -> list[dict]:
    resp = requests.get(
        "https://api.pexels.com/videos/search",
        params={"query": query, "per_page": per_page, "orientation": "portrait"},
        headers={"Authorization": API_KEY},
    )
    resp.raise_for_status()
    return resp.json().get("videos", [])


def best_vertical_file(video: dict) -> dict | None:
    files = [f for f in video["video_files"] if f["width"] and f["height"] and f["height"] > f["width"]]
    if not files:
        return None
    files.sort(key=lambda f: abs(f["height"] - 1920))
    return files[0]


def main():
    if len(sys.argv) != 3:
        sys.exit('Aufruf: python scripts/fetch_pexels_video.py "such begriff" ausgabe.mp4')
    if not API_KEY:
        sys.exit("PEXELS_API_KEY fehlt in .env")

    query, out_path = sys.argv[1], Path(sys.argv[2])
    results = search(query)
    if not results:
        sys.exit(f"Keine Ergebnisse fuer '{query}'")

    video = results[0]
    file = best_vertical_file(video)
    if not file:
        sys.exit("Kein vertikales Format gefunden")

    out_path.parent.mkdir(parents=True, exist_ok=True)
    r = requests.get(file["link"], stream=True)
    r.raise_for_status()
    with open(out_path, "wb") as f:
        for chunk in r.iter_content(chunk_size=8192):
            f.write(chunk)

    print(f"Video gespeichert: {out_path} ({file['width']}x{file['height']}, Quelle: {video['url']})")


if __name__ == "__main__":
    main()
