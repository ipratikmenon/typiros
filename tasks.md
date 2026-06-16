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

### M5 — TUI shell
- [ ] Textual-based UI: strips, autocomplete chips, e-ink-friendly theme

## Phase 2+ (placeholders, plan when Phase 1 lands)

- [ ] Android compatibility container spike
- [ ] Tier 2 escalation via `ant` (agents/*.yaml already defined)
- [ ] Memory layers: Session + User (encrypted local DB)
