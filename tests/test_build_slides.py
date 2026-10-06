import tempfile
import unittest
from pathlib import Path

from scripts import build_slides as b
from scripts.midpoint_facts import build as build_facts

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / 'reports/midpoint/src'

GOOD = ['<!-- time: 60 -->\n## Live demo: running\n1. click',
        '<!-- time: 60 -->\n## Users\n[notes](../../evidence/session06/session_notes.md)',
        '<!-- time: 60 -->\n## Decision: Persevere\n- why']


class BuildSlidesTests(unittest.TestCase):
    def test_placeholders_are_reported_with_line_numbers(self):
        problems = b.check_placeholders('x.md', 'fine\n- <<FILL THIS>> here')
        self.assertEqual(len(problems), 1)
        self.assertIn('line 2', problems[0])

    def test_unknown_tokens_are_refused_and_known_ones_filled(self):
        text, problems = b.fill('x.md', '{{AUTO_A}} and {{AUTO_B}}', {'A': '0.63'})
        self.assertIn('0.63', text)
        self.assertEqual(len(problems), 1)

    def test_a_good_deck_passes(self):
        problems, timing, total = b.check_deck(GOOD)
        self.assertEqual(problems, [])
        self.assertEqual(total, 180)

    def test_over_five_minutes_is_refused(self):
        deck = GOOD + ['<!-- time: 200 -->\n## Extra']
        problems, _, total = b.check_deck(deck)
        self.assertEqual(total, 380)
        self.assertTrue(any('over' in p for p in problems))

    def test_decision_title_must_say_pivot_or_persevere(self):
        deck = GOOD[:2] + ['<!-- time: 60 -->\n## Decision: TBD\n- The rule says Persevere']
        problems, _, _ = b.check_deck(deck)
        self.assertTrue(any('Pivot or Persevere' in p for p in problems))

    def test_deck_without_live_demo_is_refused(self):
        problems, _, _ = b.check_deck(GOOD[1:])
        self.assertTrue(any('Live demo' in p for p in problems))

    def test_missing_link_target_is_reported(self):
        problems = b.check_links('x.md', '[gone](../../evidence/session99/nothing.md)')
        self.assertEqual(len(problems), 1)

    def test_html_embeds_images_and_renders_tables(self):
        base = Path(tempfile.mkdtemp())
        (base / 'f.svg').write_text('<svg xmlns="http://www.w3.org/2000/svg"></svg>')
        out = b.slide_html('## T\n\n| a | b |\n|---|---|\n| 1 | 2 |\n\n![chart](f.svg)\n\n- **bold** point', base)
        self.assertIn('<table>', out)
        self.assertIn('data:image/svg+xml;base64,', out)
        self.assertIn('<strong>bold</strong>', out)

    def test_every_token_in_the_sources_exists(self):
        tokens = build_facts(ROOT)['tokens']
        for name in b.SOURCES:
            _, problems = b.fill(name, (SRC / name).read_text(encoding='utf-8'), tokens)
            self.assertEqual(problems, [], name)


if __name__ == '__main__':
    unittest.main()
