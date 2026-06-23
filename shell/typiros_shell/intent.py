"""Tier 1 deterministic grammar parser (PRD §10, §19.7).

Typed input is clean text, so slash commands and grammar matches are parsed
with zero model inference. Off-grammar input falls through — in the full OS
that escalates to the local LLM, then Tier 2 (PRD §5).
"""

import re
from dataclasses import dataclass, field

from . import contacts
from .contacts import Contact
from .memory import Pending


@dataclass
class ToolCall:
    tool: str
    args: dict


@dataclass
class Clarify:
    question: str
    pending: Pending
    options: list[Contact] = field(default_factory=list)


@dataclass
class Say:
    text: str


@dataclass
class Quit:
    pass


@dataclass
class Escalate:
    """Off-grammar input — Tier 1 has no parse; escalates to Tier 2 (PRD §18)."""

    text: str


Result = ToolCall | Clarify | Say | Quit | Escalate

HELP = """typirOS — type what you want done. Examples:
  call lena                          message philip sharma running late
  call lena through secondary        set alarm for 7am
  set brightness to low              turn off wifi
  remind me to call mom at 6pm       set a timer for 10 minutes
  end call                           what did i miss
  call her back                      no, secondary  (corrects last call/text)
  message lena via whatsapp          no, whatsapp  (switches channel)
  enable app instagram               (allowlists a detected container app)
  play some jazz                     pause  /  what's playing
  when i type gm, X and Y            gm  (runs a macro)
  again                              edit  (recall / show last command)
  focus 90m on writing               end focus
  digest every 30m                   digest off
Off-grammar input escalates to Tier 2 (stubbed — no live model call yet).
Slash fast paths: /call /msg /missed /help /quit"""

SLASH_ALIASES = {
    "/call": "call",
    "/msg": "message",
    "/remind": "remind me to",
    "/missed": "what did i miss",
}

TIME_RE = r"(\d{1,2}(?::\d{2})?\s*(?:am|pm)?|noon|midnight)"

PRONOUN_RE = re.compile(r"\b(him|her|them)\b", re.IGNORECASE)
TRAILING_BACK_RE = re.compile(r"\s+back$", re.IGNORECASE)


def resolve_pronouns(text: str, last_contact: Contact | None) -> str:
    """"Call him back" / "message her" / "text them" → last contact (PRD §13)."""
    if last_contact is None or not PRONOUN_RE.search(text):
        return text
    text = TRAILING_BACK_RE.sub("", text)
    return PRONOUN_RE.sub(last_contact.name, text)


def parse(raw: str) -> Result:
    text = raw.strip()
    if not text:
        return Say("")
    low = text.lower()

    # --- slash fast paths (PRD §19.3) ---
    if low in ("/quit", "/exit", "quit", "exit"):
        return Quit()
    if low in ("/help", "help", "?"):
        return Say(HELP)
    first, _, rest = low.partition(" ")
    if first in SLASH_ALIASES:
        low = f"{SLASH_ALIASES[first]} {rest}".strip()

    # --- pull the queue (PRD §19.1) ---
    if re.fullmatch(r"(what did i miss\??|anything new\??|missed)", low):
        return ToolCall("show_missed", {})

    # --- call control ---
    if re.fullmatch(r"(end( the)? call|hang up)", low):
        return ToolCall("end_call", {})

    if m := re.match(r"(?:call|phone|ring)\s+(.+)", low):
        return _parse_call(m.group(1))

    if m := re.match(r"(?:message|text|sms)\s+(.+)", low):
        return _parse_message(m.group(1))

    # --- reminders ---
    if m := re.match(r"remind me (?:to|about)\s+(.+)", low):
        body = m.group(1)
        when = None
        if t := re.search(rf"\s+at\s+{TIME_RE}$", body):
            when, body = t.group(1), body[: t.start()]
        return ToolCall("create_reminder", {"text": body.strip(), "when": when})

    # --- alarms ---
    if m := re.match(rf"(?:set (?:an? )?alarm (?:for|at)|wake me(?: up)? at)\s+{TIME_RE}", low):
        return ToolCall("set_alarm", {"when": m.group(1)})

    # --- timers ---
    if m := re.match(r"(?:set a timer for|timer)\s+(.+)", low):
        return ToolCall("set_timer", {"duration": m.group(1)})

    # --- settings ---
    if m := re.match(r"set (?:the )?(\w+) to (\w+)", low):
        return ToolCall("set_setting", {"key": m.group(1), "value": m.group(2)})
    if m := re.match(r"turn (on|off) (?:the )?(\w+)", low):
        return ToolCall("set_setting", {"key": m.group(2), "value": m.group(1)})
    if m := re.fullmatch(r"(wifi|bluetooth|dnd) (on|off)", low):
        return ToolCall("set_setting", {"key": m.group(1), "value": m.group(2)})

    # --- digest cadence (PRD §19.1) ---
    if re.fullmatch(r"digest off", low):
        return ToolCall("set_digest_cadence", {"interval": "off"})
    if m := re.match(r"digest every (.+)", low):
        return ToolCall("set_digest_cadence", {"interval": m.group(1).strip()})

    # --- app allowlist (PRD §19.9) ---
    if m := re.match(r"enable app\s+(.+)", low):
        return ToolCall("enable_app", {"app": m.group(1).strip()})

    # --- media agent ---
    if re.fullmatch(r"pause(?: (?:the )?music)?", low):
        return ToolCall("pause_media", {})
    if re.fullmatch(r"(?:what'?s playing\??|now playing\??)", low):
        return ToolCall("now_playing", {})
    if m := re.match(r"play\s+(.+)", low):
        return ToolCall("play_track", {"track": m.group(1).strip()})

    # --- focus sessions (PRD §19.2) ---
    if re.fullmatch(r"end focus|focus done|stop focus", low):
        return ToolCall("end_focus", {})
    if m := re.match(r"focus\s+(.+?)\s+on\s+(.+)", low):
        return ToolCall("start_focus", {"duration": m.group(1).strip(), "label": m.group(2).strip()})
    if m := re.match(r"focus\s+(.+)", low):
        return ToolCall("start_focus", {"duration": m.group(1).strip(), "label": "focus"})

    return Escalate(text)


def _split_channel(words: list[str]) -> tuple[list[str], str | None, str | None]:
    """Extract 'through <sim>' / 'on <app>' qualifiers (PRD §10)."""
    sim = app = None
    out: list[str] = []
    i = 0
    while i < len(words):
        if words[i] == "through" and i + 1 < len(words):
            qualifier = words[i + 1].rstrip(",")
            if qualifier in ("primary", "secondary"):
                sim = qualifier.title()
            else:
                app = qualifier
            i += 2
        elif words[i] == "via" and i + 1 < len(words):
            app = words[i + 1].rstrip(",")
            i += 2
        elif words[i] == "on" and i + 1 < len(words):
            app = words[i + 1].rstrip(",")
            i += 2
        else:
            out.append(words[i])
            i += 1
    return out, sim, app


def _parse_call(rest: str) -> Result:
    words, sim, _app = _split_channel(rest.split())
    matches, leftover = contacts.resolve(words)
    args = {"sim": sim}
    if len(matches) == 1 and not leftover:
        args["contact"] = matches[0]
        return ToolCall("make_call", args)
    if len(matches) > 1:
        return Clarify(
            "Which one?", Pending("make_call", args, "contact", matches), matches
        )
    return Say(f"No contact matching “{' '.join(words)}”.")


def _parse_message(rest: str) -> Result:
    words, sim, app = _split_channel(rest.split())
    matches, body_words = contacts.resolve(words)
    args = {"channel": app or "sms", "sim": sim}
    body = " ".join(body_words).strip(" ,:")
    if len(matches) == 1:
        args["contact"] = matches[0]
        if body:
            args["body"] = body
            return ToolCall("send_message", args)
        return Clarify("What should it say?", Pending("send_message", args, "body"))
    if len(matches) > 1:
        if body:
            args["body"] = body
        missing = "contact"
        return Clarify("Which one?", Pending("send_message", args, missing, matches), matches)
    return Say(f"No contact matching “{' '.join(words)}”.")
