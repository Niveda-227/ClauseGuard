"""Session 09: do the search words reach the clauses the model misses? (scripts/hint_eval.py)"""
import json
import shutil
import tempfile
import unittest
from pathlib import Path

import numpy as np

from clauses.data import DEFAULT_PATH
from clauses.schema import LABELS
from scripts.hint_eval import (HintEvalError, MAX_MARKS_PER_100, MIN_COVERAGE, hit_matrix, measure, run,
                               to_markdown, validation_texts)

ROOT = Path(__file__).resolve().parents[1]
K = {label: i for i, label in enumerate(LABELS)}


def row(i, company, gold, scores):
    return {'id': f'validation:{i:05d}', 'document_id': company, 'gold': gold, 'predicted': [], 'scores': scores}


class MeasureTests(unittest.TestCase):
    def test_counts_marks_missed_labels_and_reached_labels(self):
        y = np.zeros((4, 8), dtype=int)
        y[0, K['Content removal']] = 1      # missed, and has a mark: reached
        y[1, K['Content removal']] = 1      # flagged: not missed
        y[2, K['Arbitration']] = 1          # missed, no mark
        flagged = np.zeros((4, 8), dtype=bool)
        flagged[1, K['Content removal']] = True
        hits = hit_matrix(['We may delete your photos.', 'We may remove posts.', 'Disputes go to a panel.',
                           'Deleted items stay for 30 days.'])
        m = measure(y, flagged, hits)
        self.assertEqual(m['missed_labels'], 2)
        self.assertEqual(m['marks'], 2)                       # sentences 0 and 3 (sentence 1 is flagged)
        self.assertEqual(m['missed_labels_with_a_mark'], 1)
        self.assertEqual(m['percent_of_missed_labels_with_a_mark'], 50.0)
        self.assertEqual(m['marks_per_100_sentences'], 50.0)
        self.assertEqual(m['marks_that_are_annotator_labels'], 1)
        self.assertEqual(m['per_category']['Content removal'], {'missed_labels': 1, 'marks': 2, 'missed_labels_with_a_mark': 1})
        self.assertEqual(m['per_category']['Arbitration'], {'missed_labels': 1, 'marks': 0, 'missed_labels_with_a_mark': 0})

    def test_rule_constants_are_the_pre_set_ones(self):
        self.assertEqual(MIN_COVERAGE, 0.40)
        self.assertEqual(MAX_MARKS_PER_100, 20.0)


class RunTests(unittest.TestCase):
    def setUp(self):
        self.root = Path(tempfile.mkdtemp())
        (self.root / 'experiments/session07/tuned').mkdir(parents=True)
        (self.root / 'artifacts').mkdir()
        cuts = [0.5] * 8
        (self.root / 'artifacts/selected.json').write_text(json.dumps({'artifact_sha256': 'm' * 64, 'thresholds': cuts}))
        (self.root / 'experiments/session07/tuned/metrics.json').write_text(json.dumps({'model_id': 'm' * 64}))
        low = [0.1] * 8
        rows, self.split = [], []
        texts = ['We may delete your photos at any time.', 'You keep your rights.', 'Disputes go to arbitration.']
        for c, company in enumerate(['A', 'B', 'C']):
            for j, text in enumerate(texts):
                i = 3 * c + j
                gold = ['Content removal'] if j == 0 else []
                rows.append(row(i, company, gold, low))
                self.split.append({'id': f'validation:{i:05d}', 'text': text, 'labels': gold, 'document_id': company,
                                   'split': 'validation'})
        (self.root / 'experiments/session07/tuned/predictions.jsonl').write_text('\n'.join(json.dumps(r) for r in rows) + '\n')

    def test_writes_counts_and_a_decision_without_sentence_text(self):
        r = run(self.root, split_rows=self.split)
        honest = r['honest']
        self.assertEqual(honest['missed_labels'], 3)
        self.assertEqual(honest['missed_labels_with_a_mark'], 3)
        self.assertEqual(honest['marks'], 6)  # 'delete' (Content removal) and 'arbitration' (Arbitration), 3 companies
        self.assertTrue(r['rule_a_coverage_passed'])
        self.assertFalse(r['rule_b_volume_passed'])  # 66.67 marks per 100 sentences
        self.assertEqual(r['decision'], 'RECONSIDER the worth-a-look list in Session 10')
        self.assertEqual((r['coverage_result'], r['volume_result']), ('passed', 'failed'))
        self.assertFalse(r['test_split_read'])
        text = json.dumps(r) + to_markdown(r)
        for sentence in ('delete your photos', 'keep your rights', 'go to arbitration'):
            self.assertNotIn(sentence, text)

    def test_ids_and_gold_labels_must_line_up_with_the_dataset(self):
        bad = [dict(r) for r in self.split]
        bad[0]['labels'] = []
        with self.assertRaisesRegex(HintEvalError, 'Gold labels'):
            run(self.root, split_rows=bad)
        with self.assertRaisesRegex(HintEvalError, 'IDs'):
            run(self.root, split_rows=self.split[:-1])

    def test_predictions_from_another_model_are_refused(self):
        (self.root / 'experiments/session07/tuned/metrics.json').write_text(json.dumps({'model_id': 'x' * 64}))
        with self.assertRaisesRegex(HintEvalError, 'not from the model'):
            run(self.root, split_rows=self.split)

    def test_validation_texts_keeps_prediction_order(self):
        rows = [json.loads(l) for l in (self.root / 'experiments/session07/tuned/predictions.jsonl').read_text().splitlines()]
        texts = validation_texts(rows, list(reversed(self.split)))
        self.assertEqual(texts[0], 'We may delete your photos at any time.')


@unittest.skipUnless(DEFAULT_PATH.exists(), 'dataset not downloaded: run python -m clauses.cli data')
class RealValidationTests(unittest.TestCase):
    def test_missed_labels_match_the_session07_evaluation(self):
        r = run(ROOT)
        ship = json.loads((ROOT / 'experiments/session07/threshold_ship_eval.json').read_text())
        self.assertEqual(r['optimistic']['missed_labels'], ship['new_product_tuned_OPTIMISTIC']['missed_labels'])
        self.assertEqual(r['honest']['missed_labels'], ship['new_product_leave_one_company_out_HONEST']['missed_labels'])
        self.assertEqual(r['honest']['sentences'], ship['sentences'])
        self.assertEqual(r['honest']['marks'], sum(c['marks'] for c in r['honest']['per_category'].values()))


if __name__ == '__main__':
    unittest.main()
