# typirOS — Progress Log

Reverse-chronological. Every working session gets an entry.

---

## 2026-06-16 — Session 4: Phase 1 M3 — Quiet layer

- `EventSimulator` daemon thread: `/sim auto on [N]` / `/sim auto off` pushes
  sample inbound events every N seconds in interactive sessions so the `•N`
  quiet indicator increments without user action (PRD §9, §19.1).
- Digest cadence (PRD §19.1): `digest every 30m` configures a batch interval;
  auto-surfaces between REPL turns when elapsed; `digest off` disables. Stored
  in `SessionMemory.digest_interval`; timer initialised at shell launch so
  the first fire is never immediate.
- Focus sessions (PRD §19.2): `focus 90m on writing` suppresses the `•N`
  indicator, renders `[focus] writing · N left` context strip (first-priority
  strip, above call and timer), queues events silently. `end focus` (or
  auto-expiry when the timer runs out, checked at each REPL turn) produces a
  held-back digest of items that arrived during focus — using the new
  `QuietQueue.drain_from(idx)` method to extract only focus-period items
  without losing pre-focus notifications.
- `QuietQueue` gained `size()` and `drain_from(idx)`. `SessionMemory` gained
  `focus_session`, `digest_interval`, `last_digest_at`. New `FocusSession`
  dataclass and `event_sim.py` module.
- Extended `shell/demo.txt`; all M3 scenarios pass. Updated `/help`,
  `shell/README.md`.

## 2026-06-15 — Session 3: Phase 1 M2 — Conversation depth

- Session memory: `call her back` / `text them` resolve the pronoun (and a
  trailing "back") to `memory.last_contact`, which now also updates on
  inbound `/sim` events — implements PRD §13's "Call him back" example.
- Correction flow (PRD §11): `no, primary` / `no, secondary` re-dispatches
  the last call or message on the corrected SIM. For calls, the active leg
  is hung up and redialled; `last_sim` updates so the OS "remembers".
- Verified message-body capture already worked for a single unambiguous
  contact (`message lena` → `What should it say?` → send) — added to the
  demo as its own scenario and marked done.
- Macros (PRD §19.3): `when I type gm, <a> and <b>` defines a macro after
  validating each clause parses to a tool call; typing `gm` runs each
  clause through the normal loop and joins the results.
- Recall / edit (PRD §19.3): `again` re-runs the last dispatched command
  (or last-run macro); `edit` prints it back for retyping. `SessionMemory`
  gained `last_dispatch`, `last_raw`, `macros`.
- Extended `shell/demo.txt` end-to-end with all of the above; demo still
  passes. Updated `/help` and `shell/README.md`.
- M2 fully done — all tasks.md items checked off.

## 2026-06-11 — Session 2: Tracking system + PRD v1.2 + Phase 1 M1 shell

- Added PRD §19 — Distraction-Free Typing-First Addendum (v1.2): pull-not-push
  notifications, focus sessions, slash commands, macros, visual minimalism,
  voice demoted to accessibility layer, physical keyboard first-class, What-If
  Protocol formalized.
- Created tracking system: plans.md (strategy + working agreement), tasks.md
  (work items), progress.md (this file), what-ifs.md (speculative backlog).
- Built Phase 1 M1: runnable typing-first chat shell prototype in
  `shell/typiros_shell/` — deterministic Tier 1 grammar parser, Bridge Layer
  with error translation, mock telephony/device/productivity backends, contact
  disambiguation chips, context strips, quiet notification queue.
- Verified end-to-end: scripted demo covering the Phase 1 success metric
  (call, SMS, alarm, setting change) passes.

## 2026-06-11 — Session 1: Repo reboot

- Removed all huashu-design content (AI design-generation skill — no overlap
  with an OS project). Kept and adapted LICENSE (MIT), .gitignore, README.
- Project named **typirOS** (PRD text used "VOXOS"; substituted throughout).
- Committed PRD.md v1.1, README rewrite, kernel/shell/bridge scaffold, and
  8 Managed Agent YAML definitions (agents/*.yaml).
- Noted: actual GitHub repo rename to `typiros` requires owner action in
  repo Settings (no rename API access from this session).
