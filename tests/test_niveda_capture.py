import importlib.util
import json
import tempfile
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]

from unittest.mock import patch
from clauses.session_capture import capture
from clauses.task_timer import run_trial
from clauses.study import summarize

class CaptureTests(unittest.TestCase):
    def test_interface_mismatch_prevents_session(self):
        with tempfile.TemporaryDirectory() as d:
            with self.assertRaises(ValueError):capture(Path(d)/'tasks.csv','TEST01','A1','manual','desktop','OBS01')
            self.assertFalse(list(Path(d).iterdir()))
    def test_context_added_without_breaking_csv_summary(self):
        # Synthetic test trial lives only in a temporary directory.
        with tempfile.TemporaryDirectory() as d:
            output=Path(d)/'tasks.csv'
            replies=iter(['yes','','Test answer','yes','Test-only observation'])
            times=iter([0,40])
            def runner(*args):return run_trial(*args,ask=lambda _:next(replies),clock=lambda:next(times))
            with patch('clauses.session_capture.load',return_value={'model_id':'a'*64}):
                capture(output,'TEST01','A1','clauseguard','cli_html','OBS01',runner=runner)
            raw=json.loads(next(Path(d).glob('*.json')).read_text())
            self.assertEqual(raw['interface'],'cli_html');self.assertEqual(raw['observer_id'],'OBS01')
            self.assertTrue(raw['outside_team_and_consented'])
            self.assertEqual(summarize(output)['groups'][0]['success_percent'],100)
    def test_existing_trial_cannot_be_overwritten(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d);trial=p/'TEST01_A1_manual_sep22_v1.json';trial.write_text('{}')
            with self.assertRaises(ValueError):capture(p/'tasks.csv','TEST01','A1','manual','text_editor','OBS01')
            self.assertEqual(trial.read_text(),'{}')
