"""Load the story bible (characters, settings) from canon/."""
from __future__ import annotations
import yaml
from . import ROOT


def load_characters(root=ROOT) -> dict[str, dict]:
    out = {}
    for p in sorted((root / "canon" / "characters").glob("*/profile.yaml")):
        data = yaml.safe_load(p.read_text())
        backstory = p.with_name("backstory.md")
        data["backstory"] = backstory.read_text() if backstory.exists() else ""
        out[data["id"]] = data
    return out
