"""Asset engine: turn canon into consistent, reviewable prompts/specs for images, posts, and web pages.

It never calls an image model itself — it writes the prompt + metadata to assets/prompts/ so a human (or a
separate generator) can run it, and so every asset stays tied to canon.
"""
from __future__ import annotations
import json
from . import ROOT
from .canon import load_characters

STYLE = ("cinematic, naturalistic lighting, grounded near-future sci-fi, warm color palette on Earth, "
         "teal-and-silver on Terra, 35mm film grain")

TEMPLATES = {
    "portrait": "Portrait of {name}, {role}, {age}. {appearance}. Mood: {mood}. Style: {style}.",
    "social-post": "Write a short in-character post for {name} ({handle}). Voice: {voice}. Topic: {mood}. "
                   "Max 280 chars. Must include no spoilers beyond released beats. End with #EarthLike only if natural.",
    "scene": "Establishing shot: {mood}. Characters present: {name}. Style: {style}.",
}


def build(kind: str, character_id: str, mood: str, *, root=ROOT, save=True) -> dict:
    if kind not in TEMPLATES: raise ValueError(f"kind must be one of {sorted(TEMPLATES)}")
    ch = load_characters(root)[character_id]
    prompt = TEMPLATES[kind].format(
        name=ch["name"], role=ch.get("role", ""), age=ch.get("age", ""), appearance=ch.get("appearance", ""),
        handle=ch.get("channels", {}).get("in_universe_handle", ""), voice=ch.get("voice", {}).get("style", ""),
        mood=mood, style=STYLE)
    spec = {"kind": kind, "character": character_id, "mood": mood, "prompt": prompt, "status": "needs-review"}
    if save:
        d = root / "assets" / "prompts"; d.mkdir(parents=True, exist_ok=True)
        (d / f"{kind}-{character_id}-{abs(hash(mood)) % 10**6}.json").write_text(json.dumps(spec, indent=2))
    return spec
