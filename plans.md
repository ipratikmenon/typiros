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
| Android container | Mock `AndroidContainer` backend exposing `send_whatsapp(contact, body)`, `is_installed(app)` | Mirrors `telephony.py`'s mock-now/real-later pattern; real backend would be a Waydroid/Anbox bridge |
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

- **M6 — Android container (mock):** `AndroidContainer` backend; `message X
  via whatsapp` / `message X` (when only WhatsApp is reachable) grammar;
  WhatsApp joins the channel set alongside primary/secondary SIM, including
  `no, whatsapp` correction.
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

## Risks / Watch Items

- **Grammar coverage ceiling:** deterministic parsing will miss phrasings; the
  escape hatch is the Tier 1 LLM (M4). Track misses in progress.md.
- **Mock drift:** mock backends must keep the exact signatures of PRD §5's tool
  manifest, or M4 swap-in becomes a rewrite.
- **Scope gravity:** the chat-shell is fun to over-build; M1–M3 stay
  terminal-only on purpose.
