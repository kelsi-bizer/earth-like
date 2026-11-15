# 🌍 Earth-Like — a living story universe

> *Humanity finds a planet that is almost too much like home. Dr. Emma Baptiste goes to see why. Rich stays behind to bring her back.*

This repo is the **story engine**: the bible, the storyboard tracker, character memories, and the tools that let the story
leak into the real world through websites and AI-run social profiles — where **fans can change the course of the story**.

## Layout
| Path | What |
|---|---|
| `canon/` | Story bible: premise, timeline, settings, characters + backstories, 4-act arc, open questions, original draft |
| `storyboard/tracker.yaml` | Beat-by-beat tracker, release calendar, fan branch points |
| `memory/` | Per-character memories (`characters/`), fan votes, **canon ledger** |
| `earthlike/` | Engines: tracker · memory · personas (AI agents) · fans · assets · CLI |
| `channels/` | Real-world surfaces & per-channel specs |
| `assets/` | Generated prompts & approved media |
| `docs/` | Architecture, fan-canon rules, safety & disclosure |

## Quick start
```bash
pip install -r requirements.txt
python3 -m earthlike validate          # check tracker + canon
python3 -m earthlike status            # storyboard
python3 -m earthlike next              # what to work on
python3 -m earthlike persona emma-baptiste --query "Rich"   # see the (safe) agent prompt
python3 -m earthlike vote B2 fan123 sam && python3 -m earthlike tally B2
python3 -m earthlike asset portrait rich-baptiste "hopeful at dawn"
python3 -m unittest discover -s tests -t .
```

## Start here as the author
1. Read `canon/open-questions.md` and answer the 8 questions.
2. Review everything tagged `proposed` (twist, backstories, Acts II–IV) — these are drafts from your outline, not decisions.
3. Read `docs/safety-and-disclosure.md` before any public profile goes live.
