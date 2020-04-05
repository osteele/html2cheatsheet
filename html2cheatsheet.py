import requests
from bs4 import BeautifulSoup
from jinja2 import Template
from pathlib import Path
from dataclasses import dataclass
from typing import List
import re

# {Apple name: Dash name} in required output order
MODIFIERS = {"Command": "CMD", "Control": "CTRL", "Option": "ALT", "Shift": "SHIFT"}

# e.g. {"Command-": "CMD+"}, for easier substitution, below
MODIFIER_PREFIXES = {k + "-": v + "+" for k, v in MODIFIERS.items()}

# Names to remvoe from "Backslash (/)" -> "/"
PUNCTUATION_NAMES = [
    "Apostrophe",
    "Backslash",
    "Comma",
    "Equal Sign",
    "Grave Accent",
    "Hyphen",
    "Left Bracket",
    "Period",
    "Right Bracket",
    "Semicolon",
    "Slash",
]

PUNCTUATION_RE = re.compile(r"(?:" + "|".join(PUNCTUATION_NAMES) + ") \((.+?)\)")

# Exclude these
COMMON_SHORTCUTS = {
    "CTRL+Z": re.compile("Undo( the last change)?"),
    "SHIFT+CMD+Z": re.compile("Redo( the last change)?"),
    "CMD+X": "Cut",
    "CMD+C": "Copy",
    "CMD+V": "Paste",
}

REPLACEMENTS = {" (or Control-Option-C if the caption editor is open)": ""}

template = Template(Path("cheatsheet.rb.j2").read_text())


@dataclass
class Entry:
    name: str
    key: List[str]
    notes: str

    @staticmethod
    def from_row(row):
        notes, name, key = row

        for k, v in REPLACEMENTS.items():
            if k in key:
                key = key.replace(k, v)
        modifiers = []
        for k, v in MODIFIER_PREFIXES.items():
            if k in key:
                key = key.replace(k, "")
                modifiers.append(v)
        key = "".join(modifiers) + PUNCTUATION_RE.sub(r"\1", key)

        notes = notes.replace("\xa0", " ")

        return Entry(repr(name), repr(key), repr(notes))

    def is_trivial(self):
        name_pattern = COMMON_SHORTCUTS.get(self.key.strip("'"))
        name = self.name.strip("'")
        return name_pattern and (
            name == name_pattern
            if isinstance(name_pattern, str)
            else name_pattern.fullmatch(name)
        )


def gen_categories(soup):
    for section in soup.select(".Subhead"):
        title = section.select("h2.Name")[0].get_text()
        entries = [
            Entry.from_row(td.get_text().strip() for td in row.select("td"))
            for row in section.select("tr")
            if row.select("td")
        ]
        entries = [entry for entry in entries if not entry.is_trivial()]
        yield repr(title), entries


def html2cheatsheet(name, source_url):
    response = requests.get(source_url)
    assert response.status_code
    soup = BeautifulSoup(response.content, "html.parser")

    out = template.render(
        source_url=source_url,
        title=repr(name),
        filename=repr(name.replace(" ", "_")),
        keyword=repr("fcp"),
        categories=list(gen_categories(soup)),
    )

    Path("Final_Cut_Pro.rb").write_text(out + "\n")


html2cheatsheet(
    "Final Cut Pro",
    "https://support.apple.com/guide/final-cut-pro/keyboard-shortcuts-ver90ba5929/mac",
)
