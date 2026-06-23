"""Mock Files agent (PRD §16 Phase 3 M12). Real backend: on-device file index/container."""

MOCK_INDEX = [
    {"name": "Q3 Budget.xlsx", "modified": "2026-06-20"},
    {"name": "Vacation Photos.zip", "modified": "2026-06-18"},
    {"name": "Resume.pdf", "modified": "2026-06-15"},
    {"name": "Project Plan.docx", "modified": "2026-06-22"},
    {"name": "Notes.txt", "modified": "2026-06-23"},
]


class Files:
    def find_file(self, query: str) -> str:
        matches = [f for f in MOCK_INDEX if query.lower() in f["name"].lower()]
        if not matches:
            raise FileNotFoundError(f"no file matching {query!r}")
        if len(matches) == 1:
            f = matches[0]
            return f"Found: {f['name']} — modified {f['modified']}."
        lines = [f'{len(matches)} files matching "{query}":']
        lines += [f"  {f['name']} — modified {f['modified']}" for f in matches]
        return "\n".join(lines)

    def recent_files(self, n: int = 3) -> str:
        top = sorted(MOCK_INDEX, key=lambda f: f["modified"], reverse=True)[:n]
        lines = ["Recent files:"]
        lines += [f"  {f['name']} — modified {f['modified']}" for f in top]
        return "\n".join(lines)
