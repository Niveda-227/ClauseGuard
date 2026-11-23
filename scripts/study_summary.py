"""One table of every outside-user session so far, from the committed task records (Session 12, Niveda).

    python scripts/study_summary.py

Reads evidence/sessionNN/tasks.csv for every session folder (it never edits them) and the public
task banks in examples/study/ (to tell fictional documents from real ones). Writes
experiments/session12/study_summary.json and study_summary.md: per session, the participants,
ClauseGuard and manual tasks done correctly within the limit, and the median seconds; and the
totals over the sessions that used protocol sep29_v2 (the Session 04 pilot used another protocol
and a longer task, so it is listed but not added in). A task counts as successful only if it was
correct AND within the time limit, exactly as clauses.study.summarize counts it.

These are descriptive records of small samples, not a population estimate: the participants
were not sampled at random, each did one task with and one without the app, and the documents
and tasks changed from session to session.
"""
import csv
import json
import statistics
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROTOCOL = 'sep29_v2'
OUT_JSON = 'experiments/session12/study_summary.json'
OUT_MD = 'experiments/session12/study_summary.md'


def task_documents(root):
    docs = {}
    for bank in sorted((Path(root) / 'examples/study').glob('tasks_v*.json')):
        for task_id, task in json.loads(bank.read_text(encoding='utf-8'))['tasks'].items():
            docs[task_id] = task['document']
    return docs


def median(values):
    return round(statistics.median(values), 1) if values else None


def summarize_session(name, rows, docs):
    def ok(r):
        return r['correct'] == '1' and float(r['seconds']) <= float(r['limit_seconds'])
    cg = [r for r in rows if r['condition'] == 'clauseguard']
    manual = [r for r in rows if r['condition'] == 'manual']
    tasks = sorted({r['task_id'] for r in rows})
    real = [t for t in tasks if docs.get(t, '').startswith('examples/fresh/')]
    return {
        'session': name, 'protocol': sorted({r['protocol_version'] for r in rows}),
        'participants': sorted({r['participant_id'] for r in rows}), 'tasks': tasks,
        'documents': 'real' if real and len(real) == len(tasks) else 'fictional',
        'clauseguard_tasks': len(cg), 'clauseguard_successful': sum(ok(r) for r in cg),
        'manual_tasks': len(manual), 'manual_successful': sum(ok(r) for r in manual),
        'clauseguard_median_seconds': median([float(r['seconds']) for r in cg]),
        'manual_median_seconds': median([float(r['seconds']) for r in manual]),
    }


def build(root):
    root = Path(root)
    docs = task_documents(root)
    sessions = []
    for folder in sorted((root / 'evidence').glob('session[0-9][0-9]')):
        path = folder / 'tasks.csv'
        if not path.exists():
            continue
        with path.open(newline='', encoding='utf-8') as f:
            rows = list(csv.DictReader(f))
        if rows:
            sessions.append(summarize_session(folder.name.replace('session', ''), rows, docs))
    counted = [s for s in sessions if s['protocol'] == [PROTOCOL]]
    people = sorted({p for s in counted for p in s['participants']})
    totals = {k: sum(s[k] for s in counted) for k in ('clauseguard_tasks', 'clauseguard_successful', 'manual_tasks', 'manual_successful')}
    totals.update({
        'sessions': len(counted), 'first_session': counted[0]['session'] if counted else None,
        'last_session': counted[-1]['session'] if counted else None,
        'participants': len(people),
        'sessions_on_real_documents': sum(s['documents'] == 'real' for s in counted),
        'clauseguard_success_percent': round(100 * totals['clauseguard_successful'] / totals['clauseguard_tasks'], 1) if totals['clauseguard_tasks'] else None,
        'manual_success_percent': round(100 * totals['manual_successful'] / totals['manual_tasks'], 1) if totals['manual_tasks'] else None,
    })
    totals['summary'] = (f"{totals['participants']} outside participants in {totals['sessions']} sessions "
                         f"(Sessions {totals['first_session']} to {totals['last_session']}): ClauseGuard "
                         f"{totals['clauseguard_successful']}/{totals['clauseguard_tasks']} tasks correct within the limit, "
                         f"manual {totals['manual_successful']}/{totals['manual_tasks']}")
    return {'protocol_counted': PROTOCOL, 'sessions': sessions, 'totals': totals,
            'not_counted': [s['session'] for s in sessions if s not in counted],
            'note': 'Descriptive records of small, non-random samples; each participant did one task with the app and one '
                    'without; documents and tasks changed between sessions. Not a population estimate.'}


def to_markdown(r):
    lines = ['# Outside-user sessions so far (Session 12 summary)', '',
             f"From `evidence/sessionNN/tasks.csv`. A task counts as successful only if correct and within the time limit. "
             f"Totals use the sessions run with protocol `{r['protocol_counted']}`.", '',
             '| Session | Protocol | Documents | Participants | ClauseGuard correct within limit | Manual correct within limit | Median seconds (ClauseGuard / manual) |',
             '|---|---|---|---|---:|---:|---|']
    for s in r['sessions']:
        lines.append(f"| {s['session']} | {', '.join(s['protocol'])} | {s['documents']} | {', '.join(s['participants'])} | "
                     f"{s['clauseguard_successful']}/{s['clauseguard_tasks']} | {s['manual_successful']}/{s['manual_tasks']} | "
                     f"{s['clauseguard_median_seconds']} / {s['manual_median_seconds']} |")
    t = r['totals']
    lines += ['', f"**Totals ({r['protocol_counted']}):** {t['summary']}.", '']
    if r['not_counted']:
        lines.append(f"Not added in: Session {', '.join(r['not_counted'])} (another protocol: the pilot).")
        lines.append('')
    lines += [r['note'], '']
    return '\n'.join(lines)


def main():
    r = build(ROOT)
    out = ROOT / OUT_JSON
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(r, indent=2) + '\n', encoding='utf-8')
    (ROOT / OUT_MD).write_text(to_markdown(r), encoding='utf-8')
    print(r['totals']['summary'])
    print(f'Wrote {OUT_JSON} and {OUT_MD}')
    return 0


if __name__ == '__main__':
    sys.exit(main())
