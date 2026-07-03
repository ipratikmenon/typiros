# typirOS — Progress Log

Reverse-chronological. Every working session gets an entry.

---

## 2026-07-03 — Session 22: PRD v1.3 — the Power-User Compact (§20)

- Excavation pass over the whole PRD, per the founder's brief: what more
  would make typirOS the next big thing for nerds — a revolution, not an
  increment. Ran an independent brainstorm alongside a manual pass; merged,
  deduplicated against the PRD and the parked what-ifs backlog, and landed
  on 18 new ideas in four pillars.
- The core insight the addendum is built on: the PRD's founding principle
  ("total opacity of mechanism") is exactly wrong for the hacker/self-hoster
  audience — they don't trust what they can't inspect — and that tension is
  the product opportunity. Thesis: **opacity by default, sovereignty on
  demand** — the first phone that is yours the way your terminal is yours.
  Inspectability, self-hosting, and user programmability are things the
  incumbents structurally can't ship, which is what makes it defensible.
- New **PRD §20 — The Power-User Compact (v1.3)**, 18 sections in four
  pillars: **Glass Box** (Glasnost `/why` traces, Open Skull editable
  memory, Egress Ledger, `/airgap` hard mode), **Programmable Substrate**
  (Pipes, Hooks, The Wire/`typir` CLI, Webhook Inbox, Inline REPL),
  **Sovereign Stack** (BYOM Tier 2, Phone-as-Code dotfiles, tpkg package
  manager, The Forge self-written tools), **Native to Nerd Infrastructure**
  (Home agent, Matrix channel, Mesh Sync, grep-your-life, `/attest`).
  §20.19 ranks them: launch pillars are Glasnost + BYOM + Pipes + Hooks +
  The Wire. Version bumped 1.2 → 1.3.
- User decisions (asked): all 18 go into the PRD (not a curated subset),
  and scope the build now — so `plans.md` gained a **Phase 6 Plan** with a
  sandbox-feasibility table over all 18 and milestones M21–M28 (Glasnost
  first: highest evangelism-per-engineering-hour), and `tasks.md` gained
  the matching Phase 6 section, all `[ ]` todo.
- What-If Protocol kept honest: all 18 logged as WIF-018–WIF-035, accepted
  → PRD §20.x with phase estimates — same paper trail §19 left (this
  session's protocol quota satisfied eighteen times over).
- Docs-only session; re-ran `demo.txt` end-to-end anyway per the working
  agreement — exit 0.

## 2026-06-24 — Session 21: Phase 4 formally closed

- Fixed a stale doc: `tasks.md`'s M18 bullet still described the
  superseded plaintext-temp-file encryption approach (replaced during
  M16's self-audit with `sqlite3.serialize()`/`deserialize()`). Rewrote
  it to match what actually shipped.
- Added explicit M19 (custom Android ROM packaging) and M20 (battery
  optimization) entries to `tasks.md`, both marked `[-]` dropped rather
  than left as an implicit gap — both need real hardware/AOSP this
  sandbox can't provide, and no mock would be a meaningful prototype of
  either. Added a closing "Phase 4 complete" line summarizing M16–M18
  shipped, M19/M20 dropped.
- `plans.md`: marked the Phase 4 heading "✅ complete," rewrote the
  Milestones subsection with full summaries for M16/M17/M18 and explicit
  dropped lines for M19/M20, renamed the out-of-scope list heading to
  name M19/M20 directly, and added a caveat that M17's numbers are a
  software-path sanity check, not a target-hardware guarantee.
- `shell/README.md`: top heading and intro now say "Phases 1–4
  prototype," summarizing that every sandbox-feasible Phase 4 milestone
  (security audit, performance profiling, real encryption at rest) is
  done, with a pointer to `plans.md` for the two hardware-only items
  that stay out of scope and a note that Phase 5 (hardware) is next.
- Re-ran `demo.txt` end-to-end after this documentation-only batch —
  exit 0, no regression (expected; no code touched this session).
- Phase 4 is now fully and formally closed.

## 2026-06-24 — Session 20: Phase 4 M17 — Tier 1 performance profiling

- Added `benchmark.py`: times `intent.parse()` alone (the literal Tier 1
  deterministic-grammar stage) and a full `Shell.handle()` turn (parse +
  Bridge dispatch + translation) across one representative phrase per
  grammar branch in `intent.py`, 200 reps each, reporting mean/p50/p95/max.
  Pre-unlocks the Biometric Gate's `finance`/`episodic` domains first so
  `balance`/payment/`history` phrases measure steady-state dispatch rather
  than the one-time challenge pause — that pause is a real but separate
  cost, not representative of per-command latency.
- Gave `Shell.__init__` two optional `db_path`/`episodic_db_path`
  parameters (default behavior unchanged — still the stdin-tty-based
  `:memory:` vs. persistent-file choice) so the benchmark can force
  `:memory:` without touching disk or duplicating the constructor.
- Result on this sandbox's CPU: worst-case 0.36ms for `intent.parse()`
  alone, 0.74ms for a full turn — roughly 700x under the PRD's <500ms
  target. Stated the caveat plainly in the script's own output and in
  `README.md`: this confirms the software path has no gross inefficiency
  (deterministic regex/dict dispatch, no model inference in the loop),
  not a target-hardware latency guarantee — no real phone SoC available
  to benchmark against in this sandbox.
- Re-ran `demo.txt` end-to-end after the `Shell.__init__` signature
  change — exit 0, no behavior change for existing callers.
- This was the last Phase 4 milestone with no open decisions blocking it.
  All three Phase 4 milestones (M16, M17, M18) are now done — Phase 4 is
  complete except for the explicitly-out-of-scope hardware items (ROM
  packaging, battery optimization) noted in `plans.md`.

## 2026-06-24 — Session 19: Phase 4 M16 — Security audit

- Read through `bridge.py`, `main.py`, `biometric.py`,
  `backends/android.py`, `backends/finance.py` against PRD §15 (Container
  Isolation, Permission Model, Biometric Gate) — a real review with
  findings, not a confirmation pass.
- **Real gap fixed:** `SENSITIVE_TOOLS` (the Biometric Gate's tool→domain
  map) only listed `send_payment`. PRD §15 explicitly says "banking,
  payments, **personal data retrieval**" — `balance` and `episode_history`
  were dispatching with no gate at all. Added both: `balance` joins the
  `finance` domain (one unlock covers both balance checks and payments),
  `episode_history` gets its own `episodic` domain. Updated `demo.txt`
  (moved the `1234` earlier for `balance`, added one before `history with
  lena`) and re-ran end-to-end — exit 0, gate fires once per domain then
  stays silent, exactly as designed.
- **Latent landmine fixed:** `main.py`'s `_correct()` ("no, primary" /
  "no, secondary" / "no, whatsapp") called `self.bridge.dispatch()`
  directly instead of going through `_dispatch()`, which is the only
  place that checks `SENSITIVE_TOOLS` before letting a call through. Not
  exploitable today — `last_dispatch` only ever holds `make_call` or
  `send_message` — but it meant the gate's enforcement depended on every
  call site remembering to use the right method rather than being
  structurally uniform. Switched both call sites to `_dispatch()`.
- **Self-audit catch:** turned the same scrutiny on M18's own code from
  last session and found a real one — `crypto_store.py`'s first version
  decrypted the on-disk ciphertext into a plaintext temp file for sqlite3
  to open directly, and only deleted it in `close()`. A SIGKILL or OOM
  kill mid-session would have left that plaintext sitting in `/tmp`
  indefinitely — exactly the kind of crash-residue gap "encryption at
  rest" is supposed to prevent. Fixed by switching to stdlib
  `sqlite3.Connection.serialize()`/`deserialize()` (3.11+): the working
  connection is `:memory:` only, decrypted bytes go straight into it, and
  `serialize()` produces the bytes to re-encrypt on flush — plaintext
  never touches disk in any form. Verified no stray `.sqlite` files appear
  in `/tmp` after a run.
- **Confirmed compliant, no fix needed:** `AndroidContainer` has zero
  access to the User/Episodic memory objects (clean layering, never
  imported); `enable_app`'s container-then-user_memory write order means
  a rejected app (not installed) can't desync the two; container message
  history is RAM-only and doesn't survive a restart, which is *stricter*
  than PRD §15's "WhatsApp history may persist" allowance, not a
  violation of it.
- Next: M17 (Tier 1 performance profiling) — last Phase 4 milestone with
  no open decisions blocking it.

## 2026-06-24 — Session 18: Phase 4 M18 — Memory encryption at rest

- Asked the user whether to add a dependency to honor PRD §15's SQLCipher
  requirement, since `user_memory.py`/`episodic_memory.py` had been plain
  stdlib `sqlite3` since M9/M15 and the stack had been dependency-free
  through Phase 3. User chose to add one.
- New `crypto_store.py`: real AES-256-GCM via `cryptography` (now
  `shell/requirements.txt`'s one entry) — not a placeholder cipher.
  `sqlite3` can't write straight into ciphertext (that's what SQLCipher
  does at the page level, and there's no pure-Python build available
  here), so `EncryptedSqliteFile` opens a private temp-file copy for
  sqlite3 to use, decrypting the on-disk file into it at startup, and
  flushes fresh ciphertext back over the real path after every write —
  so a crash mid-session loses no more than a crash against a plain
  sqlite file would have. Per-file key stored alongside the db
  (`*.key`, `chmod 0o600`), generated on first use.
- Wired into `user_memory.py` and `episodic_memory.py`: any non-`:memory:`
  db path now goes through `crypto_store.py`; piped/scripted runs
  (`demo.txt`, the existing in-memory-DB convention) are unaffected since
  `:memory:` skips encryption entirely — there's no file to protect.
  `close()` on both classes now also cleans up the temp file.
- Verified directly (not just "it imports"): wrote a sim preference and a
  macro, confirmed the on-disk `user_memory.db` contains no `SQLite
  format 3` header and no plaintext `"secondary"` substring, then reopened
  the file in a fresh process and confirmed both values decrypt back
  correctly. Repeated the same check for `episodic_memory.db`. Re-ran
  `demo.txt` end-to-end (exit 0, no behavior change — it uses the
  in-memory path).
- Hit one sandbox-environment issue along the way: the system
  `cryptography` install was missing its `_cffi_backend` native
  dependency; `pip install --user cffi` fixed it. Unrelated to the code
  itself but worth knowing if `requirements.txt` install ever still fails
  with a `pyo3_runtime.PanicException`.
- Next: M16 (Bridge/container-isolation security audit) and M17 (Tier 1
  performance profiling) are next in Phase 4 — neither depends on
  anything decided here.

## 2026-06-24 — Session 17: Wrap-up pass + Phase 4 plan

- Wrap-up pass over tracking docs now that Phase 3 is fully done: moved
  WIF-015 (Compact mode reusing tier2's keyword-overlap scorer, shipped in
  M14) from Open/Parked to Accepted in `what-ifs.md` — it had shipped two
  sessions ago but never got moved. Logged a new WIF-016 (tappable strips
  expanding to their overlay, per PRD §9) to restore the What-If Protocol's
  one-per-session cadence, which had lapsed across M14 and M15. Fixed
  `shell/README.md`'s stale "Phase 1 prototype (runnable now)" heading and
  intro paragraph to reflect that the prototype now covers all of Phase 3.
- Scoped Phase 4 (PRD §16) against what's sandbox-feasible: ROM packaging
  and battery optimization need real hardware/AOSP and are out of scope;
  performance profiling and a Bridge/container-isolation security audit are
  genuinely buildable here. Wrote `## Phase 4 Plan — Hardening` into
  `plans.md` (mirrors the Phase 1–3 structure) and added M16 (security
  audit) / M17 (perf profiling) / M18 (memory encryption) skeletons to
  `tasks.md`.
- Surfaced one real decision point rather than deciding it solo: PRD §15
  requires SQLCipher-encrypted memory layers, but `user_memory.py` and
  `episodic_memory.py` both use plain stdlib `sqlite3` — the stack has been
  zero-dependency since Phase 1. Doing real encryption means adding the
  project's first external dependency; faking it would be worse than the
  current honest gap. Asked the user before writing any M18 code either
  way.
- Next: M16 (security audit) and M17 (perf profiling) don't depend on the
  encryption answer — start there once confirmed.

## 2026-06-24 — Session 16: Phase 3 M15 — Episodic memory + full-screen overlays

- New `episodic_memory.py`: `EpisodicMemory` — sqlite-backed (plain stdlib
  `sqlite3`, same encryption-deferred-to-Phase-4 stance as
  `user_memory.py`), `log(contact, summary)` / `recent(contact=None,
  limit=5)`. Each `log()` call also deletes rows older than 90 days, so
  the rolling window (PRD §13) is enforced on write rather than needing a
  separate cron/cleanup job. Scope decision: only contact-tied dispatches
  are logged (calls, messages, payments) — "relationship context" is the
  PRD's framing for this layer, and pure lookups (balance, weather,
  digest pulls, overlay views) don't add any.
- `bridge.py`: `Bridge.__init__` takes a fourth `episodic_memory`
  parameter; `make_call`, `end_call`, both `send_message` branches
  (telephony + Android container), and `send_payment` each call
  `self.episodic_memory.log(contact.name, result)` — logging the same
  one-line confirmation text the user already saw, so there's exactly one
  source of truth for "what happened" rather than a second summarization
  format. New `episode_history` tool (`_episode_history`) formats recent
  rows, scoped to one contact or global; new `show_overlay` tool
  (`_overlay_content`) returns the same plain-text content `now_playing`/
  `current_route` already produce, plus a canned placeholder string for
  photos (no gallery backend exists). Both gained `_translate` cases.
- `main.py`: constructs `EpisodicMemory` with the same ephemeral-for-piped-
  runs / persistent-for-interactive `:memory:` vs. `DEFAULT_DB_PATH`
  pattern already used for `UserMemory`, and passes it into `Bridge`.
- `intent.py`: new grammar `history` / `history with <contact>` →
  `episode_history` (reuses the same `contacts.resolve` disambiguation
  path as `_parse_call`/`_parse_message`/`_parse_payment` via a new
  `_parse_history` helper — ambiguous contacts get the same `[1]/[2]`
  chips); `show media|maps|photos|gallery` → `show_overlay`. `HELP`
  updated.
- New `overlays.py` (TUI-only): `OverlayScreen` base Textual `Screen` with
  a single `Binding("escape", ...)` dismiss gesture (PRD §8: "always one
  gesture away") popping back to chat; `MediaOverlay`/`MapsOverlay`/
  `PhotosOverlay` placeholder subclasses, `OVERLAYS` kind→class map.
- `tui.py`: `_on_submitted` peeks `intent.parse(raw)` (a second, throwaway
  parse — `Shell.handle` stays UI-agnostic and is the one that actually
  resolves/dispatches) purely to detect a `show_overlay` `ToolCall`; on a
  match it pushes the corresponding `Screen` from `OVERLAYS`, with the
  same response text `Shell.handle` already returned, as the overlay
  body. Verified headless via `App.run_test()`: pushing `media`/`photos`
  overlays and dismissing with Esc both work, and a running strip
  (`navigate to the airport` → `[nav]` strip) survives an overlay
  round-trip untouched. The line REPL (`main.py`) never pushes a screen —
  `show media`/etc. there just print the same content inline, per
  `plans.md`'s "TUI only" scope for M15.
- Extended `shell/demo.txt`: `history with lena`, `history`, `show media`,
  `show maps`, `show photos` appended after the M14 keyboard-mode lines.
  Demo passes end-to-end; no stray `.db` file.
- Updated `shell/README.md` ("What works", TUI section, architecture
  tree) and `tasks.md` (M15 checked off).
- M15 done — all 8 system agents, all 4 keyboard modes, both memory
  layers beyond Session, and full-screen overlays are now in place,
  completing every Phase 3 milestone in `plans.md`. Next: Phase 3 is
  fully done: confirm with the user before deciding what's next (a Phase
  3 wrap-up pass, or starting Phase 4 hardening items).

## 2026-06-24 — Session 15: Phase 3 M14 — Keyboard modes

- `tier2.py` refactored to resolve WIF-015: extracted `tokenize(text)` and
  `best_match(words, candidates)` as shared module-level functions;
  `route()` now calls them instead of inlining the keyword-overlap scoring
  logic, so Compact-mode abbreviation expansion can reuse the same "closest
  match" implementation instead of a second one.
- New `keyboard.py`: `KeyboardMode` enum (Compact/Standard/Voice First/
  Adaptive) and `Keyboard` class. No physical keyboard, mic, or
  accelerometer in this terminal prototype, so each mode is mocked at the
  behavior level: **Compact** matches raw input against a small canned
  `COMPACT_EXPANSIONS` dict via `tier2.best_match`; **Standard** is the
  unchanged default; **Voice First** has no live mic — `/voice <text>` is
  the proxy a real mic button would call; **Adaptive** reuses already-
  mocked state where it exists (`telephony.active_call`, `device.settings
  ["dnd"]`) and only mocks the two signals with no existing equivalent
  (`driving`, `motion`) via new `set_sensor`/`/sim sensor <signal> on/off`,
  switching per PRD §14's context table in priority order: active call >
  driving > motion > dnd > default voice nudge.
- `bridge.py`: `Bridge.__init__` constructs `self.keyboard = Keyboard()`;
  new route `set_keyboard_mode`; `strips()` appends `keyboard.strip(...)`
  last (lowest priority, same tier as media/navigation); `_translate`
  gained a case. `set_keyboard_mode` deliberately left out of
  `SENSITIVE_TOOLS` — switching modes isn't a sensitive action.
- `intent.py`: new grammar `keyboard mode <name>` → `set_keyboard_mode`.
  `HELP` updated.
- `main.py`: `/voice <text>` prefix re-enters `handle()` with the prefix
  stripped. Compact-mode expansion is consulted in `handle()` — **bug
  found and fixed during testing**: the first version called
  `expand_compact` on every input *before* `intent.parse`, so well-formed
  grammar could be wrongly re-matched against an unrelated abbreviation by
  keyword overlap — e.g. typing `end call` while in Compact mode scored a
  false-positive overlap (shared word "call") against the `"call lena"`
  entry in `COMPACT_EXPANSIONS` and got re-expanded into `call lena`,
  producing a spurious "already on a call" error instead of ending the
  call. Fixed by parsing normally first and only falling back to
  `expand_compact` when the result is `Escalate` (genuinely off-grammar),
  so on-grammar input is never second-guessed by the fuzzy matcher.
  `_simulate` gained a `sensor` sub-command parsing `/sim sensor <signal>
  on/off` into `keyboard.set_sensor`.
- Extended `shell/demo.txt`: Compact mode (`cl` → `end call`, verifying the
  fix), Standard, Adaptive with the full `/sim sensor` priority sequence
  (motion → driving → off → off), and `/voice call lena` → `end call`.
  Manually verified the other three Compact abbreviations (`mm`, `wdim`,
  bare `timer`) still expand correctly through the `Escalate`-gated
  fallback, and that `keyboard mode bogus` fails gracefully in language.
  Demo passes end-to-end; no stray `.db` file.
- Updated `shell/README.md` ("What works" + architecture tree) and
  `tasks.md` (M14 checked off).
- M14 done — all four keyboard modes implemented in one pass per the
  user's "yes for all 4 types". Next per `plans.md`: M15 (Episodic memory
  + full-screen overlays).

## 2026-06-23 — Session 14: Phase 3 M13 — Finance agent (mock) + Biometric gate

- New `biometric.py`: `BiometricGate` — `unlocked: set[str]` of confirmed
  domains; `is_unlocked(domain)`; `confirm(domain, passphrase)` checks
  against a fixed mock passphrase (`1234`, standing in for a fingerprint/
  face prompt with no biometric hardware in the sandbox) and adds the
  domain to `unlocked` on success. One unlock per session per domain
  (PRD §15) — once `finance` is confirmed, later payments don't re-prompt.
- New `backends/finance.py`: `Finance` mock — `balance()` returns a fixed
  starting balance; `send_payment(contact, amount)` raises on a non-positive
  amount or insufficient balance, else debits and returns a confirmation.
- `bridge.py`: new module-level `SENSITIVE_TOOLS = {"send_payment":
  "finance"}` map (tool → gate domain), imported by `main.py` so the Shell
  can pause a turn *before* dispatch — `Bridge.dispatch()` itself doesn't
  know about pending/turn-taking, so the gate check had to live one layer
  up, same boundary as the existing message-body-capture flow.
  `Bridge.__init__` constructs `self.finance = Finance()` and
  `self.biometric = BiometricGate()`; new routes `balance`, `send_payment`;
  `_translate` gained a case for both.
- `main.py`: new `Shell._dispatch(tool, args)` wraps `bridge.dispatch` —
  if the tool is in `SENSITIVE_TOOLS` and its domain isn't unlocked yet, it
  sets `memory.pending = Pending(tool, args, "biometric")` and returns
  `"Confirm with your passphrase to continue:"` instead of dispatching.
  All three ToolCall-dispatch call sites (`handle()`'s direct dispatch, and
  both branches of `_fill_pending`'s contact-resolution path) now go
  through `_dispatch` instead of `bridge.dispatch` directly, so a payment
  reached via contact disambiguation still gets gated. `_fill_pending`
  gained a `missing == "biometric"` branch: wrong passphrase returns "That
  didn't match — try again." and leaves the pending challenge active for a
  retry; correct passphrase clears pending, unlocks the domain, and
  dispatches the original tool call.
- `intent.py`: new grammar `balance\??` → `balance`; `send \$?<amount> to
  <contact>` → `send_payment` (reuses the same contact-resolution/
  disambiguation path as `_parse_call`/`_parse_message` via a new
  `_parse_payment` helper). `HELP` updated with a note about the passphrase.
- Extended `shell/demo.txt`: `balance` → `send 20 to mom` (triggers the
  challenge) → `1234` (confirms, dispatches) → `balance` (debited) → `send
  5 to mom` (now dispatches silently — domain already unlocked) after the
  M12 files lines. Manually verified the wrong-passphrase retry path and
  the insufficient-balance failure path outside the demo script (both
  fail gracefully in language). Demo passes end-to-end; no stray `.db`
  file.
- Updated `shell/README.md` ("What works" + architecture tree) and
  `tasks.md` (M13 checked off).
- M13 done — first sensitive-action gate in the codebase, enforced at the
  same Shell/Bridge boundary as the existing disambiguation-chip and
  message-body-capture flows. Next per `plans.md`: M14 (Keyboard modes).

## 2026-06-23 — Session 13: Phase 3 M12 — Files agent (mock)

- New `backends/files.py`: `Files` mock over a 5-entry in-process
  `MOCK_INDEX` (name + modified date). `find_file(query)` substring-matches
  case-insensitively against names — a single match returns `Found: <name>
  — modified <date>.`, multiple matches list each on its own line, no match
  raises `FileNotFoundError`. `recent_files(n=3)` sorts the index by
  modified date and lists the top N.
- `intent.py`: new grammar `recent files\??` → `recent_files`; `find files?
  (.+)` → `find_file`. `HELP` updated.
- `bridge.py`: `Bridge.__init__` constructs `self.files = Files()`; new
  routes `find_file`, `recent_files`. `_translate` gained a case returning
  `Couldn't find that — <detail>.` for both tools. No context strip — a
  file lookup is a one-shot result, not a persistent state like
  call/timer/media/nav.
- Extended `shell/demo.txt`: `find file budget` (single match) → `recent
  files` (top-3 listing) → `find file zzz` (graceful no-match) after the
  M11 information lines. Verified end-to-end; demo passes; no stray `.db`
  file.
- Updated `shell/README.md` ("What works" + architecture tree) and
  `tasks.md` (M12 checked off).
- M12 done. Next per `plans.md`: M13 (Finance agent mock + Biometric gate
  — first sensitive-action gate in the codebase).

## 2026-06-23 — Session 12: Phase 3 M11 — Information agent + Tier 1 graduation

- New `backends/information.py`: `Information` mock — `weather(city)`
  returns canned conditions for four cities, falling back to a generic
  mock reading for anything else; `fact(query)` looks up a small canned
  dict (`capital of france` → `Paris.`, etc.), raising `ValueError` for
  anything outside it; `time()` returns the current local time.
- `intent.py`: new grammar `(?:what's the )?weather (?:in|for|at) (.+)` →
  `get_weather`; `what's/is the time` → `get_time`; `what's/is the capital
  of (.+)` → `get_fact`. Deliberately phrased to also match the exact
  off-grammar phrasing the Tier 2 stub previously caught (`what's the
  weather in paris`) — proves the stub-to-native graduation PRD §18
  describes rather than adding a parallel grammar shape.
- `bridge.py`: `Bridge.__init__` constructs `self.information =
  Information()`; new routes `get_weather`, `get_time`, `get_fact`.
  `_translate` gained a case returning `Don't have that yet — <detail>.`
  for the three new tools, so an unrecognized fact (`capital of mars`)
  fails gracefully in language instead of crashing — distinct from the
  Tier 2 escalation path, which still handles anything that doesn't match
  the new grammar at all (`send an email to mom`).
- Extended `shell/demo.txt`: the existing `what's the weather in paris`
  line now resolves natively (previously it printed
  `[tier2-stub] typiros-information would handle: ...`); added `what's the
  capital of france` (native hit) and `what's the capital of mars` (native
  miss, graceful failure) after the M10 navigation lines. Verified
  end-to-end — `send an email to mom` still demonstrates Tier 2 escalation
  for anything outside the graduated subset; demo passes; no stray `.db`
  file.
- Updated `shell/README.md` ("What works" + architecture tree) and
  `tasks.md` (M11 checked off).
- M11 done. Next per `plans.md`: M12 (Files agent mock).

## 2026-06-23 — Session 11: Phase 3 M10 — Navigation agent (mock)

- New `backends/navigation.py`: `Navigation` mock — `navigate(destination)`
  sets `destination`/`eta_minutes` (random 5–45 to vary the mock) and
  returns `Navigating to <destination> — ETA <N> min.`; `eta()` raises if
  not navigating, else returns the ETA line; `current_route()` returns the
  same status or `Not navigating anywhere.`; `stop()` clears state and
  raises if nothing was active; `strip()` renders `[nav] <destination> ·
  ETA <N> min`.
- `bridge.py`: `Bridge.__init__` constructs `self.navigation = Navigation()`;
  new routes `navigate`, `nav_eta`, `current_route`, `stop_navigation`.
  `strips()` appends `navigation.strip()` last — lowest priority of the four
  agent strips, same reasoning as media being the first dropped under
  budget pressure. `_translate` gained a case for the four new tools.
- `intent.py`: new grammar `navigate (?:to )?(.+)` → `navigate`;
  `eta`/`how far/long (away)?` → `nav_eta`; `where am i going` →
  `current_route`; `stop|end navigat(ion|ing)` → `stop_navigation`. `HELP`
  updated.
- Extended `shell/demo.txt`: `navigate to the airport` → `eta` → `where am
  i going` → `stop navigating`, after the existing media/tier2 lines —
  proves the nav strip shares the max-3 budget with the still-active timer
  and media strips. Verified end-to-end; demo passes; confirmed no stray
  `.db` file left behind by the piped run.
- Updated `shell/README.md` ("What works" + architecture tree, M1–M15
  reference) and `tasks.md` (M10 checked off).
- M10 done. Next per `plans.md`: M11 (Information agent + Tier 1
  graduation of a weather/fact subset out of the Tier 2 stub).

## 2026-06-23 — Session 10: Phase 3 planning

- User confirmed Phase 2 (M6–M9) complete and asked to plan Phase 3 ("Full
  Agent Coverage + Keyboard System", PRD §16) — planning only, mirroring how
  Phase 2 was scoped before any code was written.
- Re-read PRD §8 (Full-Screen Overlays), §12 (System Agents table), §14
  (Keyboard System / Four Modes / Adaptive's sensor-signal table), §15
  (Privacy & Security — SQLCipher, Biometric Gate, Container Isolation),
  §16 (Phase 3 bullet list + success metric) to scope concretely.
- Wrote **Phase 3 Plan** into `plans.md`: sandbox-constraint paragraph (no
  GPS/maps API, no real filesystem container, no banking API, no biometric
  or motion/ambient-mic hardware — all mocked behind real interfaces, same
  pattern as Phase 1/2, with one exception: Textual's overlay push/dismiss
  mechanism is real since the TUI already exists, only overlay *content* is
  placeholder), a stack-decision table, an architecture-additions sketch
  (`keyboard.py`, `biometric.py`, `episodic_memory.py`, `overlays.py`,
  `backends/navigation.py`, `backends/information.py`, `backends/files.py`,
  `backends/finance.py`), six new milestones (M10–M15), and an explicit
  out-of-scope list.
- Milestones: M10 Navigation agent, M11 Information agent (graduates a
  weather/fact subset out of the Tier 2 stub into real Tier 1 grammar — the
  stub-to-native lifecycle PRD §18 describes), M12 Files agent, M13 Finance
  agent + Biometric gate (first sensitive-action gate in the codebase,
  enforced in the Bridge Layer like the M6 allowlist check), M14 Keyboard
  modes (Compact/Standard/Voice First/Adaptive — modeled as input-handling
  *behaviors* rather than on-screen layouts, since this is a terminal
  prototype with no touchscreen or mic; Adaptive driven by a new `/sim
  sensor <signal> on/off` mock, same shape as the existing `/sim` event
  injection from M3), M15 Episodic memory (sqlite, same plain-now/
  encrypt-later caveat as M9's User memory) + full-screen overlays (Textual
  `Screen` push/dismiss, TUI-only).
- Mirrored the six milestones into `tasks.md` under a new "Phase 3 — Full
  Agent Coverage + Keyboard System" section, all unchecked.
- Logged **WIF-015** (parked, P3): reuse `tier2.py`'s keyword-overlap
  scorer for Compact-mode abbreviation expansion (M14) instead of building
  a second "closest match" implementation — needs a decision on whether the
  scorer moves to a shared module before M14 starts.
- No code changes this session — planning only, per the user's request and
  the established Phase 2 precedent (plan first, build after a separate
  confirmation).

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
