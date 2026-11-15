"""Character memory: append-only JSONL per character, recalled by keyword relevance.

Memory entries carry the beat that created them so the knowledge gate can hide
anything the audience (and therefore the character, publicly) shouldn't know yet.
"""
from __future__ import annotations
import datetime as dt
import json
import re
import uuid
from . import ROOT

KINDS = {"experience", "relationship", "fan-interaction", "secret", "belief"}


def _path(character: str, root=ROOT):
    p = root / "memory" / "characters" / character
    p.mkdir(parents=True, exist_ok=True)
    return p / "memory.jsonl"


def add(character: str, text: str, *, kind="experience", beat=None, public=True,
        importance=3, root=ROOT) -> dict:
    if kind not in KINDS:
        raise ValueError(f"kind must be one of {sorted(KINDS)}")
    entry = {"id": uuid.uuid4().hex[:8], "ts": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
             "kind": kind, "beat": beat, "public": public, "importance": importance, "text": text}
    with _path(character, root).open("a") as f:
        f.write(json.dumps(entry) + "\n")
    return entry


def load(character: str, root=ROOT) -> list[dict]:
    p = _path(character, root)
    return [json.loads(l) for l in p.read_text().splitlines() if l.strip()] if p.exists() else []


def _tok(s): return set(re.findall(r"[a-z0-9']+", s.lower()))


def recall(character: str, query: str, *, limit=5, released: set[str] | None = None,
           include_secrets=False, root=ROOT) -> list[dict]:
    """Top-`limit` memories by keyword overlap + importance.

    `released`: beat ids that are public. Memories tied to an unreleased beat are excluded.
    Secrets (public=False) are excluded unless include_secrets.
    """
    q = _tok(query)
    scored = []
    for m in load(character, root):
        if released is not None and m.get("beat") and m["beat"] not in released:
            continue
        if not m.get("public", True) and not include_secrets:
            continue
        score = len(q & _tok(m["text"])) * 2 + m.get("importance", 3)
        scored.append((score, m["ts"], m))
    scored.sort(key=lambda x: (x[0], x[1]), reverse=True)
    return [m for _, _, m in scored[:limit]]
