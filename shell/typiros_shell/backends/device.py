"""Mock device-settings backend (PRD §5 set_setting). Real backend: dbus."""

KNOWN_SETTINGS = {
    "brightness": {"low", "medium", "high"},
    "volume": {"mute", "low", "medium", "high"},
    "wifi": {"on", "off"},
    "bluetooth": {"on", "off"},
    "dnd": {"on", "off"},
}


class Device:
    def __init__(self) -> None:
        self.settings = {
            "brightness": "medium",
            "volume": "medium",
            "wifi": "on",
            "bluetooth": "off",
            "dnd": "off",
        }

    def set_setting(self, key: str, value: str) -> str:
        if key not in KNOWN_SETTINGS:
            raise ValueError(f"no setting called {key!r}")
        if value not in KNOWN_SETTINGS[key]:
            allowed = ", ".join(sorted(KNOWN_SETTINGS[key]))
            raise ValueError(f"{key} can be {allowed} — not {value!r}")
        self.settings[key] = value
        if key in ("wifi", "bluetooth", "dnd"):
            label = "DND" if key == "dnd" else key.title() if key == "bluetooth" else "WiFi"
            return f"{label} {value}."
        return f"{key.title()} set to {value}."
