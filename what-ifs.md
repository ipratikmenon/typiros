# typirOS — What-Ifs

Speculative feature backlog (PRD §19.8). Agents add entries every working
session. Triage states: **accepted** (→ tasks.md), **parked**, **rejected**.

Format: `WIF-NNN · status · phase estimate · one-line rationale`

---

## Open / Parked

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

## Rejected

*(none yet)*
