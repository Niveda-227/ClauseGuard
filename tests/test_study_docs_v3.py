"""Session 07 study materials (task bank v3, documents E and F)."""
import json
import tempfile
import unittest
from pathlib import Path

from clauses.model import load
from clauses.session_v2 import load_tasks
from scripts.check_study_docs import check

ROOT = Path(__file__).resolve().parents[1]
BANK = ROOT / 'examples/study/tasks_v3.json'
# Only the sentence openings are here (needed to find the sentence); the answers stay in private/.
KEY = {
    'E1': {'target_category': 'Unilateral change', 'answer_sentence_starts_with': 'We may update these terms at any time'},
    'F1': {'target_category': 'Jurisdiction', 'answer_sentence_starts_with': 'Any legal action about these terms must be filed'},
}


class StudyDocsV3Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.bundle = load()
        cls.tmp = Path(tempfile.mkdtemp())
        key = cls.tmp / 'key.json'
        key.write_text(json.dumps(KEY))
        cls.summary = check(BANK, key, cls.bundle)
        cls.by_task = {t['task_id']: t for t in cls.summary['tasks']}

    def test_bank_has_e1_and_f1_and_no_retired_tasks(self):
        tasks = load_tasks(BANK)
        self.assertEqual(sorted(tasks), ['E1', 'F1'])
        # C1 and D1 were shown publicly in the mid-semester deck, so they are retired.
        self.assertNotIn('C1', tasks)
        self.assertNotIn('D1', tasks)

    def test_e1_answer_sentence_is_flagged(self):
        self.assertTrue(self.by_task['E1']['answer_sentence_flagged_with_target'])

    def test_f1_answer_sentence_exists_and_is_reported(self):
        # F1 tests whether people find a clause the app may NOT flag, so either result is allowed;
        # the check must still find exactly one answer sentence and report its score.
        f1 = self.by_task['F1']
        self.assertIsInstance(f1['answer_sentence_flagged_with_target'], bool)
        self.assertTrue(0.0 <= f1['target_score'] <= 1.0)

    def test_summary_contains_no_answer_text(self):
        text = json.dumps(self.summary)
        for word in ('without telling you', 'Denver', 'Colorado', 'We may update'):
            self.assertNotIn(word, text)

    def test_documents_are_marked_fictional(self):
        for name in ('document_E.txt', 'document_F.txt'):
            self.assertIn('fictional', (ROOT / 'examples/study' / name).read_text(encoding='utf-8'))


if __name__ == '__main__':
    unittest.main()
