import json
import re
import shutil
import tempfile
import unittest
from pathlib import Path

from clauses.session_v2 import run_trial_v2
from scripts.finalize_report import finalize

ROOT = Path(__file__).resolve().parents[1]
MODEL = 'b' * 64
REPO = 'https://github.com/Niveda-227/ClauseGuard'
TASKS = {'C1': {'document': 'd', 'prompt': 'p'}, 'D1': {'document': 'd', 'prompt': 'p'}}


def ask(*answers):
    it = iter(answers)
    return lambda prompt='': next(it)


def clock(*times):
    it = iter(times)
    return lambda: next(it)


class FinalizeReportTests(unittest.TestCase):
    def setUp(self):
        self.root = Path(tempfile.mkdtemp())
        (self.root / 'reports/facts').mkdir(parents=True)
        (self.root / 'reports/session04.md').write_text('---\nnorth_star:\n  value: 0.00\n  previous: null\n---\n')
        text = (ROOT / 'reports/session05.md').read_text()
        self.scaffold = text
        (self.root / 'reports/session05.md').write_text(re.sub(r'<<HUMAN:?[^>]*>>', 'written by hand', text))
        facts = json.loads((ROOT / 'reports/facts/session05.json').read_text())
        facts.update(branch_protection_verified=True, outside_user_evidence_reviewed=True, contributions_verified=True)
        facts['shipped_evidence_urls'] = [f'{REPO}/pull/{n}' for n in (18, 19, 20)]
        facts['user_change_evidence_urls'] = [f'{REPO}/issues/25']
        for m in facts['members'].values():
            m['completed_work'] = 'Did real work.'
            m['evidence_urls'] = [f'{REPO}/issues/15', f'{REPO}/pull/18']
        (self.root / 'reports/facts/session05.json').write_text(json.dumps(facts))

    def add_trials(self):
        out = self.root / 'evidence/session05/tasks.csv'
        common = dict(output=out, observer='OBS01', tasks=TASKS, say=lambda *a: None)
        run_trial_v2(participant='U002', task='C1', condition='clauseguard', interface='desktop', model_id=MODEL,
                     ask=ask('yes', 'yes', '', '', 'x', 'yes', ''), clock=clock(0.0, 40.0), **common)
        run_trial_v2(participant='U002', task='D1', condition='manual', interface='text_editor', model_id=MODEL,
                     ask=ask('yes', 'yes', '', '', 'x', 'no', ''), clock=clock(0.0, 90.0), **common)

    def test_refuses_while_human_placeholders_remain(self):
        (self.root / 'reports/session05.md').write_text(self.scaffold)
        self.add_trials()
        with self.assertRaisesRegex(ValueError, 'placeholder'):
            finalize(self.root, '05', model_id=MODEL)

    def test_refuses_a_single_bare_table_placeholder(self):
        self.add_trials()
        path = self.root / 'reports/session05.md'
        path.write_text(path.read_text().replace('written by hand', '<<HUMAN>>', 1))
        with self.assertRaisesRegex(ValueError, 'placeholder'):
            finalize(self.root, '05', model_id=MODEL)

    def test_refuses_without_evidence(self):
        with self.assertRaisesRegex(ValueError, 'does not exist'):
            finalize(self.root, '05', model_id=MODEL)

    def test_refuses_unverified_flags(self):
        self.add_trials()
        facts = json.loads((self.root / 'reports/facts/session05.json').read_text())
        facts['contributions_verified'] = False
        (self.root / 'reports/facts/session05.json').write_text(json.dumps(facts))
        with self.assertRaisesRegex(ValueError, 'contributions_verified'):
            finalize(self.root, '05', model_id=MODEL)

    def test_refuses_placeholder_links(self):
        self.add_trials()
        with self.assertRaises(ValueError):
            finalize(self.root, '05', ROOT / 'reports/facts/session05.json', model_id=MODEL)

    def test_refuses_model_mismatch(self):
        self.add_trials()
        with self.assertRaisesRegex(ValueError, 'different model'):
            finalize(self.root, '05', model_id='c' * 64)

    def test_fills_report_from_real_records(self):
        self.add_trials()
        tokens = finalize(self.root, '05', model_id=MODEL)
        text = (self.root / 'reports/session05.md').read_text()
        self.assertEqual(tokens['AUTO_VALUE'], '100.00')
        self.assertEqual(tokens['AUTO_PREVIOUS'], '0.00')
        self.assertIn('value: 100.00', text)
        self.assertIn('previous: 0.00', text)
        self.assertIn('- Ankan (Operations): Did real work.', text)
        self.assertIn('[PR #18]', text)
        self.assertNotIn('{{', text)
        self.assertTrue((self.root / 'evidence/session05/summary.json').exists())
        self.assertTrue((self.root / 'private/session05.before-finalization.md').exists())


if __name__ == '__main__':
    unittest.main()
