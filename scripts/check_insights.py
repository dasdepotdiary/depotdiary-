"""Holt echte Insights (Reach, Views, Likes, Non-Follower-Anteil) fuer die letzten
Instagram-Posts ueber die Graph API -- um zu pruefen, ob der Account uebehaupt
Distribution bekommt oder ob der Content selbst nicht zieht."""

import os
import sys
from pathlib import Path

import requests
from dotenv import load_dotenv

ROOT = Path(__file__).parent.parent
load_dotenv(ROOT / ".env")

TOKEN = os.environ.get("INSTAGRAM_ACCESS_TOKEN")
IG_ID = os.environ.get("INSTAGRAM_BUSINESS_ACCOUNT_ID")
GRAPH = "https://graph.facebook.com/v21.0"


def get(url, params):
    params = {**params, "access_token": TOKEN}
    r = requests.get(url, params=params, timeout=30)
    r.raise_for_status()
    return r.json()


def main(limit=15):
    if not TOKEN or not IG_ID:
        print("Fehlende INSTAGRAM_ACCESS_TOKEN / INSTAGRAM_BUSINESS_ACCOUNT_ID in .env")
        sys.exit(1)

    media = get(f"{GRAPH}/{IG_ID}/media", {
        "fields": "id,caption,media_type,media_product_type,timestamp,permalink",
        "limit": limit,
    })["data"]

    print(f"{'Datum':<12} {'Typ':<10} {'Reach':>7} {'Views':>7} {'Likes':>6} {'NonFoll%':>9}  Titel")
    print("-" * 100)

    for m in media:
        mid = m["id"]
        mtype = m.get("media_product_type", m.get("media_type", "?"))
        date = m["timestamp"][:10]
        title = (m.get("caption") or "").split("\n")[0][:40]

        metric_names = "reach,likes,comments,shares,saved"
        if mtype == "REELS":
            metric_names += ",plays,ig_reels_video_view_total_time"
        try:
            insights = get(f"{GRAPH}/{mid}/insights", {"metric": metric_names})["data"]
        except requests.HTTPError as e:
            print(f"{date:<12} {mtype:<10} -- Insights nicht abrufbar ({e}) -- {title}")
            continue

        vals = {i["name"]: i["values"][0]["value"] for i in insights}
        reach = vals.get("reach", 0)
        plays = vals.get("plays", vals.get("reach", 0))
        likes = vals.get("likes", 0)

        nonfoll = "?"
        try:
            demo = get(f"{GRAPH}/{mid}/insights", {
                "metric": "reach", "breakdown": "follow_type",
            })["data"]
            for d in demo:
                for v in d["values"]:
                    breakdown = v.get("value", {})
                    if isinstance(breakdown, dict):
                        follower = breakdown.get("FOLLOWER", 0)
                        nonfollower = breakdown.get("NON_FOLLOWER", 0)
                        total = follower + nonfollower
                        if total:
                            nonfoll = f"{nonfollower / total * 100:.0f}%"
        except requests.HTTPError:
            pass

        print(f"{date:<12} {mtype:<10} {reach:>7} {plays:>7} {likes:>6} {nonfoll:>9}  {title}")


if __name__ == "__main__":
    main()
