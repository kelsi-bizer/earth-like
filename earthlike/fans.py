"""Fan participation: one-person-one-vote branch polls that write to the canon ledger.

Fans never edit canon directly. A vote on an author-defined branch point yields a
`fan-influenced` ledger entry the author can accept (the default) or override.
"""
from __future__ import annotations
import collections
import datetime as dt
import json
from . import ROOT, tracker


def _ledger(root): return root / "memory" / "canon-ledger.jsonl"
def _votes(root, bid): return root / "memory" / "fans" / f"votes-{bid}.jsonl"


def cast_vote(branch_id: str, fan_id: str, option: str, root=ROOT) -> bool:
    """Record a vote. Returns False if the fan already voted (first vote wins)."""
    br = _branch(branch_id, root)
    if option not in br["options"]:
        raise ValueError(f"option must be one of {br['options']}")
    p = _votes(root, branch_id); p.parent.mkdir(parents=True, exist_ok=True)
    existing = [json.loads(l) for l in p.read_text().splitlines()] if p.exists() else []
    if any(v["fan"] == fan_id for v in existing):
        return False
    with p.open("a") as f:
        f.write(json.dumps({"fan": fan_id, "option": option,
                            "ts": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")}) + "\n")
    return True


def tally(branch_id: str, root=ROOT) -> collections.Counter:
    p = _votes(root, branch_id)
    votes = [json.loads(l) for l in p.read_text().splitlines()] if p.exists() else []
    return collections.Counter({o: 0 for o in _branch(branch_id, root)["options"]}) + collections.Counter(v["option"] for v in votes)


def close_branch(branch_id: str, root=ROOT) -> dict:
    """Close voting; write the winner to the ledger. Ties go to the earlier-listed option."""
    br = _branch(branch_id, root)
    t = tally(branch_id, root)
    winner = max(br["options"], key=lambda o: (t[o], -br["options"].index(o)))
    entry = {"ts": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"), "branch": branch_id,
             "beat": br["beat"], "question": br["question"], "winner": winner, "tally": dict(t),
             "tier": "fan-influenced", "author_review": "pending"}
    with _ledger(root).open("a") as f:
        f.write(json.dumps(entry) + "\n")
    return entry


def _branch(bid, root):
    for b in tracker.load(root).get("branches", []):
        if b["id"] == bid: return b
    raise KeyError(f"unknown branch {bid}")
