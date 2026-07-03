# typirOS — Product Requirements Document

### AI-Native Conversational Mobile Operating System

**Version 1.3 | Confidential**

-----

## Table of Contents

1. [Executive Summary](#1-executive-summary)
1. [Vision & Philosophy](#2-vision--philosophy)
1. [Core Interaction Model](#3-core-interaction-model)
1. [Input System](#4-input-system)
1. [AI Runtime Architecture](#5-ai-runtime-architecture)
1. [The Bridge Layer](#6-the-bridge-layer)
1. [App Ecosystem Strategy](#7-app-ecosystem-strategy)
1. [UI & Shell Design](#8-ui--shell-design)
1. [Multitasking Model](#9-multitasking-model)
1. [OS Grammar & Language Spec](#10-os-grammar--language-spec)
1. [Contact & Entity Resolution](#11-contact--entity-resolution)
1. [System Agents](#12-system-agents)
1. [Memory & Context Architecture](#13-memory--context-architecture)
1. [Keyboard System](#14-keyboard-system)
1. [Privacy & Security](#15-privacy--security)
1. [Build Phases](#16-build-phases)
1. [Open Problems](#17-open-problems)
1. [ant / Managed Agents Integration](#18-ant--managed-agents-integration)
1. [Distraction-Free Typing-First Addendum (v1.2)](#19-distraction-free-typing-first-addendum-v12)
1. [The Power-User Compact (v1.3)](#20-the-power-user-compact-v13)

-----

## 1. Executive Summary

typirOS is a ground-up mobile operating system built on a single radical premise: **the entire user interface is a chat window.**

There are no app icons. No home screen. No app drawer. No notification shade. No settings panels to navigate. The user types or speaks what they want, and the OS does it. Every feature, every function, every piece of the device is accessible through natural language.

The OS is powered by a two-model AI runtime — a fast on-device model for common intents, and a cloud model for complex reasoning. Underneath the chat window, a Bridge Layer routes actions to native OS APIs or an Android compatibility container, silently and invisibly. The user never knows which path their request took. They only see the outcome.

The defining principle: **radical transparency of outcome, total opacity of mechanism.**

-----

## 2. Vision & Philosophy

### The Problem with Current Mobile OS Design

Every mobile OS today is built around the same paradigm: icons represent applications, applications represent functions. The user must navigate to a function. They must remember where things live, what app does what, which settings panel controls which feature.

This is an artifact of the desktop era, ported to mobile in 2007 and never fundamentally questioned.

### The typirOS Premise

In typirOS, the user never navigates to a function. The user **states a goal**, and the OS navigates to the function on their behalf.

> *“Call Lena through Primary”* — the OS places the call.
> *“Message Philip on WhatsApp, I’ll be 10 minutes late”* — the OS sends the message.
> *“Remind me to call mom when I get home”* — the OS sets a geofenced reminder.

The mechanism is always invisible. The user’s mental model is simply:

> **“I talk to my phone. My phone does things.”**

### Design Principles

1. **One surface.** The chat window is the only UI. Everything else is invoked from it.
1. **Act first, confirm short.** The OS acts on the most probable interpretation and confirms in one line. It asks before acting only when truly ambiguous.
1. **Opacity of mechanism.** The user never sees containers, APIs, model calls, or routing decisions. Only outcomes.
1. **The OS fails in language.** Every error, every delay, every edge case is translated into a natural language response before reaching the user.
1. **Intelligence compounds.** Every interaction makes the OS smarter about this user’s context, preferences, and relationships.

-----

## 3. Core Interaction Model

### The Single Loop

Every user interaction follows one loop:

```
User Input (text or voice)
        ↓
AI Runtime classifies intent
        ↓
Tool call(s) dispatched to Bridge Layer
        ↓
Bridge Layer executes via Native API or Android Container
        ↓
Result returned to AI
        ↓
AI responds in one line of natural language
        ↓
UI updates (confirmation text + optional overlay/strip)
```

This loop is the entire OS. Every feature is a variation of this loop.

### The Confirmation Contract

typirOS commits to a specific response contract:

- **Actions completed:** One line confirmation. “Sent to Philip — WhatsApp.”
- **Actions in progress:** Present tense strip. “Calling Lena on Primary…”
- **Ambiguity:** One clarifying question, maximum. Never two.
- **Errors:** Natural language, never technical. “Couldn’t reach Philip — no signal.” Never “Error 403.”
- **Complex results:** Inline card or overlay. Maps, photos, web results appear as visual overlays over the chat.

-----

## 4. Input System

### The Input Bar

The input bar is permanent, always at the bottom of the screen. It contains exactly three elements:

- **[+] button** — attach files, photos, documents, location
- **Text field** — “Type or speak…” placeholder
- **[🎙] Mic button** / **[→] Send button** — mic when field is empty, send arrow when field has content

This is the complete UI chrome. Nothing else is permanent on screen.

### Inline Autocomplete

When the user types an intent that includes an entity name (person, place, app, file), the OS surfaces **exactly two suggestions** from the relevant data source, appearing above the keyboard as tappable chips:

```
User types: "Message Phil"

[ 👤 Philip Sharma ]  [ 👤 Philip D'Souza ]
```

Rules:

- Maximum **2 suggestions** always. Never more.
- Suggestions appear after **2–3 characters** of the entity name.
- Tapping a suggestion **completes the action immediately** if intent is unambiguous.
- If the action needs more input (e.g. message body), suggestion completes the recipient and cursor advances.
- Voice input surfaces the same suggestions visually as speech is transcribed.

### Autocomplete Data Sources by Intent

|Intent verb           |Autocomplete source               |
|----------------------|----------------------------------|
|Message / Call / Email|Contacts                          |
|Play                  |Music library + streaming         |
|Open (file)           |Recent files, Drive, local storage|
|Navigate / Directions |Saved places, recent locations    |
|Remind about          |Past reminders, calendar events   |
|Email from            |Configured email accounts         |

-----

## 5. AI Runtime Architecture

### Two-Model Design

The AI runtime uses two models in a tiered architecture:

**Tier 1 — Local Model (on-device)**

- Model: Phi-3 Mini or Gemma 2B, quantised (INT4/INT8)
- Response target: < 500ms
- Handles: ~80% of all requests
- Scope: Single clear intent, no creative generation, no real-time data required
- Examples: calls, messages, alarms, settings, reminders, music playback

**Tier 2 — Cloud Model**

- Model: Claude or equivalent frontier model
- Response target: 1–3 seconds
- Handles: Complex reasoning, creative generation, real-time information
- Requires: Active connectivity
- Examples: Email drafting, document summarisation, web search, ambiguous multi-step requests

### Routing Logic

The local model makes the routing decision on every turn:

```
Is intent clear + single + no external data needed?
    YES → Local model executes directly
    NO  → Escalate to cloud model
```

The escalation is invisible to the user. A single unified loading indicator appears regardless of which tier is processing. There is no visual distinction.

### Tool Calling Spec

The AI runtime receives a complete tool manifest at boot. This manifest describes every OS capability as a callable function. The model outputs tool calls; the Bridge Layer executes them.

**Core tool categories:**

**Communication**

```
send_message(contact, channel, account, body)
make_call(contact, sim)
send_email(to, from_account, subject, body)
```

**Device Control**

```
set_setting(key, value)
create_reminder(text, time, location_trigger)
create_event(title, start, duration, location)
get_calendar(date_range)
```

**Media**

```
play_music(query, service)
open_camera(mode)
show_photos(filter)
play_video(query)
```

**Information**

```
web_search(query)
get_weather(location, range)
get_contacts(query)
find_file(query)
```

**Navigation**

```
navigate_to(destination, mode)
get_directions(from, to)
```

### System Prompt at Boot

On device boot, the AI runtime loads a fixed system prompt containing:

1. The complete tool manifest
1. The user’s personal context (from memory layer)
1. The OS grammar spec
1. The confirmation contract
1. The opacity directive: never surface mechanism, only outcome

-----

## 6. The Bridge Layer

The Bridge Layer is the opacity engine. It sits between the AI runtime and all execution backends, ensuring nothing below it ever surfaces to the user directly.

### Responsibilities

1. **Route** every tool call to the correct backend (Native API or Android Container)
1. **Suppress** all native UI from Android containers — no dialogs, no toasts, no error screens
1. **Pre-warm** frequently used containers in the background
1. **Catch** all errors and translate to natural language
1. **Normalise** all responses into a standard result format the AI can read
1. **Gate** all permission dialogs — handled once at OS setup, never surfaced again

### Execution Backends

**Native API Backend**
Direct Linux/Android system API calls for:

- Telephony (calls, SMS)
- System settings (brightness, volume, WiFi, Bluetooth, DND)
- Calendar and reminders
- Contacts
- Camera
- Local files

**Android Compatibility Container**
Sandboxed AOSP runtime for:

- WhatsApp, Telegram, Signal
- Banking apps
- YouTube, streaming apps
- Any app without a native API equivalent

Container behavior:

- Starts silently in background when needed
- UI is suppressed — only content/data surfaces
- Returns results to Bridge Layer as structured data
- Sleeps immediately after task completion
- Error dialogs are intercepted and translated

### The Seam Prevention Table

|Failure mode           |Prevention                                                            |
|-----------------------|----------------------------------------------------------------------|
|Android container crash|Intercept all container UI; translate to chat message                 |
|Slow container wake    |Pre-warm top 3 most-used containers at boot                           |
|Permission dialog      |All permissions granted at OS setup; never ask again                  |
|App update prompt      |Suppress all container UI except core content                         |
|Network error          |Catch at bridge, return: “Couldn’t reach [service] — check connection”|
|Contact ambiguity      |Resolve before dispatch; never let two apps compete                   |
|Dual-SIM ambiguity     |Default to last-used SIM; confirm in response text                    |

-----

## 7. App Ecosystem Strategy

### Strategy: A + C

typirOS uses a combined strategy:

**Strategy A — Android Compatibility Layer**
For irreplaceable apps (WhatsApp, banking, maps, ride-hailing): run inside Android compatibility container, silently invoked by the AI, UI suppressed. Invocation is gated by a curated default allowlist, not "any detected app" — see §19.9.

**Strategy C — AI as the App**
For the long tail of functions: the AI handles them directly via APIs and tool calls, with no app required.

### The AI-Native Functions (no app needed)

|User need      |typirOS handling                        |
|---------------|--------------------------------------|
|Weather        |AI calls weather API, responds inline |
|Notes          |AI manages local markdown store       |
|Calculator     |AI computes inline in chat            |
|Reminders      |AI + system calendar API              |
|News briefing  |AI fetches + summarises via web search|
|Unit conversion|AI computes inline                    |
|Timers         |Native system timer API               |
|Alarms         |Native system alarm API               |
|Contacts lookup|AI queries local contacts database    |
|Call log       |AI queries system call log            |

### The Container-Handled Apps

|App               |Why native is required                              |
|------------------|----------------------------------------------------|
|WhatsApp          |End-to-end encrypted; no public API for personal use|
|Banking apps      |Security requirements, no API access                |
|YouTube           |No public streaming API                             |
|Ola / Uber        |Booking flow requires app                           |
|Instagram / social|No public posting API                               |

### The WhatsApp Problem — Three Angles

1. **Android container** — WhatsApp runs in container, Bridge Layer handles message dispatch and retrieval. User says “message Philip on WhatsApp” and it works seamlessly.
1. **WhatsApp Business API** — for enterprise/managed deployments, use official API for fully native integration without container.
1. **Long bet on RCS** — RCS is becoming the universal messaging layer. As WhatsApp dominance potentially erodes, typirOS is already on the right side with native messaging-first architecture.

-----

## 8. UI & Shell Design

### What the User Sees

```
┌─────────────────────────────────┐
│                                 │  ← Status bar (time, signal, battery)
├─────────────────────────────────┤
│  [Active strips — if any]       │  ← Persistent context strips
├─────────────────────────────────┤
│                                 │
│                                 │
│   Chat history / AI responses   │
│                                 │
│                                 │
│                                 │
├─────────────────────────────────┤
│  [+]  Type or speak...   [🎙/→] │  ← Input bar (always visible)
└─────────────────────────────────┘
```

Nothing else. This is the complete UI.

### Chat History

AI responses appear as bubbles on the left. User messages on the right. Standard chat convention — familiar to every smartphone user on earth.

Response bubbles contain:

- Confirmation text (primary)
- Optional inline card (weather, contact info, balance, search result)
- Optional action chip (“Call back”, “Reply”, “Navigate”)

### Full-Screen Overlays

Some responses spawn a full-screen overlay that collapses back to chat:

- Photos / gallery
- Maps / navigation
- Video playback
- Web pages
- Documents

The overlay has a single dismiss gesture (swipe down or back tap) that returns to the chat window. The chat is always one gesture away.

-----

## 9. Multitasking Model

### Persistent Context Strips

Running state is shown as compact strips pinned above the chat, below the status bar. Maximum 3 strips visible at once.

```
📞 Lena · 4:32          [Expand]
🎵 Kendrick · Humble    [Expand]
```

Strips are tappable — tap expands to the relevant overlay. The running process is never terminated by returning to chat.

### Incoming Events

Incoming calls, messages, and notifications appear as frosted glass cards that slide up over the chat window. They contain:

- **Calls:** Caller name, number, [Answer] [Decline]
- **Messages:** Sender, preview, [Reply] [Dismiss]
- **Alerts:** Content, [OK] [Action]

The chat window remains visible and interactive beneath the card. Dismiss the card and you’re back to full chat immediately.

### Voice During Active Tasks

While on a call, the chat input remains active. The user can type or speak commands that the OS handles without interrupting the call:

> *“What’s Philip’s address”* → AI responds inline, call continues
> *“Set a reminder for this evening”* → Reminder created, confirmed in chat

-----

## 10. OS Grammar & Language Spec

typirOS understands natural language, but is designed around a small learnable grammar that covers 90% of actions. The AI normalises all variations into these patterns.

### Core Grammar Patterns

|Pattern                            |Example                                |
|-----------------------------------|---------------------------------------|
|`[verb] [object]`                  |“Play music”                           |
|`[verb] [person]`                  |“Message Philip”                       |
|`[verb] [person] through [channel]`|“Call Lena through Primary”            |
|`[verb] [person] on [app]`         |“Message Philip on WhatsApp”           |
|`[verb] [object] from [source]`    |“Email from Work account”              |
|`[verb] [thing] at [time]`         |“Remind me to sleep at 11pm”           |
|`[verb] [thing] when [condition]`  |“Remind me to call mom when I get home”|
|`[verb] [setting] to [value]`      |“Set brightness to low”                |
|`show / open / find [thing]`       |“Show last week’s photos”              |

### The “through” Keyword

**“through”** is a first-class grammar primitive for disambiguation:

- `through Primary` — use SIM 1
- `through Secondary` — use SIM 2
- `through WhatsApp` — use WhatsApp
- `through Gmail` — use specific email account

### Normalisation Examples

These all resolve to the same action:

- “Message Philip”
- “Send a message to Philip”
- “I need to message Philip”
- “Text Philip”
- “Open a message window to Philip”

The AI maps them all to: `send_message(contact="Philip Sharma", channel="whatsapp")`

-----

## 11. Contact & Entity Resolution

### Disambiguation Policy

**One match:** Act immediately, no confirmation.

**Two or more matches:** Surface inline chips (max 2 shown), user taps to select:

```
[ 👤 Philip Sharma ]  [ 👤 Philip D'Souza ]
```

**Multiple channels for same contact:** Use last-used channel, confirm in response:

> “Calling Lena on Primary.”
> User corrects if wrong: “No, Secondary.” OS remembers.

### User Knowledge Graph

The OS maintains a personal knowledge graph of entities and relationships:

- Contact nicknames: “Philip” → Philip Sharma
- Channel preferences: Philip → WhatsApp (last used 2 days ago)
- SIM labels: “Primary” → Airtel +91-XXXXXXXXXX
- Location labels: “home” → saved home address
- Account labels: “Work” → work@company.com

This graph is populated automatically from usage and explicitly via commands:

> “Call this number Philip” — adds Philip to contacts
> “This is my work SIM” — labels SIM 2 as Work

-----

## 12. System Agents

The AI runtime has access to the following agent domains. Each agent has exclusive OS-level permissions for its domain.

|Agent            |Capabilities                              |Backend           |
|-----------------|------------------------------------------|------------------|
|**Communication**|SMS, calls, WhatsApp, email               |Native + Container|
|**Media**        |Music, video, camera, photos              |Native + Container|
|**Navigation**   |Maps, directions, location                |Native + Container|
|**Productivity** |Calendar, reminders, notes, timers        |Native            |
|**Device**       |Settings, WiFi, Bluetooth, DND, brightness|Native            |
|**Information**  |Web search, weather, contacts lookup      |Native + Cloud    |
|**Files**        |Local files, cloud storage                |Native + Container|
|**Finance**      |Banking apps, payment apps                |Container         |

-----

## 13. Memory & Context Architecture

### Three Memory Layers

|Layer       |Contents                                                       |Lifespan       |Storage           |
|------------|---------------------------------------------------------------|---------------|------------------|
|**Session** |Current conversation, active calls, playing media              |Until reboot   |RAM               |
|**User**    |Contact prefs, SIM labels, account nicknames, frequent commands|Permanent      |Encrypted local DB|
|**Episodic**|Summarised past interactions, relationship context             |Rolling 90 days|Encrypted local DB|

### Context Injection

On every AI turn, the runtime injects relevant context from all three layers into the model’s working context. The model does not need to ask for context it already has.

Example: “Call him back” resolves to Philip Sharma because the session memory contains the recent inbound call from Philip Sharma. The model never asks “who?”

### Privacy Guarantee

All memory layers are stored exclusively on-device in an encrypted database. Nothing from memory is sent to the cloud model without explicit user command. Cloud model calls receive only the current turn and relevant session context — not persistent user memory.

-----

## 14. Keyboard System

The keyboard is user-selectable during onboarding and changeable at any time.

### Four Keyboard Modes

**Compact**
Minuum-inspired single or double row layout. Minimal screen footprint. Relies on aggressive AI word prediction. Best for users who want maximum chat history visible.

**Standard**
Full QWERTY layout with a deeply context-aware suggestion bar above it. The suggestion bar knows the current intent and suggests contact names, command completions, and frequent phrases.

**Voice First**
Mic is the primary input method. Keyboard slides up only when the text field is explicitly tapped. Screen defaults to full chat history with prominent mic button.

**Adaptive**
The OS selects the input mode dynamically based on physical context:

|Context signal                        |Input mode                 |
|--------------------------------------|---------------------------|
|Device stationary + quiet environment |Voice nudge                |
|Device in motion (walking, travelling)|Keyboard                   |
|Driving detected                      |Voice only, keyboard locked|
|Night / DND active                    |Keyboard default           |
|Active call in progress               |Keyboard only              |

Adaptive uses accelerometer, ambient mic level, time, and telephony state. No manual switching required.

-----

## 15. Privacy & Security

### On-Device First

- All AI inference for Tier 1 runs entirely on-device. No data leaves the device for routine commands.
- All memory layers are stored on-device in SQLCipher-encrypted databases.
- Cloud model is invoked only when local model escalates, and only current-turn context is transmitted.

### Biometric Gate

- Sensitive tool calls (banking, payments, personal data retrieval) require biometric confirmation before Bridge Layer executes.
- The biometric prompt is surfaced by the OS, never by individual apps.
- One biometric unlock per session for the same app/domain.

### Container Isolation

- Android containers run in isolated sandboxes with no access to each other.
- Container data does not persist between sessions unless explicitly required (e.g. WhatsApp message history).
- No container can access the AI runtime’s memory layers.

### Permission Model

All device permissions are granted to the OS at setup, not to individual apps. The OS mediates all hardware access through the Bridge Layer. The user grants trust once — to the OS — not repeatedly to apps.

-----

## 16. Build Phases

### Phase 1 — Proof of Concept (Target: PinePhone / Linux Mobile)

- Chat shell UI running as a Linux application
- Tier 1 local model integrated (Phi-3 Mini / Gemma 2B)
- 3 working agents: Communication (SMS/calls), Device (settings), Productivity (alarms/reminders)
- Inline autocomplete for contacts
- Persistent strip system for active calls
- No Android container yet

**Success metric:** User can make a call, send an SMS, set an alarm, and change a setting — all from the chat window, end to end.

### Phase 2 — Android Container + Core Agents

- Android compatibility container integrated
- WhatsApp working via container, fully invisible to user
- Media agent (music playback, camera)
- Bridge Layer fully implemented with error translation
- Two-model architecture (Tier 1 + Tier 2 cloud)
- Memory layers implemented (Session + User)

**Success metric:** WhatsApp message sent without user ever seeing the WhatsApp UI.

### Phase 3 — Full Agent Coverage + Keyboard System

- All 8 system agents operational
- All 4 keyboard modes implemented
- Adaptive keyboard mode with sensor integration
- Episodic memory layer
- Full-screen overlays for media, maps, photos
- Biometric gating for sensitive actions

**Success metric:** All daily smartphone tasks completable through the chat window.

### Phase 4 — Hardening + Custom ROM

- Package as a custom Android ROM (AOSP base) for initial hardware targets
- Battery optimisation for continuous AI runtime
- Performance profiling — < 500ms Tier 1 response on target hardware
- Security audit of Bridge Layer and container isolation

### Phase 5 — Hardware

- Custom hardware design (deferred — see separate hardware PRD)

-----

## 17. Open Problems

These are known hard problems that require further design work:

**Emergency calls**
111/112/999 must work instantly with zero AI latency. Requires a direct hardware-level bypass that activates before the AI runtime is involved.

**Accessibility**
Visual impairment, motor impairment use cases are naturally well-served by voice-first design but require dedicated specification.

**Multi-language support**
The OS grammar must work in languages beyond English. Hindi, Tamil, and other Indian languages are high priority for the initial market.

**Battery life under continuous inference**
On-device LLM inference is power-intensive. Requires aggressive sleep/wake architecture — the local model should be dormant between turns and wake in < 100ms.

**The banking app problem**
Many Indian banking apps have root detection and emulator detection that will flag the Android container. Requires per-app workarounds or official banking partnerships.

**Child safety / parental controls**
Conversational UI makes traditional parental controls harder to implement. Requires a separate design pass.

-----

## 18. ant / Managed Agents Integration

### What ant Is

`ant` is Anthropic’s official Go-based CLI for the Claude API, launched April 2026 alongside Claude Managed Agents. Every API resource maps to a shell command — `ant messages create` calls the model, `ant beta:agents` stands up a hosted Managed Agent, and results pipe directly into any shell process. Claude Code already shells out to `ant` natively, meaning any coding agent can spin up other agents itself.

This is the same philosophical move as typirOS — collapse the interface to a single input primitive. Terminal for developers, chat window for everyone else.

-----

### ant as typirOS Tier 2 Backend

Rather than building a custom cloud inference layer, typirOS’s Tier 2 cloud model is implemented directly on top of Anthropic Managed Agents invoked via `ant`. This gives typirOS production-grade agent infrastructure without building it from scratch.

**The mapping:**

|typirOS concept                             |ant / Managed Agents equivalent                                   |
|------------------------------------------|------------------------------------------------------------------|
|System Agents (Communication, Media, etc.)|YAML-defined Managed Agents, checked into repo                    |
|Per-turn cloud execution                  |Sessions — created dynamically per task, billed to the millisecond|
|Agent tool calls                          |`ant beta:agents` invocations from Bridge Layer                   |
|Complex reasoning escalation              |Tier 1 local model shells out to `ant messages create`            |
|Agent orchestration (multi-step)          |Claude Code drives `ant`, spawning sub-agents as needed           |

-----

### Agent YAML Architecture

Each typirOS System Agent that escalates to cloud is defined as a Managed Agent YAML file, versioned in the OS repo:

```yaml
# agents/communication.yaml
name: typiros-communication
model: claude-sonnet-4-6
system: |
  You are the Communication Agent for typirOS.
  You handle calls, messages, email, and all contact resolution.
  Always respond in one line. Never surface mechanism.
  Available tools: send_message, make_call, send_email, get_contacts
tools:
  - type: agent_toolset_20260401
```

```yaml
# agents/information.yaml
name: typiros-information
model: claude-opus-4-6
system: |
  You are the Information Agent for typirOS.
  You handle web search, weather, summarisation, and complex reasoning.
  Respond concisely. User is on a mobile device.
tools:
  - type: web_search_20250305
  - type: agent_toolset_20260401
```

Agents are deployed via CI:

```bash
ant beta:agents create --file agents/communication.yaml
ant beta:agents create --file agents/information.yaml
```

-----

### Session Architecture

Sessions are the dynamic execution layer — one session per user turn that escalates to Tier 2:

```
Tier 1 local model: intent is complex → escalate
        ↓
Bridge Layer calls: ant beta:sessions create --agent-id typiros-information
        ↓
Session streams events back to Bridge Layer
        ↓
Bridge Layer translates result → natural language
        ↓
User sees one-line response. Session terminates.
```

Sessions are billed to the millisecond. Idle time is free. For typirOS’s pattern of short active turns between long idle periods, this is the most cost-efficient model possible.

-----

### The Bridge Layer → ant Interface

The Bridge Layer treats `ant` as a subprocess. All Tier 2 calls are structured as:

```bash
# Simple escalation
ant messages create \
  --model claude-sonnet-4-6 \
  --max-tokens 1024 \
  --message "{user_turn_context}"

# Agent session (complex multi-step)
ant beta:sessions create \
  --agent-id typiros-information \
  --message "{user_turn_context}" \
  --format json
```

Output is parsed as structured JSON. The Bridge Layer extracts the action and response text, executes the action via native APIs, and returns only the confirmation text to the chat shell. The `ant` subprocess is never visible to the user.

-----

### GitOps Agent Management

Agent definitions live in the typirOS repo alongside the kernel and shell code:

```
typiros/
├── kernel/
├── shell/
├── bridge/
└── agents/
    ├── communication.yaml
    ├── media.yaml
    ├── navigation.yaml
    ├── productivity.yaml
    ├── information.yaml
    ├── device.yaml
    ├── files.yaml
    └── finance.yaml
```

OS updates can ship new agent capabilities — better reasoning, new tools, updated system prompts — as a YAML diff. No app update required. No user-visible change. The conversation gets smarter silently.

-----

### Cost Model

|Execution path      |Cost                                           |
|--------------------|-----------------------------------------------|
|Tier 1 (local model)|$0 — fully on-device                           |
|Tier 2 message call |Standard Claude token rates                    |
|Tier 2 agent session|$0.08/hour + token rates, billed to millisecond|
|Idle sessions       |$0                                             |

For a typical typirOS usage pattern (80% Tier 1, 20% Tier 2 with short sessions), estimated cloud cost per user is negligible — well under $1/month for average usage.

-----

### Why This Architecture Wins

1. **No custom cloud infra to build or operate** — Anthropic runs the managed agent layer
1. **Agent capabilities update via YAML PR** — no OS firmware update needed
1. **Claude Code native** — development tooling already understands `ant`, accelerating typirOS development itself
1. **Proven production scale** — Anthropic’s infrastructure, not a custom stack
1. **Cost-efficient** — millisecond billing matches typirOS’s bursty, short-session usage pattern perfectly

-----

## 19. Distraction-Free Typing-First Addendum (v1.2)

typirOS is a **distraction-free, typing-first** operating system. Voice remains supported, but typed input is the primary interaction model. This addendum amends earlier sections where they leaned voice-first or push-interrupt-first.

### 19.1 Notification Model — Pull, Not Push *(amends §9)*

The frosted-glass interrupt cards in §9 are demoted from default to opt-in. The default state is **Quiet**:

- Incoming messages and non-urgent notifications **queue silently**. No cards, no sounds, no badges per app.
- A single subtle indicator (`•3`) appears in the status bar — the only signal that anything is waiting.
- The user pulls: typing “what did I miss” or `/missed` surfaces a batched digest.
- **Digest mode:** low-priority notifications are summarised into periodic digests (user-configurable cadence) instead of appearing individually.
- **Exception — true interrupts only:** incoming calls and explicitly starred contacts may still surface a card. Everything else waits.

### 19.2 Focus Sessions

A first-class OS primitive: `focus 90 minutes on writing`.

- During a Focus Session, the OS suppresses all queues from surfacing, auto-replies if configured, and only processes commands related to the stated goal (best-effort intent matching).
- Ending early requires a deliberate typed command — friction by design.
- Session summary on exit: what was held back, in one digest.

### 19.3 Typed Power Paths *(amends §4, §10)*

- **Slash commands** as zero-ambiguity fast paths alongside natural language: `/call lena`, `/remind 11pm sleep`, `/dnd on`. Same grammar, guaranteed parse, no AI round-trip.
- **Macros / aliases:** user-defined shorthand expanding to one or more actions. “gm” → weather + today’s calendar + reminders digest. Defined conversationally (“when I type gm, show me…”).
- **Multi-line compose & edit-before-send:** typing errors are more common than voice misrecognition; the draft is always editable before dispatch, and the last sent command is recallable for edit (`↑` convention).

### 19.4 Visual Minimalism *(amends §8)*

- Default responses are **text-only summaries**. Inline cards and overlays render only on explicit request (“show me”).
- No decorative animation, no sound effects in the core loop. Grayscale-first, e-ink-friendly aesthetic.
- Typography is the interface: hierarchy via weight and spacing, not color and chrome.

### 19.5 Voice as Accessibility Layer *(amends §14)*

- Voice input remains fully functional but is repositioned as an accessibility and hands-busy layer, not the primary path.
- §14 Adaptive mode inverts its defaults: keyboard is primary in all contexts except driving.
- Phase 1 ships keyboard-only; voice lands in Phase 3.

### 19.6 Physical Keyboard as First-Class Citizen

- Bluetooth/USB HID keyboards are first-class input devices with full shortcut support.
- The OS grammar and slash commands are designed to be fully drivable from a hardware keyboard — relevant for an eventual BlackBerry-style form factor (feeds Phase 5 hardware PRD).

### 19.7 Architectural Consequences

- Typed input is clean text — no ASR noise. Tier 1 local parse rates rise, grammar normalisation simplifies, and the <500ms target becomes beatable more often.
- The Tier 1 grammar engine gains a **deterministic pre-parser**: slash commands and exact grammar matches bypass the model entirely (0ms inference).
- Notification queueing becomes a Bridge Layer responsibility: containers and native APIs deliver into the queue; nothing surfaces without a pull or a true-interrupt flag.

### 19.8 The What-If Protocol

typirOS development runs a continuous speculative-design loop:

- Every working session, agents ask **“what if?”** about the current build and log candidate features to `what-ifs.md` with a rationale and a phase estimate.
- What-ifs are triaged into `tasks.md` (accepted), kept (parked), or closed (rejected with reason).
- Accepted what-ifs that change product behavior get folded into the PRD as numbered addenda.
- This section itself is the first output of the protocol.

### 19.9 Curated App Allowlist — Friction by Design for Container Apps *(amends §7)*

§7's Strategy A states that container apps are "silently invoked by the AI" the moment they're detected. That default is replaced with **restraint by policy**, merging the typing-first philosophy with a Light-Phone-style curated toolset:

- The Android container has a **default allowlist** of sanctioned apps reachable from chat (WhatsApp ships allowed by default; the long tail does not).
- Any container app outside the allowlist is **installed but inert** from the chat's perspective — detected, but not dispatchable — until the user deliberately runs `enable app <name>`.
- Enabling an app is friction by design, mirroring 19.2's "ending a focus session requires a deliberate typed command": a one-line confirmation (`Enabled: <app>. It will route silently from now on.`), not a settings-screen toggle.
- This changes Phase 2's success metric from *"any detected app works invisibly"* to *"only sanctioned apps work invisibly, and granting a new one is a conscious act"* — restraint lives in the allowlist gate, not in the UI.

-----

## 20. The Power-User Compact (v1.3)

v1.2 built the distraction-free, typing-first OS. v1.3 names the audience that
will carry it to the world: hackers, self-hosters, terminal people,
keyboard-driven-workflow people — the crowd that buys Framework laptops, runs
Home Assistant, treats dotfiles as identity, and evangelizes what it trusts.

For that audience, §2's Design Principle 3 (*"total opacity of mechanism"*) is
exactly backwards: they do not trust what they cannot inspect. This addendum
resolves the tension without breaking the product for everyone else:

> **Opacity by default. Sovereignty on demand.**

The pitch in one line: **the first phone that is yours the way your terminal is
yours.** Every capability below cuts against the incumbents' business models —
inspectability, self-hosting, and user programmability are things Apple and
Google structurally cannot ship. That is what makes this a defensible
revolution rather than a feature list.

Four pillars:

|Pillar|Claim|Sections|
|---|---|---|
|**Glass Box**|Privacy and mechanism are verifiable, not promised|20.1–20.4|
|**Programmable Substrate**|The phone is a Unix node you can compose and script|20.5–20.9|
|**Sovereign Stack**|You own the brain, the config, and the capability set|20.10–20.13|
|**Native to Nerd Infrastructure**|First-class citizen of the homelab, not a silo|20.14–20.18|

### Pillar I — Glass Box

#### 20.1 Glasnost Mode *(amends §2, §6)*

- `/why` after any action prints the full truthful trace of the last turn:
  parsed intent, tier-routing decision (and the reason), the exact tool-call
  JSON, which backend executed it, latency, and token cost. `/trace on`
  streams the same live for every turn.
- Design Principle 3 becomes a per-user posture, not a law: normies get
  opacity; nerds get a glass box. For this audience, *seeing* the mechanism is
  the trust mechanism.
- No other OS has ever let the user ask "why did you do that?" and get a
  complete, honest answer.
- Bridge Layer consequence: every turn retains a structured trace object
  (parse → route → dispatch → result → translation), whether or not anyone asks.

#### 20.2 Open Skull — Inspectable, Editable Memory *(amends §13)*

- `memory show`, `memory diff last week`, `memory forget philip's channel
  preference`, `memory edit` — all three memory layers rendered as
  human-readable records the user can read, correct, and delete line-by-line.
- The OS's beliefs about you stop being a black-box store and become a file
  you own; a wrong inference is fixable instead of haunting you.
- Pairs with 20.1 as the two halves of one promise: **nothing about you is
  hidden from you.**

#### 20.3 Egress Ledger — Verifiable Privacy *(amends §6, §15)*

- Every byte that leaves the device is logged and attributed — to a turn, a
  tool call, or a container — and queryable in the grammar: `show network
  today`, `what did the banking container send`.
- A chat-driven firewall: `block facebook.com everywhere`.
- §13/§15 *assert* on-device privacy; the ledger makes the claim
  **falsifiable**, which is the only kind of privacy claim this audience
  believes. "Trust us" becomes "check us."

#### 20.4 Local-Only Hard Mode *(amends §5, §15, §19.1)*

- `/airgap on` verifiably disables Tier 2 — not "prefers local" but *cannot
  escalate*. The software sibling of a hardware mic switch.
- The OS degrades honestly in language: "Can't summarise that offline — I can
  queue it." Queued escalations surface via the §19.1 digest when the gate
  reopens.
- Makes typirOS the only phone that is fully itself on a plane, in a dead
  zone, or in a country you don't trust.

### Pillar II — Programmable Substrate

#### 20.5 Pipes — the Grammar Is a Shell *(amends §10, §19.3)*

- `|` becomes a first-class grammar primitive: `calendar tomorrow | summarize
  | message lena`, `photos last week | filter receipts | email to accountant`.
- Each command's structured output (§6 already normalises results) feeds the
  next command's input slot. Composition, not just invocation: fifty verbs
  compose into thousands of workflows nobody had to design.
- The deterministic pre-parser (§19.7) splits on `|` with zero inference; each
  segment then parses normally.
- This is the moment terminal people recognize the OS as *theirs*.

#### 20.6 Hooks — the OS as an Event Bus *(amends §10, §12, §19.1)*

- Trigger→action rules in the same grammar: `when battery below 20, dnd on`;
  `when message from mom arrives during focus, allow through`; `every monday
  8am, run gm`.
- `when` (§10) generalises from one hard-coded reminder condition to *any OS
  event*; `every` adds schedules. `/hooks` lists and edits the rule set.
- System Agents (§12) gain a responsibility: emitting events onto the bus.
  The §19.1 notification queue becomes just one consumer of it.
- No one has shipped a phone where the user programs the phone's *behavior*,
  not just its apps.

#### 20.7 The Wire — SSH Into Your Phone *(amends §19.6; extends §15)*

- The chat loop is exposed as an authenticated line protocol: `ssh phone`
  drops you into the same conversation from a laptop.
- A `typir` CLI lets shell scripts drive the device: `typir "message lena
  running late"`, `typir --json battery`. Your phone becomes an addressable
  node in cron jobs, CI pipelines, and your editor config.
- Security model: key-based auth, per-key capability scoping, Biometric Gate
  (§15) domains enforced identically over the wire.
- The one-line pitch that sells itself at every Linux meetup on earth:
  **you can pipe your phone.**

#### 20.8 Webhook Inbox — Your Infrastructure Talks Back *(amends §19.1)*

- An authenticated endpoint (LAN/VPN-reachable) where external systems post
  into the quiet notification queue: CI failure, Grafana alert, Home Assistant
  event, `curl` from anywhere.
- Inbound webhooks are hookable (20.6): `when webhook deploy-failed arrives,
  mark urgent`.
- The pull-based Quiet model now covers your *servers*, not just your
  contacts — typirOS is the natural pager for self-hosters. The inbound half
  of The Wire.

#### 20.9 Inline REPL *(amends §7)*

- A sandboxed real interpreter as an AI-native function: `> py: [x**2 for x
  in range(10)]`, plus a scratch space for jq/awk one-liners.
- Replaces §7's "calculator" row with the calculator this audience actually
  wants. Output is pipeable (20.5).

### Pillar III — Sovereign Stack

#### 20.10 Sovereign Tier 2 — Bring Your Own Model *(amends §5, §18)*

- Tier 2 escalation becomes a pluggable provider interface: `set brain to
  ollama.homelab.lan` points the cloud tier at your own llama.cpp/vLLM box,
  any compatible API, or a VPN-reachable homelab GPU.
- ant / Anthropic Managed Agents (§18) remains the managed **default**, not
  the mandate.
- The purchase-deciding feature for self-hosters: a phone whose intelligence
  you fully own is a category no vendor has ever shipped. It also converts
  §5's "requires connectivity" weakness into a resilience story — your LAN
  model works when the internet doesn't.

#### 20.11 Phone-as-Code — Dotfiles for Your Phone *(amends §13, §16)*

- Every piece of OS state that is *configuration* — macros, hooks, allowlist,
  agent settings, keyboard mode, digest cadence — lives as plain-text files in
  one directory that is a git repo. `typir apply` makes the device match the
  files.
- Wipe your phone, clone your repo, and you're home in ninety seconds. Share
  your setup the way people share editor configs.
- §13 consequence: the User memory layer splits into config-as-files
  (versionable, shareable) vs. learned data (private, 20.2-inspectable).
- Reproducibility is a value this crowd holds almost religiously; no mobile
  OS has ever offered it.

#### 20.12 tpkg — the Agent Package Manager *(amends §12, §18, §19.9)*

- Community-authored capability packs — agent YAMLs, grammar verbs, macros,
  hooks — installable via `tpkg install gtd`, signed, versioned, diffable,
  from a public registry. AUR for your phone's brain.
- §18's GitOps agent management is producer-side only; tpkg opens it to the
  community and creates the ecosystem moat.
- Packs are plain text, so they're **auditable before install**; the §19.9
  allowlist gate extends naturally to third-party capabilities — restraint by
  policy, again.

#### 20.13 The Forge — the OS Writes Its Own Tools *(amends §7, §15, §18)*

- "I need something that tracks my caffeine intake" → the OS (via §18's
  agent runtime, which can already spawn agents) writes the tool, sandboxes
  it, and registers it in the tool manifest — callable on the next turn.
- Source is shown for review before activation (20.1 synergy); generated code
  runs under an explicit §15 sandbox policy.
- Strategy C (§7, "AI as the app") taken to its logical end: the long tail of
  apps isn't curated, it's **generated on demand**. The single most "the
  future arrived" demo in the deck.

### Pillar IV — Native to Nerd Infrastructure

#### 20.14 Home — the Ninth Agent *(amends §7, §12)*

- A first-class **Home** agent speaking Home Assistant's API and MQTT
  natively: `lights off downstairs`, `is the garage open`, and — compounding
  with 20.6 — `when I leave home, arm the alarm`.
- §12's roster grows to nine. The eight agents cover the phone; Home covers
  the nerd's house, and Home Assistant's install base is precisely the target
  buyer.
- Conversational control of HA is *better* than HA's own dashboards — a case
  where typirOS beats the incumbent tool, not just matches it.

#### 20.15 Matrix as a First-Class Channel *(amends §7, §12)*

- Native Matrix support: `message philip through matrix`, backed by your own
  homeserver. The Communication agent treats it as a peer of SMS/WhatsApp.
- A fourth angle on §7's WhatsApp Problem: bridges become the escape hatch,
  and typirOS is the only phone whose flagship messaging path is federated
  and self-hostable.
- Ship it for credibility with the audience that sets everyone else's
  opinions, not for volume.

#### 20.16 Mesh Sync — Local-First Multi-Device State *(amends §13, §15)*

- Memory layers and chat history CRDT-sync across your devices over
  LAN/VPN with end-to-end encryption and **no vendor account**.
- Start a thought on the phone, finish it via The Wire (20.7) on a laptop —
  same conversation, same memory.
- "Syncthing for your OS state." The §13 privacy guarantee extends across
  devices without a cloud in the middle.

#### 20.17 grep-your-life — the Transcript Is a Dataset *(amends §10, §13)*

- Every turn is appended to a local, exportable JSONL log with a query
  grammar over it: `history | grep lena | last month`. jq-able, yours.
- The chat window quietly becomes the best lifelog ever built, because it is
  a *complete* record of everything you asked your computer to do — and it
  composes with Pipes (20.5) and Open Skull (20.2) for free.

#### 20.18 `/attest` — Reproducible Builds, Runtime Attestation *(amends §15, §16)*

- The ROM builds reproducibly from public source; `/attest` makes the runtime
  prove itself on demand — hash of the running system prompt, tool-manifest
  version, model checksums.
- "The OS isn't injecting ads into my AI" becomes checkable, not vibes. The
  long-game credibility play that multiplies trust in everything above.

### 20.19 Positioning & Sequencing

- **Launch pillars (Tier A):** Glasnost (20.1), Sovereign Tier 2 (20.10),
  Pipes (20.5), Hooks (20.6), The Wire (20.7). Together they are one coherent
  story — *verifiable, sovereign, programmable* — that no incumbent can copy
  without betraying its business model.
- **Strong differentiators (Tier B):** 20.2–20.4, 20.8, 20.11–20.14.
- **Fast-follow credibility features (Tier C):** 20.9, 20.15–20.18 — shipped
  to keep the promise honest, not to headline the launch.
- Per §19.8, each section entered through the What-If Protocol
  (WIF-018–WIF-035) and is triaged into build phases in `plans.md`
  (Phase 6 — The Power-User Compact).

-----

*typirOS PRD v1.3 — Confidential*
*“If the user has to think about how the phone is doing it, the OS has failed.”*
*“…unless the user asks. Then the OS shows its work.”*
