# Working in this repo
- `canon/` is the source of truth. `locked` canon is never contradicted; mark new ideas `proposed`.
- After editing tracker/characters run `python3 -m earthlike validate` and `python3 -m unittest discover -s tests -t .`.
- Agents/personas must go through `earthlike/personas.py` (knowledge gate + disclosure). Never hand-write persona prompts that bypass it.
- Never publish to a real channel without the approval flow in `docs/safety-and-disclosure.md`.
- Original draft lives in `canon/source/` — don't edit it; supersede via canon files.
