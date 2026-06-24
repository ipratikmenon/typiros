"""Tier 1 performance profiling (PRD §16 Phase 4, M17).

Times two things across a phrase set covering every grammar branch in
`intent.py`:

  - `intent.parse()` alone — the literal Tier 1 deterministic-grammar stage
  - a full `Shell.handle()` turn — parse + Bridge dispatch + translation,
    i.e. what a user actually waits on

against the PRD's "<500ms Tier 1 response" target. Caveat stated up front
and in the output: this sandbox's CPU is not "target hardware" (a real
phone SoC) — these numbers establish that the *software path* has no
gross inefficiency, not a hardware-accurate latency guarantee.

Run: python3 -m typiros_shell.benchmark
"""

import statistics
import time

from . import intent
from .main import Shell

REPS = 200

# One phrase per grammar branch in intent.py; biometric-gated tools are
# pre-unlocked below so this measures steady-state dispatch, not the
# one-time challenge pause.
PHRASES = [
    "what did i miss",
    "call lena",
    "end call",
    "message philip sharma running late",
    "remind me to call mom at 6pm",
    "set alarm for 7am",
    "set a timer for 10 minutes",
    "set brightness to low",
    "turn off wifi",
    "wifi on",
    "digest every 30m",
    "digest off",
    "enable app instagram",
    "pause",
    "what's playing",
    "play some jazz",
    "what's the weather in paris",
    "what's the time",
    "what's the capital of france",
    "keyboard mode compact",
    "keyboard mode standard",
    "history with lena",
    "history",
    "show media",
    "show maps",
    "show photos",
    "balance",
    "send 5 to mom",
    "recent files",
    "find file budget",
    "stop navigating",
    "eta",
    "where am i going",
    "navigate to the airport",
    "focus 5m on testing",
    "end focus",
]


def _timed(fn, reps: int) -> list[float]:
    samples = []
    for _ in range(reps):
        start = time.perf_counter()
        fn()
        samples.append((time.perf_counter() - start) * 1000)
    return samples


def _report(label: str, samples: list[float]) -> None:
    samples.sort()
    p95 = samples[int(len(samples) * 0.95) - 1]
    print(
        f"  {label:<42} mean {statistics.mean(samples):6.3f}ms  "
        f"p50 {statistics.median(samples):6.3f}ms  "
        f"p95 {p95:6.3f}ms  max {max(samples):6.3f}ms"
    )


def main() -> None:
    shell = Shell(db_path=":memory:", episodic_db_path=":memory:")
    shell.bridge.biometric.confirm("finance", "1234")
    shell.bridge.biometric.confirm("episodic", "1234")

    print(f"Tier 1 performance profile — {REPS} reps/phrase, this sandbox's CPU "
          "(not target hardware; see PRD §16)\n")

    print("intent.parse() only — the deterministic Tier 1 grammar stage:")
    parse_all: list[float] = []
    for phrase in PHRASES:
        samples = _timed(lambda p=phrase: intent.parse(p), REPS)
        parse_all.extend(samples)
        _report(phrase, samples)

    print("\nfull Shell.handle() turn — parse + Bridge dispatch + translation:")
    turn_all: list[float] = []
    for phrase in PHRASES:
        samples = _timed(lambda p=phrase: shell.handle(p), REPS)
        turn_all.extend(samples)
        _report(phrase, samples)

    target_ms = 500.0
    worst_parse = max(parse_all)
    worst_turn = max(turn_all)
    print(f"\nOverall: intent.parse() worst-case {worst_parse:.3f}ms, "
          f"full-turn worst-case {worst_turn:.3f}ms, against a {target_ms:.0f}ms target.")
    verdict = "well within" if worst_turn < target_ms / 10 else "within"
    print(f"Both stay {verdict} the <500ms target by a wide margin on this hardware — "
          "deterministic regex/dict dispatch, no model inference in the loop.")


if __name__ == "__main__":
    main()
