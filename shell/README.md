# Shell

The chat-window UI — the entire user-facing surface of typirOS (PRD §8),
typing-first and distraction-free (PRD §19).

## Phases 1–4 prototype (runnable now)

A Python implementation of the single loop (PRD §3): deterministic Tier 1
grammar parser → Bridge Layer → mock backends → one-line confirmation.
Covers every sandbox-feasible milestone through Phase 4 (full agent
coverage, keyboard system, episodic memory, full-screen overlays, a
security audit, performance profiling, and real encryption at rest) — see
[plans.md](../plans.md) for what's left (Phase 4's two hardware-only
items, ROM packaging and battery optimization, stay out of scope; Phase 5
hardware is next). Stdlib-only through Phase 3; Phase 4 M18 adds the
project's first dependency (`cryptography`, for real memory encryption at
rest — see below).

```bash
cd shell
pip install -r requirements.txt    # one dependency: cryptography (M18)
python3 -m typiros_shell           # interactive
python3 -m typiros_shell < demo.txt  # scripted end-to-end demo
```

What works:

- **Grammar (PRD §10):** `call lena`, `call lena through secondary`,
  `message philip sharma running late`, `set alarm for 7am`,
  `set brightness to low`, `turn off wifi`, `remind me to call mom at 6pm`,
  `set a timer for 10 minutes`, `end call`
- **Slash fast paths (PRD §19.3):** `/call`, `/msg`, `/remind`, `/missed`,
  `/help`, `/quit`
- **Disambiguation chips (PRD §11):** `message phil` → `[1] Philip Sharma  [2] Philip D'Souza`
- **Context strips (PRD §9):** active call and running timer render as a
  text header, max 3
- **Quiet queue (PRD §19.1):** inbound events queue silently (`/sim sms
  lena: hey` to simulate); only a `•N` prompt indicator appears; pull the
  digest with `what did i miss`
- **Session memory / pronoun resolution (PRD §13):** `call her back`,
  `text them` resolve to the last contact you called, messaged, or heard
  from
- **Correction flow (PRD §11):** after a call or message, `no, secondary` /
  `no, primary` silently re-dispatches the same action on the other SIM and
  the OS remembers the preference
- **Message-body capture (PRD §10):** `message lena` (single unambiguous
  contact, no body) prompts `What should it say?` before sending
- **Macros (PRD §19.3):** `when I type gm, what did i miss and set an alarm
  for 7am` defines `gm`; typing `gm` runs both actions and prints both
  results
- **Recall / edit (PRD §19.3):** `again` re-runs the last command; `edit`
  prints it back for retyping with changes
- **Digest cadence (PRD §19.1):** `digest every 30m` configures auto-batching;
  the digest surfaces automatically between turns when the interval elapses;
  `digest off` disables
- **Focus sessions (PRD §19.2):** `focus 90m on writing` suppresses the quiet
  indicator and shows `[focus] writing · 89:30 left` strip; `end focus`
  produces a held-back digest of everything queued during the session; focus
  also auto-expires in real-time when the timer runs out
- **Background event simulation:** `/sim auto on [N]` starts a daemon thread
  that pushes sample inbound events every N seconds (default 30), making the
  `•N` indicator increment between turns without any user action; `/sim auto off`
  stops it (interactive sessions only — not used in demo.txt)
- **Android container + app allowlist (PRD §7, §19.9):** `message X via
  whatsapp` / `message X on instagram` route through the mock
  `AndroidContainer` backend instead of telephony; `no, whatsapp` switches
  the last message's channel. Only allowlisted apps (WhatsApp by default)
  dispatch silently — anything else detected in the container (Instagram)
  fails in language with a pointer to `enable app <name>`, the deliberate
  opt-in
- **Media agent (mock):** `play some jazz` / `pause` / `what's playing`
  drive the mock `Media` backend; `[media] <track> · playing|paused` strip
  shares the max-3 budget with call/timer/focus strips
- **Tier 2 stub (PRD §18):** input that doesn't parse on-grammar escalates
  instead of failing in language — `tier2.py` reads the `agents/*.yaml`
  manifests, picks the best-matching System Agent by keyword overlap, and
  returns a canned `[tier2-stub] typiros-information would handle: "..."`
  response. No subprocess, no API call — proves the two-model routing shape
  without cloud credentials
- **User memory layer (PRD §13):** SIM corrections (`no, secondary`) and
  macro definitions now persist to a local sqlite file
  (`typiros_shell/user_memory.db`) and survive process restarts — call Lena
  once with `no, secondary` and every future `call lena` in a later session
  defaults to Secondary. Piped/scripted runs (`demo.txt`, tests) use an
  in-memory DB instead, so the demo stays deterministic across repeated runs
- **Memory encryption at rest (Phase 4 M18, PRD §15):** `user_memory.db`
  and `episodic_memory.db` are AES-256-GCM ciphertext on disk
  (`crypto_store.py`) — the project's first dependency outside the
  standard library (`cryptography`). sqlite3 can't write straight into
  ciphertext, so the working file lives in a private temp path for the
  process lifetime and the encrypted bytes are flushed back to disk after
  every write; the per-file key lives alongside it (`*.key`, `0o600`).
  In-memory (piped/scripted) runs skip encryption entirely, same as the
  plaintext-vs-`:memory:` split above
- **Navigation agent (mock, Phase 3 M10):** `navigate to the airport` /
  `eta` / `where am i going` / `stop navigating` drive the mock `Navigation`
  backend; `[nav] <destination> · ETA <N> min` strip shares the max-3 budget
  with call/timer/media/focus strips
- **Information agent (mock, Phase 3 M11):** `weather in paris` / `what's
  the time` / `what's the capital of france` now resolve through real Tier 1
  grammar and the mock `Information` backend instead of escalating —
  graduated out of the Tier 2 stub as a small canned subset. Queries outside
  that subset (`what's the capital of mars`) fail gracefully in language;
  anything else off-grammar (`send an email to mom`) still escalates to
  `tier2.py` unchanged
- **Files agent (mock, Phase 3 M12):** `find file budget` / `recent files`
  search a small mock file index; a single match returns one line, multiple
  matches list each, no match fails gracefully in language
- **Finance agent (mock) + Biometric gate (Phase 3 M13, PRD §15):** `balance`
  / `send 20 to mom` drive the mock `Finance` backend; the first sensitive
  action in a session pauses for a typed passphrase (`1234` — a mock
  fingerprint/face prompt) via `biometric.py`'s `BiometricGate`, gated at
  the Bridge Layer the same way the M6 allowlist check is; a wrong
  passphrase re-prompts, a correct one unlocks the `finance` domain for the
  rest of the session so further `balance`/payment calls dispatch silently
  (both are gated — M16's audit found `balance` had been dispatching
  unauthenticated, against PRD §15's "personal data retrieval" wording)
- **Keyboard system (mock, Phase 3 M14, PRD §14):** `keyboard mode compact`
  / `standard` / `voice first` / `adaptive` switch input mode; `[keyboard]`
  strip shows the active non-Standard mode. **Compact** expands a small set
  of abbreviations (`cl`, `mm`, `wdim`, `timer`) via `tier2.py`'s shared
  keyword-overlap scorer (`tokenize`/`best_match`, resolving WIF-015) —
  tried only as a fallback when the raw input doesn't already match Tier 1
  grammar, so on-grammar commands like `end call` are never misfired
  against an unrelated abbreviation. **Voice First** has no mic in this
  prototype; `/voice <text>` is the proxy a real mic button would call.
  **Adaptive** switches automatically per PRD §14's context table — reuses
  the telephony backend's active-call state and the device backend's `dnd`
  setting where they already exist, and mocks the two signals with no
  existing equivalent (`driving`, `motion`) via `/sim sensor <signal>
  on/off`
- **Episodic memory (Phase 3 M15, PRD §13):** `history` / `history with
  lena` reads a rolling, sqlite-backed log of past contact-tied actions
  (calls, messages, payments) via `episodic_memory.py`'s `EpisodicMemory`
  — separate from the permanent User memory layer (prefs/macros) and the
  RAM-only Session memory. Logged on every dispatched call/message/payment
  in `bridge.py`; rows older than 90 days are pruned on each write so the
  table stays a true rolling window. Piped/scripted runs use an in-memory
  DB, same pattern as `user_memory.py`. Gated by the Biometric Gate as of
  M16 — relationship history is "personal data retrieval" under PRD §15
  too, not just finance
- **Full-screen overlays (Phase 3 M15, PRD §8, TUI only):** `show media` /
  `show maps` / `show photos` push a placeholder full-screen `Screen`
  (`overlays.py`) over the chat in the TUI — single dismiss gesture is
  Esc, matching the PRD's "always one gesture away" rule; any running
  call/timer/media keeps going underneath. In the line REPL the same
  commands just print the content inline — no overlay support there by
  design (TUI only per `plans.md`)
- **Memory encryption at rest (Phase 4 M18, PRD §15):** `user_memory.db`
  and `episodic_memory.db` are AES-256-GCM ciphertext on disk
  (`crypto_store.py`) — the project's first dependency outside the
  standard library (`cryptography`). Plaintext never touches disk: the
  working sqlite connection lives entirely in memory
  (`sqlite3.Connection.serialize()`/`deserialize()`, stdlib 3.11+) and is
  re-encrypted back to its on-disk path after every write. In-memory
  (piped/scripted) runs skip this entirely — no file to protect
- **Security audit (Phase 4 M16, PRD §15):** reviewed the Bridge Layer,
  Biometric Gate, and Android container against Container
  Isolation/Permission Model/Biometric Gate. Found and fixed: the
  Biometric Gate had only covered `send_payment`, leaving `balance` and
  `episode_history` ("personal data retrieval" per PRD §15) dispatching
  unauthenticated; `no, primary`/`no, secondary` corrections bypassed the
  gate entirely by calling the Bridge directly instead of through the
  gate-checking dispatch path; and M18's own first pass at encryption
  decrypted to a plaintext temp file that an unclean kill would have left
  on disk — replaced with the in-memory approach above
- **Performance profiling (Phase 4 M17, PRD §16):** `python3 -m
  typiros_shell.benchmark` times `intent.parse()` alone and a full
  `Shell.handle()` turn (parse + Bridge dispatch + translation) across one
  phrase per grammar branch, 200 reps each. Worst case observed on this
  sandbox's CPU: 0.74ms for a full turn — about 700x under the PRD's
  <500ms target. Stated caveat: this is a software-path sanity check
  (deterministic regex/dict dispatch, no model inference), not a
  target-hardware latency guarantee — a real phone SoC wasn't available
  to benchmark against

## Running

```bash
cd shell
python3 -m typiros_shell           # line REPL (Phase 1 M1–M4 baseline)
python3 -m typiros_shell --tui     # Textual TUI (Phase 1 M5)
python3 -m typiros_shell < demo.txt  # scripted end-to-end demo
python3 -m typiros_shell.benchmark   # Tier 1 performance profile (Phase 4 M17)
```

## TUI (M5)

`python3 -m typiros_shell --tui` opens a Textual-based chat window.

Layout (top → bottom):
- **Status bar** — title; shows `· focus: <label>` during a focus session
- **Strips bar** — persistent context strips (`[focus]`, `[call]`, `[timer]`); hidden when none active
- **Chat log** — scrollable history of every input/response pair
- **Chips bar** — disambiguation chips (`[1] Philip Sharma  [2] Philip D'Souza`); shown only during an ambiguous match
- **Input bar** — single-line text input; type anything, press Enter

The UI layer (`tui.py`) is a drop-in replacement for `main.py`; the intent
parser, bridge, memory, and all backends are unchanged. `tui.py` also owns
the one TUI-only feature, full-screen overlays (Phase 3 M15): it peeks the
parsed intent to detect a `show_overlay` command and pushes the matching
`Screen` from `overlays.py` — `main.py`/`bridge.py` stay UI-agnostic and
just return text either way.

## Architecture

```
typiros_shell/
├── main.py           # REPL: prompt, strips header, pending-slot filling
├── intent.py         # Tier 1 deterministic parser (grammar + slash commands)
├── bridge.py         # Bridge Layer: routing + error→language translation
├── contacts.py       # contact store, prefix resolution, 2-chip max
├── memory.py         # session memory (last SIM, last contact, pending)
├── user_memory.py    # User memory layer: sqlite-backed SIM prefs, allowlist, macros
├── crypto_store.py   # AES-256-GCM encryption-at-rest for user/episodic memory sqlite files (M18)
├── notifications.py  # quiet queue + digest
├── tier2.py          # Tier 2 stub: off-grammar input → agents/*.yaml-routed canned response; shares tokenize/best_match with keyboard.py
├── biometric.py      # Mock Biometric Gate: passphrase challenge, one unlock/session/domain
├── keyboard.py       # Keyboard System (PRD §14): Compact/Standard/Voice First/Adaptive modes
├── episodic_memory.py # Episodic memory layer: sqlite-backed rolling 90-day log of contact-tied actions
├── overlays.py       # Full-screen overlay Screens (Media/Maps/Photos placeholders) — tui.py only
├── benchmark.py      # Tier 1 performance profiling (M17): intent.parse + Shell.handle latency
└── backends/         # mocks with PRD §5 tool-manifest signatures
    ├── telephony.py  # make_call / end_call / send_message
    ├── device.py     # set_setting
    ├── productivity.py # alarms, reminders, timers
    ├── android.py    # AndroidContainer mock: installed apps, allowlist gate, send
    ├── media.py      # Media mock: play / pause / now_playing
    ├── navigation.py # Navigation mock: navigate / eta / current_route / stop
    ├── information.py # Information mock: weather / time / canned facts
    ├── files.py      # Files mock: find_file / recent_files over a mock index
    └── finance.py    # Finance mock: balance / send_payment — gated by biometric.py
```

The UI layer (main.py) is deliberately thin: M5 replaces it with a TUI and
later a mobile shell without touching intent/bridge/backends. Off-grammar
input escalates to the Tier 2 stub (M8); a real local LLM Tier 1 fallback
remains a Phase 1 M4 item for real hardware.

See [plans.md](../plans.md) for milestones M1–M15.
