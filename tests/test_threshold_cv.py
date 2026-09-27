import json
import tempfile
import unittest
from pathlib import Path

import numpy as np

from clauses.schema import LABELS
from scripts.threshold_cv import best_threshold, decide, load_predictions, run

ROOT = Path(__file__).resolve().parents[1]


def write(rows):
    path = Path(tempfile.mkdtemp()) / 'p.jsonl'
    path.write_text('\n'.join(json.dumps(r) for r in rows))
    return path


def row(i, company, gold, scores):
    return {'id': f'validation:{i:05d}', 'document_id': company, 'gold': gold, 'predicted': [], 'scores': scores}


class ThresholdCVTests(unittest.TestCase):
    def test_refuses_test_split(self):
        path = write([{'id': 'test:00001', 'document_id': 'A', 'gold': [], 'scores': [0.1] * 8}])
        with self.assertRaises(ValueError):
            load_predictions(path)

    def test_decision_is_strict_like_the_product(self):
        self.assertEqual(decide(np.array([[0.5] * 8]), [0.5] * 8).sum(), 0)

    def test_tie_prefers_higher_threshold(self):
        y = np.array([1, 0]); s = np.array([0.95, 0.05])
        self.assertEqual(best_threshold(y, s), 0.9)

    def test_loco_never_better_than_in_sample_on_average(self):
        rng = np.random.default_rng(0)
        rows = []
        for i in range(400):
            company = f'C{i % 5}'
            gold = [LABELS[0]] if rng.random() < 0.2 else []
            base = 0.35 if gold else 0.15
            rows.append(row(i, company, gold, [float(np.clip(base + rng.normal(0, 0.15), 0, 1))] + [0.01] * 7))
        r = run(write(rows))
        self.assertLessEqual(r['leave_one_company_out_HONEST']['macro_f1'],
                             r['tuned_in_sample_OPTIMISTIC']['macro_f1'] + 1e-9)

    def test_real_predictions_run_and_match_reported_baseline(self):
        r = run(ROOT / 'experiments/session04/hybrid/predictions.jsonl')
        self.assertEqual(r['sentences'], 2275)
        self.assertAlmostEqual(r['fixed_0_5']['macro_f1'], 0.6333, places=4)


if __name__ == '__main__':
    unittest.main()
