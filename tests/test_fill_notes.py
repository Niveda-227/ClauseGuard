"""Session 10: filling and checking a teammate's notes (scripts/fill_notes.py)."""
import json
import tempfile
import unittest
from pathlib import Path

from scripts.fill_notes import MARK, fill


class FillNotesTests(unittest.TestCase):
    def setUp(self):
        self.root = Path(tempfile.mkdtemp())
        (self.root / 'experiments/session10').mkdir(parents=True)
        (self.root / 'experiments/session10/r.json').write_text(json.dumps({'k': 0.61234, 'n': 17}))
        (self.root / 'experiments/session09').mkdir(parents=True)
        (self.root / 'experiments/session09/old.json').write_text(json.dumps({'k': 1}))
        self.notes = self.root / 'notes.md'

    def write(self, text):
        self.notes.write_text(text)
        return self.notes

    def test_tokens_are_filled_and_words_kept(self):
        out = fill(self.write('Kappa {{FROM:experiments/session10/r.json#k|2}} over {{FROM:experiments/session10/r.json#n}}.'
                              ' Hard ones: the `python3.12` line was fine.'), self.root)
        self.assertEqual(out.splitlines()[0], 'Kappa 0.61 over 17. Hard ones: the `python3.12` line was fine.')
        self.assertTrue(out.endswith(MARK + '\n'))
        self.write(out)
        self.assertEqual(fill(self.notes, self.root), out)  # a second run changes nothing
        self.write(out + '<<WORDS>>\n')
        with self.assertRaisesRegex(ValueError, 'filled before'):
            fill(self.notes, self.root)

    def test_hand_places_left_are_refused(self):
        with self.assertRaisesRegex(ValueError, 'by hand'):
            fill(self.write('Seen: <<WORDS: what you saw>>'), self.root)

    def test_typed_decimal_numbers_are_refused(self):
        with self.assertRaisesRegex(ValueError, '0.61'):
            fill(self.write('Kappa was 0.61 by my count.'), self.root)

    def test_tokens_outside_session10_results_are_refused(self):
        with self.assertRaisesRegex(ValueError, 'experiments/session10/'):
            fill(self.write('{{FROM:experiments/session09/old.json#k}}'), self.root)


if __name__ == '__main__':
    unittest.main()
