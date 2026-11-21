"""Session 12: the pre-set rule for reporting the one-time test-split result (docs/decisions/2026-11-18_final_test_rule.md)."""
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RULE = json.loads((ROOT / 'docs/decisions/final_test_rule.json').read_text(encoding='utf-8'))
MEMO = (ROOT / 'docs/decisions/2026-11-18_final_test_rule.md').read_text(encoding='utf-8')


def value(rel, key):
    data = json.loads((ROOT / rel).read_text(encoding='utf-8'))
    for part in key.split('.'):
        data = data[part]
    return data


class FinalTestRuleTests(unittest.TestCase):
    def test_the_rule_names_the_shipped_model(self):
        manifest = json.loads((ROOT / 'artifacts/selected.json').read_text(encoding='utf-8'))
        self.assertEqual(RULE['model']['model_sha256'], manifest['artifact_sha256'])
        self.assertEqual(RULE['model']['release'], '1.0.0')
        self.assertIn(RULE['model']['model_sha256'], MEMO)

    def test_the_comparison_numbers_exist_in_their_sources(self):
        honest = RULE['compare_with']['honest_validation_macro_f1']
        optimistic = RULE['compare_with']['optimistic_validation_macro_f1']
        self.assertEqual(value(honest['source'], honest['key']), 0.6768)
        self.assertEqual(value(optimistic['source'], optimistic['key']), 0.7244)

    def test_the_memo_states_the_same_rule(self):
        rule = RULE['rule']
        self.assertEqual(rule['margin'], 0.05)
        for text in (rule['if_within'], rule['if_below'], rule['if_above']):
            self.assertIn(text, MEMO)
        self.assertIn('Within 0.05 either way', MEMO)
        self.assertIn('The test split is read once and never again.', MEMO)


if __name__ == '__main__':
    unittest.main()
