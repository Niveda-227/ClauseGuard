import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from scripts.check_evidence import FIELDS, check

MODEL = b'pretend model bytes'
SHA = hashlib.sha256(MODEL).hexdigest()


def make_repo(rows, session='06', notes=None, earlier=None, extra=None):
    root = Path(tempfile.mkdtemp())
    (root / 'artifacts').mkdir()
    (root / 'artifacts/selected.joblib').write_bytes(MODEL)
    folder = root / f'evidence/session{session}'
    folder.mkdir(parents=True)
    lines = [','.join(FIELDS)]
    for p, task, cond, ok in rows:
        model = SHA if cond == 'clauseguard' else 'manual'
        lines.append(f'2026-10-03T15:00:00+00:00,{p},{task},{cond},{int(ok)},60.0,180,{model},sep29_v2')
        (folder / f'{p}_{task}_{cond}_sep29_v2.json').write_text(json.dumps({
            'record': {'participant_id': p, 'task_id': task, 'condition': cond},
            'outside_team_and_consented': True}))
    (folder / 'tasks.csv').write_text('\n'.join(lines) + '\n')
    people = sorted({r[0] for r in rows})
    (folder / 'session_notes.md').write_text(notes if notes is not None else '\n'.join(f'## {p}' for p in people))
    (folder / 'README.md').write_text('# Evidence\n')
    if earlier:
        e = root / 'evidence/session05'
        e.mkdir(parents=True)
        e.joinpath('tasks.csv').write_text(','.join(FIELDS) + '\n' +
                                           f'2026-09-27T15:00:00+00:00,{earlier},C1,manual,1,80,180,manual,sep29_v2\n')
    if extra:
        extra(folder)
    return root


def status(results, name_part):
    return [s for s, name, _ in results if name_part in name][0]


GOOD = [('U003', 'C1', 'clauseguard', True), ('U003', 'D1', 'manual', True),
        ('U004', 'C1', 'manual', False), ('U004', 'D1', 'clauseguard', True)]


class CheckEvidenceTests(unittest.TestCase):
    def test_clean_folder_has_no_failures(self):
        results = check(make_repo(GOOD, earlier='U002'), '06')
        self.assertFalse([r for r in results if r[0] == 'FAIL'], results)

    def test_reused_participant_fails(self):
        results = check(make_repo(GOOD, earlier='U003'), '06')
        self.assertEqual(status(results, 'participant is new'), 'FAIL')

    def test_email_in_notes_fails(self):
        results = check(make_repo(GOOD, notes='## U003\n## U004\ncontact jane.doe@umd.edu'), '06')
        self.assertEqual(status(results, 'email'), 'FAIL')

    def test_unfilled_placeholder_fails(self):
        results = check(make_repo(GOOD, notes='## U003\n## U004\n<<answer>>'), '06')
        self.assertEqual(status(results, 'session_notes.md has no unfilled'), 'FAIL')

    def test_missing_trial_record_fails(self):
        root = make_repo(GOOD, extra=lambda f: (f / 'U003_C1_clauseguard_sep29_v2.json').unlink())
        self.assertEqual(status(check(root, '06'), 'one trial record'), 'FAIL')

    def test_same_condition_twice_is_a_warning(self):
        rows = [('U003', 'C1', 'clauseguard', True), ('U003', 'D1', 'clauseguard', True)]
        self.assertEqual(status(check(make_repo(rows), '06'), 'one task manually'), 'WARN')

    def test_badly_named_screenshot_fails(self):
        def shots(folder):
            (folder / 'screenshots').mkdir()
            (folder / 'screenshots/Screenshot 2026-10-03 at 3.14.15 PM.png').write_bytes(b'x')
        self.assertEqual(status(check(make_repo(GOOD, extra=shots), '06'), 'screenshot names'), 'FAIL')


if __name__ == '__main__':
    unittest.main()
