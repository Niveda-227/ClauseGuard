"""Session 12: one table of every outside-user session (scripts/study_summary.py)."""
import csv
import json
import tempfile
import unittest
from pathlib import Path

from scripts import study_summary

ROOT = Path(__file__).resolve().parents[1]
HEADER = ['recorded_at_utc', 'participant_id', 'task_id', 'condition', 'correct', 'seconds', 'limit_seconds', 'model_id', 'protocol_version']


def write(root, session, rows):
    folder = Path(root) / 'evidence' / f'session{session}'
    folder.mkdir(parents=True)
    with (folder / 'tasks.csv').open('w', newline='') as f:
        w = csv.writer(f)
        w.writerow(HEADER)
        w.writerows(rows)


class StudySummaryTests(unittest.TestCase):
    def test_success_needs_correct_and_within_the_limit_and_the_pilot_is_not_added(self):
        with tempfile.TemporaryDirectory() as d:
            (Path(d) / 'examples/study').mkdir(parents=True)
            (Path(d) / 'examples/study/tasks_v9.json').write_text(json.dumps({'tasks': {
                'X1': {'document': 'examples/fresh/a.txt'}, 'Y1': {'document': 'examples/fresh/b.txt'}}}))
            write(d, '04', [['t', 'U001', 'A1', 'manual', '1', '200', '180', 'manual', 'old_v1']])
            write(d, '05', [['t', 'U002', 'X1', 'clauseguard', '1', '50', '180', 'm', 'sep29_v2'],
                            ['t', 'U002', 'Y1', 'manual', '1', '181', '180', 'manual', 'sep29_v2'],
                            ['t', 'U003', 'Y1', 'clauseguard', '0', '40', '180', 'm', 'sep29_v2'],
                            ['t', 'U003', 'X1', 'manual', '1', '60', '180', 'manual', 'sep29_v2']])
            r = study_summary.build(d)
        t = r['totals']
        self.assertEqual((t['sessions'], t['participants'], t['clauseguard_successful'], t['manual_successful']), (1, 2, 1, 1))
        self.assertEqual(r['not_counted'], ['04'])
        self.assertEqual(r['sessions'][1]['documents'], 'real')
        self.assertEqual(r['sessions'][0]['documents'], 'fictional')
        self.assertIn('2 outside participants in 1 sessions', t['summary'])

    def test_the_committed_records_add_up(self):
        r = study_summary.build(ROOT)
        counted = [s for s in r['sessions'] if s['protocol'] == ['sep29_v2']]
        self.assertEqual(r['totals']['clauseguard_tasks'], sum(s['clauseguard_tasks'] for s in counted))
        self.assertEqual(r['totals']['participants'], len({p for s in counted for p in s['participants']}))
        self.assertIn('04', r['not_counted'])

    def test_the_table_has_one_row_per_session_and_no_task_text(self):
        r = study_summary.build(ROOT)
        md = study_summary.to_markdown(r)
        self.assertEqual(sum(l.startswith('| ') and l[2:4].isdigit() for l in md.splitlines()), len(r['sessions']))
        self.assertNotIn('prompt', json.dumps(r))


if __name__ == '__main__':
    unittest.main()
