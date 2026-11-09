"""Session 10 study materials: task bank v5 on the fresh real Terms of Service (tasks I1 and J1)."""
import json
import tempfile
import unittest
from pathlib import Path

from clauses.absence import worth_a_look
from clauses.model import analyze, load
from clauses.session_v2 import load_tasks
from scripts.check_study_docs import check, verdict

ROOT = Path(__file__).resolve().parents[1]
BANK = ROOT / 'examples/study/tasks_v5.json'
# Only sentence openings are here (needed to find the sentences); the answers stay in private/.
KEY = {
    'I1': {'target_category': 'Unilateral change',
           'answer_sentence_starts_with': 'However, we may choose to change the prices for existing customers.',
           'distractor_starts_with': 'We reserve the right at any time to modify or discontinue'},
    'J1': {'target_category': 'Unilateral termination',
           'answer_sentence_starts_with': 'The owners and creators of Crowdsignal may, in their sole and absolute discretion'},
}


class StudyDocsV5Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.bundle = load()
        key = Path(tempfile.mkdtemp()) / 'key.json'
        key.write_text(json.dumps(KEY))
        cls.summary = check(BANK, key, cls.bundle)
        cls.by_task = {t['task_id']: t for t in cls.summary['tasks']}
        cls.basecamp = analyze((ROOT / 'examples/fresh/basecamp_terms.txt').read_text(encoding='utf-8'), cls.bundle)
        cls.crowdsignal = analyze((ROOT / 'examples/fresh/crowdsignal_terms.txt').read_text(encoding='utf-8'), cls.bundle)

    def test_bank_has_i1_and_j1_on_the_fresh_documents(self):
        tasks = load_tasks(BANK)
        self.assertEqual(sorted(tasks), ['I1', 'J1'])
        self.assertEqual(tasks['I1']['document'], 'examples/fresh/basecamp_terms.txt')
        self.assertEqual(tasks['J1']['document'], 'examples/fresh/crowdsignal_terms.txt')

    def test_i1_answer_is_missed_and_the_flagged_sentence_is_a_distractor(self):
        i1 = self.by_task['I1']
        self.assertEqual((i1['answer'], i1['answer_sentence_cue'], i1['target_score']), ('sentence', 'none', 0.618))
        self.assertFalse(i1['answer_sentence_in_worth_a_look'])
        self.assertEqual(i1['other_sentences_with_target_label'], 1)
        self.assertEqual(i1['distractor_flagged_categories'],
                         ['Unilateral termination', 'Unilateral change', 'Content removal'])
        s = self.basecamp['sentences']
        self.assertEqual(s[74]['text'], 'However, we may choose to change the prices for existing customers.')
        self.assertIn('at least 30 days notice', s[75]['text'])
        self.assertEqual((s[74]['labels'], s[74]['possible'], s[75]['labels']), ([], [], []))
        change = {c['category']: c for c in worth_a_look(self.basecamp)['categories']}['Unilateral change']
        self.assertEqual((change['flagged_sentence_ids'], [x['sentence_id'] for x in change['worth_a_look']]), ([71], [12, 67]))

    def test_j1_answer_is_flagged(self):
        j1 = self.by_task['J1']
        self.assertEqual((j1['answer_sentence_cue'], j1['target_score'], j1['other_sentences_with_target_label']),
                         ('flagged', 0.802, 0))
        self.assertEqual(self.crowdsignal['sentences'][73]['labels'], ['Unilateral termination'])
        self.assertIn('with or without notice', self.crowdsignal['sentences'][73]['text'])

    def test_verdict_lines(self):
        self.assertEqual(verdict(self.by_task['I1']),
                         "I1: MODEL MISSES IT | target score 0.618 (cut-off 0.80) | extra labels on answer 0 | other "
                         "'Unilateral change' sentences 1 | answer listed as worth a look: no (2 listed) | distractor "
                         "flagged as: Unilateral termination, Unilateral change, Content removal")
        self.assertEqual(verdict(self.by_task['J1']),
                         "J1: FAIR | target score 0.802 (cut-off 0.70) | extra labels on answer 0 | other "
                         "'Unilateral termination' sentences 0 | answer listed as worth a look: no (2 listed)")

    def test_summary_contains_no_answer_text_or_positions(self):
        text = json.dumps(self.summary)
        for word in ('prices', 'notice', 'discretion', 'reserve', 'sentence_id'):
            self.assertNotIn(word, text)


if __name__ == '__main__':
    unittest.main()
