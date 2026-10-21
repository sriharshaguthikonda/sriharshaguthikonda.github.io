"""Regression check for the approved single-line homepage headline."""
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]


class HeroFieldsTests(unittest.TestCase):
    def test_headline_and_contacts(self):
        source = (ROOT / "index.html").read_text(encoding="utf-8")
        self.assertEqual(source.count('class="hero-disciplines"'), 1)
        self.assertIn(
            "<span>Medicine · Neuroscience · AI Systems · Software &amp; Hardware Engineering</span>",
            source,
        )
        self.assertNotIn("Areas of work", source)
        self.assertNotIn('class="hero-card"', source)
        self.assertIn('class="cv__contact-grid hero-contact-grid"', source)


if __name__ == "__main__":
    unittest.main()
