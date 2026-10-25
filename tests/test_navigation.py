"""Regression checks for public website section/navigation integrity."""
from __future__ import annotations

from pathlib import Path
import re
import unittest

from scripts.sync_navigation import (
    DEFAULT_HTML, NavigationError, actual_targets, document_entries,
    generated_html, validate,
)


class NavigationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = DEFAULT_HTML.read_text(encoding="utf-8")
        cls.clean = generated_html(cls.source)

    def test_committed_navigation_is_up_to_date(self):
        # A browser-valid HTML format change must not fail semantic CI.
        validate(self.source)
        self.assertEqual(actual_targets(self.source),
                         [entry.id for entry in document_entries(self.source)])

    def test_editor_multiline_and_reordered_attributes(self):
        edited = self.clean.replace(
            '<ul id="compass-links">',
            '<ul class="toc"\n id="compass-links">', 1
        ).replace(
            '<a href="#employment">',
            '<a class="jump"\n data-test="wrapped"\n href="#employment">', 1
        ).replace(
            '>Research Mission</a>',
            '>Research\n    Mission</a>', 1
        )
        self.assertNotEqual(edited, self.clean)
        validate(edited)
        self.assertEqual(actual_targets(edited), actual_targets(self.clean))
        self.assertEqual(generated_html(edited), self.clean)

    def test_navigation_label_drift_is_rejected(self):
        dirty = self.clean.replace('>Key Skills</a>', '>Wrong Label</a>', 1)
        with self.assertRaisesRegex(NavigationError, "label/group differs"):
            validate(dirty)

    def test_navigation_group_drift_is_rejected(self):
        dirty = self.clean.replace(
            '<span class="compass__group-label">Overview</span>',
            '<span class="compass__group-label">Wrong group</span>', 1
        )
        with self.assertRaisesRegex(NavigationError, "label/group differs"):
            validate(dirty)

    def test_multiple_navigation_lists_rejected(self):
        repeated = self.clean.replace(
            '<ul id="compass-links">',
            '<ul id="compass-links"></ul>\n<ul id="compass-links">', 1
        )
        with self.assertRaisesRegex(NavigationError, "exactly one|Duplicate HTML id"):
            validate(repeated)

    def test_generator_is_idempotent(self):
        self.assertEqual(generated_html(self.clean), self.clean)

    def test_navigation_follows_document_not_subject_groups(self):
        self.assertEqual(
            actual_targets(self.clean),
            [entry.id for entry in document_entries(self.clean)]
        )

    def test_swapped_links_fail(self):
        links = list(re.finditer(r'^[ ]*<li>.*?<a href="#[^"]+".*?</li>$',
                                 self.clean, re.MULTILINE))
        self.assertGreater(len(links), 2)
        first, second = links[0], links[1]
        swapped = (self.clean[:first.start()] +
                   second.group() + "\n" + first.group() +
                   self.clean[second.end():])
        with self.assertRaises(NavigationError):
            validate(swapped)
        self.assertEqual(generated_html(swapped), self.clean)

    def test_new_section_requires_navigation_sync(self):
        extra = '<section id="future-project"><h2>Future Project</h2></section>'
        dirty = self.clean.replace('<section id="community">', extra + '\n<section id="community">', 1)
        self.assertNotEqual(dirty, self.clean)
        with self.assertRaises(NavigationError):
            validate(dirty)
        fixed = generated_html(dirty)
        validate(fixed)
        order = actual_targets(fixed)
        self.assertEqual(order.index("future-project") + 1, order.index("community"))

    def test_missing_navigation_target_fails(self):
        dirty = self.clean.replace('href="#languages"', 'href="#does-not-exist"', 1)
        with self.assertRaises(NavigationError):
            validate(dirty)

    def test_duplicate_ids_fail_even_outside_navigation(self):
        dirty = self.clean.replace('id="community"', 'id="languages"', 1)
        with self.assertRaisesRegex(NavigationError, "Duplicate HTML id"):
            generated_html(dirty)

    def test_moving_sections_requires_new_navigation_order(self):
        a = re.search(r'<section id="achievements"[^>]*>.*?</section>', self.clean, re.S)
        b = re.search(r'<section id="presentations"[^>]*>.*?</section>', self.clean, re.S)
        self.assertIsNotNone(a)
        self.assertIsNotNone(b)
        moved = (self.clean[:a.start()] + b.group() +
                 self.clean[a.end():b.start()] + a.group() +
                 self.clean[b.end():])
        with self.assertRaises(NavigationError):
            validate(moved)
        fixed = generated_html(moved)
        validate(fixed)
        order = actual_targets(fixed)
        self.assertLess(order.index("presentations"), order.index("achievements"))

    def test_nested_whisper_stays_after_ai_section(self):
        order = actual_targets(self.clean)
        self.assertEqual(order.index("whisper-training-work"),
                         order.index("ai-skills") + 1)

    def test_group_labels_must_not_reorder_links(self):
        changed = self.clean.replace(
            'data-nav-group="Overview"', 'data-nav-group="Updated overview"', 1
        )
        self.assertNotEqual(changed, self.clean)
        fixed = generated_html(changed)
        self.assertEqual(actual_targets(fixed), actual_targets(self.clean))
        validate(fixed)

    def test_explicit_nested_item_missing_label_rejected(self):
        dirty = self.clean.replace(
            'data-nav-label="↳ Whisper model training"',
            '', 1
        )
        self.assertNotEqual(dirty, self.clean)
        with self.assertRaisesRegex(NavigationError, "needs id and data-nav-label"):
            generated_html(dirty)


if __name__ == "__main__":
    unittest.main()
