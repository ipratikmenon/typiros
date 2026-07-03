# typirOS — Tasks

Work item tracker. States: `[ ]` todo · `[~]` in progress · `[x]` done · `[-]` dropped.
Strategy in [plans.md](plans.md) · log in [progress.md](progress.md) · ideas in [what-ifs.md](what-ifs.md).

---

## Phase 0 — Repo & Docs

- [x] Wipe huashu-design content, rebrand repo content to typirOS
- [x] PRD.md (v1.1) committed
- [x] Agent YAML scaffold (8 agents) committed
- [x] PRD v1.2 addendum — distraction-free typing-first (§19)
- [x] PRD v1.3 addendum — the Power-User Compact (§20, WIF-018–035) (2026-07-03)
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

### M12 — Files agent (mock) ✅ (2026-06-23)
- [x] `backends/files.py`: `find_file(query)`, `recent_files()` over a mock index
- [x] `find file <query>` / `recent files` grammar

### M13 — Finance agent (mock) + Biometric gate ✅ (2026-06-23)
- [x] `backends/finance.py`: `balance()`, `send_payment(contact, amount)`
- [x] `biometric.py`: mock passphrase challenge, one unlock per session per domain (PRD §15)
- [x] `balance` / `send <amt> to <contact>` grammar; payment gated by the challenge before dispatch

### M14 — Keyboard modes ✅ (2026-06-24)
- [x] `keyboard.py`: `KeyboardMode` enum (Compact/Standard/Voice First/Adaptive)
- [x] `keyboard mode <name>` manual switch grammar
- [x] Compact: abbreviation expansion reusing `tier2.py`'s keyword-overlap scorer
- [x] Voice First: `/voice <text>` transcription proxy (no mic)
- [x] Adaptive: `/sim sensor <signal> on/off` drives automatic mode switching per PRD §14's context table

### M15 — Episodic memory + full-screen overlays ✅ (2026-06-24)
- [x] `episodic_memory.py`: sqlite-backed rolling 90-day summarized log of dispatched actions
- [x] `overlays.py`: Textual `Screen` subclasses for Media/Maps/Photos placeholders
- [x] Single-gesture (Esc) dismiss back to chat; TUI only, line REPL unaffected

## Phase 4 — Hardening

Detailed scope in [plans.md](plans.md#phase-4-plan--hardening). ROM packaging
and battery optimization are hardware-only and out of scope; performance
profiling and the security audit are genuinely buildable in this sandbox.

### M16 — Bridge Layer + container isolation security audit ✅ (2026-06-24)
- [x] Reviewed `bridge.py`, `main.py`, `biometric.py`, `backends/android.py`,
      `backends/finance.py` against PRD §15 (Container Isolation,
      Permission Model, Biometric Gate)
- [x] Finding 1 (real gap): Biometric Gate covered `send_payment` only —
      PRD §15 says "banking, payments, **personal data retrieval**";
      `balance` and `episode_history` dispatched unauthenticated. Fixed:
      `SENSITIVE_TOOLS` now also gates `balance` (finance domain) and
      `episode_history` (its own domain)
- [x] Finding 2 (latent landmine, not currently exploitable): `_correct()`
      called `bridge.dispatch()` directly, bypassing the gate `main.py`'s
      `_dispatch()` enforces everywhere else. Not reachable today (only
      `make_call`/`send_message` ever populate `last_dispatch`) but fixed
      so the gate stays uniform regardless of entry point
- [x] Finding 3 (self-audit of M18): the just-shipped `crypto_store.py`
      decrypted into a plaintext temp file on disk for sqlite3 to open —
      an unclean kill (SIGKILL/OOM) would've left that plaintext sitting
      in `/tmp` indefinitely. Fixed by switching to stdlib
      `sqlite3.Connection.serialize()`/`deserialize()` (3.11+, in-memory
      DB) — plaintext now never touches disk at all
- [x] Confirmed compliant (no fix needed): `AndroidContainer` has no
      access to User/Episodic memory; `enable_app` can't desync the
      allowlist (container raises before the User-memory write); container
      message history is RAM-only and doesn't persist across restarts —
      stricter than PRD's "WhatsApp history may persist" allowance, not a
      violation
- [x] `demo.txt` updated for the two newly-gated tools (passphrase moved
      earlier for `balance`, added before `history with lena`); re-ran
      end-to-end, exit 0

### M17 — Tier 1 performance profiling ✅ (2026-06-24)
- [x] `benchmark.py`: times `intent.parse()` alone and a full `Shell.handle()`
      turn (parse + Bridge dispatch + translation) across one phrase per
      grammar branch, 200 reps each, mean/p50/p95/max
- [x] Pre-unlocks the Biometric Gate's `finance`/`episodic` domains so
      `balance`/`send <amt>`/`history` measure steady-state dispatch, not
      the one-time challenge pause
- [x] Reported against PRD's <500ms target with the sandbox-CPU caveat
      stated up front and in the output — worst case observed: 0.74ms
      full-turn, ~700x under target on this hardware

### M18 — Memory encryption at rest ✅ (2026-06-24)
- [x] User decision: add `cryptography` as the project's first
      non-stdlib dependency (`shell/requirements.txt`)
- [x] `crypto_store.py`: AES-256-GCM encryption-at-rest. First pass
      decrypted into a private temp-file copy for sqlite3 to open
      directly; M16's security audit found that left plaintext on disk
      across an unclean kill, so it was replaced with stdlib
      `sqlite3.Connection.serialize()`/`deserialize()` (3.11+) — the
      working connection is `:memory:` only and plaintext never touches
      disk in any form; ciphertext is written back after every write,
      with the per-file key stored alongside (`0o600`)
- [x] `user_memory.py` / `episodic_memory.py` wired to `crypto_store.py`
      for any non-`:memory:` db path; piped/scripted runs unaffected
- [x] Verified: on-disk `.db` files contain no SQLite header and no
      plaintext field values; reopening after "restart" decrypts
      correctly; no stray plaintext files left in `/tmp`

### M19 — Custom Android ROM packaging — [-] dropped (out of scope)
Needs a real AOSP build environment and target hardware; nothing to
prototype in a Python shell. See [plans.md](plans.md#phase-4-plan--hardening).

### M20 — Battery optimization — [-] dropped (out of scope)
Needs real hardware power telemetry to optimize against; not modelable
against a mock. See [plans.md](plans.md#phase-4-plan--hardening).

**Phase 4 complete (2026-06-24).** M16–M18 shipped; M19/M20 are explicitly
out of scope for this sandbox (hardware-only, no mock would be meaningful)
and stay dropped rather than open — see `plans.md` for the reasoning.

## Phase 6 — The Power-User Compact

Detailed scope in [plans.md](plans.md#phase-6-plan--the-power-user-compact);
vision in PRD §20 (v1.3). Phase 5 (hardware) stays deferred — Phase 6 is pure
software and independent of it. "Opacity by default, sovereignty on demand."

### M21 — Glasnost Mode (PRD §20.1)
- [ ] Bridge retains a structured per-turn trace (parse → route → tool call → backend → latency)
- [ ] `/why` pretty-prints the last turn's trace
- [ ] `/trace on|off` streams the trace live for every turn

### M22 — Pipes (PRD §20.5)
- [ ] Deterministic pre-parser splits on `|`; each segment parses normally
- [ ] Structured results fold left-to-right into the next segment's input slot

### M23 — Hooks (PRD §20.6)
- [ ] `when <event>, <command>` / `every <interval>, <command>` grammar
- [ ] Rule engine + mock event emissions (battery tick, inbound SMS, focus start/end)
- [ ] `/hooks` lists and removes rules

### M24 — Open Skull (PRD §20.2)
- [ ] `memory show` / `memory forget <fact>` / `memory edit` over the User + Episodic sqlite layers

### M25 — Local-Only Hard Mode (PRD §20.4)
- [ ] `/airgap on|off`; tier router refuses escalation while on
- [ ] Honest degradation in language; queued escalations surface in the next digest

### M26 — The Wire, prototype (PRD §20.7)
- [ ] `typir` CLI / socket front-end driving the same `Shell` instance
- [ ] Real key-based auth hardening deferred (out of sandbox scope)

### M27 — Power-substrate extras (PRD §20.8, §20.9, §20.11, §20.12, §20.17)
- [ ] grep-your-life: JSONL lifelog of every turn + query verb
- [ ] Inline REPL: restricted sandbox, pipeable output
- [ ] Webhook Inbox: local HTTP endpoint → quiet queue
- [ ] Phone-as-Code: plain-text config dir + `typir apply`
- [ ] tpkg (local only): `tpkg install <pack.yaml>` merges verbs/macros

### M28 — Home agent (mock) + BYOM provider seam (PRD §20.14, §20.10)
- [ ] Ninth agent over a mock Home Assistant backend with fake entities
- [ ] `tier2.py` provider interface: ant-shaped default + stub `local-http` provider

Out of sandbox scope (design-only, per plans.md): real Matrix integration,
CRDT mesh sync (§20.16), `/attest` (§20.18), tpkg registry/signing, Forge
codegen (§20.13 beyond a mock flow), real egress accounting (§20.3 beyond an
attributed mock log).
