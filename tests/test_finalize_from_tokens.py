"""Session 09: {{FROM:...}} tokens and the trials table in scripts/finalize_report.py."""
import json
import tempfile
import unittest
from pathlib import Path

from clauses.session_v2 import run_trial_v2
from scripts.finalize_report import finalize, from_value

MODEL = 'c' * 64
REPO = 'https://github.com/Niveda-227/ClauseGuard'
TASKS = {'G1': {'document': 'd', 'prompt': 'p'}, 'H1': {'document': 'd', 'prompt': 'p'}}
SCAFFOLD = """---
north_star:
  value: {{AUTO_VALUE}}
  previous: {{AUTO_PREVIOUS}}
---
Honest marks per 100 sentences: {{FROM:experiments/session09/hint.json#honest.marks_per_100_sentences}}.
Share: {{FROM:experiments/session09/hint.json#honest.share|%1}}%. Decision: {{FROM:experiments/session09/hint.json#decision}}.
First group: {{FROM:experiments/session09/hint.json#groups.1.n|2}}.
Participants: {{AUTO_PARTICIPANT_IDS}}.

{{AUTO_TRIALS_TABLE}}

{{AUTO_CONTRIBUTIONS}}
"""


def ask(*answers):
    it = iter(answers)
    return lambda prompt='': next(it)


def clock(*times):
    it = iter(times)
    return lambda: next(it)


class FromTokenTests(unittest.TestCase):
    def setUp(self):
        self.root = Path(tempfile.mkdtemp())
        (self.root / 'reports/facts').mkdir(parents=True)
        (self.root / 'experiments/session09').mkdir(parents=True)
        (self.root / 'reports/session08.md').write_text('---\nnorth_star:\n  value: 100.00\n  previous: 100.00\n---\n')
        (self.root / 'experiments/session09/hint.json').write_text(json.dumps({
            'honest': {'marks_per_100_sentences': 31.65, 'share': 0.5065},
            'decision': 'RECONSIDER the list in Session 10', 'groups': [{'n': 1}, {'n': 2.5}]}))
        (self.root / 'experiments/session09/old.json').write_text(json.dumps({'superseded_by': 'x', 'a': 1}))
        self.facts = {
            'repo_url': REPO, 'protocol': 'sep29_v2', 'branch_protection_verified': True,
            'outside_user_evidence_reviewed': True, 'contributions_verified': True,
            'shipped_evidence_urls': [f'{REPO}/pull/68'], 'user_change_evidence_urls': [f'{REPO}/issues/66'],
            'number_sources': ['experiments/session09/hint.json'],
            'members': {n: {'github': h, 'completed_work': 'Did real work.', 'evidence_urls': [f'{REPO}/issues/63']}
                        for n, h in (('Ameer', 'sohail-umd'), ('Hemanth', 'hreddy14'), ('Jayakrishna', 'Jayakrishna-Reddy'),
                                     ('Niveda', 'Niveda-227'), ('Ankan', 'royak747'))},
        }
        self.write_facts()
        (self.root / 'reports/session09.md').write_text(SCAFFOLD)
        out = self.root / 'evidence/session09/tasks.csv'
        common = dict(output=out, observer='OBS01', tasks=TASKS, say=lambda *a: None)
        run_trial_v2(participant='U011', task='G1', condition='clauseguard', interface='web', model_id=MODEL,
                     ask=ask('yes', 'yes', '', '', 'x', 'yes', ''), clock=clock(0.0, 61.25), **common)
        run_trial_v2(participant='U011', task='H1', condition='manual', interface='text_editor', model_id=MODEL,
                     ask=ask('yes', 'yes', '', '', 'x', 'no', ''), clock=clock(0.0, 90.5), **common)

    def write_facts(self):
        (self.root / 'reports/facts/session09.json').write_text(json.dumps(self.facts))

    def test_tokens_are_filled_from_the_json_file(self):
        finalize(self.root, '09', model_id=MODEL)
        text = (self.root / 'reports/session09.md').read_text()
        self.assertIn('Honest marks per 100 sentences: 31.65.', text)
        self.assertIn('Share: 50.7%.', text)  # 0.5065 x 100 = 50.65, rounded half up
        self.assertIn('Decision: RECONSIDER the list in Session 10.', text)
        self.assertIn('First group: 2.50.', text)
        self.assertIn('Participants: U011.', text)
        self.assertIn('| U011 | G1 | ClauseGuard | web | yes | 61.25 |', text)
        self.assertIn('| U011 | H1 | manual | text_editor | no | 90.5 |', text)
        self.assertNotIn('{{', text)

    def test_a_source_must_be_listed_in_number_sources(self):
        self.facts['number_sources'] = []
        self.write_facts()
        with self.assertRaisesRegex(ValueError, 'number_sources'):
            finalize(self.root, '09', model_id=MODEL)

    def test_missing_keys_superseded_files_and_bad_formats_are_refused(self):
        sources = ['experiments/session09/hint.json', 'experiments/session09/old.json']
        with self.assertRaisesRegex(ValueError, "no key 'nope'"):
            from_value(self.root, sources[0], 'honest.nope', False, None, sources)
        with self.assertRaisesRegex(ValueError, 'superseded'):
            from_value(self.root, sources[1], 'a', False, None, sources)
        with self.assertRaisesRegex(ValueError, 'not a number or a text'):
            from_value(self.root, sources[0], 'honest', False, None, sources)
        with self.assertRaisesRegex(ValueError, 'value is text'):
            from_value(self.root, sources[0], 'decision', False, '1', sources)
        with self.assertRaisesRegex(ValueError, 'not a JSON file'):
            from_value(self.root, '../outside.json', 'a', False, None, ['../outside.json'])

    def test_a_key_that_contains_a_dot_is_found(self):
        (self.root / 'experiments/session09/cue.json').write_text(json.dumps({'margins': {'0.05': {'honest': {'n': 6}}}}))
        sources = ['experiments/session09/cue.json']
        self.assertEqual(from_value(self.root, sources[0], 'margins.0.05.honest.n', False, None, sources), '6')
        with self.assertRaisesRegex(ValueError, 'no key'):
            from_value(self.root, sources[0], 'margins.0.10.honest.n', False, None, sources)

    def test_an_unknown_token_is_refused(self):
        path = self.root / 'reports/session09.md'
        path.write_text(SCAFFOLD + '{{FROM:experiments/session09/hint.json}}\n')
        with self.assertRaisesRegex(ValueError, 'Unknown or unfilled'):
            finalize(self.root, '09', model_id=MODEL)


if __name__ == '__main__':
    unittest.main()
