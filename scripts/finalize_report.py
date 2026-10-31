"""Fill a weekly report scaffold from facts + real task records. Works for any session.

Three kinds of placeholders live in reports/sessionNN.md:
  {{AUTO_...}}     filled by THIS script from reports/facts/sessionNN.json and evidence/
  {{FROM:<path>#<key.path>}}   (Session 09) filled by THIS script with one value from a JSON file
                   in the repository, for example
                   {{FROM:experiments/session09/hint_eval.json#honest.marks_per_100_sentences}}
                   Keys are separated by dots; a number picks a list item (groups.0.tasks); a key
                   that itself contains a dot also works (margins.0.05.leave_one_company_out_HONEST).
                   Optional format after a bar: |2 = two decimals, |%1 = times 100 with one decimal
                   (a share of 0.5065 becomes 50.6). The file must be listed under "number_sources"
                   in the facts file, so scripts/check_report_numbers.py checks it too.
  <<HUMAN: ...>>   written BY HAND before running this script (words only: every number in the
                   report must come from a token or a listed source, see check_report_numbers.py)

The script refuses to write anything if a <<HUMAN>> placeholder is still present, if any
fact is missing or malformed, or if the task records do not exist. It never invents data.
"""
import argparse
import json
import re
import sys
from decimal import ROUND_HALF_UP, Decimal
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from clauses.model import DEFAULT_MODEL, load  # noqa: E402
from clauses.study import summarize  # noqa: E402

PEOPLE = [('Ameer', 'Product'), ('Hemanth', 'Engineering'), ('Jayakrishna', 'Data&Eval'),
          ('Niveda', 'Users&Research'), ('Ankan', 'Operations')]
REPORTED_SESSIONS = ['04', '05', '07', '08', '09', '10', '11', '12']
HANDLE = re.compile(r'[A-Za-z0-9](?:[A-Za-z0-9-]{0,37}[A-Za-z0-9])?')
FROM = re.compile(r'{{FROM:([^#{}|]+)#([^{}|]+)(?:\|(%?)(\d))?}}')


def from_value(root, rel, key, scale, decimals, sources):
    """One value from a JSON file in the repository, formatted for the report."""
    root = Path(root).resolve()
    label = f'{{{{FROM:{rel}#{key}}}}}'
    if rel not in sources:
        raise ValueError(f'{label}: {rel} is not listed under number_sources in the facts file.')
    path = (root / rel).resolve()
    if not path.is_relative_to(root) or path.suffix != '.json' or not path.is_file():
        raise ValueError(f'{label}: {rel} is not a JSON file in the repository.')
    value = json.loads(path.read_text(encoding='utf-8'))
    if isinstance(value, dict) and 'superseded_by' in value:
        raise ValueError(f'{label}: {rel} is superseded by {value["superseded_by"]}.')
    parts = key.split('.')
    while parts:
        part = parts.pop(0)
        # A key may itself contain dots (cue_eval.json uses margins such as "0.05"): join the next parts until it matches.
        while isinstance(value, dict) and part not in value and parts:
            part = part + '.' + parts.pop(0)
        if isinstance(value, list) and part.isdigit() and int(part) < len(value):
            value = value[int(part)]
        elif isinstance(value, dict) and part in value:
            value = value[part]
        else:
            raise ValueError(f'{label}: no key {part!r} in {rel}.')
    if isinstance(value, bool) or not isinstance(value, (int, float, str)):
        raise ValueError(f'{label}: the value is not a number or a text.')
    if decimals is None:
        if scale:
            raise ValueError(f'{label}: |% needs a number of decimals, for example |%1.')
        return str(value)
    if isinstance(value, str):
        raise ValueError(f'{label}: a format was given but the value is text.')
    number = Decimal(str(value)) * (100 if scale else 1)
    return str(number.quantize(Decimal(1).scaleb(-int(decimals)), rounding=ROUND_HALF_UP))


def trials_table(csv_path):
    """A Markdown table with one row per trial in tasks.csv (and the interface from its trial record)."""
    import csv
    with Path(csv_path).open(newline='', encoding='utf-8') as f:
        rows = list(csv.DictReader(f))
    lines = ['| Participant | Task | Condition | Interface | Correct within the limit | Seconds |',
             '|---|---|---|---|---|---:|']
    for r in rows:
        record = Path(csv_path).parent / f"{r['participant_id']}_{r['task_id']}_{r['condition']}_{r['protocol_version']}.json"
        interface = json.loads(record.read_text(encoding='utf-8')).get('interface', 'not recorded') if record.exists() else 'not recorded'
        ok = r['correct'] == '1' and float(r['seconds']) <= float(r['limit_seconds'])
        condition = 'ClauseGuard' if r['condition'] == 'clauseguard' else 'manual'
        lines.append(f"| {r['participant_id']} | {r['task_id']} | {condition} | {interface} | {'yes' if ok else 'no'} | {r['seconds']} |")
    return '\n'.join(lines), sorted({r['participant_id'] for r in rows})


def text_value(value, label):
    if not isinstance(value, str) or not value.strip() or re.search(r'TODO|PENDING|REPLACE|<<|{{', value):
        raise ValueError(f'Provide a real value for {label}.')
    return value.strip()


def links(values, label, repo):
    if not isinstance(values, list) or not values:
        raise ValueError(f'{label} needs at least one issue, PR or commit link.')
    pattern = re.escape(repo) + r'/(issues/\d+|pull/\d+|commit/[0-9a-f]{7,40})'
    for v in values:
        if not isinstance(v, str) or not re.fullmatch(pattern, v):
            raise ValueError(f'{label}: {v!r} is not an issue/PR/commit URL in {repo}.')
    def name(url):
        kind, ref = url.rsplit('/', 2)[-2:]
        return {'pull': f'PR #{ref}', 'issues': f'issue #{ref}'}.get(kind, f'commit {ref[:7]}')
    return ', '.join(f'[{name(v)}]({v})' for v in values)


def previous_value(root, session):
    idx = REPORTED_SESSIONS.index(session)
    if idx == 0:
        return 'null'
    prev = root / f'reports/session{REPORTED_SESSIONS[idx - 1]}.md'
    m = re.search(r'^  value: (.+)$', prev.read_text(encoding='utf-8'), re.M)
    if not m:
        raise ValueError(f'Could not read the previous value from {prev.name}.')
    return m.group(1).strip()


def finalize(root, session, facts_path=None, model_id=None):
    root = Path(root)
    report_path = root / f'reports/session{session}.md'
    facts_path = Path(facts_path or root / f'reports/facts/session{session}.json')
    text = report_path.read_text(encoding='utf-8')

    human = re.findall(r'<<[^>]*>>', text)
    if human:
        raise ValueError(f'{len(human)} <<...>> placeholder(s) still in the report. First: {human[0][:70]}...')

    facts = json.loads(facts_path.read_text(encoding='utf-8'))
    repo = text_value(facts.get('repo_url'), 'repo_url').rstrip('/')
    if not re.fullmatch(r'https://github\.com/[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+', repo):
        raise ValueError('repo_url must be the GitHub repository URL.')
    for flag in ('branch_protection_verified', 'outside_user_evidence_reviewed', 'contributions_verified'):
        if facts.get(flag) is not True:
            raise ValueError(f'{flag} must be true, and only after a person has checked it.')
    protocol = text_value(facts.get('protocol'), 'protocol')

    csv_path = root / f'evidence/session{session}/tasks.csv'
    if not csv_path.exists():
        raise ValueError(f'{csv_path.relative_to(root)} does not exist. Merge the real session evidence first.')
    summary = summarize(csv_path)
    model_id = model_id or load(DEFAULT_MODEL)['model_id']
    tool = [g for g in summary['groups'] if g['condition'] == 'clauseguard' and g['protocol_version'] == protocol]
    manual = [g for g in summary['groups'] if g['condition'] == 'manual' and g['protocol_version'] == protocol]
    if len(tool) != 1:
        raise ValueError(f'Expected exactly one ClauseGuard group under protocol {protocol}; found {len(tool)}.')
    tool = tool[0]
    if tool['model_id'] != model_id:
        raise ValueError('ClauseGuard trials used a different model than the one in the product. Explain before reporting.')

    tokens = {
        'AUTO_VALUE': f"{tool['success_percent']:.2f}",
        'AUTO_PREVIOUS': previous_value(root, session),
        'AUTO_TOOL_RESULT': f"{tool['successful_tasks']}/{tool['tasks']} ClauseGuard tasks correct within "
                            f"{int(tool['limit_seconds'])} seconds ({tool['success_percent']:.2f}%), "
                            f"{tool['participants']} outside participant(s), median {tool['median_seconds_all_tasks']:.1f} s",
        'AUTO_MANUAL_RESULT': (f"{manual[0]['successful_tasks']}/{manual[0]['tasks']} manual tasks correct within the limit "
                               f"({manual[0]['success_percent']:.2f}%), median {manual[0]['median_seconds_all_tasks']:.1f} s")
                              if manual else 'no manual-condition trials recorded this week',
        'AUTO_PROTOCOL': protocol,
        'AUTO_MODEL_ID': model_id,
        'AUTO_EVIDENCE_LINKS': f'[task records](../evidence/session{session}/tasks.csv), '
                               f'[trial files and notes](../evidence/session{session}/), '
                               f'[summary](../evidence/session{session}/summary.json)',
        'AUTO_SHIPPED_LINKS': links(facts.get('shipped_evidence_urls'), 'shipped_evidence_urls', repo),
        'AUTO_CHANGE_LINKS': links(facts.get('user_change_evidence_urls'), 'user_change_evidence_urls', repo),
    }
    table, participants = trials_table(csv_path)
    tokens['AUTO_TRIALS_TABLE'] = table
    tokens['AUTO_PARTICIPANT_IDS'] = ', '.join(participants)
    contributions = []
    members = facts.get('members', {})
    for name, hat in PEOPLE:
        m = members.get(name, {})
        handle = text_value(m.get('github'), f'{name} github')
        if not HANDLE.fullmatch(handle):
            raise ValueError(f'Invalid GitHub handle for {name} (no @).')
        tokens[f'AUTO_GITHUB_{name}'] = handle
        work = text_value(m.get('completed_work'), f'{name} completed_work')
        contributions.append(f'- {name} ({hat}): {work} (evidence: {links(m.get("evidence_urls"), name + " evidence_urls", repo)})')
    tokens['AUTO_CONTRIBUTIONS'] = '\n'.join(contributions)

    for key, value in tokens.items():
        text = text.replace('{{' + key + '}}', value)
    sources = facts.get('number_sources', [])
    text = FROM.sub(lambda m: from_value(root, m.group(1).strip(), m.group(2).strip(), m.group(3) == '%',
                                         m.group(4), sources), text)
    leftover = re.findall(r'{{[^{}]*}}', text)
    if leftover:
        raise ValueError(f'Unknown or unfilled token(s): {leftover[:5]}')
    if re.search(r'TODO|PENDING|DRAFT', text):
        raise ValueError('TODO / PENDING / DRAFT still appears in the report.')

    backup = root / f'private/session{session}.before-finalization.md'
    backup.parent.mkdir(parents=True, exist_ok=True)
    backup.write_text(report_path.read_text(encoding='utf-8'), encoding='utf-8')
    report_path.write_text(text, encoding='utf-8')
    (csv_path.parent / 'summary.json').write_text(json.dumps(summary, indent=2) + '\n', encoding='utf-8')
    return tokens


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument('--session', required=True, choices=REPORTED_SESSIONS[1:])
    p.add_argument('--facts')
    a = p.parse_args()
    try:
        tokens = finalize(ROOT, a.session, a.facts)
    except (ValueError, OSError, KeyError, TypeError) as e:
        p.exit(2, f'Not finalized: {e}\n')
    print(f"Updated reports/session{a.session}.md")
    print(f"  north-star value: {tokens['AUTO_VALUE']}   previous: {tokens['AUTO_PREVIOUS']}")
    print(f"  {tokens['AUTO_TOOL_RESULT']}")
    print(f"  manual: {tokens['AUTO_MANUAL_RESULT']}")
    print('Now read the whole report yourself before committing.')


if __name__ == '__main__':
    main()
