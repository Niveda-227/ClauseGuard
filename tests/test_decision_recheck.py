"""Tests for scripts/decision_recheck.py on a small made-up repository."""
import csv
import json
import shutil
import tempfile
import unittest
from pathlib import Path

from scripts.decision_recheck import MIN_PARTICIPANTS, RecheckError, run, to_markdown

ROOT = Path(__file__).resolve().parents[1]
FIELDS = ['recorded_at_utc', 'participant_id', 'task_id', 'condition', 'correct', 'seconds',
          'limit_seconds', 'model_id', 'protocol_version']


def make_repo(results, sha='a' * 64, honest=0.68, baseline=0.25):
    """results: {session: [(participant, condition, correct, seconds), ...]}"""
    root = Path(tempfile.mkdtemp())
    (root / 'docs/decisions').mkdir(parents=True)
    shutil.copy(ROOT / 'docs/decisions/midpoint_rule.json', root / 'docs/decisions/midpoint_rule.json')
    for rel, data in {
        'experiments/session05/threshold_cv.json': {'leave_one_company_out_HONEST': {'macro_f1': honest}},
        'experiments/session04/baseline/metrics.json': {'macro_f1_8': baseline},
        'artifacts/selected.json': {'artifact_sha256': sha},
        'experiments/session07/tuned/metrics.json': {'model_id': sha},
    }.items():
        (root / rel).parent.mkdir(parents=True, exist_ok=True)
        (root / rel).write_text(json.dumps(data))
    for session, rows in results.items():
        path = root / f'evidence/session{session}/tasks.csv'
        path.parent.mkdir(parents=True)
        with path.open('w', newline='') as f:
            w = csv.DictWriter(f, fieldnames=FIELDS)
            w.writeheader()
            for p, cond, ok, sec in rows:
                w.writerow({'recorded_at_utc': '2026-10-01T00:00:00+00:00', 'participant_id': p, 'task_id': 'E1',
                            'condition': cond, 'correct': int(ok), 'seconds': sec, 'limit_seconds': 180,
                            'model_id': sha if cond == 'clauseguard' else 'manual', 'protocol_version': 'sep29_v2'})
    return root


def people(n, cg_ok=True, manual_ok=True, start=10):
    rows = []
    for i in range(n):
        p = f'U{start + i:03d}'
        rows += [(p, 'clauseguard', cg_ok, 60), (p, 'manual', manual_ok, 90)]
    return rows


class DecisionRecheckTests(unittest.TestCase):
    def test_keep_when_enough_people_and_no_problem(self):
        r = run(make_repo({'07': people(MIN_PARTICIPANTS)}), 0, 'notes')
        self.assertEqual(r['outcome'], 'KEEP THE PRODUCT DIRECTION')

    def test_not_enough_participants(self):
        r = run(make_repo({'07': people(MIN_PARTICIPANTS - 1)}), 0, 'notes')
        self.assertEqual(r['outcome'], 'NOT ENOUGH PARTICIPANTS')

    def test_change_when_clauseguard_is_far_below_manual(self):
        r = run(make_repo({'07': people(MIN_PARTICIPANTS, cg_ok=False)}), 0, 'notes')
        self.assertEqual(r['outcome'], 'CHANGE INTERFACE OR JOB')

    def test_change_when_anyone_was_misled_by_wrong_tags(self):
        r = run(make_repo({'07': people(MIN_PARTICIPANTS)}), 1, 'notes')
        self.assertEqual(r['outcome'], 'CHANGE INTERFACE OR JOB')

    def test_pivot_when_the_model_gate_fails(self):
        r = run(make_repo({'07': people(MIN_PARTICIPANTS)}, honest=0.30, baseline=0.25), 0, 'notes')
        self.assertEqual(r['outcome'], 'PIVOT')

    def test_late_answers_are_not_successes(self):
        rows = [(f'U{i:03d}', 'clauseguard', True, 200) for i in range(MIN_PARTICIPANTS)]
        rows += [(f'U{i:03d}', 'manual', True, 60) for i in range(MIN_PARTICIPANTS)]
        r = run(make_repo({'07': rows}), 0, 'notes')
        self.assertEqual(r['clauseguard']['successes'], 0)

    def test_sessions_are_pooled_and_listed(self):
        r = run(make_repo({'05': people(3, start=2), '06': people(3, start=20)}), 0, 'notes')
        self.assertEqual(r['participant_count'], 6)
        self.assertEqual([s['session'] for s in r['per_session']], ['05', '06'])

    def test_the_human_inputs_are_required(self):
        repo = make_repo({'07': people(MIN_PARTICIPANTS)})
        with self.assertRaises(RecheckError):
            run(repo, None, 'notes')
        with self.assertRaises(RecheckError):
            run(repo, 0, '<<which notes>>')

    def test_markdown_shows_the_outcome(self):
        text = to_markdown(run(make_repo({'07': people(MIN_PARTICIPANTS)}), 0, 'notes'))
        self.assertIn('**Outcome: KEEP THE PRODUCT DIRECTION**', text)


if __name__ == '__main__':
    unittest.main()
