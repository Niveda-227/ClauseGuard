"""Tests for scripts/fragment_trial.py with made-up sentences (no dataset needed)."""
import json
import unittest

from scripts.fragment_trial import TrialError, no_lowercase, run, short_no_end_mark, to_markdown


def row(i, text, labels):
    return {'id': f'validation:{i:05d}', 'text': text, 'labels': labels, 'document_id': 'C', 'split': 'validation'}


def pred(i, gold, predicted):
    return {'id': f'validation:{i:05d}', 'document_id': 'C', 'gold': gold, 'predicted': predicted, 'scores': [0.0] * 8}


def make(n_headings=6):
    rows, preds = [], []
    for i in range(n_headings):  # short headings wrongly tagged
        rows.append(row(i, 'LIMITATION OF LIABILITY', []))
        preds.append(pred(i, [], ['Limitation of liability']))
    i = n_headings
    rows.append(row(i, 'We are not liable for any loss you suffer from using the service.', ['Limitation of liability']))
    preds.append(pred(i, ['Limitation of liability'], ['Limitation of liability']))
    rows.append(row(i + 1, 'You can rate each ride after it ends.', []))
    preds.append(pred(i + 1, [], []))
    return rows, preds


class FragmentTrialTests(unittest.TestCase):
    def test_short_wrongly_tagged_headings_pass(self):
        r = run(*make(6))
        by = {c['candidate']: c for c in r['candidates']}
        self.assertEqual(by['fewer_than_4_words']['wrong_tags_removed'], 6)
        self.assertEqual(by['fewer_than_4_words']['correct_tags_removed'], 0)
        self.assertTrue(by['fewer_than_4_words']['passes'])
        # Ties go to the first listed candidate that passes.
        self.assertEqual(r['recommendation'], 'fewer_than_4_words')

    def test_too_few_wrong_tags_removed_does_not_pass(self):
        r = run(*make(4))
        self.assertIsNone(r['recommendation'])

    def test_a_label_on_a_hidden_sentence_fails_the_candidate(self):
        rows, preds = make(6)
        rows[0]['labels'] = ['Limitation of liability']
        preds[0]['gold'] = ['Limitation of liability']
        r = run(rows, preds)
        by = {c['candidate']: c for c in r['candidates']}
        self.assertFalse(by['fewer_than_4_words']['passes'])

    def test_mismatched_files_stop(self):
        rows, preds = make(6)
        with self.assertRaises(TrialError):
            run(rows, preds[:-1])
        preds[0]['gold'] = ['Arbitration']
        with self.assertRaises(TrialError):
            run(rows, preds)

    def test_no_sentence_text_in_output(self):
        r = run(*make(6))
        text = json.dumps(r) + to_markdown(r)
        self.assertNotIn('LIMITATION OF LIABILITY', text)
        self.assertNotIn('rate each ride', text)

    def test_rules(self):
        self.assertTrue(no_lowercase('TERMINATION'))
        self.assertFalse(no_lowercase('Termination'))
        self.assertFalse(no_lowercase('12.'))
        self.assertTrue(short_no_end_mark('5. Termination of your account'))
        self.assertFalse(short_no_end_mark('We may end your account.'))


if __name__ == '__main__':
    unittest.main()
