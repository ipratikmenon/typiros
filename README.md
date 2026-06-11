<div align="center">

# typirOS

### AI-Native Conversational Mobile Operating System

> *"If the user has to think about how the phone is doing it, the OS has failed."*

[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Status](https://img.shields.io/badge/status-PRD%20%2F%20concept-blueviolet)]()

</div>

---

## What is typirOS?

typirOS is a ground-up mobile operating system built on a single radical premise: **the entire user interface is a chat window.**

There are no app icons, no home screen, no app drawer, no settings panels. The user types or speaks what they want, and the OS does it. Every feature is reached through natural language, routed by a two-tier AI runtime (on-device model + cloud model) through a Bridge Layer that silently dispatches to native OS APIs or an Android compatibility container.

> **"I talk to my phone. My phone does things."**

Full spec: **[PRD.md](PRD.md)**

---

## Design Principles

1. **One surface.** The chat window is the only UI.
2. **Act first, confirm short.** Act on the most probable interpretation; confirm in one line.
3. **Opacity of mechanism.** Containers, APIs, and routing decisions never surface — only outcomes.
4. **The OS fails in language.** Every error becomes natural language, never a stack trace or error code.
5. **Intelligence compounds.** Every interaction sharpens the OS's model of the user's context and relationships.

---

## Architecture at a Glance

```
User Input (text or voice)
        ↓
AI Runtime classifies intent (Tier 1 on-device / Tier 2 cloud)
        ↓
Tool call(s) dispatched to Bridge Layer
        ↓
Bridge Layer executes via Native API or Android Container
        ↓
Result returned to AI → one-line natural language response
```

- **Tier 1 (on-device):** Phi-3 Mini / Gemma 2B, <500ms, handles ~80% of requests
- **Tier 2 (cloud):** Claude, via `ant` / Anthropic Managed Agents — complex reasoning, web search, drafting
- **Bridge Layer:** routes, suppresses native UI, translates errors, normalises results
- **8 System Agents:** Communication, Media, Navigation, Productivity, Device, Information, Files, Finance

---

## Repository Structure

```
typiros/
├── PRD.md          # Full Product Requirements Document (v1.2)
├── plans.md        # Detailed planning + working agreement
├── tasks.md        # Work item tracker
├── progress.md     # Session-by-session log
├── what-ifs.md     # Speculative feature backlog (What-If Protocol, PRD §19.8)
├── kernel/         # OS / ROM layer (Phase 4 — custom AOSP-based ROM)
├── shell/          # Chat-window shell — runnable Phase 1 prototype (Python)
├── bridge/         # Bridge Layer — routing, opacity, error translation
└── agents/         # Managed Agent definitions (Tier 2 cloud backends)
    ├── communication.yaml
    ├── media.yaml
    ├── navigation.yaml
    ├── productivity.yaml
    ├── information.yaml
    ├── device.yaml
    ├── files.yaml
    └── finance.yaml
```

---

## Build Phases

| Phase | Focus | Success Metric |
|---|---|---|
| 1 — Proof of Concept | Chat shell UI on Linux Mobile (PinePhone), Tier 1 local model, 3 agents (Communication, Device, Productivity) | Make a call, send an SMS, set an alarm, change a setting — all from chat |
| 2 — Android Container + Core Agents | Android compatibility container, WhatsApp via container, Media agent, full Bridge Layer, Tier 2 cloud | WhatsApp message sent without the user ever seeing the WhatsApp UI |
| 3 — Full Agent Coverage + Keyboard | All 8 agents, all 4 keyboard modes, episodic memory, overlays, biometric gating | All daily smartphone tasks completable through chat |
| 4 — Hardening + Custom ROM | AOSP-based custom ROM, battery optimisation, security audit | <500ms Tier 1 response on target hardware |
| 5 — Hardware | Custom hardware (separate PRD) | — |

See [PRD.md § 16](PRD.md#16-build-phases) for full detail.

---

## Open Problems

Emergency calls, accessibility, multi-language grammar (Hindi/Tamil priority), battery life under continuous inference, banking-app root/emulator detection, and parental controls in a conversational UI — see [PRD.md § 17](PRD.md#17-open-problems).

---

## License

MIT — see [LICENSE](LICENSE).
