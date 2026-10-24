"""Session 08 explanation check (clauses/explain_check.py) and the Session 08 evidence checks."""
import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from clauses.explain_check import CARDS, load_cards, load_key, run_check, summarize
from clauses.schema import EXPLANATIONS
from scripts.check_evidence import FIELDS, check

KEY = {'X1': 'b', 'X2': 'c', 'X3': 'a', 'X4': 'b'}


def scripted(*answers):
    it = iter(answers)
    return lambda prompt='': next(it)


class ExplainCheckTests(unittest.TestCase):
    def setUp(self):
        self.items = load_cards()
        self.out = Path(tempfile.mkdtemp())

    def test_cards_show_the_apps_explanations_word_for_word(self):
        for item in self.items:
            self.assertEqual(item['explanation'], EXPLANATIONS[item['category']])

    def test_public_cards_contain_no_answers(self):
        text = CARDS.read_text(encoding='utf-8')
        self.assertNotIn('"answer', text)
        self.assertNotIn('"correct', text)

    def test_record_is_scored_with_the_private_key(self):
        rec = run_check(self.out, 'U900', 'OBS01', self.items, KEY,
                        ask=scripted('yes', 'b', 'a', 'a', 'skip', 'mixed up law and courts'), say=lambda *a: None)
        self.assertEqual(rec['answers'], {'X1': 'b', 'X2': 'a', 'X3': 'a', 'X4': None})
        self.assertEqual(rec['score'], 2)
        self.assertEqual(rec['answered'], 3)
        saved = json.loads((self.out / 'U900_explain_v1.json').read_text())
        self.assertTrue(saved['outside_team_and_consented'])

    def test_no_consent_records_nothing(self):
        with self.assertRaises(ValueError):
            run_check(self.out, 'U900', 'OBS01', self.items, KEY, ask=scripted('no'), say=lambda *a: None)
        self.assertFalse(list(self.out.iterdir()))

    def test_existing_record_is_never_overwritten(self):
        (self.out / 'U900_explain_v1.json').write_text('{}')
        with self.assertRaises(ValueError):
            run_check(self.out, 'U900', 'OBS01', self.items, KEY, ask=scripted('yes'), say=lambda *a: None)
        self.assertEqual((self.out / 'U900_explain_v1.json').read_text(), '{}')

    def test_names_are_refused_as_codes(self):
        with self.assertRaises(ValueError):
            run_check(self.out, 'Jane Doe', 'OBS01', self.items, KEY, ask=scripted('yes'), say=lambda *a: None)

    def test_the_key_is_never_printed(self):
        shown = []
        run_check(self.out, 'U901', 'OBS01', self.items, KEY,
                  ask=scripted('yes', 'a', 'a', 'a', 'a', ''), say=lambda *a: shown.append(' '.join(map(str, a))))
        self.assertFalse([line for line in shown if 'correct' in line.lower() or 'key' in line.lower()])

    def test_incomplete_key_is_refused(self):
        path = self.out / 'key.json'
        path.write_text(json.dumps({'answers': {'X1': 'b'}}))
        with self.assertRaises(ValueError):
            load_key(path, self.items)

    def test_summary_counts_per_card(self):
        run_check(self.out, 'U900', 'OBS01', self.items, KEY, ask=scripted('yes', 'b', 'c', 'a', 'b', ''), say=lambda *a: None)
        run_check(self.out, 'U901', 'OBS01', self.items, KEY, ask=scripted('yes', 'a', 'c', 'a', 'skip', ''), say=lambda *a: None)
        s = summarize(self.out, self.items)
        self.assertEqual(s['per_card']['X1'], {'category': 'Jurisdiction', 'correct': 1, 'answered': 2})
        self.assertEqual(s['per_card']['X4']['answered'], 1)
        self.assertEqual(s['total_correct'], 6)  # U900: 4 of 4, U901: 2 of 3


class Session08EvidenceCheckTests(unittest.TestCase):
    def make_repo(self, interface='web', explain=('U008', 'U009')):
        root = Path(tempfile.mkdtemp())
        (root / 'artifacts').mkdir()
        model = b'model'
        (root / 'artifacts/selected.joblib').write_bytes(model)
        sha = hashlib.sha256(model).hexdigest()
        folder = root / 'evidence/session08'
        folder.mkdir(parents=True)
        lines = [','.join(FIELDS)]
        for p, task, cond in (('U008', 'E1', 'clauseguard'), ('U008', 'F1', 'manual'),
                              ('U009', 'E1', 'manual'), ('U009', 'F1', 'clauseguard')):
            lines.append(f"2026-10-24T15:00:00+00:00,{p},{task},{cond},1,60.0,180,{sha if cond == 'clauseguard' else 'manual'},sep29_v2")
            (folder / f'{p}_{task}_{cond}_sep29_v2.json').write_text(json.dumps({
                'record': {'participant_id': p, 'task_id': task, 'condition': cond},
                'outside_team_and_consented': True, 'interface': interface if cond == 'clauseguard' else 'text_editor'}))
        (folder / 'tasks.csv').write_text('\n'.join(lines) + '\n')
        (folder / 'session_notes.md').write_text('## U008\n## U009\n')
        (folder / 'README.md').write_text('# Evidence\n')
        for p in explain:
            (folder / f'{p}_explain_v1.json').write_text(json.dumps({'participant_id': p, 'outside_team_and_consented': True}))
        return root

    def status(self, results, part):
        return [s for s, name, _ in results if part in name][0]

    def test_clean_session_08_folder_passes(self):
        results = check(self.make_repo(), '08')
        self.assertFalse([r for r in results if r[0] == 'FAIL'], results)
        self.assertEqual(self.status(results, 'used the web app'), 'PASS')
        self.assertEqual(self.status(results, 'every participant did the explanation check'), 'PASS')

    def test_desktop_trials_are_flagged_for_explanation(self):
        self.assertEqual(self.status(check(self.make_repo(interface='desktop'), '08'), 'used the web app'), 'WARN')

    def test_missing_explanation_check_is_a_warning(self):
        results = check(self.make_repo(explain=('U008',)), '08')
        self.assertEqual(self.status(results, 'every participant did the explanation check'), 'WARN')

    def test_explanation_record_from_a_stranger_fails(self):
        results = check(self.make_repo(explain=('U008', 'U009', 'U777')), '08')
        self.assertEqual(self.status(results, 'belong to this week'), 'FAIL')


if __name__ == '__main__':
    unittest.main()
