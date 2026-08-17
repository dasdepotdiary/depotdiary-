"""Postet das fertige Reel-Video (mit echtem Voiceover) als Instagram Reel.

Anders als Carousel/Story braucht ein Video einen Verarbeitungsschritt bei Meta
(status_code muss auf FINISHED wechseln), bevor media_publish funktioniert.

Aufruf:
  python scripts/publish_instagram_reel.py erklaerstueck_ki-blase --caption "..."          (Trockenlauf)
  python scripts/publish_instagram_reel.py erklaerstueck_ki-blase --caption "..." --live   (wirklich veroeffentlichen)
"""

import argparse
import json
import os
import sys
import time
from datetime import datetime
from pathlib import Path

import requests
from dotenv import load_dotenv

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))
load_dotenv(ROOT / ".env")

import site_sync

GRAPH_VERSION = "v21.0"
GRAPH_URL = f"https://graph.facebook.com/{GRAPH_VERSION}"


def get_config():
    token = os.environ.get("INSTAGRAM_ACCESS_TOKEN")
    ig_id = os.environ.get("INSTAGRAM_BUSINESS_ACCOUNT_ID")
    base_url = os.environ.get("PUBLIC_BASE_URL")
    missing = [n for n, v in [("INSTAGRAM_ACCESS_TOKEN", token), ("INSTAGRAM_BUSINESS_ACCOUNT_ID", ig_id), ("PUBLIC_BASE_URL", base_url)] if not v]
    if missing:
        sys.exit(f"Fehlt in .env: {', '.join(missing)}")
    return token, ig_id, base_url.rstrip("/")


def create_reel_container(token: str, ig_id: str, video_url: str, caption: str) -> str:
    resp = requests.post(f"{GRAPH_URL}/{ig_id}/media", data={
        "media_type": "REELS",
        "video_url": video_url,
        "caption": caption,
        "access_token": token,
    })
    if not resp.ok:
        sys.exit(f"Fehler beim Reel-Container: {resp.status_code} {resp.text}")
    return resp.json()["id"]


def wait_until_finished(token: str, container_id: str, timeout_s: int = 180) -> None:
    start = time.time()
    while time.time() - start < timeout_s:
        resp = requests.get(f"{GRAPH_URL}/{container_id}", params={
            "fields": "status_code,status",
            "access_token": token,
        })
        data = resp.json()
        status = data.get("status_code")
        print(f"  Status: {status}")
        if status == "FINISHED":
            return
        if status == "ERROR":
            sys.exit(f"Meta-Verarbeitung fehlgeschlagen: {data}")
        time.sleep(8)
    sys.exit("Timeout: Video wurde nicht rechtzeitig fertig verarbeitet.")


def publish_container(token: str, ig_id: str, creation_id: str) -> dict:
    resp = requests.post(f"{GRAPH_URL}/{ig_id}/media_publish", data={
        "creation_id": creation_id,
        "access_token": token,
    })
    if not resp.ok:
        sys.exit(f"Fehler beim Veroeffentlichen: {resp.status_code} {resp.text}")
    return resp.json()


def log_result(entry: dict):
    log_path = ROOT / "data" / "published_log.json"
    log_path.parent.mkdir(exist_ok=True)
    log = json.loads(log_path.read_text(encoding="utf-8")) if log_path.exists() else []
    log.append(entry)
    log_path.write_text(json.dumps(log, ensure_ascii=False, indent=2), encoding="utf-8")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("post_name")
    parser.add_argument("--caption", required=True)
    parser.add_argument("--live", action="store_true")
    args = parser.parse_args()

    token, ig_id, base_url = get_config()

    video_relpath = site_sync.stage_video(args.post_name)
    video_url = f"{base_url}/{video_relpath}"
    print(f"{'LIVE' if args.live else 'TROCKENLAUF'} -- Reel fuer '{args.post_name}'")
    print(f"  Video-URL: {video_url}")

    container_id = create_reel_container(token, ig_id, video_url, args.caption)
    print(f"  Container erzeugt: {container_id}")
    print("  Warte auf Meta-Verarbeitung ...")
    wait_until_finished(token, container_id)

    result = {
        "post_name": args.post_name, "type": "reel",
        "timestamp": datetime.now().isoformat(),
        "container_id": container_id, "live": args.live, "published": False,
    }

    if args.live:
        publish_result = publish_container(token, ig_id, container_id)
        result["published"] = True
        result["media_id"] = publish_result.get("id")
        print(f"  Veroeffentlicht: {publish_result}")
    else:
        print("  Trockenlauf abgeschlossen -- mit --live wirklich posten.")

    log_result(result)
    print("\nProtokolliert in data/published_log.json")


if __name__ == "__main__":
    main()
