"""Storyboard tracker: load, validate, report, and decide what can be released."""
from __future__ import annotations
import datetime as dt
import yaml
from . import ROOT

STATUSES = ["idea", "outlined", "drafted", "reviewed", "locked", "released"]
CANON = {"locked", "open", "fan-influenced", "proposed"}


def load(root=ROOT) -> dict:
    return yaml.safe_load((root / "storyboard" / "tracker.yaml").read_text())


def save(data: dict, root=ROOT) -> None:
    (root / "storyboard" / "tracker.yaml").write_text(
        yaml.safe_dump(data, sort_keys=False, allow_unicode=True))


def validate(data: dict, character_ids: set[str]) -> list[str]:
    """Return a list of human-readable problems (empty list = valid)."""
    errs: list[str] = []
    beats = {b["id"]: b for b in data["beats"]}
    if len(beats) != len(data["beats"]):
        errs.append("duplicate beat ids")
    acts = {a["id"] for a in data["acts"]}
    branches = {b["id"]: b for b in data.get("branches", [])}
    for b in data["beats"]:
        i = b["id"]
        if b.get("status") not in STATUSES:
            errs.append(f"{i}: bad status {b.get('status')!r}")
        if b.get("canon") not in CANON:
            errs.append(f"{i}: bad canon tier {b.get('canon')!r}")
        if b.get("act") not in acts:
            errs.append(f"{i}: unknown act {b.get('act')!r}")
        for c in b.get("characters", []):
            if c not in character_ids:
                errs.append(f"{i}: unknown character {c!r}")
        for r in b.get("requires", []):
            if r not in beats:
                errs.append(f"{i}: requires unknown beat {r!r}")
        if b.get("branch") and b["branch"] not in branches:
            errs.append(f"{i}: unknown branch {b['branch']!r}")
        if b.get("status") == "released" and not b.get("release_date"):
            errs.append(f"{i}: released but no release_date")
    for br in branches.values():
        if br["beat"] not in beats:
            errs.append(f"branch {br['id']}: unknown beat {br['beat']!r}")
    # cycle check
    state: dict[str, int] = {}
    def visit(n, path):
        if state.get(n) == 1:
            errs.append("cycle: " + " -> ".join(path + [n])); return
        if state.get(n) == 2 or n not in beats: return
        state[n] = 1
        for r in beats[n].get("requires", []): visit(r, path + [n])
        state[n] = 2
    for n in beats: visit(n, [])
    return errs


def is_released(beat: dict, today: dt.date | None = None) -> bool:
    today = today or dt.date.today()
    d = beat.get("release_date")
    if beat.get("status") != "released" or not d:
        return False
    if isinstance(d, str): d = dt.date.fromisoformat(d[:10])
    if isinstance(d, dt.datetime): d = d.date()
    return d <= today


def released_ids(data: dict, today=None) -> set[str]:
    return {b["id"] for b in data["beats"] if is_released(b, today)}


def next_actions(data: dict) -> list[str]:
    """Beats whose prerequisites are all done, ordered by how close they are to release."""
    beats = {b["id"]: b for b in data["beats"]}
    rank = {s: n for n, s in enumerate(STATUSES)}
    out = []
    for b in data["beats"]:
        if b["status"] == "released": continue
        ready = all(rank[beats[r]["status"]] >= rank["drafted"] for r in b.get("requires", []))
        if ready:
            nxt = STATUSES[rank[b["status"]] + 1]
            out.append((-rank[b["status"]], b["id"], f"{b['id']} '{b['title']}': {b['status']} -> {nxt}"))
    return [x[2] for x in sorted(out)]


def report(data: dict) -> str:
    lines = ["Storyboard status", "================="]
    for a in data["acts"]:
        bs = [b for b in data["beats"] if b["act"] == a["id"]]
        lines.append(f"\n{a['id']}: {a['title']} ({len(bs)} beats)")
        for b in bs:
            lines.append(f"  [{b['status']:<8}] {b['id']:<5} {b['title']}  ({b['canon']})")
    return "\n".join(lines)
