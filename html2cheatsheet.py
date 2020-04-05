import requests
from bs4 import BeautifulSoup
from jinja2 import Template
from pathlib import Path
from dataclasses import dataclass
from typing import List
import re


@dataclass
class Entry:
    name: str
    key: List[str]
    notes: str

    @staticmethod
    def from_row(row):
        notes, name, key = row
        notes = notes.replace(r"\xa0", " ")
        key = key.replace("Command-", "CMD+")
        key = key.replace("Control-", "CTRL+")
        key = key.replace("Shift-", "SHIFT+")
        key = key.replace("Option-", "ALT+")
        key = re.sub(
            r"(Grave Accent|Comma|Hyphen|Period|Equal Sign|Left Bracket|Backslash|SlashRight Bracket|Semicolon|Apostrophe) \((.+?)\)",
            r"\2",
            key,
        )
        return Entry(name, key, notes)


template = Template(Path("cheatsheet.jinja").read_text())


def gen_categories(soup):
    for section in soup.select(".Subhead"):
        title = section.select("h2.Name")[0].get_text()
        # row: [descripion, name, key]
        # rows = [
        #     [repr(td.get_text()) for td in row.select("td")]
        #     for row in section.select("tr")
        # ]
        entries = [
            Entry.from_row(repr(td.get_text()) for td in row.select("td"))
            for row in section.select("tr")
            if row.select("td")
        ]
        # print(entries[0])
        # break
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
