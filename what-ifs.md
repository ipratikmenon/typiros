# typirOS — What-Ifs

Speculative feature backlog (PRD §19.8). Agents add entries every working
session. Triage states: **accepted** (→ tasks.md), **parked**, **rejected**.

Format: `WIF-NNN · status · phase estimate · one-line rationale`

---

## Open / Parked

- **WIF-017 · parked · P4** — What if the Biometric Gate's "personal data
  retrieval" scope (PRD §15) extended past finance/episodic-history to the
  Files agent (`find file`/`recent files`) and the Photos overlay? M16's
  security audit drew the line at finance + episodic history because
  those map cleanly onto the PRD's own examples ("banking, payments,
  personal data retrieval" read as relationship/financial data), but a
  stricter reading could call a user's file index or photo library
  "personal data" too. Didn't gate them this session — doing so would
  make the gate fire on nearly every read-only lookup, which cuts against
  "one unlock per session, rest dispatch silently." Needs a decision on
  where the line actually sits before extending `SENSITIVE_TOOLS` further.
- **WIF-016 · parked · P4** — What if strips were tappable, expanding to
  the matching overlay, per PRD §9 ("Strips are tappable — tap expands to
  the relevant overlay")? Phase 3 M15 built the overlay push/dismiss
  mechanism (`overlays.py`) but the only trigger is typed grammar (`show
  media`/`show maps`/`show photos`) — there's no path from clicking a
  `[media]`/`[nav]` strip in the TUI to its overlay. Textual `Static`
  widgets support `on_click`; the strips bar would need to become
  per-strip clickable widgets instead of one joined `Static` string, and
  each strip would need to carry its own `kind` so the click handler knows
  which `OVERLAYS` entry to push. Needs a decision on whether that
  refactor (one `Static` → N clickable strips) is worth it for a
  prototype that's primarily typing-first by design (PRD §19) — tapping a
  strip is arguably secondary to typing the same command.
- **WIF-013 · parked · P2** — What if the Tier 2 stub (Phase 2 M8) doubled
  as a grammar-gap logger? Every off-grammar input that falls through to
  `tier2.py` is, by definition, a Tier 1 miss. Logging those misses (text +
  timestamp, no PII beyond what's already typed) would build a real dataset
  for prioritizing future grammar coverage — turns the "escape hatch" into
  a feedback loop instead of a dead end. Needs a decision on whether logs
  live in the new sqlite User-memory DB (M9) or a separate flat file.
- **WIF-012 · parked · P5** — What if the TUI had a light/e-ink theme toggle?
  The current `tui.py` CSS is dark-terminal-first. A `--light` flag (or a `/theme
  light` command) could swap the palette to `#ffffff`/`#000000` for real e-ink
  displays (PineNote, Onyx BOOX). Textual's `dark` reactive plus a CSS variable
  swap would make this one-liner once the theme tokens are factored out.
- **WIF-011 · parked · P3** — What if Focus Sessions could auto-reply?
  PRD §19.2 mentions "auto-replies if configured." A simple implementation:
  at focus start the user optionally types `focus 1h on writing, auto-reply
  "I'm in focus mode — back at [end time]"` and any inbound SMS during focus
  gets that reply dispatched silently via the telephony backend. Needs a
  starred-contact exception (PRD §19.1: true interrupts still surface).
- **WIF-010 · parked · P2** — What if "no, X" were a general correction
  primitive, not just SIM? M2 implements `no, secondary`/`no, primary` by
  re-dispatching `last_dispatch` with a swapped `sim`. The same shape could
  fix any slot of the last action — "no, whatsapp" (channel), "no, 8pm"
  (alarm time), "no, mom" (recipient) — by detecting which slot the
  correction value fits and swapping it in. Needs a slot-type registry per
  tool so "no, X" doesn't misfire on an unrelated tool.
- **WIF-005 · parked · P3** — What if the OS learned macros automatically?
  Detect repeated command sequences ("weather" then "calendar" every morning)
  and offer: "You do this daily — want 'gm' to do both?" Compounds intelligence
  (PRD principle 5) without the user designing macros.
- **WIF-006 · parked · P3** — What if `/missed` digests were prioritized by
  the knowledge graph? Sender importance (starred, frequency, recency of
  conversation) orders the digest, so the pull is glanceable in one line.
- **WIF-007 · parked · P4** — What if Focus Sessions had a hardware
  expression? A physical slider/switch (Phase 5 hardware) that enters Quiet —
  friction-by-design made tactile.
- **WIF-008 · parked · P2** — What if the shell had a "dry run" prefix?
  `? message philip running late` shows exactly what would be dispatched
  (recipient, channel, SIM) without sending. Trust-building during onboarding.
- **WIF-009 · parked · P3** — What if undo were a grammar primitive? "undo"
  within N seconds recalls an outbound message (where channel supports it),
  cancels a just-set alarm, reverts a setting. Act-first-confirm-short needs
  a safety net.

## Accepted (moved to tasks.md / PRD)

- **WIF-018 · accepted → PRD §20.1 · P2** — What if the user could ask the OS
  "why did you do that?" and get a complete, honest answer? `/why` prints the
  last turn's full trace (parse, tier route, tool-call JSON, backend, latency);
  `/trace on` streams it live. Inverts Design Principle 3 per-user: opacity by
  default, glass box on demand. Became Glasnost Mode.
- **WIF-019 · accepted → PRD §20.2 · P2** — What if the OS's beliefs about you
  were a file you own? `memory show/diff/forget/edit` over all three memory
  layers — wrong inferences become fixable. Became Open Skull.
- **WIF-020 · accepted → PRD §20.3 · P4** — What if privacy were falsifiable
  instead of promised? Every byte leaving the device logged and attributed,
  queryable in grammar, plus a chat-driven firewall. Became the Egress Ledger.
- **WIF-021 · accepted → PRD §20.4 · P2** — What if the cloud tier had a
  verifiable kill switch? `/airgap on` makes Tier 2 escalation impossible (not
  discouraged), with honest degradation and queued escalations surfacing via
  digest. Became Local-Only Hard Mode.
- **WIF-022 · accepted → PRD §20.5 · P3** — What if `|` were a grammar
  primitive and the chat window were an actual shell? Structured results feed
  the next command's input slot; the pre-parser splits segments
  deterministically. Became Pipes.
- **WIF-023 · accepted → PRD §20.6 · P3** — What if the user could program the
  phone's *behavior*, not just its apps? `when <event>, <command>` /
  `every <schedule>, <command>` rules over an OS event bus. Became Hooks.
- **WIF-024 · accepted → PRD §20.7 · P3–P4** — What if you could SSH into your
  phone's conversation and drive it from scripts (`typir "message lena ..."`)?
  Key-based auth, per-key capability scoping, gate domains enforced over the
  wire. Became The Wire.
- **WIF-025 · accepted → PRD §20.8 · P3** — What if your servers could post
  into the quiet queue (CI failures, Grafana alerts) through an authenticated
  webhook endpoint, hookable via WIF-023's rules? Became the Webhook Inbox.
- **WIF-026 · accepted → PRD §20.9 · P3** — What if the "calculator" were a
  sandboxed real interpreter (`py:` / jq scratchpad) with pipeable output?
  Became the Inline REPL.
- **WIF-027 · accepted → PRD §20.10 · P3** — What if Tier 2 were a pluggable
  endpoint — your API key, your homelab GPU, Ollama over the LAN — with ant as
  the managed default rather than the mandate? Became Sovereign Tier 2 (BYOM).
- **WIF-028 · accepted → PRD §20.11 · P3** — What if all OS configuration
  (macros, hooks, allowlist, modes) were plain-text files in a git repo, with
  `typir apply` to converge the device? Dotfiles for your phone. Became
  Phone-as-Code.
- **WIF-029 · accepted → PRD §20.12 · P4** — What if capability packs (agent
  YAMLs + verbs + macros + hooks) were signed, versioned, auditable-before-
  install, and community-published — AUR for your phone's brain, gated by the
  §19.9 allowlist pattern? Became tpkg.
- **WIF-030 · accepted → PRD §20.13 · P4–P5** — What if the long tail of apps
  were *generated on demand*? The OS writes a requested tool, shows the source
  for review, sandboxes and registers it on approval. Became The Forge.
- **WIF-031 · accepted → PRD §20.14 · P3** — What if a ninth System Agent
  spoke Home Assistant/MQTT natively, compounding with Hooks (`when I leave
  home, arm the alarm`)? Became the Home agent.
- **WIF-032 · accepted → PRD §20.15 · P3–P4** — What if the flagship messaging
  path were federated and self-hostable? Matrix as a first-class channel and a
  fourth angle on the WhatsApp problem. Became §20.15.
- **WIF-033 · accepted → PRD §20.16 · P4–P5** — What if memory layers and chat
  history CRDT-synced across devices over LAN/VPN, E2E encrypted, with no
  vendor account? Became Mesh Sync.
- **WIF-034 · accepted → PRD §20.17 · P2** — What if every turn were appended
  to a local queryable JSONL lifelog (`history | grep lena | last month`)?
  Became grep-your-life.
- **WIF-035 · accepted → PRD §20.18 · P5–P6** — What if the build were
  reproducible and the runtime could attest to itself (`/attest`: system-prompt
  hash, manifest version, model checksums)? Became §20.18.
- **WIF-001 · accepted → PRD §19.1 · P1** — What if notifications were
  pull-based by default? Became the Quiet model.
- **WIF-002 · accepted → PRD §19.3 · P1** — What if slash commands bypassed
  the model entirely? Became the deterministic pre-parser.
- **WIF-003 · accepted → PRD §19.2 · P1/P3** — What if focus were an OS
  primitive, not an app? Became Focus Sessions.
- **WIF-004 · accepted → PRD §19.6 · P5** — What if a hardware keyboard were
  first-class? Folded into hardware-PRD inputs.
- **WIF-014 · accepted → PRD §19.9 · P2** — What if typirOS merged LightOS's
  restraint (subtraction-based minimalism) with its own abstraction
  (apps hidden, not removed)? Became the curated App Allowlist: a default
  allowlist gates the `AndroidContainer` backend, with `enable app <name>`
  as the deliberate opt-in for anything outside it. Phase 2 M6 scope
  updated in plans.md/tasks.md to build the gate alongside the mock
  backend, not as a later bolt-on.
- **WIF-015 · accepted → Phase 3 M14 · P3** — What if Compact keyboard mode
  reused `tier2.py`'s keyword-overlap scorer for abbreviation expansion
  instead of a separate lookup table? Resolved by extracting
  `tier2.tokenize()`/`tier2.best_match()` as shared module-level
  functions; `keyboard.py`'s `expand_compact()` and `tier2.route()` both
  call them now, so Tier 2 routing and Compact-mode prediction share one
  "closest match" implementation instead of drifting into two.

## Rejected

*(none yet)*
