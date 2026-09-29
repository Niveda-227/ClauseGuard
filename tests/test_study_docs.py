import json
import tempfile
import unittest
from pathlib import Path

from clauses.model import load
from scripts.check_study_docs import check

ROOT = Path(__file__).resolve().parents[1]
KEY = {
    'C1': {'target_category': 'Content removal', 'answer_sentence_starts_with': 'We may remove any photos'},
    'D1': {'target_category': 'Limitation of liability', 'answer_sentence_starts_with': 'Our total liability'},
}


class StudyDocTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.bundle = load()
        cls.tmp = Path(tempfile.mkdtemp())

    def write_key(self, key):
        path = self.tmp / 'key.json'
        path.write_text(json.dumps(key))
        return path

    def test_both_tasks_are_fair(self):
        out = check(ROOT / 'examples/study/tasks_v2.json', self.write_key(KEY), self.bundle)
        self.assertTrue(all(t['answer_sentence_flagged_with_target'] for t in out['tasks']))

    def test_summary_contains_no_answer_text(self):
        out = json.dumps(check(ROOT / 'examples/study/tasks_v2.json', self.write_key(KEY), self.bundle))
        self.assertNotIn('We may remove', out)
        self.assertNotIn('total liability', out)

    def test_missing_answer_sentence_is_an_error(self):
        bad = {**KEY, 'C1': {**KEY['C1'], 'answer_sentence_starts_with': 'No such sentence'}}
        with self.assertRaises(ValueError):
            check(ROOT / 'examples/study/tasks_v2.json', self.write_key(bad), self.bundle)


if __name__ == '__main__':
    unittest.main()
