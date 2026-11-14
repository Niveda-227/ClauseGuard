"""Session 11: the domain-shift reminder in the web app (docs/decisions/2026-11-11_final_model_rule.md)."""
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STATIC = ROOT / 'webapp/static'


class ShiftNoteTests(unittest.TestCase):
    def test_the_note_is_under_the_findings_heading_and_hidden_until_a_result(self):
        html = (STATIC / 'index.html').read_text(encoding='utf-8')
        note = re.search(r'<p class="shift-note" id="shift-note" hidden>([^<]+)</p>', html)
        self.assertIsNotNone(note)
        self.assertIn('no flag does not mean the clause is not there', note.group(1))
        self.assertLess(html.index('id="summary"'), html.index('id="shift-note"'))
        self.assertLess(html.index('id="shift-note"'), html.index('id="results"'))
        self.assertIsNone(re.search(r'\d', note.group(1)), 'the note must not quote a number')

    def test_the_script_shows_it_exactly_when_there_is_a_result(self):
        js = (STATIC / 'app.js').read_text(encoding='utf-8')
        self.assertIn("shiftNote: $('shift-note')", js)
        self.assertIn('if (els.shiftNote) els.shiftNote.hidden = !has;', js)
        css = (STATIC / 'app.css').read_text(encoding='utf-8')
        self.assertIn('.shift-note {', css)
        self.assertIn('[hidden] { display: none !important; }', css)


if __name__ == '__main__':
    unittest.main()
