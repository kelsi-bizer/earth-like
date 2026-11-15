# Architecture — Story Universe Engine

```
 canon/ (bible)  ──►  storyboard/tracker.yaml  ──►  RELEASE CLOCK ──► channels/ (web, social)
     │                       │                           │
     ▼                       ▼                           ▼
 characters ───►  Persona runtime (agents) ◄── Knowledge gate ◄── released beats
                         │         ▲
                  memory/ (per-character JSONL)      fans: DMs, comments, votes
                         │                              │
                         └────────► Canon ledger ◄──────┘  (author reviews)
 Asset engine: canon ─► prompts/specs ─► assets/ (human/generator reviewed)
```

## Components (all in `earthlike/`)
| Module | Job |
|---|---|
| `canon.py` | Loads characters/settings from `canon/`. |
| `tracker.py` | Beat/arc state machine (`idea→outlined→drafted→reviewed→locked→released`), validation, "what's next". |
| `memory.py` | Append-only per-character memory; recall by relevance; memories tied to unreleased beats and secrets are hidden. |
| `personas.py` | Builds a persona system prompt = profile + public backstory + released facts + recalled memories + guardrails. LLM is pluggable (`DryRun`, `Anthropic`). |
| `fans.py` | One-fan-one-vote polls on author-defined **branch points**; winner is written to `memory/canon-ledger.jsonl` as `fan-influenced`, `author_review: pending`. |
| `assets.py` | Generates reviewable prompts/specs (portraits, posts, scenes) from canon. |
| `cli.py` | `python -m earthlike validate|status|next|persona|remember|recall|vote|tally|close|asset`. |

## Key idea: the Knowledge Gate
Characters in public channels may only know **facts revealed by beats that are `released` and whose `release_date` has passed**.
This prevents AI personas from spoiling the story, and keeps the real-world reveal schedule authoritative.
Backstory text after a `**Proposed` marker is withheld from agents until the author approves it.

## Data contracts
- Beat: see header of `storyboard/tracker.yaml`.
- Memory entry: `{id, ts, kind, beat, public, importance, text}`.
- Ledger entry: `{ts, branch, beat, question, winner, tally, tier, author_review}`.

## Roadmap
1. ✅ Bible, tracker, memory, persona prompt builder, fan branches, asset prompts (this PR).
2. Channel adapters (Bluesky/X/Discord/website CMS) with human-approval queue → publish.
3. Scheduler: posts + DMs on the release clock; "in-universe time" posts.
4. Memory summarization/decay; relationship graph between characters.
5. Fan identity layer (accounts, anti-brigading), moderation pipeline.
6. Asset generation adapters (image/audio/video) writing into `assets/`.
