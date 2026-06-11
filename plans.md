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

## Phase 2+ (per PRD §16, not yet planned in detail)

Android container, Tier 2 via `ant`/Managed Agents (`agents/*.yaml` already
scaffolded), media agent, memory layers, keyboard system, ROM packaging.
Detailed plans to be written when Phase 1 M1–M3 are done.

---

## Risks / Watch Items

- **Grammar coverage ceiling:** deterministic parsing will miss phrasings; the
  escape hatch is the Tier 1 LLM (M4). Track misses in progress.md.
- **Mock drift:** mock backends must keep the exact signatures of PRD §5's tool
  manifest, or M4 swap-in becomes a rewrite.
- **Scope gravity:** the chat-shell is fun to over-build; M1–M3 stay
  terminal-only on purpose.
