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
import socket
import subprocess
import sys
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path

import requests

ROOT = Path(__file__).parent.parent

try:
    from dotenv import load_dotenv
    load_dotenv(ROOT / ".env")
except ImportError:
    pass  # in GitHub Actions: env vars come from secrets, no .env/dotenv needed
QUEUE_PATH = ROOT / "queue" / "publish_queue.json"
GRAPH_VERSION = "v21.0"
GRAPH_URL = f"https://graph.facebook.com/{GRAPH_VERSION}"

RUN_ID = f"{socket.gethostname()}-{os.getpid()}-{uuid.uuid4().hex[:8]}"
STALE_CLAIM_SECONDS = 900  # haengengebliebener Claim (Absturz/Timeout) wird nach 15 Min wieder freigegeben


def _graph_post(url, data, attempts=4, backoff=30):
    """POST mit Retry+Backoff -- gilt fuer Media-Erstellung UND media_publish gleichermassen.
    War vorher nur um die Erstellung gebaut; media_publish schlug am 2026-08-31 und 2026-09-01
    je einmal mit einem 400er fehl (vermutlich kurzes Story-API-Rate-Limit) und brach die
    jeweilige Aktion sofort ohne Retry ab -- deshalb hier fuer beide Schritte einheitlich."""
    last_error = None
    for attempt in range(attempts):
        resp = requests.post(url, data=data)
        if resp.ok:
            return resp
        last_error = resp.text
        if attempt < attempts - 1:
            time.sleep(backoff)
    raise RuntimeError(f"POST {url} nach {attempts} Versuchen fehlgeschlagen: {last_error}")


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


def entry_key(entry):
    """Identifiziert einen Queue-Eintrag ueber Lauf-Grenzen hinweg (keine echte ID im Schema)."""
    return (entry.get("post_name"), entry.get("action"), entry.get("fire_at"))


def find_entry(queue, key):
    for e in queue:
        if entry_key(e) == key:
            return e
    return None


def is_due(entry, now=None) -> bool:
    now = now or datetime.now(timezone.utc)
    status = entry.get("status")
    if status == "claiming":
        claimed_at = entry.get("claimed_at")
        if not claimed_at:
            return False
        claimed_dt = datetime.fromisoformat(claimed_at).astimezone(timezone.utc)
        if (now - claimed_dt).total_seconds() < STALE_CLAIM_SECONDS:
            return False  # noch von einem laufenden Prozess beansprucht
        # verwaister Claim (Absturz/Timeout) -- wieder freigeben, unten neu beanspruchbar
    elif status != "pending":
        return False
    fire_at = datetime.fromisoformat(entry["fire_at"])
    return now >= fire_at.astimezone(timezone.utc)


def publish_carousel(token, ig_id, base_url, entry) -> dict:
    name = entry["post_name"]
    children_ids = []
    for i in range(1, entry["slide_count"] + 1):
        image_url = f"{base_url}/assets/posts/{name}/slide_{i}.png?v={int(time.time())}"
        resp = _graph_post(f"{GRAPH_URL}/{ig_id}/media", {
            "image_url": image_url, "is_carousel_item": "true", "access_token": token,
        })
        children_ids.append(resp.json()["id"])
        time.sleep(1)
    resp = _graph_post(f"{GRAPH_URL}/{ig_id}/media", {
        "media_type": "CAROUSEL", "children": ",".join(children_ids),
        "caption": entry.get("caption", ""), "access_token": token,
    })
    creation_id = resp.json()["id"]
    resp = _graph_post(f"{GRAPH_URL}/{ig_id}/media_publish", {
        "creation_id": creation_id, "access_token": token,
    })
    return resp.json()


def publish_reel(token, ig_id, base_url, entry) -> dict:
    name = entry["post_name"]
    video_url = f"{base_url}/assets/posts_video/{name}/reel.mp4"
    resp = _graph_post(f"{GRAPH_URL}/{ig_id}/media", {
        "media_type": "REELS", "video_url": video_url,
        "caption": entry.get("caption", ""), "access_token": token,
    })
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

    resp = _graph_post(f"{GRAPH_URL}/{ig_id}/media_publish", {
        "creation_id": container_id, "access_token": token,
    })
    return resp.json()


def publish_story(token, ig_id, base_url, entry) -> dict:
    name = entry["post_name"]
    story_dir = ROOT / "docs" / "assets" / "posts_9x16" / name
    filename = "story_announcement.png" if (story_dir / "story_announcement.png").exists() else "slide_1.png"
    image_url = f"{base_url}/assets/posts_9x16/{name}/{filename}?v={int(time.time())}"
    resp = _graph_post(f"{GRAPH_URL}/{ig_id}/media", {
        "image_url": image_url, "media_type": "STORIES", "access_token": token,
    })
    container_id = resp.json()["id"]
    resp = _graph_post(f"{GRAPH_URL}/{ig_id}/media_publish", {
        "creation_id": container_id, "access_token": token,
    })
    return resp.json()


def publish_story_sequence(token, ig_id, base_url, entry) -> dict:
    name = entry["post_name"]
    story_dir = ROOT / "docs" / "assets" / "posts_9x16" / name
    slides = sorted(story_dir.glob("slide_*.png"), key=lambda p: int(p.stem.split("_")[1]))
    if not slides:
        raise RuntimeError(f"Keine Slides gefunden in {story_dir}")
    media_ids = []
    for i, slide in enumerate(slides, 1):
        image_url = f"{base_url}/assets/posts_9x16/{name}/{slide.name}?v={int(time.time())}"
        try:
            resp = _graph_post(f"{GRAPH_URL}/{ig_id}/media", {
                "image_url": image_url, "media_type": "STORIES", "access_token": token,
            })
            container_id = resp.json()["id"]
            resp2 = _graph_post(f"{GRAPH_URL}/{ig_id}/media_publish", {
                "creation_id": container_id, "access_token": token,
            })
            media_ids.append(resp2.json()["id"])
        except Exception as exc:
            raise RuntimeError(
                f"Folie {i}/{len(slides)} fehlgeschlagen, bereits veroeffentlicht: {media_ids}: {exc}"
            ) from exc
        if i < len(slides):
            time.sleep(2)
    return {"id": media_ids[0], "media_ids": media_ids}


DISPATCH = {
    "carousel": publish_carousel, "reel": publish_reel, "story": publish_story,
    "story_sequence": publish_story_sequence,
}


def sync_from_remote():
    """Holt den aktuellen Stand von origin, BEVOR die Queue gelesen wird --
    verhindert, dass ein lokaler manueller Lauf einen Eintrag doppelt
    veroeffentlicht, den die GitHub-Actions-Cron zwischen 'pending pruefen'
    und 'wirklich posten' bereits erledigt hat (echte Race Condition,
    schon zweimal passiert). In CI ist der Checkout eh schon frisch,
    dort ist das ein no-op."""
    try:
        subprocess.run(
            ["git", "pull", "--rebase", "--autostash", "origin", "main"],
            cwd=ROOT, capture_output=True, text=True, timeout=30, check=False,
        )
    except Exception:
        pass  # kein Git verfuegbar o.ae. -- mit dem lokalen Stand weitermachen


def _run_git(args, timeout=30):
    return subprocess.run(["git", *args], cwd=ROOT, capture_output=True, text=True, timeout=timeout)


def _repo_is_clean_except_queue() -> bool:
    """Nur wenn sonst nichts Unbezogenes im Arbeitsbaum steht, machen wir automatisch
    Commits/Pushes fuer die Queue-Datei -- sonst wuerden wir unabhaengige, noch nicht
    committete Arbeit des Nutzers mit reinziehen."""
    status = _run_git(["status", "--porcelain"])
    dirty_other = [l for l in status.stdout.splitlines() if l.strip() and "publish_queue.json" not in l]
    return not dirty_other


def _git_commit_and_push(message, retries=3) -> bool:
    """Committet & pusht die aktuelle queue/publish_queue.json. Bei Push-Konflikt (ein
    anderer Lauf -- lokal oder Cron -- war schneller) wird per rebase integriert und
    erneut versucht; bei echtem inhaltlichen Konflikt auf DIESER Datei (beide Seiten haben
    denselben Eintrag angefasst) wird abgebrochen statt automatisch 'geloest' -- der
    Aufrufer muss dann den Fernstand neu laden und pruefen, ob er das Rennen verloren hat.
    Genau diese fehlende Sperre hat am 2026-09-06 zu einem doppelt veroeffentlichten Reel
    gefuehrt (lokaler Re-Upload-Lauf + GitHub-Actions-Cron haben denselben pending-Eintrag
    fast zeitgleich abgefeuert)."""
    _run_git(["add", str(QUEUE_PATH)])
    diff = _run_git(["diff", "--cached", "--quiet", "--", str(QUEUE_PATH)])
    if diff.returncode == 0:
        return True  # nichts zu committen
    commit = _run_git(["commit", "-m", message])
    if commit.returncode != 0:
        return False
    for _ in range(retries):
        push = _run_git(["push", "origin", "main"])
        if push.returncode == 0:
            return True
        pull = _run_git(["pull", "--rebase", "--autostash", "origin", "main"])
        if pull.returncode != 0:
            _run_git(["rebase", "--abort"])
            return False
    return False


def _discard_failed_claim_and_sync():
    """Wirft einen gescheiterten lokalen Claim-Versuch weg und synct hart auf den
    Fernstand -- wird nur aufgerufen, nachdem _git_commit_and_push() False zurueckgegeben
    hat, der Claim also ohnehin verloren ist."""
    _run_git(["fetch", "origin", "main"])
    _run_git(["reset", "--hard", "origin/main"])


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true", help="Zeigt faellige Eintraege, postet nichts wirklich")
    args = parser.parse_args()

    sync_from_remote()
    token, ig_id, base_url = get_config()
    queue = load_queue()
    now = datetime.now(timezone.utc)
    due_keys = [entry_key(e) for e in queue if is_due(e, now)]

    if not due_keys:
        print("Nichts faellig.")
        return

    if args.dry_run:
        for key in due_keys:
            print(f"Faellig: {key[0]} ({key[1]})")
        return

    use_lock = _repo_is_clean_except_queue()
    if not use_lock:
        print("WARNUNG: Arbeitsbaum hat unabhaengige, unbezogene Aenderungen -- "
              "Claim-Sperre wird uebersprungen, Queue-Status wird nur lokal gespeichert (nicht gepusht).")

    for key in due_keys:
        queue = load_queue()
        entry = find_entry(queue, key)
        if entry is None or not is_due(entry, datetime.now(timezone.utc)):
            print(f"Uebersprungen (nicht mehr faellig, vermutlich schon von anderem Lauf erledigt): {key[0]} ({key[1]})")
            continue

        label = f"{entry['post_name']} ({entry['action']})"
        print(f"Faellig: {label}")

        if use_lock:
            entry["status"] = "claiming"
            entry["claimed_by"] = RUN_ID
            entry["claimed_at"] = datetime.now(timezone.utc).isoformat()
            save_queue(queue)
            if not _git_commit_and_push(f"Claim: {label} [skip ci]"):
                print(f"  Uebersprungen: Rennen verloren (ein anderer Lauf war schneller) -- {label}")
                _discard_failed_claim_and_sync()
                continue
            # Nach Push (moeglicherweise inkl. Rebase) den Eintrag frisch von der Platte
            # lesen -- die In-Memory-Kopie kann durch den Rebase veraltet sein.
            queue = load_queue()
            entry = find_entry(queue, key)

        try:
            result = DISPATCH[entry["action"]](token, ig_id, base_url, entry)
            entry["status"] = "done"
            entry["published_at"] = datetime.now(timezone.utc).isoformat()
            entry["media_id"] = result.get("id")
            if "media_ids" in result:
                entry["media_ids"] = result["media_ids"]
            print(f"  Veroeffentlicht: {result}")
        except Exception as exc:
            entry["status"] = "error"
            entry["error"] = str(exc)
            print(f"  FEHLER: {exc}")

        save_queue(queue)
        if use_lock:
            if not _git_commit_and_push(f"Queue-Status: {label} [skip ci]"):
                print(f"  WARNUNG: Ergebnis fuer {label} konnte nicht gepusht werden -- bitte manuell pruefen/pushen.")


if __name__ == "__main__":
    main()
