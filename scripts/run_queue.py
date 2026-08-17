"""Fuehrt faellige Eintraege aus queue/publish_queue.json aus -- laeuft in GitHub Actions,
unabhaengig vom lokalen Rechner. Braucht nur INSTAGRAM_ACCESS_TOKEN,
INSTAGRAM_BUSINESS_ACCOUNT_ID, PUBLIC_BASE_URL als Umgebungsvariablen (GitHub Secrets).

Ein Eintrag wird NUR angefasst, wenn er hier schon fertig vorbereitet und
committed liegt (Bilder/Video schon unter docs/assets/... oeffentlich) --
dieses Skript staged nichts neu, es veroeffentlicht nur, was schon bereit ist.

Queue-Eintrag-Schema (queue/publish_queue.json, Liste von Objekten):
  {
    "post_name": "erklaerstueck_xyz",
    "action": "carousel" | "reel" | "story",
    "caption": "...",              (nicht noetig bei "story")
    "slide_count": 5,               (nur bei "carousel")
    "fire_at": "2026-08-18T20:30:00+02:00",
    "status": "pending" | "done" | "error"
  }

Aufruf (lokal zum Testen, ohne wirklich zu posten):
  python scripts/run_queue.py --dry-run
Aufruf (wie in der Action, postet wirklich faellige Eintraege):
  python scripts/run_queue.py
"""

import argparse
import json
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import requests

ROOT = Path(__file__).parent.parent
QUEUE_PATH = ROOT / "queue" / "publish_queue.json"
GRAPH_VERSION = "v21.0"
GRAPH_URL = f"https://graph.facebook.com/{GRAPH_VERSION}"


def get_config():
    token = os.environ.get("INSTAGRAM_ACCESS_TOKEN")
    ig_id = os.environ.get("INSTAGRAM_BUSINESS_ACCOUNT_ID")
    base_url = os.environ.get("PUBLIC_BASE_URL")
    missing = [n for n, v in [("INSTAGRAM_ACCESS_TOKEN", token), ("INSTAGRAM_BUSINESS_ACCOUNT_ID", ig_id), ("PUBLIC_BASE_URL", base_url)] if not v]
    if missing:
        sys.exit(f"Fehlt als Umgebungsvariable: {', '.join(missing)}")
    return token, ig_id, base_url.rstrip("/")


def load_queue():
    if not QUEUE_PATH.exists():
        return []
    return json.loads(QUEUE_PATH.read_text(encoding="utf-8"))


def save_queue(queue):
    QUEUE_PATH.write_text(json.dumps(queue, ensure_ascii=False, indent=2), encoding="utf-8")


def is_due(entry) -> bool:
    if entry.get("status") != "pending":
        return False
    fire_at = datetime.fromisoformat(entry["fire_at"])
    return datetime.now(timezone.utc) >= fire_at.astimezone(timezone.utc)


def publish_carousel(token, ig_id, base_url, entry) -> dict:
    name = entry["post_name"]
    children_ids = []
    for i in range(1, entry["slide_count"] + 1):
        image_url = f"{base_url}/assets/posts/{name}/slide_{i}.png"
        resp = requests.post(f"{GRAPH_URL}/{ig_id}/media", data={
            "image_url": image_url, "is_carousel_item": "true", "access_token": token,
        })
        resp.raise_for_status()
        children_ids.append(resp.json()["id"])
        time.sleep(1)
    resp = requests.post(f"{GRAPH_URL}/{ig_id}/media", data={
        "media_type": "CAROUSEL", "children": ",".join(children_ids),
        "caption": entry.get("caption", ""), "access_token": token,
    })
    resp.raise_for_status()
    creation_id = resp.json()["id"]
    resp = requests.post(f"{GRAPH_URL}/{ig_id}/media_publish", data={
        "creation_id": creation_id, "access_token": token,
    })
    resp.raise_for_status()
    return resp.json()


def publish_reel(token, ig_id, base_url, entry) -> dict:
    name = entry["post_name"]
    video_url = f"{base_url}/assets/posts_video/{name}/reel.mp4"
    resp = requests.post(f"{GRAPH_URL}/{ig_id}/media", data={
        "media_type": "REELS", "video_url": video_url,
        "caption": entry.get("caption", ""), "access_token": token,
    })
    resp.raise_for_status()
    container_id = resp.json()["id"]

    start = time.time()
    while time.time() - start < 180:
        resp = requests.get(f"{GRAPH_URL}/{container_id}", params={
            "fields": "status_code", "access_token": token,
        })
        status = resp.json().get("status_code")
        if status == "FINISHED":
            break
        if status == "ERROR":
            raise RuntimeError(f"Meta-Verarbeitung fehlgeschlagen: {resp.json()}")
        time.sleep(8)
    else:
        raise RuntimeError("Timeout bei Video-Verarbeitung")

    resp = requests.post(f"{GRAPH_URL}/{ig_id}/media_publish", data={
        "creation_id": container_id, "access_token": token,
    })
    resp.raise_for_status()
    return resp.json()


def publish_story(token, ig_id, base_url, entry) -> dict:
    name = entry["post_name"]
    image_url = f"{base_url}/assets/posts_9x16/{name}/slide_1.png"
    last_error = None
    for attempt in range(4):
        resp = requests.post(f"{GRAPH_URL}/{ig_id}/media", data={
            "image_url": image_url, "media_type": "STORIES", "access_token": token,
        })
        if resp.ok:
            container_id = resp.json()["id"]
            resp2 = requests.post(f"{GRAPH_URL}/{ig_id}/media_publish", data={
                "creation_id": container_id, "access_token": token,
            })
            resp2.raise_for_status()
            return resp2.json()
        last_error = resp.text
        time.sleep(30)
    raise RuntimeError(f"Story-Publish nach 4 Versuchen fehlgeschlagen: {last_error}")


DISPATCH = {"carousel": publish_carousel, "reel": publish_reel, "story": publish_story}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true", help="Zeigt faellige Eintraege, postet nichts wirklich")
    args = parser.parse_args()

    token, ig_id, base_url = get_config()
    queue = load_queue()
    due = [e for e in queue if is_due(e)]

    if not due:
        print("Nichts faellig.")
        return

    for entry in due:
        print(f"Faellig: {entry['post_name']} ({entry['action']})")
        if args.dry_run:
            continue
        try:
            result = DISPATCH[entry["action"]](token, ig_id, base_url, entry)
            entry["status"] = "done"
            entry["published_at"] = datetime.now(timezone.utc).isoformat()
            entry["media_id"] = result.get("id")
            print(f"  Veroeffentlicht: {result}")
        except Exception as exc:
            entry["status"] = "error"
            entry["error"] = str(exc)
            print(f"  FEHLER: {exc}")

    if not args.dry_run:
        save_queue(queue)


if __name__ == "__main__":
    main()
