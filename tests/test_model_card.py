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

    def test_the_card_names_the_shipped_file_and_the_one_time_test_result(self):
        text = CARD.read_text(encoding='utf-8')
        self.assertIn('artifacts/selected.joblib', text)
        self.assertIn('dafbb5470f2fb2678cae273eac7c23046bbad0487c7be247174a99a08ad493bd', text)
        self.assertIn('scripts/reproduce_model.py', text)
        self.assertIn('read once with the frozen release in Session 12', text)
        self.assertIn('experiments/session12/test_eval.md', text)
        if (ROOT / 'experiments/session12/test_eval.json').exists():
            ledger = (ROOT / 'experiments/test_exposure.jsonl').read_text(encoding='utf-8')
            self.assertEqual(len([l for l in ledger.splitlines() if l.strip()]), 1, 'the test split is read once')


if __name__ == '__main__':
    unittest.main()
