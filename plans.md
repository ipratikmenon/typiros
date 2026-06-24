# typirOS — Plans

Detailed planning document. Strategy lives here; granular work items live in
[tasks.md](tasks.md); the historical record lives in [progress.md](progress.md);
speculative features live in [what-ifs.md](what-ifs.md).

---

## Working Agreement

1. **Every working session updates** `tasks.md` (work item states) and
   `progress.md` (dated log entry). No silent work.
2. **The What-If Protocol runs continuously** (PRD §19.8): each session, agents
   log at least one speculative "what if?" to `what-ifs.md`. Triage decisions
   (accept → tasks.md / park / reject) are recorded there.
3. **Accepted what-ifs that change product behavior** are folded into PRD.md
   as numbered addenda (§19 was the first).
4. **The prototype must always run.** Every commit leaves `shell/` in a state
   where the end-to-end demo passes.

---

## North Star

A distraction-free, **typing-first** mobile OS where the entire UI is a chat
window (PRD v1.2). Pull-based notifications, deterministic typed fast paths,
text-only minimalist output, voice demoted to an accessibility layer.

---

## Phase 1 Plan — Proof of Concept (current)

**Goal (PRD §16):** make a call, send an SMS, set an alarm, change a setting —
all from the chat window, end to end.

### Stack decision

| Decision | Choice | Rationale |
|---|---|---|
| Language | Python 3.11, stdlib only | Runs anywhere (including this sandbox), zero deps, fast iteration; UI layer is swappable later |
| UI | Line-based REPL first, TUI (Textual) second, mobile shell (Linux/GTK) third | Prove the interaction loop before investing in chrome |
| Tier 1 engine | Deterministic grammar pre-parser (PRD §19.7) now; local LLM (Phi-3/Gemma) later | Typed input is clean text — the grammar covers Phase 1 verbs without a model |
| Backends | Mock implementations behind the Bridge interface | Same interface real backends (ModemManager, dbus, AOSP container) will implement |

### Architecture (shell/)

```
shell/typiros_shell/
├── main.py           # REPL loop: input bar, strips header, quiet indicator
├── intent.py         # Tier 1 deterministic parser: grammar (§10) + slash commands (§19.3)
├── bridge.py         # Bridge Layer: routes tool calls, translates errors (§6)
├── contacts.py       # Contact store, prefix resolution, 2-chip disambiguation (§11)
├── memory.py         # Session memory: last contact, last SIM, pending action (§13)
├── notifications.py  # Quiet queue + /missed digest (§19.1)
└── backends/
    ├── telephony.py  # make_call, send_message (mock)
    ├── device.py     # set_setting (mock)
    └── productivity.py # create_reminder, set_alarm, timers (mock)
```

### Milestones

- **M1 — Core loop (this session):** REPL + grammar parser + bridge + mock
  backends. Success metric demo passes scripted.
- **M2 — Conversation depth:** session memory ("call him back"), corrections
  ("no, Secondary"), message-body capture flow, macros.
- **M3 — Quiet layer:** simulated inbound events, digest mode, focus sessions.
- **M4 — Real backends:** swap telephony mock for ModemManager/ofono on a
  Linux Mobile target; Tier 1 LLM fallback for off-grammar input.
- **M5 — TUI shell:** persistent strips, autocomplete chips above input,
  e-ink-friendly rendering.

## Phase 2 Plan — Android Container + Core Agents

**Goal (PRD §16):** send a WhatsApp message without the user ever seeing the
WhatsApp UI — the success metric is the container being functionally
invisible, reachable through the same chat-window grammar as everything else.

### Sandbox constraint

This dev environment has no AOSP/Waydroid runtime, no real WhatsApp
account/API, and no wired Tier 2 model credentials. Per the Phase 1 working
agreement ("mock backends behind the Bridge interface, same shape real
backends will implement"), Phase 2 continues that pattern one layer up:
container and Tier 2 are mocked behind real interfaces, so M4-style swap-in
later is a backend replacement, not a rewrite.

| Decision | Choice | Rationale |
|---|---|---|
| Android container | Mock `AndroidContainer` backend exposing `send_whatsapp(contact, body)`, `is_installed(app)`, gated by an `is_allowed(app)` allowlist check (PRD §19.9) | Mirrors `telephony.py`'s mock-now/real-later pattern; real backend would be a Waydroid/Anbox bridge. Detected ≠ dispatchable — only allowlisted apps route silently by default |
| App allowlist | Default allowlist seeded with `whatsapp`; `enable app <name>` grammar adds an app, one-line confirmation, no settings screen | PRD §19.9 — restraint by policy, not UI; merges LightOS's subtraction-based minimalism with typirOS's abstraction (WIF-014, accepted) |
| WhatsApp routing | Bridge Layer treats `whatsapp` as a channel alongside `primary`/`secondary` SIM in `send_message` | Reuses existing channel-selection + correction-flow (`no, whatsapp`) machinery from M2, no new grammar shape |
| Media agent | Mock `Media` backend: `play(track)`, `pause()`, `now_playing()` — printed strip, no real audio | Same mock-strip pattern as `productivity.py` timers |
| Tier 2 escalation | Stub `Tier2` module: routes off-grammar input through the same `agents/*.yaml` manifests, returns a canned/echo response tagged `[tier2-stub]` | Proves the two-model routing shape without requiring API credentials in this sandbox; swappable for a real `ant` call |
| Memory: User layer | SQLite file (`shell/typiros_shell/user_memory.db`, stdlib `sqlite3`) for contacts/preferences/macros that persist across runs | Session memory is already RAM-only; User layer per PRD §13 needs durability — sqlite needs zero new deps |

### Architecture additions (shell/)

```
shell/typiros_shell/
├── tier2.py             # Stub Tier 2 router: off-grammar input → canned/echo response
├── user_memory.py        # SQLite-backed User memory layer (contacts, prefs, macros)
└── backends/
    ├── android.py        # AndroidContainer mock: send_whatsapp, is_installed
    └── media.py           # Media mock: play, pause, now_playing
```

### Milestones

- **M6 — Android container (mock) + app allowlist:** `AndroidContainer`
  backend; `message X via whatsapp` / `message X` (when only WhatsApp is
  reachable) grammar; WhatsApp joins the channel set alongside
  primary/secondary SIM, including `no, whatsapp` correction. Gated by a
  default allowlist (PRD §19.9): only allowlisted apps dispatch silently;
  `enable app <name>` is the deliberate opt-in for anything else detected in
  the container.
- **M7 — Media agent (mock):** `play <track>`, `pause`, `what's playing`
  grammar; now-playing context strip (max-3 strip budget, same as call/timer).
- **M8 — Tier 2 stub + two-model routing:** off-grammar input that fails Tier
  1 routes to `tier2.py` instead of failing in language; canned/echo response
  clearly tagged as a stub; manifest-driven routing reads `agents/*.yaml` to
  prove the wiring without a live API call.
- **M9 — User memory layer:** sqlite-backed contacts/preferences/macros that
  persist across process restarts; session memory unchanged (RAM, per-run);
  migration path: existing in-memory `Contacts`/macros seed the DB on first
  run.

### Explicitly out of scope for Phase 2 (sandbox)

- Real Waydroid/Anbox container, real WhatsApp account/session
- Real Tier 2 model API calls (no credentials in this environment)
- ROM packaging, physical keyboard input, hardware strips (Phase 5)

---

## Phase 3 Plan — Full Agent Coverage + Keyboard System

**Goal (PRD §16):** all 8 System Agents operational, all 4 keyboard modes
implemented (including Adaptive's sensor-driven switching), an Episodic
memory layer, full-screen overlays, and biometric gating for sensitive
actions — success metric is "all daily smartphone tasks completable through
the chat window."

### Sandbox constraint

This dev environment has no GPS/maps API, no real filesystem container, no
banking/payments API, no fingerprint/face sensor, and no accelerometer or
ambient-mic hardware. Phase 3 continues the Phase 1/2 pattern exactly: every
new agent and sensor is a mock behind the real interface PRD §5/§14/§15
describe, so a later hardware swap-in is a backend replacement, not a
rewrite. The one exception is full-screen overlays — Textual is a real
terminal UI framework already in the stack (M5), so the overlay *mechanism*
(push/dismiss, single gesture back to chat) can be genuinely built; only the
*content* (maps tiles, photos, video frames) is placeholder.

### Stack decision

| Decision | Choice | Rationale |
|---|---|---|
| Navigation agent | Mock `Navigation` backend: `navigate(destination)`, `eta()`, `current_route()` — printed strip, no real routing | Same printed-strip mock pattern as `media.py`; real backend would be a maps API or container app |
| Information agent | Promote a small canned subset (`weather in <city>`, simple fact lookups) out of the Tier 2 stub into a real Tier 1 grammar + mock `Information` backend; everything else still escalates to `tier2.py` | Demonstrates an agent graduating from "stub-routed" to "natively handled" — the exact lifecycle PRD §18 describes for Tier 1 grammar growth |
| Files agent | Mock `Files` backend: `find_file(query)`, `recent_files()` over a small in-process mock index | No real filesystem container available; same shape a real on-device index would expose |
| Finance agent | Mock `Finance` backend: `balance()`, `send_payment(contact, amount)` | Container-backed per PRD §12; first agent that needs the Biometric Gate |
| Biometric gate | Mock `biometric.py`: typed-passphrase challenge stands in for a fingerprint/face prompt; one unlock per session per domain (PRD §15) | No biometric hardware in sandbox; gate sits in the Bridge Layer ahead of dispatch, same enforcement point as the M6 allowlist check |
| Keyboard modes | `keyboard.py`: session-level `KeyboardMode` enum — Compact (abbreviation expansion reusing `tier2.py`'s keyword-overlap scorer), Standard (current default), Voice First (`/voice <text>` text-proxy for a transcribed utterance, no mic), Adaptive (auto-switches from mocked sensor signals) | No physical keyboard hardware or mic in this terminal prototype — modes become input-handling *behaviors*, not on-screen layouts, until a real touchscreen/keyboard shell exists |
| Adaptive sensor signals | `/sim sensor <signal> on/off` (e.g. `driving`, `call-active`) flips `KeyboardMode` per PRD §14's context table | No accelerometer/ambient-mic hardware; mirrors the existing `/sim` event-injection pattern from M3 |
| Episodic memory | `episodic_memory.py`: separate sqlite file, rolling 90-day window, one summarized row per dispatched action | Same plain-sqlite-now/encrypt-later caveat already flagged in `user_memory.py` (M9) — encryption stays a Phase 4 item |
| Full-screen overlays | `overlays.py`: Textual `Screen` subclasses (Media/Maps/Photos placeholders) pushed via `app.push_screen()`, dismissed by a single key (Esc) back to chat | TUI (M5) already runs Textual — overlay push/dismiss mechanics are real; only the rendered content is a placeholder |

### Architecture additions (shell/)

```
shell/typiros_shell/
├── keyboard.py          # KeyboardMode enum, mode switching, Adaptive sensor rules
├── biometric.py         # Mock biometric challenge gate (§15), one unlock/session/domain
├── episodic_memory.py   # sqlite-backed rolling 90-day episodic summaries
├── overlays.py          # Textual Screen subclasses: Media/Maps/Photos placeholders (TUI only)
└── backends/
    ├── navigation.py    # Navigation mock: navigate, eta, current_route
    ├── information.py   # Information mock: canned weather/fact lookups (Tier 1 subset)
    ├── files.py         # Files mock: find_file, recent_files over a mock index
    └── finance.py       # Finance mock: balance, send_payment — gated by biometric.py
```

### Milestones

- **M10 — Navigation agent (mock):** `navigate <destination>` / `eta` /
  `where am I going` grammar; `[nav]` context strip joins the max-3 budget.
- **M11 — Information agent (mock) + Tier 1 graduation:** `weather in
  <city>` and a small fact-lookup set move from the Tier 2 stub into real
  Tier 1 grammar backed by a mock `Information` backend; everything else
  still escalates to `tier2.py`.
- **M12 — Files agent (mock):** `find file <query>` / `recent files`
  grammar over a small mock index.
- **M13 — Finance agent (mock) + Biometric gate:** `balance` / `send <amt>
  to <contact>` grammar; first wiring of `biometric.py`'s mock challenge
  ahead of dispatch, one unlock per session per domain (PRD §15).
- **M14 — Keyboard modes:** `KeyboardMode` enum (Compact/Standard/Voice
  First/Adaptive); `keyboard mode <name>` to switch manually; Compact's
  abbreviation expansion; `/voice <text>` proxy; `/sim sensor <signal>
  on/off` drives Adaptive's automatic switching per PRD §14.
- **M15 — Episodic memory + full-screen overlays:** `episodic_memory.py`
  rolling 90-day summarized log; `overlays.py` Textual screens for
  Media/Maps/Photos, single-gesture dismiss back to chat (TUI only — no
  overlay support in the line REPL).

### Explicitly out of scope for Phase 3 (sandbox)

- Real GPS/maps API, real routing/traffic data
- Real banking/payments API, PCI compliance, real money movement
- Real fingerprint/face biometric hardware
- Real accelerometer/ambient-mic sensors
- Real filesystem container / on-device file index
- SQLCipher encryption for User or Episodic memory (Phase 4 hardening item)

---

## Phase 4 Plan — Hardening

PRD §16's Phase 4 bullets, against what's actually buildable in this sandbox:

| PRD §16 bullet | Sandbox-feasible? | Why |
|---|---|---|
| Package as custom Android ROM (AOSP base) | No | Needs a real AOSP build environment and target hardware; nothing to prototype in a Python shell |
| Battery optimization for continuous AI runtime | No | Needs real hardware power telemetry; not modelable against a mock |
| Performance profiling — <500ms Tier 1 response | Partial | Can benchmark Tier 1 parse + Bridge dispatch latency on sandbox CPU; honest caveat that this isn't "target hardware" per the PRD's own phrasing |
| Security audit of Bridge Layer + container isolation | Yes | A real code review of `bridge.py`/`android.py` against PRD §15 (Container Isolation, Permission Model, Biometric Gate), with actionable stdlib-only fixes |

**Goal:** do the two genuinely sandbox-feasible items for real — a real benchmark, a
real code review — rather than mocking "hardening" the way earlier phases mocked
hardware. ROM packaging and battery optimization stay out of scope; they need
real hardware/AOSP, not a different mock.

### Open decision: memory encryption at rest (PRD §15)

PRD §15 specifies "All memory layers are stored on-device in SQLCipher-encrypted
databases." `user_memory.py` (M9) and `episodic_memory.py` (M15) both use plain
stdlib `sqlite3` — Python's stdlib has no AES/authenticated-encryption primitive,
so honoring this for real means adding the project's first dependency outside the
standard library (e.g. `cryptography` or `pysqlcipher3`). Faking it (e.g. a
reversible XOR "cipher") would be worse than not mentioning it — it isn't
security. This is the one stack decision Phase 4 can't make unilaterally; tracked
as a question to the user before any encryption work starts, not something to
implement silently in either direction.

### Milestones

- **M16 — Bridge Layer + container isolation security audit:** read through
  `bridge.py` and `backends/android.py` against PRD §15's Container Isolation /
  Permission Model / Biometric Gate requirements; document findings (gaps, not
  just confirmations) and fix what's fixable with stdlib only.
- **M17 — Tier 1 performance profiling:** a benchmark script timing grammar
  parse (`intent.parse`) + `Bridge.dispatch` across the full grammar surface,
  reported against the PRD's <500ms target with the sandbox-CPU caveat stated
  up front.
- **M18 — Memory encryption at rest (blocked on user decision above).**

### Explicitly out of scope for Phase 4 (sandbox)

- Custom Android ROM / AOSP packaging — needs real hardware build environment
- Battery optimization — needs real hardware power telemetry
- True target-hardware performance numbers — sandbox CPU isn't representative

---

## Risks / Watch Items

- **Grammar coverage ceiling:** deterministic parsing will miss phrasings; the
  escape hatch is the Tier 1 LLM (M4). Track misses in progress.md.
- **Mock drift:** mock backends must keep the exact signatures of PRD §5's tool
  manifest, or M4 swap-in becomes a rewrite.
- **Scope gravity:** the chat-shell is fun to over-build; M1–M3 stay
  terminal-only on purpose.
