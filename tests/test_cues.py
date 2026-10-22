"""Session 08 review cues: uncertain flags and possible categories near a cut-off (clauses/cues.py)."""
import unittest
from pathlib import Path

import numpy as np

from clauses.cues import MARGIN, review_cues
from clauses.display import result_label
from clauses.export import render_html
from clauses.model import analyze, load
from clauses.schema import LABELS

ROOT = Path(__file__).resolve().parents[1]
DOCS = ['examples/fictional_terms.txt', 'examples/study/document_E.txt', 'examples/study/document_F.txt']
CUTS = [0.5] * len(LABELS)


def scores_with(**by_index):
    s = [0.01] * len(LABELS)
    for i, v in by_index.items():
        s[int(i[1:])] = v
    return s


class ReviewCueRuleTests(unittest.TestCase):
    def test_margin_is_the_pre_set_value(self):
        # Fixed before any Session 08 result: the app's Session 04 "near threshold" distance.
        self.assertEqual(MARGIN, 0.05)

    def test_flag_just_above_the_cut_off_is_uncertain(self):
        self.assertEqual(review_cues(scores_with(k0=0.53), CUTS), ([LABELS[0]], []))

    def test_clear_flag_is_not_uncertain(self):
        self.assertEqual(review_cues(scores_with(k0=0.90), CUTS), ([], []))

    def test_score_just_below_the_cut_off_is_possible(self):
        self.assertEqual(review_cues(scores_with(k6=0.48), CUTS), ([], [LABELS[6]]))

    def test_score_exactly_on_the_cut_off_is_possible_not_flagged(self):
        # A category is flagged only when the score is ABOVE its cut-off.
        self.assertEqual(review_cues(scores_with(k6=0.5), CUTS), ([], [LABELS[6]]))

    def test_far_below_is_nothing(self):
        self.assertEqual(review_cues(scores_with(k6=0.30), CUTS), ([], []))

    def test_bad_input_is_refused(self):
        with self.assertRaises(ValueError):
            review_cues([0.1] * 3, CUTS)
        with self.assertRaises(ValueError):
            review_cues(scores_with(), CUTS, margin=0)


class ReviewCuesInTheProductTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.bundle = load()
        cls.cuts = np.asarray(cls.bundle['manifest']['thresholds'])
        cls.results = {d: analyze((ROOT / d).read_text(encoding='utf-8'), cls.bundle) for d in DOCS}

    def rows(self):
        for result in self.results.values():
            yield from result['sentences']

    def test_flags_are_unchanged(self):
        # Cues add information only: every flag is still exactly "score above cut-off".
        for row in self.rows():
            expected = [l for l, t in zip(LABELS, self.cuts) if row['scores'][l] > t]
            self.assertEqual(row['labels'], expected)

    def test_near_threshold_keeps_its_old_meaning(self):
        for row in self.rows():
            old_rule = bool(np.min(np.abs(np.array([row['scores'][l] for l in LABELS]) - self.cuts)) < 0.05)
            self.assertEqual(row['near_threshold'], old_rule)
            self.assertEqual(row['near_threshold'], bool(row['uncertain'] or row['possible']))

    def test_uncertain_are_flagged_and_possible_are_not(self):
        for row in self.rows():
            self.assertTrue(set(row['uncertain']) <= set(row['labels']))
            self.assertFalse(set(row['possible']) & set(row['labels']))

    def test_document_f_names_one_possible_jurisdiction_sentence(self):
        rows = [r for r in self.results['examples/study/document_F.txt']['sentences'] if r['possible']]
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]['possible'], ['Jurisdiction'])
        self.assertEqual(rows[0]['labels'], [])

    def test_list_text_and_export_show_the_cue(self):
        row = next(r for r in self.results['examples/study/document_F.txt']['sentences'] if r['possible'])
        self.assertIn('No category flagged (possible: Jurisdiction) | ', result_label(row))
        html = render_html(self.results['examples/study/document_F.txt'])
        self.assertIn('Possible, not flagged', html)

    def test_rows_without_cues_still_render(self):
        # Results saved before Session 08 have no 'uncertain'/'possible' keys.
        old = {'sentence_id': 0, 'text': 'Support is available.', 'labels': [], 'near_threshold': False}
        self.assertTrue(result_label(old).startswith('1. No category flagged | '))


if __name__ == '__main__':
    unittest.main()
