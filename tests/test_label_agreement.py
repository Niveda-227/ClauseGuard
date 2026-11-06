"""Session 10: agreement between the two annotators (scripts/label_agreement.py)."""
import unittest

from fresh_fixture import temp_root, write_labels
from scripts.check_labels import PUBLISHED
from scripts.label_agreement import AgreementError, gold, kappa, run, to_markdown


def rule(words):
    def choose(doc_id, i, text):
        return [label for word, label in words if word in text.lower()]
    return choose


A1 = rule([('arbitrat', 'Arbitration'), ('governed by', 'Choice of law'), ('terminate', 'Unilateral termination')])
A2 = rule([('arbitrat', 'Arbitration'), ('governed by', 'Choice of law'), ('suspend', 'Unilateral termination')])


class KappaTests(unittest.TestCase):
    def test_known_values(self):
        self.assertEqual(kappa([(True, True), (False, False)] * 5), 1.0)
        self.assertIsNone(kappa([(False, False)] * 10))
        # 20 items: both yes 5, A only 5, B only 0, both no 10 -> p_o 0.75, p_e 0.5*0.25+0.5*0.75 = 0.5
        pairs = [(True, True)] * 5 + [(True, False)] * 5 + [(False, False)] * 10
        self.assertEqual(kappa(pairs), 0.5)
        self.assertIsNone(kappa([]))


class AgreementTests(unittest.TestCase):
    def setUp(self):
        self.root = temp_root()

    def test_stops_when_a_set_of_labels_is_missing(self):
        write_labels(self.root, 'A1', A1, PUBLISHED)
        with self.assertRaisesRegex(AgreementError, 'A2'):
            run(self.root)

    def test_identical_labels_agree_perfectly(self):
        write_labels(self.root, 'A1', A1, PUBLISHED)
        write_labels(self.root, 'A2', A1, PUBLISHED)
        r = run(self.root)
        self.assertEqual(r['sentences'], 376)
        self.assertEqual(r['pooled_kappa'], 1.0)
        self.assertEqual(r['sentences_with_any_disagreement'], 0)
        self.assertEqual(r['strict_labels'], r['lenient_labels'])
        self.assertIsNone(r['per_category']['Content removal']['kappa'])
        self.assertEqual(r['per_category']['Content removal']['kappa_text'], 'not defined')
        self.assertEqual((r['pooled_kappa_text'], r['per_category']['Arbitration']['kappa_text']), ('1.00', '1.00'))

    def test_strict_is_both_and_lenient_is_either(self):
        write_labels(self.root, 'A1', A1, PUBLISHED)
        write_labels(self.root, 'A2', A2, PUBLISHED)
        r = run(self.root)
        c = r['per_category']['Unilateral termination']
        self.assertEqual(c['both'] + (c['A1'] - c['both']) + (c['A2'] - c['both']), c['either'])
        strict, lenient = gold(self.root, 'strict'), gold(self.root, 'lenient')
        for d in strict:
            for s, l in zip(strict[d], lenient[d]):
                self.assertTrue(s <= l)
        self.assertEqual(sum(len(x) for d in strict for x in strict[d]), r['strict_labels'])
        self.assertEqual(sum(len(x) for d in lenient for x in lenient[d]), r['lenient_labels'])
        self.assertEqual(r['per_category']['Arbitration']['kappa'], 1.0)

    def test_markdown_has_no_sentence_text(self):
        write_labels(self.root, 'A1', A1, PUBLISHED)
        write_labels(self.root, 'A2', A2, PUBLISHED)
        md = to_markdown(run(self.root))
        self.assertIn("Cohen's kappa", md)
        self.assertIn('not defined', md)
        self.assertNotIn('arbitrat', md.lower().replace('arbitration', ''))


if __name__ == '__main__':
    unittest.main()
