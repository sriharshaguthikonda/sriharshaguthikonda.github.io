"""Regression tests for the 2026-10-21 layout and structure repair campaign.

Each test pins one defect fixed in that campaign so it cannot silently
return: invalid list nesting, section-level card chrome, geometry-changing
active-section highlight, <br> spacing hacks, duplicate CSS, inline poster
styling, empty showcase labels and lightbox focus management.
"""
from html.parser import HTMLParser
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[1]
HTML = (ROOT / "index.html").read_text(encoding="utf-8")
CSS = (ROOT / "styles.css").read_text(encoding="utf-8")


class _ListStructureParser(HTMLParser):
    """Flags content elements placed as direct children of <ul>."""

    TRACKED = {"ul", "li", "figure", "div", "p", "article", "details", "summary", "section"}

    def __init__(self):
        super().__init__()
        self.stack = []
        self.violations = []

    def handle_starttag(self, tag, attrs):
        if tag in self.TRACKED:
            parent = self.stack[-1] if self.stack else None
            if tag == "ul" and parent == "ul":
                self.violations.append(("ul-directly-in-ul", self.getpos()))
            if tag in ("figure", "div", "p", "article") and parent == "ul":
                self.violations.append((tag + "-directly-in-ul", self.getpos()))
            self.stack.append(tag)

    def handle_endtag(self, tag):
        if self.stack and self.stack[-1] == tag:
            self.stack.pop()


class _InteractiveMarkup(HTMLParser):
    """Inspect attributes and section nesting independently of formatting."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.in_key_skills = False
        self.key_skills_article = False
        self.accessible_poster = False

    def handle_starttag(self, tag, attrs):
        attributes = dict(attrs)
        if tag == "section" and attributes.get("id") == "key-skills":
            self.in_key_skills = True
        elif tag == "article" and self.in_key_skills:
            self.key_skills_article = True
        if "data-open-full" in attributes:
            self.accessible_poster = (
                self.accessible_poster
                or (attributes.get("tabindex") == "0"
                    and attributes.get("role") == "button")
            )

    def handle_endtag(self, tag):
        if tag == "section" and self.in_key_skills:
            self.in_key_skills = False


class ListStructureTests(unittest.TestCase):
    def test_no_content_elements_directly_inside_ul(self):
        parser = _ListStructureParser()
        parser.feed(HTML)
        self.assertEqual(parser.violations, [])


class CardArchitectureTests(unittest.TestCase):
    def test_key_skills_is_an_article_card(self):
        parser = _InteractiveMarkup()
        parser.feed(HTML)
        self.assertTrue(parser.key_skills_article, "Key Skills must contain an article")
        self.assertNotIn("cv__skills", HTML)

    def test_media_card_has_no_own_rule_block(self):
        for match in re.finditer(r"([^{}]+)\{([^{}]*)\}", CSS):
            selectors = [s.strip() for s in match.group(1).split(",")]
            if ".media-card" in selectors:
                self.fail(".media-card still carries standalone card chrome")

    def test_section_active_highlight_changes_no_geometry(self):
        match = re.search(r"\.section--active\s*\{([^}]*)\}", CSS)
        self.assertTrue(match, ".section--active rule missing")
        block = match.group(1)
        self.assertNotRegex(block, r"(?m)^\s*(padding|margin|border)\s*:")
        self.assertIn("outline:", block)

    def test_no_standalone_br_spacers(self):
        self.assertIsNone(re.search(r"\n[ \t]*<br>[ \t]*\n", HTML))

    def test_layout_spacing_comes_from_css(self):
        self.assertIn("main.cv{ margin-top: 27px; }", CSS)


class CssHygieneTests(unittest.TestCase):
    def test_universal_inline_block_exists_once(self):
        self.assertEqual(CSS.count("#2100fd"), 1)

    def test_research_poster_styles_live_in_css(self):
        self.assertNotIn('style="width: 100%; margin: 0 auto;', HTML)
        self.assertRegex(CSS, r"\.inline-image-card\s*\{[^}]*border-radius: 12px")

    def test_no_empty_showcase_labels(self):
        self.assertNotIn('medical-ai-showcase__label"></p>', HTML)
        self.assertNotIn(".medical-ai-showcase__label {", CSS)


class ContentPreservationTests(unittest.TestCase):
    def test_languages_disclosure_keeps_newest_content(self):
        self.assertIn("Urdu", HTML)
        self.assertIn("TOEFL iBT", HTML)

    def test_video_allowlist_unchanged(self):
        self.assertIn("'N33zBv5VpOA', 'movqx-3nQjI', 'Kaqcmn6OtZg', '9xNq9vT0xfM'", HTML)


class InteractionTests(unittest.TestCase):
    def test_lightbox_manages_focus(self):
        self.assertIn("closeBtn.focus()", HTML)
        self.assertIn("lastOpener", HTML)

    def test_poster_opener_is_keyboard_reachable(self):
        parser = _InteractiveMarkup()
        parser.feed(HTML)
        self.assertTrue(parser.accessible_poster, "Poster must be keyboard accessible")

    def test_featured_iframe_has_descriptive_title(self):
        self.assertIn('title="Comparison of tools for CRISPR knockout screen analysis', HTML)


if __name__ == "__main__":
    unittest.main()
