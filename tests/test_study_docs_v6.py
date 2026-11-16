"""Session 11 study materials: task bank v6 (tasks K1 and L1), answers the panel lists but the model misses."""
import json
import tempfile
import unittest
from pathlib import Path

from clauses.absence import worth_a_look
from clauses.model import analyze, load
from clauses.session_v2 import load_tasks
from scripts.check_study_docs import check, verdict

ROOT = Path(__file__).resolve().parents[1]
BANK = ROOT / 'examples/study/tasks_v6.json'
# Only sentence openings are here (needed to find the sentences); the answers stay in private/.
KEY = {
    'K1': {'target_category': 'Limitation of liability',
           'answer_sentence_starts_with': "As a condition of access to Cloudup, you understand and agree that Automattic's liability shall not exceed",
           'distractor_starts_with': 'Automattic shall not have any liability for any indirect'},
    'L1': {'target_category': 'Content removal',
           'answer_sentence_starts_with': 'We reserve the right to delete any free account that has not been logged into',
           'distractor_starts_with': 'Individual voter data that is older than 3 months'},
}


class StudyDocsV6Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.bundle = load()
        key = Path(tempfile.mkdtemp()) / 'key.json'
        key.write_text(json.dumps(KEY))
        cls.summary = check(BANK, key, cls.bundle)
        cls.by_task = {t['task_id']: t for t in cls.summary['tasks']}

    def panel(self, doc, category):
        a = analyze((ROOT / f'examples/fresh/{doc}_terms.txt').read_text(encoding='utf-8'), self.bundle)
        return {c['category']: c for c in worth_a_look(a)['categories']}[category]

    def test_bank_has_k1_and_l1_on_fresh_documents(self):
        tasks = load_tasks(BANK)
        self.assertEqual(sorted(tasks), ['K1', 'L1'])
        self.assertEqual(tasks['K1']['document'], 'examples/fresh/cloudup_terms.txt')
        self.assertEqual(tasks['L1']['document'], 'examples/fresh/crowdsignal_terms.txt')

    def test_k1_answer_is_missed_but_listed_and_the_flags_point_elsewhere(self):
        k1 = self.by_task['K1']
        self.assertEqual((k1['answer_sentence_cue'], k1['target_score'], k1['other_sentences_with_target_label']), ('none', 0.426, 3))
        self.assertTrue(k1['answer_sentence_in_worth_a_look'])
        self.assertEqual(k1['distractor_flagged_categories'], ['Limitation of liability'])
        p = self.panel('cloudup', 'Limitation of liability')
        self.assertEqual(p['flagged_sentence_ids'], [30, 54, 55])
        self.assertIn({'sentence_id': 56, 'words': ['liability']}, p['worth_a_look'])

    def test_l1_answer_is_missed_but_listed_under_a_category_with_no_flag(self):
        l1 = self.by_task['L1']
        self.assertEqual((l1['answer_sentence_cue'], l1['target_score'], l1['worth_a_look_sentences_for_target']), ('none', 0.37, 4))
        self.assertTrue(l1['answer_sentence_in_worth_a_look'])
        self.assertEqual(l1['distractor_flagged_categories'], [])
        p = self.panel('crowdsignal', 'Content removal')
        self.assertEqual(p['flagged'], 0)
        self.assertEqual([x['sentence_id'] for x in p['worth_a_look']], [47, 96, 129, 131])

    def test_verdict_lines(self):
        self.assertEqual(verdict(self.by_task['K1']),
                         "K1: MODEL MISSES IT | target score 0.426 (cut-off 0.75) | extra labels on answer 0 | other "
                         "'Limitation of liability' sentences 3 | answer listed as worth a look: yes (5 listed) | "
                         "distractor flagged as: Limitation of liability")
        self.assertEqual(verdict(self.by_task['L1']),
                         "L1: MODEL MISSES IT | target score 0.37 (cut-off 0.80) | extra labels on answer 0 | other "
                         "'Content removal' sentences 0 | answer listed as worth a look: yes (4 listed) | "
                         "distractor flagged as: nothing")

    def test_summary_contains_no_answer_text_or_positions(self):
        text = json.dumps(self.summary)
        for word in ('5.23', 'exceed', 'logged', 'months', 'sentence_id'):
            self.assertNotIn(word, text)


if __name__ == '__main__':
    unittest.main()
