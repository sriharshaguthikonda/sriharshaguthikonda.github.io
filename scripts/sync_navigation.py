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


class NavigationMarkup(HTMLParser):
    """Parse navigation as HTML, including multiline and reordered attributes.

    Record the exact <ul> span only for explicit regeneration. Validation
    compares the rendered link structure rather than source formatting.
    """

    def __init__(self, source: str) -> None:
        super().__init__(convert_charrefs=True)
        self.source = source
        self.line_offsets = [0]
        for line in source.splitlines(keepends=True):
            self.line_offsets.append(self.line_offsets[-1] + len(line))
        self.matches = 0
        self.depth = 0
        self.start = -1
        self.end = -1
        self.entries: list[NavEntry] = []
        self.item: dict | None = None
        self.collect: str | None = None

    def offset(self) -> int:
        line, column = self.getpos()
        return self.line_offsets[line - 1] + column

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attributes = dict(attrs)
        if tag == "ul":
            if attributes.get("id") == "compass-links":
                self.matches += 1
                if self.matches != 1 or self.depth:
                    raise NavigationError('Expected exactly one <ul id="compass-links">')
                self.depth = 1
                self.start = self.offset()
            elif self.depth:
                raise NavigationError("Nested lists are not valid navigation items")
            return
        if not self.depth:
            return
        if tag == "li":
            if self.item is not None:
                raise NavigationError("Nested navigation items are not supported")
            self.item = {"href": None, "label": [], "group": []}
        elif tag == "span" and self.item is not None and self.collect != "label":
            classes = (attributes.get("class") or "").split()
            if "compass__group-label" in classes:
                self.collect = "group"
        elif tag == "a":
            if self.item is None or self.item["href"] is not None:
                raise NavigationError("Each navigation item needs exactly one link")
            self.item["href"] = attributes.get("href") or ""
            self.collect = "label"

    def handle_data(self, data: str) -> None:
        if self.item is not None and self.collect:
            self.item[self.collect].append(data)

    def handle_endtag(self, tag: str) -> None:
        if tag == "ul":
            if self.depth:
                if self.item is not None:
                    raise NavigationError("Navigation item is not closed")
                self.depth = 0
                closing_gt = self.source.find(">", self.offset())
                if closing_gt == -1:
                    raise NavigationError("Navigation list has no closing tag")
                self.end = closing_gt + 1
            return
        if not self.depth:
            return
        if tag == "a" and self.collect == "label":
            self.collect = None
        elif tag == "span" and self.collect == "group":
            self.collect = None
        elif tag == "li":
            if self.item is None or self.item["href"] is None:
                raise NavigationError("Navigation item has no link")
            href = self.item["href"]
            if not href.startswith("#"):
                raise NavigationError("Navigation links must point to page anchors")
            label = " ".join("".join(self.item["label"]).split())
            group = " ".join("".join(self.item["group"]).split())
            self.entries.append(NavEntry(href[1:], label, group))
            self.item = None
            self.collect = None


def navigation_markup(source: str) -> NavigationMarkup:
    parser = NavigationMarkup(source)
    parser.feed(source)
    parser.close()
    if parser.matches != 1 or parser.depth or parser.end < 0:
        raise NavigationError('Expected exactly one closed <ul id="compass-links">')
    return parser


def actual_targets(source: str) -> list[str]:
    return [item.id for item in navigation_markup(source).entries]


def generated_html(source: str) -> str:
    markup = navigation_markup(source)
    newline = "\r\n" if "\r\n" in source else "\n"
    start_line = source.rfind("\n", 0, markup.start) + 1
    indent = source[start_line:markup.start]
    if indent.strip():
        raise NavigationError("Navigation list must begin on its own line")
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
    return source[:markup.start] + newline.join(lines) + source[markup.end:]


def validate(source: str) -> None:
    expected = document_entries(source)
    actual = navigation_markup(source).entries
    expected_order = [item.id for item in expected]
    actual_order = [item.id for item in actual]
    if actual_order != expected_order:
        raise NavigationError(
            "Jump to order, coverage or nesting differs from the page.\n"
            "  Expected: " + ", ".join(expected_order) + "\n"
            "  Actual:   " + ", ".join(actual_order)
        )
    for item, wanted in zip(actual, expected):
        if (item.label, item.group) != (wanted.label, wanted.group):
            raise NavigationError(
                "Navigation label/group differs for #" + item.id
                + ": expected " + repr((wanted.label, wanted.group))
                + ", actual " + repr((item.label, item.group))
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
