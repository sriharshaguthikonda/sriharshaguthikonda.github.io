"""Regression check for the approved single-line homepage headline."""
from html.parser import HTMLParser
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]


class _HeroText(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.in_hero = False
        self.text = []

    def handle_starttag(self, tag, attrs):
        if tag == "p" and "hero-disciplines" in dict(attrs).get("class", "").split():
            self.in_hero = True

    def handle_endtag(self, tag):
        if tag == "p":
            self.in_hero = False

    def handle_data(self, data):
        if self.in_hero:
            self.text.append(data)


class HeroFieldsTests(unittest.TestCase):
    def test_headline_and_contacts(self):
        source = (ROOT / "index.html").read_text(encoding="utf-8")
        self.assertEqual(source.count('class="hero-disciplines"'), 1)
        parser = _HeroText()
        parser.feed(source)
        self.assertEqual(
            " ".join("".join(parser.text).split()),
            "Medicine · Neuroscience · AI Systems · Software & Hardware Engineering",
        )
        self.assertNotIn("Areas of work", source)
        self.assertNotIn('class="hero-card"', source)
        self.assertIn('class="cv__contact-grid hero-contact-grid"', source)


if __name__ == "__main__":
    unittest.main()
