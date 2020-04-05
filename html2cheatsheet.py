import requests
from bs4 import BeautifulSoup
from jinja2 import Template
from pathlib import Path
from dataclasses import dataclass
from typing import List
import re

MODIFIERS = {"Command": "CMD", "Control": "CTRL", "Option": "ALT", "Shift": "SHIFT"}

MODIFIER_PREFIXES = {k + "-": v + "+" for k, v in MODIFIERS.items()}

PUNCTUATION_NAMES = [
    "Apostrophe",
    "Backslash",
    "Comma",
    "Equal Sign",
    "Grave Accent",
    "Hyphen",
    "Left Bracket",
    "Period",
    "Semicolon",
    "SlashRight Bracket",
]

PUNCTUATION_RE = re.compile(r"(?:" + "|".join(PUNCTUATION_NAMES) + ") \((.+?)\)")

CUT_COPY_PASTE = {("Cut", "CMD+X"), ("Copy", "CMD+C"), ("Paste", "CMD+V")}


@dataclass
class Entry:
    name: str
    key: List[str]
    notes: str

    @staticmethod
    def from_row(row):
        notes, name, key = row
        notes = notes.replace("\xa0", " ")

        modifiers = []
        for k, v in MODIFIER_PREFIXES.items():
            if k in key:
                key = key.replace(k, "")
                modifiers.append(v)
        key = "".join(modifiers) + PUNCTUATION_RE.sub(r"\1", key)

        return Entry(repr(name), repr(key), repr(notes))


template = Template(Path("cheatsheet.jinja").read_text())


def gen_categories(soup):
    for section in soup.select(".Subhead"):
        title = section.select("h2.Name")[0].get_text()
        entries = [
            Entry.from_row(td.get_text().strip() for td in row.select("td"))
            for row in section.select("tr")
            if row.select("td")
        ]
        entries = [
            entry
            for entry in entries
            if (entry.name.strip("'"), entry.key.strip("'")) not in CUT_COPY_PASTE
        ]
        yield repr(title), entries


response = requests.get(
    "https://support.apple.com/guide/final-cut-pro/keyboard-shortcuts-ver90ba5929/mac"
)
assert response.status_code
soup = BeautifulSoup(response.content, "html.parser")

out = template.render(
    title=repr("Final Cut Pro"),
    filename=repr("Final_Cut_Pro"),
    keyword=repr("fcp"),
    categories=list(gen_categories(soup)),
)

Path("Final_Cut_Pro.rb").write_text(out)
