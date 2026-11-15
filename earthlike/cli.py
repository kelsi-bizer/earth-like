"""`python -m earthlike <command>` — the control panel for the story universe."""
from __future__ import annotations
import argparse, json, sys
from . import assets, fans, memory, personas, tracker
from .canon import load_characters


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="earthlike")
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("validate", help="check tracker + canon consistency")
    sub.add_parser("status", help="storyboard status")
    sub.add_parser("next", help="what to work on next")
    p = sub.add_parser("persona", help="print a character's system prompt"); p.add_argument("character"); p.add_argument("--query", default="")
    p = sub.add_parser("remember", help="add a memory"); p.add_argument("character"); p.add_argument("text"); p.add_argument("--beat"); p.add_argument("--secret", action="store_true")
    p = sub.add_parser("recall"); p.add_argument("character"); p.add_argument("query")
    p = sub.add_parser("vote"); p.add_argument("branch"); p.add_argument("fan"); p.add_argument("option")
    p = sub.add_parser("tally"); p.add_argument("branch")
    p = sub.add_parser("close"); p.add_argument("branch")
    p = sub.add_parser("asset"); p.add_argument("kind"); p.add_argument("character"); p.add_argument("mood")
    a = ap.parse_args(argv)

    if a.cmd in ("validate", "status", "next"):
        data = tracker.load()
        if a.cmd == "validate":
            errs = tracker.validate(data, set(load_characters()))
            print("\n".join(errs) if errs else f"OK: {len(data['beats'])} beats, {len(load_characters())} characters")
            return 1 if errs else 0
        print(tracker.report(data) if a.cmd == "status" else "\n".join(tracker.next_actions(data)))
    elif a.cmd == "persona": print(personas.build_system_prompt(a.character, a.query))
    elif a.cmd == "remember": print(json.dumps(memory.add(a.character, a.text, beat=a.beat, public=not a.secret)))
    elif a.cmd == "recall":
        for m in memory.recall(a.character, a.query): print(f"- {m['text']}")
    elif a.cmd == "vote": print("recorded" if fans.cast_vote(a.branch, a.fan, a.option) else "already voted")
    elif a.cmd == "tally": print(dict(fans.tally(a.branch)))
    elif a.cmd == "close": print(json.dumps(fans.close_branch(a.branch), indent=2))
    elif a.cmd == "asset": print(json.dumps(assets.build(a.kind, a.character, a.mood), indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
