"""Session 11: every number in docs/MODEL_CARD.md matches its source file."""
import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CARD = ROOT / 'docs/MODEL_CARD.md'
ROW = re.compile(r'^\| ([^|]+) \| ([0-9.]+) \| ([^|]+\.json) \| ([^|]+) \|$')


def value(data, key):
    for part in key.split('.'):
        data = data[part]
    return data


class ModelCardTests(unittest.TestCase):
    def rows(self):
        return [ROW.match(l).groups() for l in CARD.read_text(encoding='utf-8').splitlines() if ROW.match(l)]

    def test_every_number_matches_its_source(self):
        rows = self.rows()
        self.assertEqual(len(rows), 8)
        for name, number, source, key in rows:
            v = value(json.loads((ROOT / source.strip()).read_text(encoding='utf-8')), key.strip())
            self.assertAlmostEqual(float(number), float(v), places=6, msg=name)
            self.assertEqual(len(number.split('.')[1]) if '.' in number else 0,
                             len(str(v).split('.')[1]) if '.' in str(v) else 0, msg=f'{name}: same precision as the source')

    def test_the_card_names_the_shipped_file_and_no_test_result(self):
        text = CARD.read_text(encoding='utf-8')
        self.assertIn('artifacts/selected.joblib', text)
        self.assertIn('dafbb5470f2fb2678cae273eac7c23046bbad0487c7be247174a99a08ad493bd', text)
        self.assertIn('Final test not evaluated', text)
        self.assertIn('scripts/reproduce_model.py', text)
        self.assertNotIn('experiments/session12', text)


if __name__ == '__main__':
    unittest.main()
