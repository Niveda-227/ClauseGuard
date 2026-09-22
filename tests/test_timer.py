"""Mock observations stay in temporary directories; they are not user evidence."""
import json
import tempfile
import unittest
from pathlib import Path
from clauses.task_timer import run_trial
from clauses.study import summarize


class TimerTests(unittest.TestCase):
    def test_measured_duration_and_raw_record(self):
        with tempfile.TemporaryDirectory() as d:
            replies = iter(['yes', '', 'Arbitration is required.', 'maybe', 'yes', 'Filter was easy to find.'])
            times = iter([100.0, 141.5])
            p = Path(d) / 'tasks.csv'
            r = run_trial(p, 'TEST01', 'A1', 'clauseguard', 'a'*64,
                          ask=lambda _: next(replies), clock=lambda: next(times))
            self.assertEqual(r['seconds'], 41.5)
            self.assertEqual(summarize(p)['groups'][0]['success_percent'], 100)
            raw = json.loads(next(Path(d).glob('*.json')).read_text())
            self.assertEqual(raw['participant_answer'], 'Arbitration is required.')
            with self.assertRaises(ValueError):
                run_trial(p, 'TEST01', 'A1', 'clauseguard', 'a'*64)

    def test_declining_consent_creates_no_evidence(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / 'tasks.csv'
            with self.assertRaises(ValueError):
                run_trial(p, 'TEST01', 'A1', 'manual', 'manual', ask=lambda _: 'no')
            self.assertEqual(list(Path(d).iterdir()), [])

    def test_late_correct_answer_is_unsuccessful(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / 'tasks.csv'
            replies = iter(['yes', '', 'Correct answer', 'yes', ''])
            times = iter([0, 181])
            run_trial(p, 'TEST01', 'A1', 'manual', 'manual',
                      ask=lambda _: next(replies), clock=lambda: next(times))
            self.assertEqual(summarize(p)['groups'][0]['success_percent'], 0)
