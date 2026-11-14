"""Session 11: the ablation and its pre-set rule (scripts/ablation.py)."""
import json
import unittest
from pathlib import Path

from sklearn.pipeline import FeatureUnion

from scripts.ablation import AblationError, CUTS, FEATURES, WEIGHTS, decide, make, name, run, simplicity

ROOT = Path(__file__).resolve().parents[1]
RULE = json.loads((ROOT / 'docs/decisions/final_model_rule.json').read_text())


def configs(scores):
    out = []
    for (f, w, c), s in zip([(f, w, c) for f in FEATURES for w in WEIGHTS for c in CUTS], scores):
        out.append({'name': name(f, w, c), 'features': f, 'class_weight': w, 'cut_offs': c, 'honest_macro_f1': s})
    return out


class RuleTests(unittest.TestCase):
    def test_the_rule_file_is_the_frozen_one(self):
        self.assertEqual(RULE['written'], '2026-11-10')
        self.assertEqual((RULE['rule']['min_gain'], RULE['rule']['tie_margin']), (0.02, 0.005))
        self.assertEqual(RULE['shipped'], {'features': 'hybrid', 'class_weight': 'balanced', 'cut_offs': 'per_category'})

    def test_keep_when_nothing_beats_the_shipped_model_by_the_margin(self):
        scores = [0.60] * 12
        scores[8] = 0.6768                       # hybrid / balanced / per_category (shipped)
        scores[0] = 0.6967                       # word / balanced / per_category: +0.0199, not enough
        d = decide(configs(scores), RULE)
        self.assertEqual(d['result'], 'KEEP the shipped model for the final release')
        self.assertFalse(d['switch'])
        self.assertEqual((d['best_other'], d['best_other_honest_macro_f1']), ('word / balanced / per_category', 0.6967))

    def test_switch_to_the_simplest_configuration_near_the_best(self):
        scores = [0.60] * 12
        scores[8] = 0.6768
        scores[10] = 0.7100                      # hybrid / none / per_category: best
        scores[1] = 0.7060                       # word / balanced / fixed_0.5: within 0.005 and simpler
        d = decide(configs(scores), RULE)
        self.assertTrue(d['switch'])
        self.assertEqual(d['chosen'], 'word / balanced / fixed_0.5')
        self.assertEqual(d['result'], 'SWITCH to word / balanced / fixed_0.5 at the Session 12 freeze')

    def test_simplicity_order(self):
        c = configs([0.5] * 12)
        order = sorted(c, key=simplicity)
        self.assertEqual(order[0]['features'] in ('word', 'char'), True)
        self.assertEqual(order[0]['cut_offs'], 'fixed_0.5')
        self.assertEqual(order[-1]['name'], 'hybrid / balanced / per_category')


class PipelineTests(unittest.TestCase):
    def test_the_three_feature_sets(self):
        self.assertIsInstance(make('hybrid', 'balanced').named_steps['features'], FeatureUnion)
        self.assertEqual(make('char', 'none').named_steps['features'].analyzer, 'char_wb')
        self.assertEqual(make('word', 'balanced').named_steps['features'].ngram_range, (1, 2))
        self.assertIsNone(make('word', 'none').named_steps['classifier'].estimator.class_weight)

    def test_validation_rows_that_do_not_match_the_committed_predictions_stop_the_ablation(self):
        with self.assertRaisesRegex(AblationError, 'do not match'):
            run(ROOT, train_rows=[{'id': 'train:0', 'text': 'x', 'labels': [], 'document_id': 'a', 'split': 'train'}],
                val_rows=[{'id': 'validation:0', 'text': 'x', 'labels': [], 'document_id': 'b', 'split': 'validation'}])


if __name__ == '__main__':
    unittest.main()
