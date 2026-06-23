# typirOS — Progress Log

Reverse-chronological. Every working session gets an entry.

---

## 2026-06-23 — Session 9: Phase 2 M8 + M9 — Tier 2 stub, User memory layer

User asked to plan and complete all remaining Phase 2 sprints in one pass.

**M8 — Tier 2 stub + two-model routing:**
- New `tier2.py`: `_load_manifests()` regex-parses `agents/*.yaml` (`name:`
  line + the `You handle/dispatch ...` sentence) into keyword sets — no
  PyYAML dependency, keeping the project's stdlib-only stack decision.
  `route(text)` scores each manifest by word overlap with the input and
  returns `[tier2-stub] <agent-name> would handle: "<text>"`, defaulting to
  `typiros-information` on no match.
- `intent.py`: new `Escalate(text)` result type replaces the old generic
  "I can't parse that" `Say` fallback at the end of `parse()` — keeps Tier 1
  pure/deterministic while making the escalation explicit in the type
  system. `HELP` updated.
- `main.py`: `Shell.handle()` routes `Escalate` results through
  `tier2.route()`.
- Verified: off-grammar phrases route to the right agent by keyword overlap
  — "what's the weather in paris" → `typiros-information`, "send an email
  to mom" → `typiros-communication`. Added both to `demo.txt`.

**M9 — User memory layer:**
- New `user_memory.py`: `UserMemory` wraps a stdlib `sqlite3` connection
  (file `typiros_shell/user_memory.db`) with three tables — `sim_preference`
  (contact → SIM), `enabled_apps` (Phase 2 M6 allowlist), `macros`
  (trigger → `\x1f`-joined actions). PRD §13 calls for an *encrypted* local
  DB; the prototype docstring is explicit that encryption is deferred to
  Phase 4 hardening (§15), not silently implied.
- `bridge.py`: `Bridge.__init__` now takes a `UserMemory` and seeds
  `self.android.allowlist` from `user_memory.enabled_apps()` on construction
  — apps enabled in a prior session stay enabled. `make_call`/`send_message`
  consult `user_memory.get_sim_preference(contact.name)` before falling back
  to session-level `last_sim`. `enable_app` now persists via
  `user_memory.enable_app(...)` after a successful enable.
- `main.py`: `Shell.__init__` picks `:memory:` for piped/non-tty runs
  (`demo.txt`, tests) and the real DB file for interactive runs — keeps the
  scripted demo reproducible across repeated runs while real usage persists.
  Loads persisted macros into session memory at startup. `_correct()`
  persists the SIM preference after a successful `no, primary`/`no,
  secondary` redispatch; `_define_macro()` persists the macro definition.
- Verified manually with two sequential interactive process runs (real DB
  file, not demo.txt): `call lena` → `no, secondary` in run 1, then plain
  `call lena` in run 2 dials Secondary automatically — preference survived
  the restart. Same check for a macro defined in run 1 and invoked in run 2.
  Cleaned up the test DB file afterward; added
  `shell/typiros_shell/user_memory.db` to `.gitignore`.
- `demo.txt` still passes end-to-end (ephemeral `:memory:` DB keeps it
  deterministic); confirmed no stray `.db` file is left behind by a demo run.
- Updated `shell/README.md` (What works + architecture tree) and `tasks.md`
  (M8, M9 checked off). **Phase 2 M6–M9 all done** — every milestone in the
  current `plans.md` Phase 2 plan is now built and demoed.

## 2026-06-23 — Session 8: Phase 2 M7 — Media agent (mock)

- New `backends/media.py`: `Media` mock — `play(track)` sets
  `current_track`/`playing=True`; `pause()` raises if nothing is playing,
  no-ops with "Already paused" if already paused, else flips `playing` and
  returns `Paused — <track>.`; `now_playing()` returns `Playing|Paused —
  <track>.` or `Nothing playing.`; `strip()` renders `[media] <track> ·
  playing|paused`.
- `bridge.py`: `Bridge.__init__` constructs `self.media = Media()`; new
  routes `play_track`, `pause_media`, `now_playing`. `strips()` appends
  `self.media.strip()` after telephony/productivity, still capped at 3 —
  media is the first strip dropped under budget pressure since it's the
  least urgent of the four.  `_translate` gained a case for the three new
  tools.
- `intent.py`: new grammar `play (.+)` → `play_track`; `pause(?: music)?` →
  `pause_media`; `what's playing` / `now playing` → `now_playing`. `HELP`
  updated.
- Extended `shell/demo.txt`: `play some jazz` → `what did i miss` (proves
  the media strip survives an unrelated turn) → `pause`. Verified
  end-to-end with the timer strip also active (budget-sharing works).
  Demo passes.
- Updated `shell/README.md` ("What works" + architecture tree) and
  `tasks.md` (M7 checked off).
- M7 done. Next up per `plans.md`: M8 (Tier 2 stub + two-model routing).

## 2026-06-23 — Session 7: Phase 2 M6 — Android container (mock) + app allowlist

- New `backends/android.py`: `AndroidContainer` mock with `installed`
  (`whatsapp`, `instagram`) and `allowlist` (`whatsapp` by default) sets.
  `is_installed`/`is_allowed` check membership; `enable(app)` raises if not
  installed, no-ops if already enabled, otherwise adds to the allowlist and
  returns the PRD §19.9 confirmation line (`Enabled: <app>. It will route
  silently from now on.`); generic `send(app, contact, body)` returns
  `Sent to <contact> — <DisplayName>.`
- `bridge.py`: `send_message` now checks `self.android.is_installed(channel)`
  before falling back to telephony/SMS — if the channel is a detected
  container app, it must also be allowlisted or the call raises
  `PermissionError` translated to `Couldn't send it — <app> isn't enabled
  yet — try \`enable app <app>\`.`. New `enable_app` route calls
  `android.enable`. `_translate` gained an `enable_app` case.
  `Bridge.__init__` now constructs `self.android = AndroidContainer()`.
- `intent.py`: `_split_channel` gained a `via` keyword alongside
  `through`/`on` (`message lena via whatsapp`); new `enable app (.+)`
  grammar → `ToolCall("enable_app", {"app": ...})`. `HELP` updated.
- `main.py`: `CORRECTION_RE` extended to accept `whatsapp` alongside
  `primary`/`secondary`; `_correct()` branches on the corrected value —
  `whatsapp` swaps the last `send_message`'s `channel` slot instead of
  `sim` (only valid for `send_message`; calls reject the correction in
  language).
- Extended `shell/demo.txt`: `message mom take it easy` → `no, whatsapp`
  (channel-correction, succeeds since WhatsApp is allowlisted by default)
  → `message philip sharma hey on instagram` (fails, not enabled) →
  `enable app instagram` → same message (now succeeds). Verified end-to-end,
  demo passes.
- Updated `shell/README.md` ("What works" + architecture tree) and
  `tasks.md` (M6 checked off). PRD §19.9 / WIF-014 already recorded last
  session — no further doc changes needed there.
- M6 done. Next up: M7 (mock Media agent) per `plans.md`.

## 2026-06-17 — Session 6: Phase 2 planning

- Phase 1 (M1–M5) confirmed complete; user agreed to begin scoping Phase 2
  ("Android Container + Core Agents", PRD §16) rather than continue tweaking
  Phase 1. Asked the user whether to mock everything, wire a real Tier 2 API,
  or just plan first — chose **just plan, don't build yet**.
- Wrote a detailed Phase 2 plan in `plans.md`, replacing the old placeholder
  section: stack-decision table (Android container, WhatsApp channel
  routing, Media agent, Tier 2 stub, User memory layer — all mocked behind
  real interfaces, mirroring the Phase 1 mock-backend pattern), an
  architecture-additions sketch (`tier2.py`, `user_memory.py`,
  `backends/android.py`, `backends/media.py`), four new milestones (M6–M9),
  and an explicit out-of-scope list (real Waydroid/Anbox, real WhatsApp
  account, real Tier 2 API calls, ROM packaging/hardware — all blocked by
  the sandbox having no Android runtime, no WhatsApp credentials, and no
  wired model API key).
- Mirrored the new milestones into `tasks.md` under a "Phase 2 — Android
  Container + Core Agents" section (M6 Android container, M7 Media agent,
  M8 Tier 2 stub, M9 User memory layer), each broken into concrete unchecked
  work items.
- No code changes this session — planning only, per user's explicit choice.
  Next session should start M6 (mock `AndroidContainer` backend + WhatsApp
  channel routing) once the user confirms the plan.
- Follow-up design discussion: explored a universal rendering-layer idea
  (apps stay installed in the container but every app's content, not just
  outbound actions, is normalized into typirOS's one plain text style —
  closer to a screen-reader-to-chat pipeline than the Bridge Layer's current
  command-only routing) and a LightOS/typirOS merge idea (LightOS reaches
  distraction-freedom by *subtracting* apps; typirOS reaches it by
  *abstracting* them — a merge would add a curated default tool/app
  allowlist gating the Phase 2 `AndroidContainer` backend, with a deliberate
  `enable app X` opt-in for anything outside it). Logged as **WIF-014**
  (parked, P2) — needs a PRD-level decision before it changes M6's backend
  contract. No plans.md/tasks.md changes yet; current Phase 2 plan stands
  until that decision is made.
- User decided: accept the merge. Added **PRD §19.9 "Curated App Allowlist —
  Friction by Design for Container Apps"** (amends §7's Strategy A, which
  previously said container apps are "silently invoked... the moment
  they're detected"). New default: a curated allowlist (seeded with
  WhatsApp) gates the container; anything else detected is installed but
  inert until a deliberate `enable app <name>` command. Phase 2's success
  metric reframed from "any detected app works invisibly" to "only
  sanctioned apps work invisibly, and granting a new one is a conscious
  act." Updated `plans.md` (M6 stack-decision row + milestone description)
  and `tasks.md` (M6 work items: `is_allowed` check, default allowlist,
  `enable app` grammar, non-allowlisted dispatch failing in language) to
  build the gate alongside the `AndroidContainer` mock, not as a later
  bolt-on. WIF-014 moved from parked to accepted.

## 2026-06-16 — Session 5: Phase 1 M5 — Textual TUI shell

- New `shell/typiros_shell/tui.py`: `TypirApp(App)` with five stacked widgets —
  status bar, strips bar, `RichLog` chat history, chips bar, input row (indicator
  + `Input`). Replaces the line REPL without touching intent/bridge/backends.
- Grayscale-first, e-ink-friendly CSS: `#111111` background, `#e0e0e0` text,
  `#444444` borders — no colour highlights anywhere (PRD §19.4).
- Status bar turns `typirOS 0.1  ·  focus: <label>` during a focus session.
- Strips bar (focus/call/timer) hidden when empty; auto-refreshed every 0.5s
  via `set_interval`, so the timer countdown and focus strip stay live.
- Chips bar shows disambiguation options (`[1] Philip Sharma …`) only while
  `memory.pending.options` is non-empty; hides after selection.
- Quiet indicator (`•N`) lives in the input row and is suppressed during focus.
- Auto-expiry and auto-digest handled in the 0.5s poll (same logic as REPL).
- `__main__.py` checks for `--tui` flag; existing line REPL is unchanged fallback.
- Headless Textual test (`app.run_test()`) validates the full
  call → disambiguation → body-capture → focus session flow.
- Phase 1 (M1–M5) now complete. M4 (real backends) is a separate track
  requiring PinePhone/ModemManager hardware.

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
