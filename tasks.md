# typirOS — Tasks

Work item tracker. States: `[ ]` todo · `[~]` in progress · `[x]` done · `[-]` dropped.
Strategy in [plans.md](plans.md) · log in [progress.md](progress.md) · ideas in [what-ifs.md](what-ifs.md).

---

## Phase 0 — Repo & Docs

- [x] Wipe huashu-design content, rebrand repo content to typirOS
- [x] PRD.md (v1.1) committed
- [x] Agent YAML scaffold (8 agents) committed
- [x] PRD v1.2 addendum — distraction-free typing-first (§19)
- [x] Tracking system: plans.md, tasks.md, progress.md, what-ifs.md
- [ ] Rename GitHub repo huashu-design → typiros (manual — needs repo Settings, owner action)

## Phase 1 — Proof of Concept

### M1 — Core loop ✅ (2026-06-11)
- [x] Shell package scaffold (`shell/typiros_shell/`)
- [x] Tier 1 deterministic grammar parser (call / message / remind / alarm / set / timer)
- [x] Slash-command fast paths (`/call`, `/msg`, `/remind`, `/missed`, `/help`, `/quit`) — PRD §19.3
- [x] Bridge Layer with error translation (PRD §6)
- [x] Mock backends: telephony, device settings, productivity
- [x] Contact resolution + 2-chip disambiguation (PRD §11)
- [x] Persistent context strips (active call / timer) in REPL header
- [x] Quiet notification queue + `/missed` digest (PRD §19.1)
- [x] End-to-end scripted demo: call + SMS + alarm + setting (success metric) — `shell/demo.txt` passes

### M2 — Conversation depth ✅ (2026-06-15)
- [x] Session memory: "call him back" resolves from last inbound/outbound contact
- [x] Correction flow: "no, Secondary" re-dispatches last action with new channel
- [x] Message-body capture: "message philip" → prompt for body → send
- [x] User-defined macros ("gm" → digest) — PRD §19.3
- [x] Edit-before-send / recall last command

### M3 — Quiet layer ✅ (2026-06-16)
- [x] Simulated inbound events (message arrives while user types)
- [x] Digest mode with configurable cadence
- [x] Focus sessions (`focus 90m on writing`) — PRD §19.2
- [ ] Starred-contact true-interrupt exception

### M4 — Real ground
- [ ] Tier 1 local LLM fallback for off-grammar input
- [ ] ModemManager/ofono telephony backend (Linux Mobile target)
- [ ] Settings backend via dbus

### M5 — TUI shell ✅ (2026-06-16)
- [x] Textual-based UI: strips, autocomplete chips, e-ink-friendly theme

## Phase 2 — Android Container + Core Agents

Detailed scope in [plans.md](plans.md#phase-2-plan--android-container--core-agents).
Sandbox has no real Android runtime, WhatsApp account, or Tier 2 credentials —
all Phase 2 backends are mocks behind real interfaces, same pattern as Phase 1.

### M6 — Android container (mock) + app allowlist ✅ (2026-06-23)
- [x] `backends/android.py`: `AndroidContainer` mock (`send`, `is_installed`, `is_allowed`, `enable`)
- [x] Default allowlist seeded with `whatsapp`; PRD §19.9
- [x] `enable app <name>` grammar — deliberate opt-in, one-line confirmation
- [x] WhatsApp/Instagram as channels alongside primary/secondary SIM in `send_message`
- [x] `message X via whatsapp` / `message X on instagram` grammar; `no, whatsapp` correction
- [x] Dispatch to a non-allowlisted app fails in language ("X isn't enabled yet — try `enable app X`")

### M7 — Media agent (mock) ✅ (2026-06-23)
- [x] `backends/media.py`: `Media` mock (`play`, `pause`, `now_playing`)
- [x] `play <track>` / `pause` / `what's playing` grammar
- [x] Now-playing context strip (within max-3 strip budget)

### M8 — Tier 2 stub + two-model routing ✅ (2026-06-23)
- [x] `tier2.py`: off-grammar input routes here instead of failing in language
- [x] Canned/echo response tagged `[tier2-stub]`
- [x] Routing reads `agents/*.yaml` manifests (no live API call)

### M9 — User memory layer ✅ (2026-06-23)
- [x] `user_memory.py`: sqlite-backed SIM preferences, app allowlist, macros
- [x] SIM corrections (`no, secondary`) and macro definitions persist across
      restarts; session loads persisted macros at startup
- [x] Scripted/piped runs (demo.txt, tests) use an in-memory DB so they stay
      deterministic; only interactive runs persist to disk
- [x] Session memory (RAM, per-run) stays unchanged

## Phase 3 — Full Agent Coverage + Keyboard System

Detailed scope in [plans.md](plans.md#phase-3-plan--full-agent-coverage--keyboard-system).
Sandbox has no GPS/maps API, no real filesystem container, no banking API,
no biometric or motion/ambient-mic hardware — all Phase 3 backends/sensors
are mocks behind real interfaces, same pattern as Phase 1/2. Full-screen
overlays are the one exception: the Textual push/dismiss mechanism is real,
only the rendered content is placeholder.

### M10 — Navigation agent (mock) ✅ (2026-06-23)
- [x] `backends/navigation.py`: `Navigation` mock (`navigate`, `eta`, `current_route`)
- [x] `navigate <destination>` / `eta` / `where am I going` grammar
- [x] `[nav]` context strip (max-3 strip budget)

### M11 — Information agent (mock) + Tier 1 graduation ✅ (2026-06-23)
- [x] `backends/information.py`: canned weather/fact lookups
- [x] `weather in <city>` and a small fact set move from `tier2.py` stub into real Tier 1 grammar
- [x] Everything else still escalates to `tier2.py` unchanged

### M12 — Files agent (mock)
- [ ] `backends/files.py`: `find_file(query)`, `recent_files()` over a mock index
- [ ] `find file <query>` / `recent files` grammar

### M13 — Finance agent (mock) + Biometric gate
- [ ] `backends/finance.py`: `balance()`, `send_payment(contact, amount)`
- [ ] `biometric.py`: mock passphrase challenge, one unlock per session per domain (PRD §15)
- [ ] `balance` / `send <amt> to <contact>` grammar; payment gated by the challenge before dispatch

### M14 — Keyboard modes
- [ ] `keyboard.py`: `KeyboardMode` enum (Compact/Standard/Voice First/Adaptive)
- [ ] `keyboard mode <name>` manual switch grammar
- [ ] Compact: abbreviation expansion reusing `tier2.py`'s keyword-overlap scorer
- [ ] Voice First: `/voice <text>` transcription proxy (no mic)
- [ ] Adaptive: `/sim sensor <signal> on/off` drives automatic mode switching per PRD §14's context table

### M15 — Episodic memory + full-screen overlays
- [ ] `episodic_memory.py`: sqlite-backed rolling 90-day summarized log of dispatched actions
- [ ] `overlays.py`: Textual `Screen` subclasses for Media/Maps/Photos placeholders
- [ ] Single-gesture (Esc) dismiss back to chat; TUI only, line REPL unaffected
