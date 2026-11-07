"""Session 10: the shipped model on fresh real Terms of Service (scripts/fresh_eval.py)."""
import json
import shutil
import unittest

import numpy as np

from clauses.data import DEFAULT_PATH
from clauses.model import load, predict_rows
from clauses.labelling import load_document
from clauses.schema import LABELS
from fresh_fixture import ROOT, temp_root, write_labels
from scripts.check_labels import PUBLISHED
from scripts.fresh_eval import (TEST_COMPANIES, VALIDATION_COMPANIES, FreshEvalError, company_overlap, decide,
                                measure, run, to_markdown)

K = {label: i for i, label in enumerate(LABELS)}
RULE = json.loads((ROOT / 'docs/decisions/fresh_rule.json').read_text())


def repo_copy():
    root = temp_root()
    for rel in ('artifacts/selected.json', 'docs/decisions/fresh_rule.json', 'experiments/session07/threshold_ship_eval.json'):
        (root / rel).parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT / rel, root / rel)
    return root


class CompanyTests(unittest.TestCase):
    def test_fresh_companies_are_not_in_unfair_tos(self):
        self.assertEqual(company_overlap(ROOT), [])

    def test_an_unfair_tos_company_is_caught(self):
        root = repo_copy()
        path = root / 'examples/fresh/manifest.json'
        m = json.loads(path.read_text())
        m['documents'][1]['company'] = 'Automattic (Evernote)'
        path.write_text(json.dumps(m))
        self.assertEqual(company_overlap(root), ['cloudup'])

    @unittest.skipUnless(DEFAULT_PATH.exists(), 'dataset not downloaded (python -m clauses.cli data)')
    def test_company_lists_match_the_dataset(self):
        # Train and validation only: the test split stays unread until Session 12.
        from clauses.data import load_split
        self.assertEqual(sorted({r['document_id'] for r in load_split('validation')}), sorted(VALIDATION_COMPANIES))
        selected = json.loads((ROOT / 'artifacts/selected.json').read_text())
        self.assertEqual(sorted({r['document_id'] for r in load_split('train')}), sorted(selected['train_documents']))
        self.assertEqual(len(TEST_COMPANIES), 10)
        self.assertFalse(set(TEST_COMPANIES) & (set(VALIDATION_COMPANIES) | set(selected['train_documents'])))


class MeasureTests(unittest.TestCase):
    def setUp(self):
        n = 6
        self.cuts = np.full(8, 0.5)
        self.y = np.zeros((n, 8), dtype=bool)
        self.scores = np.zeros((n, 8))
        self.hits = np.zeros((n, 8), dtype=bool)
        self.doc = np.array([0, 0, 0, 1, 1, 1])
        a, t = K['Arbitration'], K['Unilateral termination']
        self.y[0, a] = True; self.scores[0, a] = 0.9          # correct tag
        self.scores[1, a] = 0.8                                # wrong tag
        self.y[2, a] = True; self.scores[2, a] = 0.42; self.hits[2, a] = True   # missed, cue at 0.10 only, mark (doc 0 has an Arbitration flag)
        self.y[3, t] = True; self.scores[3, t] = 0.47; self.hits[3, t] = True   # missed, cue at 0.05, mark (doc 1 has no flag)
        self.hits[4, t] = True                                 # a mark that is not an answer

    def test_counts(self):
        m = measure(self.y, self.scores > self.cuts, self.scores, self.cuts, self.hits, self.doc)
        self.assertEqual((m['answer_labels'], m['flags'], m['correct_tags'], m['wrong_tags'], m['missed_labels']), (3, 2, 1, 1, 2))
        self.assertEqual(m['categories_in_macro_f1'], ['Unilateral termination', 'Arbitration'])
        self.assertEqual(m['per_category']['Arbitration']['f1'], 0.5)
        self.assertEqual(m['per_category']['Unilateral termination']['f1'], 0.0)
        self.assertEqual(m['macro_f1'], 0.25)
        self.assertIsNone(m['per_category']['Jurisdiction']['f1'])
        self.assertEqual(m['possible_cues']['0.05']['missed_labels_reached'], 1)
        self.assertEqual(m['possible_cues']['0.10']['missed_labels_reached'], 2)
        self.assertEqual(m['marks_all']['marks'], 3)
        self.assertEqual(m['marks_all']['missed_labels_reached'], 2)
        self.assertEqual(m['marks_zero_flag_only']['marks'], 2)
        self.assertEqual(m['marks_zero_flag_only']['missed_labels_reached'], 1)
        self.assertEqual(m['marks_zero_flag_only']['share_of_missed_labels_reached'], 0.5)
        self.assertEqual(m['marks_zero_flag_only']['reached_text'], '1 of 2 (50.0%)')
        # Everything must be plain Python values, so the result can be written as JSON.
        d = decide(RULE, m, 0.6768)
        self.assertEqual(json.loads(json.dumps({'m': m, 'd': d}))['d'], d)
        self.assertIs(type(d['cue_margin']['passed']), bool)
        self.assertIs(type(m['marks_all']['share_of_missed_labels_reached']), float)
        self.assertEqual((m['per_category']['Arbitration']['f1_text'], m['per_category']['Jurisdiction']['f1_text']),
                         ('0.50', 'not defined'))

    def test_no_answers_at_all_stops(self):
        with self.assertRaises(FreshEvalError):
            measure(np.zeros((2, 8), dtype=bool), np.zeros((2, 8), dtype=bool), np.zeros((2, 8)), self.cuts,
                    np.zeros((2, 8), dtype=bool), np.array([0, 0]))


class DecideTests(unittest.TestCase):
    def strict(self, macro, cue_share, cue_100, mark_share, mark_100):
        return {'macro_f1': macro, 'missed_labels': 10,
                'possible_cues': {'0.10': {'share_of_missed_labels_reached': cue_share, 'cues_per_100_sentences': cue_100,
                                           'missed_labels_reached': 2}},
                'marks_zero_flag_only': {'share_of_missed_labels_reached': mark_share, 'marks_per_100_sentences': mark_100,
                                         'missed_labels_reached': 4}}

    def test_the_limits_are_inclusive(self):
        d = decide(RULE, self.strict(0.5268, 0.20, 5.0, 0.40, 20.0), 0.6768)
        self.assertEqual(d['domain_shift']['result'], 'HOLDS UP on fresh documents')
        self.assertEqual(d['cue_margin']['result'], 'ADOPT the 0.10 margin in Session 11')
        self.assertEqual(d['zero_flag_marks']['result'], 'MAKE zero-flag-only the default in Session 11')
        self.assertEqual(d['zero_flag_marks']['summary'], 'reach 40.0% of the missed labels (4 of 10), 20.00 per 100 '
                                                          'sentences (needs at least 40% and at most 20 per 100)')
        self.assertEqual(d['domain_shift']['summary'], 'fresh macro-F1 0.5268 against 0.6768 on validation, a drop of '
                                                       '0.1500 (the limit is 0.15)')

    def test_failing_each_rule(self):
        d = decide(RULE, self.strict(0.52, 0.5, 5.1, 0.39, 1.0), 0.6768)
        self.assertEqual(d['domain_shift']['result'], 'DOMAIN SHIFT: treat it as the main risk in Session 11')
        self.assertEqual((d['cue_margin']['coverage_passed'], d['cue_margin']['volume_passed']), (True, False))
        self.assertEqual(d['cue_margin']['result'], 'KEEP the 0.05 margin')
        self.assertEqual(d['zero_flag_marks']['result'], 'KEEP showing all marks, off-by-default toggle stays')

    def test_no_missed_labels_keeps_the_current_setting(self):
        d = decide(RULE, self.strict(0.9, None, 0.0, None, 0.0), 0.6768)
        self.assertFalse(d['cue_margin']['passed'])
        self.assertIn('cannot be measured', d['zero_flag_marks']['note'])


class EndToEndTests(unittest.TestCase):
    def test_model_flags_as_answers_give_a_perfect_score_and_no_text_is_written(self):
        root = repo_copy()
        bundle = load()
        flags = {}
        for doc_id in ('basecamp', 'cloudup', 'crowdsignal'):
            _, _, sentences = load_document(doc_id, root)
            _, pred = predict_rows(bundle, [s.text for s in sentences])
            flags[doc_id] = [[LABELS[k] for k in range(8) if row[k]] for row in pred]
        write_labels(root, 'A1', lambda d, i, t: flags[d][i], PUBLISHED)
        write_labels(root, 'A2', lambda d, i, t: flags[d][i], PUBLISHED)
        r = run(root)
        self.assertEqual(r['sentences'], 376)
        self.assertEqual(r['strict']['macro_f1'], 1.0)
        self.assertEqual(r['strict']['wrong_tags'] + r['strict']['missed_labels'], 0)
        self.assertEqual(r['errors_strict'], [])
        self.assertEqual(r['rules']['domain_shift']['result'], 'HOLDS UP on fresh documents')
        md = to_markdown(r)
        text = (root / 'examples/fresh/cloudup_terms.txt').read_text()
        longest = max(text.splitlines(), key=len)
        self.assertNotIn(longest[:60], md + json.dumps(r))

    def test_stops_without_both_label_sets(self):
        root = repo_copy()
        write_labels(root, 'A1', lambda d, i, t: [], PUBLISHED)
        with self.assertRaises(ValueError):
            run(root)


if __name__ == '__main__':
    unittest.main()
