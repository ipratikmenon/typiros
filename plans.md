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

## Phase 4 Plan — Hardening ✅ complete (2026-06-24)

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

### Stack decision: memory encryption at rest (PRD §15) — resolved

PRD §15 specifies "All memory layers are stored on-device in SQLCipher-encrypted
databases." `user_memory.py` (M9) and `episodic_memory.py` (M15) used plain
stdlib `sqlite3` — Python's stdlib has no AES/authenticated-encryption primitive,
so honoring this for real meant adding a dependency. Asked the user rather than
deciding solo or faking it; the user chose to add one. `cryptography` (AES-256-GCM)
is now the project's first dependency outside the standard library
(`shell/requirements.txt`), wired in via `crypto_store.py` — see M18.

### Milestones

- **M16 — Bridge Layer + container isolation security audit ✅:** read through
  `bridge.py`, `main.py`, `biometric.py`, `backends/android.py`, and
  `backends/finance.py` against PRD §15's Container Isolation / Permission
  Model / Biometric Gate requirements. Found and fixed three real gaps —
  `SENSITIVE_TOOLS` only covered `send_payment` (PRD §15 also names
  "personal data retrieval"; `balance`/`episode_history` now gated too);
  `_correct()` bypassed the gate by calling the Bridge directly instead of
  the gate-checking dispatch path; and M18's first cut at encryption left
  plaintext in a temp file on disk, caught by turning the same audit on
  the prior session's own code.
- **M17 — Tier 1 performance profiling ✅:** `benchmark.py` times
  `intent.parse` and a full `Shell.handle()` turn across every grammar
  branch, reported against the PRD's <500ms target with the sandbox-CPU
  caveat stated up front. Worst case observed: 0.74ms — ~700x under
  target on this hardware.
- **M18 — Memory encryption at rest ✅:** user chose to add `cryptography`
  as the project's first dependency; `crypto_store.py` does real
  AES-256-GCM via stdlib `sqlite3.serialize()`/`deserialize()` so
  plaintext never touches disk.
- **M19 — Custom Android ROM packaging — dropped (out of scope).**
- **M20 — Battery optimization — dropped (out of scope).**

### Explicitly out of scope for Phase 4 (sandbox) — M19/M20

- Custom Android ROM / AOSP packaging — needs real hardware build environment
- Battery optimization — needs real hardware power telemetry
- True target-hardware performance numbers — sandbox CPU isn't representative;
  M17's numbers are a software-path sanity check, not a hardware guarantee

---

## Phase 6 Plan — The Power-User Compact

**Goal (PRD §20, v1.3):** the "revolution for nerds" wave — *opacity by
default, sovereignty on demand*. Phase 5 (hardware) stays deferred and
independent; Phase 6 is pure software and proceeds in this sandbox the same
way Phases 1–4 did: real mechanisms where feasible, mocks behind real
interfaces where not. Full idea set and rationale: PRD §20.1–§20.19
(WIF-018–WIF-035).

### Sandbox feasibility over the 18 sections

| PRD § | Idea | Sandbox-feasible? | Why |
|---|---|---|---|
| 20.1 | Glasnost Mode (`/why`, `/trace`) | Yes | Bridge already produces dispatch records; retain a per-turn trace and pretty-print it |
| 20.2 | Open Skull (memory verbs) | Yes | sqlite layers exist (M9/M15); needs read/diff/forget verbs |
| 20.3 | Egress Ledger | Partial | No real network stack; mock backends can log attributed "egress" and expose the query verb |
| 20.4 | Local-Only Hard Mode | Yes | A flag the tier router honors + honest degradation copy + digest-queued escalations |
| 20.5 | Pipes | Yes | Pre-parser splits on `\|`; fold structured results through segments |
| 20.6 | Hooks | Yes | Tiny rule engine + mock event emissions (battery tick, inbound SMS) |
| 20.7 | The Wire | Yes (prototype) | The Shell loop is stdin/stdout already; a socket/CLI front-end is thin. Real key-auth hardening is P4-grade later work |
| 20.8 | Webhook Inbox | Yes (prototype) | Local HTTP endpoint feeding the existing quiet queue |
| 20.9 | Inline REPL | Yes | Restricted-`exec` sandbox; output joins the pipe grammar |
| 20.10 | Sovereign Tier 2 (BYOM) | Partial | `tier2.py` grows a provider interface; a real local-HTTP backend needs an inference box this sandbox lacks |
| 20.11 | Phone-as-Code | Yes | Config state serializes to plain text; `typir apply` reloads it |
| 20.12 | tpkg | Partial | Local `tpkg install ./pack.yaml` merging verbs/macros is buildable; registry + signing is not |
| 20.13 | The Forge | Thin | Mock generated-tool flow (write stub → show source → approve → hot-register); no real codegen without Tier 2 credentials |
| 20.14 | Home agent | Yes (mock) | Ninth agent over a mock HA backend with fake entities, same pattern as every other agent |
| 20.15 | Matrix channel | Thin | Mock channel only; real matrix-nio needs a homeserver |
| 20.16 | Mesh Sync | No | Real CRDTs/multi-device out of scope, same convention as ROM/battery in Phase 4 |
| 20.17 | grep-your-life | Yes | The shell sees every turn; append JSONL + query verb |
| 20.18 | `/attest` | No | Meaningless without a reproducible build to attest; design sketch only |

### Milestones

- **M21 — Glasnost Mode:** per-turn structured trace retained by the Bridge;
  `/why` pretty-prints the last one (parse → route → tool call → backend →
  latency); `/trace on|off` streams live. The highest
  evangelism-per-engineering-hour item — do it first.
- **M22 — Pipes:** `|` in the deterministic pre-parser; each segment parses
  normally; structured results fold left-to-right into the next segment's
  input slot.
- **M23 — Hooks:** `when <event>, <command>` / `every <interval>, <command>`
  grammar; tiny rule engine; mock backends emit events (battery tick, inbound
  SMS, focus start/end); `/hooks` lists/removes rules.
- **M24 — Open Skull:** `memory show` / `memory forget <fact>` /
  `memory edit` verbs over the existing User + Episodic sqlite layers.
- **M25 — Local-Only Hard Mode:** `/airgap on|off`; tier router refuses
  escalation while on; degradation in language; queued escalations surface in
  the next digest.
- **M26 — The Wire (prototype):** `typir` CLI / socket front-end driving the
  same `Shell` instance — proves the phone-as-addressable-node shape;
  real auth hardening deferred.
- **M27 — Power-substrate extras (grab-bag, each small):** grep-your-life
  JSONL lifelog + query verb; Inline REPL; Webhook Inbox (local HTTP →
  quiet queue); Phone-as-Code (`typir apply` over plain-text config);
  local-only `tpkg install <pack.yaml>`.
- **M28 — Home agent (mock) + BYOM provider seam:** ninth agent over fake HA
  entities; `tier2.py` provider interface with the ant-shaped default and a
  stub `local-http` provider.

### Explicitly out of scope for Phase 6 (sandbox)

- Real Matrix homeserver integration (mock channel only)
- Real CRDT mesh sync across devices
- `/attest` beyond a design sketch — needs a reproducible build to attest
- tpkg registry, signing, and distribution — local pack install only
- The Forge with real Tier 2 codegen — mock flow only (no cloud credentials)
- Real netfilter-level egress accounting — attributed mock-egress log only

---

## Risks / Watch Items

- **Grammar coverage ceiling:** deterministic parsing will miss phrasings; the
  escape hatch is the Tier 1 LLM (M4). Track misses in progress.md.
- **Mock drift:** mock backends must keep the exact signatures of PRD §5's tool
  manifest, or M4 swap-in becomes a rewrite.
- **Scope gravity:** the chat-shell is fun to over-build; M1–M3 stay
  terminal-only on purpose.
