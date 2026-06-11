# Bridge Layer

The opacity engine. Sits between the AI runtime and all execution backends —
Native API, Android compatibility container, and `ant` / Anthropic Managed
Agents for Tier 2.

Responsibilities:

- Route every tool call to the correct backend
- Suppress all native/container UI — no dialogs, no toasts
- Pre-warm frequently used containers
- Catch all errors and translate to natural language
- Normalise responses into a standard result format
- Gate permission dialogs (handled once at OS setup)

See [PRD.md § 6](../PRD.md#6-the-bridge-layer) and [§ 18](../PRD.md#18-ant--managed-agents-integration).
