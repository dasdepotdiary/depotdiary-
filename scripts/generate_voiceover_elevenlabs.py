"""Erzeugt eine Voiceover-Audiodatei per ElevenLabs-API aus dem Skript eines Posts.

Braucht ELEVENLABS_API_KEY in .env.

Aufruf:
  python scripts/generate_voiceover_elevenlabs.py marktupdate_speicherchips
  python scripts/generate_voiceover_elevenlabs.py marktupdate_speicherchips --voice-id <id>
"""

import argparse
import json
import os
import sys
from pathlib import Path

import requests
from dotenv import load_dotenv

ROOT = Path(__file__).parent.parent
load_dotenv(ROOT / ".env")

API_KEY = os.environ.get("ELEVENLABS_API_KEY")
DEFAULT_VOICE_ID = "21m00Tcm4TlvDq8ikWAM"  # "Rachel", ElevenLabs Premade-Stimme, mehrsprachig


def list_voices():
    resp = requests.get("https://api.elevenlabs.io/v1/voices", headers={"xi-api-key": API_KEY})
    resp.raise_for_status()
    return resp.json()["voices"]


def synthesize(text: str, voice_id: str, out_path: Path):
    resp = requests.post(
        f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}",
        headers={"xi-api-key": API_KEY, "Content-Type": "application/json"},
        json={
            "text": text,
            "model_id": "eleven_multilingual_v2",
            "voice_settings": {"stability": 0.5, "similarity_boost": 0.75},
        },
    )
    if not resp.ok:
        sys.exit(f"ElevenLabs-Fehler: {resp.status_code} {resp.text}")
    out_path.write_bytes(resp.content)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("post_name")
    parser.add_argument("--voice-id", default=DEFAULT_VOICE_ID)
    parser.add_argument("--list-voices", action="store_true")
    args = parser.parse_args()

    if not API_KEY:
        sys.exit("ELEVENLABS_API_KEY fehlt in .env")

    if args.list_voices:
        for v in list_voices():
            print(f"{v['voice_id']}  {v['name']}  ({v.get('labels', {})})")
        return

    timing_path = ROOT / "output" / args.post_name / "timing.json"
    if not timing_path.exists():
        sys.exit(f"Nicht gefunden: {timing_path}. Erst den Post-Generator laufen lassen.")
    data = json.loads(timing_path.read_text(encoding="utf-8"))
    full_text = " ".join(s["text"] for s in data["sentences"])

    out_path = ROOT / "output" / args.post_name / "voiceover_elevenlabs.mp3"
    synthesize(full_text, args.voice_id, out_path)
    print(f"Audio erzeugt: {out_path}")


if __name__ == "__main__":
    main()
