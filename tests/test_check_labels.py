"""Session 10: checking and publishing an annotator's labels (scripts/check_labels.py)."""
import json
import unittest

from clauses.labelling import fingerprint, label_path
from fresh_fixture import edit_label_file, temp_root, write_labels
from scripts.check_labels import PUBLISHED, check, publish


def arbitration_rule(doc_id, i, text):
    return ['Arbitration'] if 'arbitrat' in text.lower() else []


class CheckLabelsTests(unittest.TestCase):
    def setUp(self):
        self.root = temp_root()

    def test_missing_labels_are_reported_for_every_document(self):
        problems, _ = check('A1', self.root)
        self.assertEqual(len(problems), 3)
        self.assertTrue(all('missing' in p for p in problems))

    def test_complete_valid_labels_pass_and_counts_add_up(self):
        write_labels(self.root, 'A1', arbitration_rule)
        problems, counts = check('A1', self.root)
        self.assertEqual(problems, [])
        self.assertEqual(counts['sentences'], 376)
        self.assertEqual(counts['labelled_sentences'], counts['per_category']['Arbitration'])
        self.assertGreater(counts['per_category']['Arbitration'], 0)

    def test_incomplete_unknown_category_and_unsure_with_labels_fail(self):
        write_labels(self.root, 'A1', arbitration_rule)
        edit_label_file(self.root, 'A1', 'cloudup', lambda r: r.update(complete=False))
        edit_label_file(self.root, 'A1', 'basecamp', lambda r: r['sentences'][0].update(labels=['Privacy']))
        edit_label_file(self.root, 'A1', 'crowdsignal',
                        lambda r: r['sentences'][1].update(labels=['Arbitration'], unsure=True))
        problems, _ = check('A1', self.root)
        text = ' '.join(problems)
        self.assertIn('cloudup: not complete', text)
        self.assertIn('basecamp: sentence 1 has unknown', text)
        self.assertIn('crowdsignal: sentence 2 is marked unsure', text)

    def test_offsets_that_do_not_match_the_document_fail(self):
        write_labels(self.root, 'A1', arbitration_rule)
        edit_label_file(self.root, 'A1', 'cloudup', lambda r: r['sentences'][5].update(start=0))
        problems, _ = check('A1', self.root)
        self.assertEqual(problems, ['cloudup: sentence 6 does not match the document'])

    def test_publish_copies_unchanged_so_the_fingerprint_stays_the_same(self):
        write_labels(self.root, 'A1', arbitration_rule)
        before = fingerprint('A1', self.root)
        copied = publish('A1', self.root)
        self.assertEqual(copied, [f'{PUBLISHED}/A1/{d}.json' for d in ('basecamp', 'cloudup', 'crowdsignal')]
                         + ['experiments/session10/labels_A1.json'])
        self.assertEqual(fingerprint('A1', self.root, PUBLISHED), before)
        s = json.loads((self.root / 'experiments/session10/labels_A1.json').read_text())
        self.assertEqual((s['fingerprint'], s['sentences'], s['minutes_labelling']), (before, 376, 3))
        self.assertNotIn('arbitrat', json.dumps(s).lower().replace('arbitration', ''))
        self.assertEqual(check('A1', self.root, PUBLISHED)[0], [])

    def test_publish_refuses_labels_that_fail_the_check(self):
        write_labels(self.root, 'A1', arbitration_rule)
        edit_label_file(self.root, 'A1', 'cloudup', lambda r: r.update(complete=False))
        with self.assertRaisesRegex(ValueError, 'do not pass'):
            publish('A1', self.root)
        self.assertFalse((self.root / PUBLISHED).exists())

    def test_publish_refuses_to_overwrite_different_published_labels(self):
        write_labels(self.root, 'A1', arbitration_rule)
        publish('A1', self.root)
        edit_label_file(self.root, 'A1', 'cloudup', lambda r: r['sentences'][0].update(labels=['Arbitration']))
        with self.assertRaisesRegex(ValueError, 'Not overwriting'):
            publish('A1', self.root)
        self.assertTrue(label_path('A1', 'cloudup', self.root, PUBLISHED).exists())


if __name__ == '__main__':
    unittest.main()
