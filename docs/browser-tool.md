# Browser Tool — exploration (status: `proposed`)

Goal: let Earth-Like persona agents and the author's tooling read the web (research, fan-channel monitoring, asset reference)
and, later, post via channel adapters — without breaking `docs/safety-and-disclosure.md`.

## What browser-harness is
[browser-use/browser-harness](https://github.com/browser-use/browser-harness) (MIT): a thin CDP (Chrome DevTools Protocol) layer
that lets a coding agent drive **the user's real, logged-in Chrome**. Agent writes Python snippets against helpers
(`new_tab()`, `page_info()`, …) run via `browser-use <<'PY' … PY`; missing helpers are written into `agent-workspace/agent_helpers.py`.
Also exposes MCP (`uvx browser-use --cli-mcp`). Needs Chrome 144+ with remote debugging enabled.

## Fit and risks
| Issue | Why it matters here |
|---|---|
| Drives the real profile; approval is whole-browser, not per-site | Conflicts with safety rule 4 (never touch credentials) and rule 5 (nothing publishes without approval). A persona agent must never inherit the author's logins. |
| Agent self-writes helpers | Unreviewed code path; bypasses `personas.py` gating if helpers call an LLM. |
| Page content is untrusted | Prompt-injection from fan posts/web pages could steer an agent. |

**Recommendation:** use browser-harness as a *backend*, not as the tool surface agents see. Wrap it in `earthlike/browser.py`.

## Proposed design
```
persona/research agent ──► earthlike.browser.Browser (policy layer) ──► Backend
                                   │                                    ├─ PlaywrightBackend  (default: isolated, no logins, tests)
                                   ▼                                    └─ HarnessBackend     (browser-harness over CDP; opt-in)
                          audit log (memory/browser-log.jsonl)
```
- **Small fixed verb set** exposed to agents: `open(url)`, `read(selector|None)` → text/markdown, `screenshot()`, `links()`.
  Interactive verbs (`click`, `type`, `submit`) are a separate `Interactive` capability, off by default.
- **Policy layer** (pure Python, unit-testable offline like the rest of the repo):
  - domain allowlist/denylist in `channels/browser-policy.yaml`; deny `file:`, `chrome:`, localhost, internal IPs;
  - read-only by default; any write/post action must come from the approval queue (roadmap step 2), never directly from an agent;
  - never fill password/payment fields; refuse pages matching login/checkout patterns;
  - returned page text wrapped as `<untrusted_web_content>` and never concatenated into the persona *system* prompt;
    persona replies still go through `personas.build_system_prompt` (knowledge gate + disclosure);
  - every call appended to an audit log; size/time/page-count limits.
- **HarnessBackend** runs against a **dedicated Chrome profile** (`--user-data-dir`, no personal sign-ins), not the author's daily browser;
  `agent_helpers.py` not agent-writable in production (helpers added by PR only).
- **Surfaces:** (a) Python API for agents; (b) `python -m earthlike browse <url>` CLI; (c) optionally an MCP server later.

## Phased plan
1. `Backend` protocol + `FakeBackend` + policy layer + tests (no network). 
2. `PlaywrightBackend` (read-only) for research/monitoring.
3. `HarnessBackend` spike in a dedicated profile; compare reliability on JS-heavy sites.
4. Hook posting through channel adapters behind the approval queue (not via free-form clicking).

## Open questions for the author
1. Primary use: research/monitoring only, or posting to socials too?
2. OK to dedicate a separate Chrome profile/machine, or must it use your logged-in browser?
3. Python-only API, or also expose as an MCP server for other agents?
