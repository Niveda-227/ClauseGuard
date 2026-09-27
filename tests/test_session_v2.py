import json
import tempfile
import unittest
from pathlib import Path

from clauses.session_v2 import PROTOCOL, load_tasks, run_trial_v2
from clauses.study import summarize

MODEL = 'a' * 64
TASKS = {'C1': {'document': 'examples/study/document_C.txt', 'prompt': 'Find the removal sentence.'}}


def scripted(*answers):
    it = iter(answers)
    return lambda prompt='': next(it)


def fake_clock(*times):
    it = iter(times)
    return lambda: next(it)


class SessionV2Tests(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.out = self.tmp / 'tasks.csv'

    def run_ok(self, answers, times=(100.0, 112.5), **kw):
        args = dict(output=self.out, participant='U002', task='C1', condition='clauseguard',
                    interface='desktop', observer='OBS01', model_id=MODEL, tasks=TASKS,
                    ask=scripted(*answers), clock=fake_clock(*times), say=lambda *a: None)
        args.update(kw)
        return run_trial_v2(**args)

    def test_clock_excludes_answer_entry(self):
        # consent, restated, start, stop, answer, correct, notes
        row = self.run_ok(['yes', 'yes', '', '', 'the removal sentence', 'yes', 'used filter'])
        self.assertEqual(row['seconds'], 12.5)
        self.assertEqual(row['protocol_version'], PROTOCOL)
        record = json.loads((self.tmp / f'U002_C1_clauseguard_{PROTOCOL}.json').read_text())
        self.assertEqual(record['task_prompt'], 'Find the removal sentence.')
        self.assertTrue(record['prompt_restated_correctly'])
        self.assertEqual(record['prompt_readings'], 1)
        self.assertEqual(record['interface'], 'desktop')

    def test_prompt_reread_is_counted(self):
        self.run_ok(['yes', 'no', 'yes', '', '', 'answer', 'no', ''])
        record = json.loads((self.tmp / f'U002_C1_clauseguard_{PROTOCOL}.json').read_text())
        self.assertEqual(record['prompt_readings'], 2)

    def test_unconfirmed_prompt_records_nothing(self):
        with self.assertRaises(ValueError):
            self.run_ok(['yes', 'no', 'no', 'no'])
        self.assertFalse(self.out.exists())

    def test_no_consent_records_nothing(self):
        with self.assertRaises(ValueError):
            self.run_ok(['no'])
        self.assertFalse(self.out.exists())

    def test_late_correct_answer_is_unsuccessful(self):
        self.run_ok(['yes', 'yes', '', '', 'answer', 'yes', ''], times=(0.0, 200.0))
        group = summarize(self.out)['groups'][0]
        self.assertEqual(group['successful_tasks'], 0)

    def test_interface_condition_pairing_enforced(self):
        with self.assertRaises(ValueError):
            self.run_ok(['yes'], condition='manual', interface='desktop')

    def test_unknown_task_rejected(self):
        with self.assertRaises(ValueError):
            self.run_ok(['yes'], task='Z9')

    def test_duplicate_trial_refused(self):
        self.run_ok(['yes', 'yes', '', '', 'a', 'yes', ''])
        with self.assertRaises(ValueError):
            self.run_ok(['yes', 'yes', '', '', 'a', 'yes', ''])

    def test_public_task_bank_rejects_answers(self):
        path = self.tmp / 'bank.json'
        path.write_text(json.dumps({'tasks': {'C1': {'document': 'd', 'prompt': 'p', 'answer': 'x'}}}))
        with self.assertRaises(ValueError):
            load_tasks(path)


if __name__ == '__main__':
    unittest.main()
