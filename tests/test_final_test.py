"""Session 12: the one-time test-split run (scripts/final_test.py) and its check (scripts/check_final_test.py).

These tests never open the dataset: they score a few made-up sentences."""
import json
import shutil
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from clauses.model import load
from scripts import check_final_test, final_test

ROOT = Path(__file__).resolve().parents[1]
MADE_UP = [
    ('We may terminate your account at any time without notice.', ['Unilateral termination']),
    ('We may change these terms at any time.', ['Unilateral change']),
    ('These terms are governed by the laws of the State of California.', ['Choice of law']),
    ('Any dispute will be settled by binding arbitration.', ['Arbitration']),
    ('We are not liable for any indirect damages.', ['Limitation of liability']),
    ('You can contact us by email.', []),
]


def rows():
    return [{'id': f'made-up:{i}', 'text': t, 'labels': l, 'document_id': f'Company{i % 2}', 'split': 'test'}
            for i, (t, l) in enumerate(MADE_UP)]


def temp_root(d):
    root = Path(d)
    for rel in (final_test.RULE, final_test.VALIDATION):
        (root / rel).parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(ROOT / rel, root / rel)
    rule = json.loads((ROOT / final_test.RULE).read_text(encoding='utf-8'))
    (root / 'RELEASE.json').write_text(json.dumps({'version': '1.0.0', 'model_sha256': rule['model']['model_sha256'],
                                                   'cut_offs': {'A': 0.75}, 'product_files': {'app.py': '0' * 64}}))
    return root


def record(root, result, readings=1):
    (root / 'experiments/session12').mkdir(parents=True, exist_ok=True)
    (root / final_test.OUT_JSON).write_text(json.dumps(result, indent=2) + '\n')
    (root / final_test.OUT_MD).write_text(final_test.to_markdown(result))
    line = json.dumps({'model_id': result['model_sha256'], 'by': 'scripts/final_test.py'})
    (root / 'experiments/test_exposure.jsonl').write_text((line + '\n') * readings)


class FinalTestTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.bundle = load()

    def test_the_rule_wording_at_the_margins(self):
        rule = json.loads((ROOT / final_test.RULE).read_text(encoding='utf-8'))
        self.assertEqual(final_test.decide(0.7268, 0.6768, rule)[1], 'CONSISTENT with the honest validation estimate')
        self.assertEqual(final_test.decide(0.6268, 0.6768, rule)[1], 'CONSISTENT with the honest validation estimate')
        self.assertEqual(final_test.decide(0.6267, 0.6768, rule), (-0.0501, 'LOWER than the honest validation estimate'))
        self.assertEqual(final_test.decide(0.7269, 0.6768, rule)[1], 'HIGHER than the honest validation estimate')

    def test_the_result_counts_add_up_and_carry_no_text(self):
        with tempfile.TemporaryDirectory() as d:
            r = final_test.run(temp_root(d), rows(), self.bundle)
        self.assertEqual((r['sentences'], r['companies'], r['gold_labels']), (6, 2, 5))
        self.assertEqual(r['correct_tags'] + r['missed_labels'], r['gold_labels'])
        self.assertEqual(r['correct_tags'] + r['wrong_tags'], r['flags'])
        self.assertEqual(r['honest_validation_macro_f1'], 0.6768)
        self.assertEqual(len(r['per_category']), 8)
        text = json.dumps(r) + final_test.to_markdown(r)
        self.assertNotIn('arbitration.', text)
        self.assertNotIn('California', text)

    def test_it_stops_before_reading_when_not_the_release_or_already_read(self):
        with tempfile.TemporaryDirectory() as d:
            root = temp_root(d)
            with self.assertRaises(final_test.Stop):
                final_test.preconditions(root)  # no product files: not the release
            (root / 'experiments').mkdir(exist_ok=True)
            (root / 'experiments/test_exposure.jsonl').write_text('{"at": "earlier"}\n')
            with mock.patch.object(final_test, 'check_release', return_value=(True, [])):
                with self.assertRaisesRegex(final_test.Stop, 'already read'):
                    final_test.preconditions(root)

    def test_the_record_check_needs_exactly_one_reading_and_matching_files(self):
        with tempfile.TemporaryDirectory() as d:
            root = temp_root(d)
            result = final_test.run(root, rows(), self.bundle)
            record(root, result)
            ok, lines = check_final_test.check(root)
            self.assertTrue(ok, lines)
            self.assertEqual(lines[-1], 'FINAL TEST RECORD OK')
            record(root, result, readings=2)
            self.assertFalse(check_final_test.check(root)[0])
            record(root, result)
            (root / final_test.OUT_MD).write_text('edited by hand\n')
            self.assertFalse(check_final_test.check(root)[0])

    def test_the_record_check_does_not_open_the_dataset(self):
        with tempfile.TemporaryDirectory() as d:
            root = temp_root(d)
            record(root, final_test.run(root, rows(), self.bundle))
            with mock.patch('clauses.data.load_split', side_effect=AssertionError('the dataset was opened')):
                self.assertTrue(check_final_test.check(root)[0])


if __name__ == '__main__':
    unittest.main()
