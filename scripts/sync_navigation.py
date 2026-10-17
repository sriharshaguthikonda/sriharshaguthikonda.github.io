#!/usr/bin/env python3
"""Keep #compass-links in the exact order of navigable items in index.html.

The document, not the desktop/mobile TOC or category labels, owns the order.
Pure Python standard library; safe for --check in CI.
"""
from __future__ import annotations

import argparse
import difflib
import html as html_entities
from html.parser import HTMLParser
from pathlib import Path
import re
import sys
from collections import Counter
from dataclasses import dataclass


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_HTML = ROOT / "index.html"
TOC_RE = re.compile(
    r'(?P<indent>^[ \t]*)<ul[ \t]+id=["\x27]compass-links["\x27][^>]*>'
    r'[\s\S]*?^[ \t]*</ul>',
    re.MULTILINE,
)
NAV_HREF_RE = re.compile(r'<a[ \t]+href=["\x27]#([^"\x27]+)["\x27]')
VALID_ID_RE = re.compile(r"^[A-Za-z][A-Za-z0-9_:.\\-]*$")


class NavigationError(ValueError):
    """Navigation cannot be safely generated or verified."""


@dataclass(frozen=True)
class NavEntry:
    id: str
    label: str
    group: str = ""


class DocumentIndex(HTMLParser):
    """Record sections in HTML opening-tag order, including explicit sublinks."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.ids: list[str] = []
        self.sections: list[dict] = []
        self.entries: list[tuple[str, dict]] = []
        self.section_stack: list[dict] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        a = dict(attrs)
        ident = a.get("id")
        if ident is not None:
            self.ids.append(ident)
        if tag == "section":
            record = {
                "id": ident,
                "label": a.get("data-nav-label", ""),
                "group": a.get("data-nav-group", ""),
                "exclude": a.get("data-nav-exclude") == "true",
                "heading": [],
                "heading_seen": False,
                "collecting": False,
            }
            self.section_stack.append(record)
            self.sections.append(record)
            if ident:
                self.entries.append(("section", record))
        elif tag == "h2" and self.section_stack:
            record = self.section_stack[-1]
            if not record["heading_seen"]:
                record["heading_seen"] = True
                record["collecting"] = True
        elif tag == "details" and "data-nav-item" in a:
            if not ident or not a.get("data-nav-label"):
                raise NavigationError("An indexed <details> needs id and data-nav-label")
            if not self.section_stack:
                raise NavigationError("Indexed <details> must belong to a section")
            if self.section_stack[-1]["exclude"]:
                raise NavigationError("Indexed <details> belongs to an excluded section")
            self.entries.append(("details", {
                "id": ident,
                "label": a["data-nav-label"],
                "group": "",
            }))

    def handle_data(self, data: str) -> None:
        if self.section_stack and self.section_stack[-1]["collecting"]:
            self.section_stack[-1]["heading"].append(data)

    def handle_endtag(self, tag: str) -> None:
        if tag == "h2" and self.section_stack:
            self.section_stack[-1]["collecting"] = False
        elif tag == "section":
            if not self.section_stack:
                raise NavigationError("Unexpected </section>")
            self.section_stack.pop()


def document_entries(source: str) -> list[NavEntry]:
    parser = DocumentIndex()
    parser.feed(source)
    parser.close()
    if parser.section_stack:
        raise NavigationError("Unclosed <section> found in index.html")
    duplicates = [ident for ident, count in Counter(parser.ids).items() if count > 1]
    if duplicates:
        raise NavigationError("Duplicate HTML id(s): " + ", ".join(duplicates))
    result = []
    for kind, record in parser.entries:
        if kind == "section":
            if record["exclude"] or not record["id"]:
                continue
            if not record["heading_seen"]:
                if record["label"] or record["group"]:
                    raise NavigationError(
                        "Section " + record["id"] + " has navigation metadata but no h2"
                    )
                continue  # E.g. hidden references placeholder; no public heading.
            label = record["label"] or " ".join("".join(record["heading"]).split())
        else:
            label = record["label"]
        if not label or not VALID_ID_RE.fullmatch(record["id"]):
            raise NavigationError("Missing label or invalid id: " + str(record["id"]))
        result.append(NavEntry(record["id"], label, record["group"] or ""))
    if not result:
        raise NavigationError("No navigable page sections")
    return result


def toc_match(source: str) -> re.Match[str]:
    matches = list(TOC_RE.finditer(source))
    if len(matches) != 1:
        raise NavigationError("Expected exactly one <ul id=\"compass-links\">")
    return matches[0]


def actual_targets(source: str) -> list[str]:
    block = toc_match(source).group(0)
    return NAV_HREF_RE.findall(block)


def generated_html(source: str) -> str:
    match = toc_match(source)
    newline = "\r\n" if "\r\n" in source else "\n"
    indent = match.group("indent")
    lines = [indent + '<ul id="compass-links">']
    for item in document_entries(source):
        group = (
            '<span class="compass__group-label">'
            + html_entities.escape(item.group)
            + "</span>"
        ) if item.group else ""
        lines.append(
            indent + "  <li>" + group
            + '<a href="#' + item.id + '">'
            + html_entities.escape(item.label)
            + "</a></li>"
        )
    lines.append(indent + "</ul>")
    new_block = newline.join(lines)
    return source[:match.start()] + new_block + source[match.end():]


def validate(source: str) -> None:
    entries = document_entries(source)
    target_order = [item.id for item in entries]
    actual_order = actual_targets(source)
    if actual_order != target_order:
        raise NavigationError(
            "Jump to order, coverage or nesting differs from the page.\n"
            "  Expected: " + ", ".join(target_order) + "\n"
            "  Actual:   " + ", ".join(actual_order)
        )
    expected = generated_html(source)
    if source != expected:
        raise NavigationError(
            "Navigation link labels or visual groups are stale. "
            "Run: python scripts/sync_navigation.py --fix"
        )


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    mode = p.add_mutually_exclusive_group(required=True)
    mode.add_argument("--fix", action="store_true", help="regenerate TOC from page")
    mode.add_argument("--check", action="store_true", help="check without changes")
    p.add_argument("--file", type=Path, default=DEFAULT_HTML, help="HTML page to validate")
    args = p.parse_args(argv)
    path: Path = args.file
    try:
        with path.open("r", encoding="utf-8", newline="") as handle:
            source = handle.read()
        expected = generated_html(source)
        if args.check:
            validate(source)
            print("Navigation OK: " + str(len(document_entries(source))) + " links in page order.")
            return 0
        if expected != source:
            with path.open("w", encoding="utf-8", newline="") as handle:
                handle.write(expected)
            print("Navigation updated: " + str(len(document_entries(source))) + " links.")
        else:
            print("Navigation already in sync.")
        validate(expected)
        return 0
    except (OSError, NavigationError) as error:
        print("Navigation ERROR: " + str(error), file=sys.stderr)
        if args.check and "source" in locals():
            try:
                expected = generated_html(source)
                print("".join(difflib.unified_diff(
                    source.splitlines(keepends=True),
                    expected.splitlines(keepends=True),
                    fromfile="committed/index.html",
                    tofile="expected/index.html"
                ))[:9000], file=sys.stderr)
            except NavigationError:
                pass
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
