"""Tests for scripts/compare_thresholds.py on a small made-up repo (no dataset needed)."""
import json
import random
import tempfile
import unittest
from pathlib import Path

import numpy as np

from clauses.schema import LABELS
from scripts.compare_thresholds import CompareError, compare, to_markdown
from scripts.threshold_cv import decide

THRESHOLDS = [0.75, 0.70, 0.80, 0.80, 0.80, 0.65, 0.55, 0.80]
NEW_SHA = 'b' * 64


def write_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data), encoding='utf-8')


def write_rows(path, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(''.join(json.dumps(r) + '\n' for r in rows), encoding='utf-8')


def make_repo(n=300, seed=7):
    rng = random.Random(seed)
    root = Path(tempfile.mkdtemp())
    old, new = [], []
    for i in range(n):
        gold = [l for l in LABELS if rng.random() < 0.08]
        scores = [round(min(0.99, max(0.01, (0.65 if l in gold else 0.25) + rng.uniform(-0.3, 0.3))), 4) for l in LABELS]
        base = {'id': f'validation:{i:05d}', 'document_id': f'Company{i % 4}', 'gold': gold, 'scores': scores}
        old.append({**base, 'predicted': [l for l, s in zip(LABELS, scores) if s > 0.5]})
        new.append({**base, 'predicted': [l for l, s, t in zip(LABELS, scores, THRESHOLDS) if s > t]})
    write_rows(root / 'experiments/session04/hybrid/predictions.jsonl', old)
    write_rows(root / 'experiments/session07/tuned/predictions.jsonl', new)
    write_json(root / 'experiments/session04/hybrid/metrics.json', {'model_id': 'a' * 64})
    write_json(root / 'experiments/session07/tuned/metrics.json', {'model_id': NEW_SHA})
    write_json(root / 'artifacts/selected.json', {'artifact_sha256': NEW_SHA, 'thresholds': THRESHOLDS})
    write_json(root / 'artifacts/tuned.json', {'artifact_sha256': NEW_SHA, 'thresholds': THRESHOLDS})
    write_json(root / 'experiments/session05/threshold_cv.json',
               {'tuned_in_sample_OPTIMISTIC': {'thresholds': dict(zip(LABELS, THRESHOLDS))}})
    return root


class CompareThresholdTests(unittest.TestCase):
    def test_counts_add_up_and_three_columns_exist(self):
        root = make_repo()
        r = compare(root)
        for key in ('old_product_fixed_0_5', 'new_product_tuned_OPTIMISTIC', 'new_product_leave_one_company_out_HONEST'):
            block = r[key]
            # Every gold label is either a correct tag or a missed label.
            self.assertEqual(block['correct_tags'] + block['missed_labels'], r['gold_labels'])
            # Every flag is either a correct tag or a wrong tag.
            self.assertEqual(block['correct_tags'] + block['wrong_tags'], block['flags'])
        self.assertEqual(r['companies'], 4)
        self.assertFalse(r['checks']['test_split_read'])

    def test_higher_thresholds_mean_fewer_flags(self):
        r = compare(make_repo())
        self.assertLess(r['new_product_tuned_OPTIMISTIC']['flags'], r['old_product_fixed_0_5']['flags'])

    def test_stops_when_app_runs_a_different_model(self):
        root = make_repo()
        write_json(root / 'artifacts/selected.json', {'artifact_sha256': 'c' * 64})
        with self.assertRaises(CompareError):
            compare(root)

    def test_stops_when_thresholds_differ_from_experiment(self):
        root = make_repo()
        write_json(root / 'artifacts/tuned.json', {'thresholds': [0.5] * len(LABELS)})
        with self.assertRaises(CompareError):
            compare(root)

    def test_stops_when_scores_differ(self):
        root = make_repo()
        path = root / 'experiments/session07/tuned/predictions.jsonl'
        rows = [json.loads(l) for l in path.read_text().splitlines()]
        rows[0]['scores'][0] += 0.1
        write_rows(path, rows)
        with self.assertRaises(CompareError):
            compare(root)

    def test_refuses_test_split_rows(self):
        root = make_repo()
        path = root / 'experiments/session07/tuned/predictions.jsonl'
        rows = [json.loads(l) for l in path.read_text().splitlines()]
        rows[0]['id'] = 'test:00000'
        write_rows(path, rows)
        with self.assertRaises(CompareError):
            compare(root)

    def test_markdown_labels_optimistic_and_honest(self):
        text = to_markdown(compare(make_repo()))
        self.assertIn('(optimistic)', text)
        self.assertIn('(honest)', text)
        self.assertIn('"no flag" must never be read as "safe"', text)

    def test_decide_is_strict(self):
        # A score exactly at the threshold is NOT flagged, same as the app.
        self.assertEqual(decide(np.array([[0.75]]), [0.75]).tolist(), [[0]])


if __name__ == '__main__':
    unittest.main()
