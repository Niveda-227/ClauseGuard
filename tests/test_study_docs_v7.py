"""Session 12 study materials: task bank v7 (tasks M1 and N1), the final user check on the frozen release.
In both tasks the app flags the answer sentence."""
import json
import tempfile
import unittest
from pathlib import Path

from clauses.absence import worth_a_look
from clauses.model import analyze, load
from clauses.session_v2 import load_tasks
from scripts.check_study_docs import check, verdict

ROOT = Path(__file__).resolve().parents[1]
BANK = ROOT / 'examples/study/tasks_v7.json'
# Only sentence openings are here (needed to find the sentences); the answers stay in private/.
KEY = {
    'M1': {'target_category': 'Arbitration',
           'answer_sentence_starts_with': 'We both agree to resolve any disputes arising out of these Terms or your use of Cloudup through final and binding arbitration',
           'distractor_starts_with': 'You agree that these Terms, and your use of Cloudup, are governed by California law'},
    'N1': {'target_category': 'Content removal',
           'answer_sentence_starts_with': 'We do not pre-screen content, but we reserve the right',
           'distractor_starts_with': 'Termination will furthermore result in the deletion of your account'},
}


class StudyDocsV7Tests(unittest.TestCase):
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

    def test_bank_has_m1_and_n1_on_fresh_documents(self):
        tasks = load_tasks(BANK)
        self.assertEqual(sorted(tasks), ['M1', 'N1'])
        self.assertEqual(tasks['M1']['document'], 'examples/fresh/cloudup_terms.txt')
        self.assertEqual(tasks['N1']['document'], 'examples/fresh/basecamp_terms.txt')

    def test_m1_answer_is_the_only_arbitration_flag(self):
        m1 = self.by_task['M1']
        self.assertEqual((m1['answer_sentence_cue'], m1['target_score'], m1['other_sentences_with_target_label']), ('flagged', 0.983, 0))
        self.assertEqual(m1['distractor_flagged_categories'], ['Choice of law'])
        self.assertEqual(self.panel('cloudup', 'Arbitration')['flagged_sentence_ids'], [62])

    def test_n1_answer_is_flagged_and_one_other_sentence_too(self):
        n1 = self.by_task['N1']
        self.assertEqual((n1['answer_sentence_cue'], n1['target_score'], n1['other_sentences_with_target_label']), ('flagged', 0.996, 1))
        self.assertEqual(n1['distractor_flagged_categories'], ['Unilateral termination'])
        self.assertEqual(self.panel('basecamp', 'Content removal')['flagged_sentence_ids'], [71, 119])

    def test_verdict_lines(self):
        self.assertEqual(verdict(self.by_task['M1']),
                         "M1: FAIR | target score 0.983 (cut-off 0.80) | extra labels on answer 0 | other 'Arbitration' "
                         "sentences 0 | answer listed as worth a look: no (10 listed) | distractor flagged as: Choice of law")
        self.assertEqual(verdict(self.by_task['N1']),
                         "N1: FAIR | target score 0.996 (cut-off 0.80) | extra labels on answer 0 | other 'Content removal' "
                         "sentences 1 | answer listed as worth a look: no (5 listed) | distractor flagged as: Unilateral termination")

    def test_summary_contains_no_answer_text_or_positions(self):
        text = json.dumps(self.summary)
        for word in ('binding', 'pre-screen', 'California', 'sentence_id'):
            self.assertNotIn(word, text)


if __name__ == '__main__':
    unittest.main()
