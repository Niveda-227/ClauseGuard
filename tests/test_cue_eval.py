"""Tests for scripts/cue_eval.py on a small made-up repository (no dataset needed)."""
import json
import random
import tempfile
import unittest
from pathlib import Path

import numpy as np

from clauses.cues import review_cues
from clauses.schema import LABELS
from scripts.cue_eval import CueEvalError, cues, run, to_markdown

CUTS = [0.75, 0.70, 0.80, 0.80, 0.80, 0.65, 0.55, 0.80]
SHA = 'd' * 64


def make_repo(n=400, seed=3):
    rng = random.Random(seed)
    root = Path(tempfile.mkdtemp())
    rows = []
    for i in range(n):
        gold = [l for l in LABELS if rng.random() < 0.08]
        scores = [round(min(0.99, max(0.01, (0.7 if l in gold else 0.3) + rng.uniform(-0.35, 0.35))), 4) for l in LABELS]
        rows.append({'id': f'validation:{i:05d}', 'document_id': f'Company{i % 5}', 'gold': gold, 'scores': scores,
                     'predicted': [l for l, s, t in zip(LABELS, scores, CUTS) if s > t]})
    pred = root / 'experiments/session07/tuned/predictions.jsonl'
    pred.parent.mkdir(parents=True)
    pred.write_text(''.join(json.dumps(r) + '\n' for r in rows))
    (root / 'experiments/session07/tuned/metrics.json').write_text(json.dumps({'model_id': SHA}))
    (root / 'artifacts').mkdir()
    (root / 'artifacts/selected.json').write_text(json.dumps({'artifact_sha256': SHA, 'thresholds': CUTS}))
    return root


class CueEvalTests(unittest.TestCase):
    def test_matrix_rule_matches_the_product_rule(self):
        rng = np.random.default_rng(0)
        scores = rng.random((200, len(LABELS)))
        flagged, uncertain, possible = cues(scores, CUTS, 0.05)
        for i in range(len(scores)):
            u, p = review_cues(scores[i], CUTS)
            self.assertEqual([LABELS[k] for k in np.flatnonzero(uncertain[i])], u)
            self.assertEqual([LABELS[k] for k in np.flatnonzero(possible[i])], p)

    def test_counts_add_up(self):
        r = run(make_repo())
        for col in r['margins'].values():
            for block in col.values():
                self.assertLessEqual(block['missed_labels_with_a_possible_cue'], block['missed_labels'])
                self.assertEqual(block['possible_cues_that_are_annotator_labels'], block['missed_labels_with_a_possible_cue'])
                self.assertLessEqual(block['uncertain_flags'], block['flags'])
        self.assertFalse(r['test_split_read'])

    def test_bigger_margin_never_gives_fewer_cues(self):
        r = run(make_repo())
        h = {k: v['leave_one_company_out_HONEST']['possible_cues'] for k, v in r['margins'].items()}
        self.assertLessEqual(h['0.03'], h['0.05'])
        self.assertLessEqual(h['0.05'], h['0.10'])

    def test_stops_when_predictions_are_from_another_model(self):
        root = make_repo()
        (root / 'artifacts/selected.json').write_text(json.dumps({'artifact_sha256': 'e' * 64, 'thresholds': CUTS}))
        with self.assertRaises(CueEvalError):
            run(root)

    def test_stops_when_cut_offs_do_not_match_the_predictions(self):
        root = make_repo()
        (root / 'artifacts/selected.json').write_text(json.dumps({'artifact_sha256': SHA, 'thresholds': [0.5] * 8}))
        with self.assertRaises(CueEvalError):
            run(root)

    def test_refuses_test_split_rows(self):
        root = make_repo()
        path = root / 'experiments/session07/tuned/predictions.jsonl'
        lines = path.read_text().splitlines()
        row = json.loads(lines[0]); row['id'] = 'test:00000'; lines[0] = json.dumps(row)
        path.write_text('\n'.join(lines) + '\n')
        with self.assertRaises(ValueError):
            run(root)

    def test_markdown_states_the_rule_and_labels_both_columns(self):
        text = to_markdown(run(make_repo()))
        self.assertIn('Rule set before running', text)
        self.assertIn('(optimistic)', text)
        self.assertIn('(honest)', text)


if __name__ == '__main__':
    unittest.main()
