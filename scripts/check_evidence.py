"""Check a week's outside-user evidence before it is committed.

    python scripts/check_evidence.py --session 06

Checks evidence/sessionNN/ for:
  - tasks.csv: the recorder's schema, protocol sep29_v2 only, ClauseGuard trials ran the shipped model
  - one trial record (JSON) per row, with consent recorded, matching the row
  - participants are NEW: none of them appears in an earlier session's evidence
  - design: each participant did one task manually and the other with ClauseGuard
  - session_notes.md and README.md exist, with no unfilled << >> placeholders
  - privacy: no email addresses or phone numbers in any text file; screenshot names follow the pattern
Prints PASS / WARN / FAIL per check and exits 1 if anything FAILs. It changes nothing.
"""
import argparse
import csv
import hashlib
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FIELDS = ['recorded_at_utc', 'participant_id', 'task_id', 'condition', 'correct', 'seconds',
          'limit_seconds', 'model_id', 'protocol_version']
PROTOCOL = 'sep29_v2'
EMAIL = re.compile(r'[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}')
PHONE = re.compile(r'\(?\b[0-9]{3}\)?[ .-][0-9]{3}[ .-][0-9]{4}\b')
SHOT = re.compile(r'^\d{4}-\d{2}-\d{2}_U\d{3}_[A-Z]\d_(clauseguard|manual)(_\d+)?\.(png|jpg|jpeg)$')
TEXT_SUFFIXES = {'.md', '.csv', '.json', '.txt'}


def rows_of(path):
    with Path(path).open(newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        return reader.fieldnames, list(reader)


def check(root, session):
    root = Path(root)
    folder = root / f'evidence/session{session}'
    results = []

    def add(status, name, detail=''):
        results.append((status, name, detail))

    csv_path = folder / 'tasks.csv'
    if not csv_path.exists():
        add('FAIL', 'tasks.csv exists', f'{csv_path.relative_to(root)} not found')
        return results
    fields, rows = rows_of(csv_path)
    add('PASS' if fields == FIELDS else 'FAIL', 'tasks.csv has the recorder\'s columns', '' if fields == FIELDS else str(fields))
    if not rows:
        add('FAIL', 'tasks.csv has trials', 'no rows')
        return results
    add('PASS', 'tasks.csv has trials', f'{len(rows)} trials')

    bad_protocol = [r['participant_id'] for r in rows if r['protocol_version'] != PROTOCOL]
    add('FAIL' if bad_protocol else 'PASS', f'every trial uses protocol {PROTOCOL}', ', '.join(bad_protocol))
    shipped = hashlib.sha256((root / 'artifacts/selected.joblib').read_bytes()).hexdigest()
    other_model = [f"{r['participant_id']} {r['task_id']}" for r in rows
                   if r['condition'] == 'clauseguard' and r['model_id'] != shipped]
    add('FAIL' if other_model else 'PASS', 'ClauseGuard trials ran the shipped model', ', '.join(other_model))

    missing, mismatch, no_consent = [], [], []
    for r in rows:
        j = folder / f"{r['participant_id']}_{r['task_id']}_{r['condition']}_{r['protocol_version']}.json"
        if not j.exists():
            missing.append(j.name)
            continue
        data = json.loads(j.read_text(encoding='utf-8'))
        rec = data.get('record', {})
        if (rec.get('participant_id'), rec.get('task_id'), rec.get('condition')) != (r['participant_id'], r['task_id'], r['condition']):
            mismatch.append(j.name)
        if data.get('outside_team_and_consented') is not True:
            no_consent.append(j.name)
    add('FAIL' if missing else 'PASS', 'one trial record (JSON) per row', ', '.join(missing))
    add('FAIL' if mismatch else 'PASS', 'trial records match tasks.csv', ', '.join(mismatch))
    add('FAIL' if no_consent else 'PASS', 'consent recorded in every trial', ', '.join(no_consent))

    participants = sorted({r['participant_id'] for r in rows})
    earlier = {}
    for other in sorted((root / 'evidence').glob('session*/tasks.csv')):
        name = other.parent.name
        if name >= f'session{session}':
            continue
        for r in rows_of(other)[1]:
            earlier.setdefault(r['participant_id'], name)
    reused = [f'{p} (already in {earlier[p]})' for p in participants if p in earlier]
    add('FAIL' if reused else 'PASS', 'every participant is new this week', ', '.join(reused))

    design = []
    for p in participants:
        mine = [r for r in rows if r['participant_id'] == p]
        conds = sorted(r['condition'] for r in mine)
        tasks = sorted(r['task_id'] for r in mine)
        if conds != ['clauseguard', 'manual'] or len(set(tasks)) != 2:
            design.append(f'{p}: {", ".join(r["task_id"] + "/" + r["condition"] for r in mine)}')
    add('WARN' if design else 'PASS', 'each participant did one task manually and one with ClauseGuard',
        '; '.join(design) + (' (explain in session_notes.md)' if design else ''))

    for fname in ('session_notes.md', 'README.md'):
        f = folder / fname
        if not f.exists():
            add('FAIL', f'{fname} exists', 'missing')
            continue
        text = f.read_text(encoding='utf-8')
        left = re.findall(r'<<[^>]*>>', text)
        add('FAIL' if left else 'PASS', f'{fname} has no unfilled << >> placeholders', ', '.join(left[:5]))
        if fname == 'session_notes.md':
            absent = [p for p in participants if p not in text]
            add('FAIL' if absent else 'PASS', 'session_notes.md has a section for every participant', ', '.join(absent))

    leaks = []
    for f in sorted(folder.rglob('*')):
        if f.is_file() and f.suffix.lower() in TEXT_SUFFIXES:
            text = f.read_text(encoding='utf-8', errors='replace')
            for pattern, what in ((EMAIL, 'email'), (PHONE, 'phone number')):
                for m in pattern.findall(text):
                    leaks.append(f'{f.relative_to(folder)}: {what} "{m}"')
    add('FAIL' if leaks else 'PASS', 'no email addresses or phone numbers', '; '.join(leaks))

    shots = [f for f in (folder / 'screenshots').glob('*') if f.is_file()] if (folder / 'screenshots').exists() else []
    badnames = [f.name for f in shots if not SHOT.match(f.name)]
    add('FAIL' if badnames else 'PASS', 'screenshot names follow YYYY-MM-DD_U00X_TASK_condition.png', ', '.join(badnames))
    if shots:
        add('WARN', f'{len(shots)} screenshot(s): open every one yourself',
            'this script cannot see faces, names, usernames or notifications')
    else:
        add('WARN', 'no screenshots', 'fine if participants declined; say so in README.md')
    return results


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument('--session', required=True, help='Two digits, e.g. 06')
    a = p.parse_args(argv)
    if not re.fullmatch(r'\d{2}', a.session):
        p.error('Use two digits, e.g. --session 06')
    results = check(ROOT, a.session)
    for status, name, detail in results:
        print(f'{status:4s}  {name}' + (f'  -> {detail}' if detail and status != 'PASS' else ''))
    failed = any(s == 'FAIL' for s, _, _ in results)
    print('\nNOT READY: fix every FAIL before committing.' if failed else '\nEvidence folder is ready to commit.')
    return 1 if failed else 0


if __name__ == '__main__':
    sys.exit(main())
