# Shell

The chat-window UI — the entire user-facing surface of typirOS (PRD §8),
typing-first and distraction-free (PRD §19).

## Phase 1 prototype (runnable now)

A dependency-free Python implementation of the single loop (PRD §3):
deterministic Tier 1 grammar parser → Bridge Layer → mock backends →
one-line confirmation.

```bash
cd shell
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

## Architecture

```
typiros_shell/
├── main.py           # REPL: prompt, strips header, pending-slot filling
├── intent.py         # Tier 1 deterministic parser (grammar + slash commands)
├── bridge.py         # Bridge Layer: routing + error→language translation
├── contacts.py       # contact store, prefix resolution, 2-chip max
├── memory.py         # session memory (last SIM, last contact, pending)
├── notifications.py  # quiet queue + digest
└── backends/         # mocks with PRD §5 tool-manifest signatures
    ├── telephony.py  # make_call / end_call / send_message
    ├── device.py     # set_setting
    └── productivity.py # alarms, reminders, timers
```

The UI layer (main.py) is deliberately thin: M5 replaces it with a TUI and
later a mobile shell without touching intent/bridge/backends. Off-grammar
input currently fails in language; M4 adds the Tier 1 local-LLM fallback.

See [plans.md](../plans.md) for milestones M1–M5.
