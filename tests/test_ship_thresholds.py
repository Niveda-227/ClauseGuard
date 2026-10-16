import json
import tempfile
import unittest
from pathlib import Path

from clauses import model
from clauses.evaluate import evaluate
from clauses.schema import LABELS
from scripts.ship_thresholds import ShipError, build, compare_thresholds, max_score_difference, sha256

WORDS = ['liability damages', 'terminate account', 'change terms', 'remove content',
         'using service agree', 'governed laws', 'courts jurisdiction', 'binding arbitration']


def rows(split, n):
    out = []
    for i in range(n):
        k = i % 9
        text = f'sentence {i} plain words' if k == 8 else f'we may {WORDS[k]} number {i}'
        out.append({'id': f'{split}:{i:05d}', 'text': text, 'labels': [] if k == 8 else [LABELS[k]],
                    'document_id': f'C{i % 3}', 'split': split})
    return out


def make_repo():
    root = Path(tempfile.mkdtemp())
    (root / 'artifacts').mkdir()
    base = model.train(rows('train', 90), 'baseline')
    model.save(base, root / 'artifacts/hybrid.joblib')
    val = rows('validation', 45)
    evaluate(model.load(root / 'artifacts/hybrid.joblib'), val, root / 'experiments/session04/hybrid')
    copy = model.load(root / 'artifacts/hybrid.joblib')
    expected = dict(zip(LABELS, model.tune(copy, val)['manifest']['thresholds']))
    return root, val, expected


class ShipThresholdTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.root, cls.val, cls.expected = make_repo()

    def test_builds_evaluates_and_promotes(self):
        r = build(self.root, self.val, do_promote=True, expected=self.expected)
        self.assertTrue(r['promoted_to_product'])
        self.assertEqual(sha256(self.root / 'artifacts/selected.joblib'), r['tuned_model_sha256'])
        self.assertNotEqual(r['tuned_model_sha256'], r['base_model_sha256'])
        metrics = json.loads((self.root / 'experiments/session07/tuned/metrics.json').read_text())
        self.assertEqual(metrics['model_id'], r['tuned_model_sha256'])
        self.assertEqual(metrics['threshold_source'], 'validation_per_label_F1_tuned')
        self.assertLessEqual(r['max_score_difference_vs_session04'], 1e-6)
        self.assertFalse(r['test_split_evaluated'])

    def test_thresholds_that_disagree_with_the_experiment_stop_the_build(self):
        wrong = {**self.expected, LABELS[0]: 0.15}
        with self.assertRaises(ShipError):
            build(self.root, self.val, expected=wrong)

    def test_refuses_to_tune_on_training_rows(self):
        with self.assertRaises(ShipError):
            build(self.root, rows('train', 10), expected=self.expected)

    def test_refuses_a_base_model_that_is_not_the_reported_one(self):
        root, val, expected = make_repo()
        m = root / 'experiments/session04/hybrid/metrics.json'
        data = json.loads(m.read_text())
        data['model_id'] = '0' * 64
        m.write_text(json.dumps(data))
        with self.assertRaises(ShipError):
            build(root, val, expected=expected)

    def test_compare_thresholds_lists_each_difference(self):
        self.assertEqual(compare_thresholds([0.5] * 8, {l: 0.5 for l in LABELS}, LABELS), [])
        self.assertEqual(len(compare_thresholds([0.5] * 8, {l: 0.7 for l in LABELS}, LABELS)), 8)

    def test_test_split_predictions_are_refused(self):
        p = Path(tempfile.mkdtemp()) / 'p.jsonl'
        p.write_text(json.dumps({'id': 'test:00001', 'scores': [0.1] * 8}) + '\n')
        with self.assertRaises(ShipError):
            max_score_difference(p, p)


if __name__ == '__main__':
    unittest.main()
