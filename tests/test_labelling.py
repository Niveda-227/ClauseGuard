"""Session 10: the labelling tool (clauses/labelling.py)."""
import json
import shutil
import tempfile
import unittest
from pathlib import Path

from clauses.labelling import fingerprint, label, label_path, parse_answer, status

ROOT = Path(__file__).resolve().parents[1]


def answers(*items):
    it = iter(items)
    return lambda prompt='': next(it)


class ParseTests(unittest.TestCase):
    def test_numbers_become_category_names_in_label_order(self):
        self.assertEqual(parse_answer('5,1'), ('labels', ['Limitation of liability', 'Contract by using']))
        self.assertEqual(parse_answer(' 3 '), ('labels', ['Unilateral change']))
        self.assertEqual(parse_answer('2, 2'), ('labels', ['Unilateral termination']))
        self.assertEqual(parse_answer(''), ('labels', []))

    def test_commands_and_bad_input(self):
        self.assertEqual(parse_answer('?'), ('unsure', []))
        self.assertEqual(parse_answer('B'), ('back', None))
        self.assertEqual(parse_answer('q'), ('quit', None))
        for bad in ('9', '0', '1;2', 'yes', '1,,2'):
            self.assertEqual(parse_answer(bad), ('bad', None), bad)


class LabelFlowTests(unittest.TestCase):
    def setUp(self):
        self.root = Path(tempfile.mkdtemp())
        (self.root / 'examples').mkdir()
        shutil.copytree(ROOT / 'examples/fresh', self.root / 'examples/fresh')
        self.out = []

    def run_label(self, doc, *items):
        clock = iter(range(0, 10000))
        return label(doc, 'A1', self.root, ask=answers(*items), say=self.out.append, clock=lambda: next(clock))

    def test_quit_saves_and_the_next_run_continues(self):
        record = self.run_label('cloudup', '1', '', 'q')
        self.assertEqual(len(record['sentences']), 2)
        self.assertFalse(record['complete'])
        saved = json.loads(label_path('A1', 'cloudup', self.root).read_text())
        self.assertEqual(saved['sentences'][0]['labels'], ['Limitation of liability'])
        record = self.run_label('cloudup', *([''] * 75))
        self.assertTrue(record['complete'])
        self.assertEqual(len(record['sentences']), 77)
        self.assertEqual([s['sentence_id'] for s in record['sentences']], list(range(77)))

    def test_back_unsure_bad_and_help(self):
        record = self.run_label('cloudup', '2', 'b', '3', 'x', 'h', '?', 'q')
        self.assertEqual(record['sentences'][0]['labels'], ['Unilateral change'])
        self.assertEqual(record['sentences'][1], {**record['sentences'][1], 'labels': [], 'unsure': True})
        self.assertTrue(any('Not understood' in line for line in self.out))

    def test_fingerprint_only_when_every_document_is_done(self):
        self.assertIsNone(fingerprint('A1', self.root))
        for doc, n in (('basecamp', 156), ('cloudup', 77), ('crowdsignal', 143)):
            self.run_label(doc, *([''] * n))
        fp = fingerprint('A1', self.root)
        self.assertRegex(fp, r'^[0-9a-f]{64}$')
        self.assertEqual(status('A1', self.root, say=self.out.append), fp)

    def test_a_changed_document_is_refused(self):
        path = self.root / 'examples/fresh/cloudup_terms.txt'
        path.write_text(path.read_text() + 'Extra.\n')
        with self.assertRaisesRegex(ValueError, 'SHA-256'):
            self.run_label('cloudup', 'q')

    def test_unknown_annotator_is_refused(self):
        with self.assertRaisesRegex(ValueError, 'A1'):
            label('cloudup', 'A3', self.root, ask=answers('q'), say=self.out.append)


if __name__ == '__main__':
    unittest.main()
