"""Session 08 re-check of the mid-semester decision rule ("what would change our mind").

    python scripts/decision_recheck.py --misled 0 --misled-source "<<which notes you read>>"

The mid-semester decision memo (docs/decisions/2026-10-06_midpoint_decision.md, section 5) says:
  "from Session 08 onward, with at least 6 participants, a ClauseGuard success rate more than
   25 percentage points below manual, or any participant misled by wrong tags, means changing the
   interface or the job; failing the model gate means a pivot."

This script applies exactly that sentence, with the thresholds from docs/decisions/midpoint_rule.json:
  - model gate: the product model's honest macro-F1 (leave-one-company-out, experiments/session05/
    threshold_cv.json) is at least 0.10 above the unigram baseline (experiments/session04/baseline/
    metrics.json), and the app runs the evaluated model (artifacts/selected.json = experiments/
    session07/tuned/metrics.json)
  - participants: distinct outside participants in every evidence/sessionNN/tasks.csv under
    protocol sep29_v2 (Session 05 onward); at least 6 needed
  - success: correct within the time limit; ClauseGuard rate vs manual rate, all sessions pooled
    (each ClauseGuard trial ran the product of its week; the per-session table shows which model)
  - misled by wrong tags: a PERSON's judgement from the session notes, given with --misled and
    --misled-source. The script cannot read notes; it records what you state.

Outcomes:
  PIVOT                       the model gate fails
  CHANGE INTERFACE OR JOB     enough participants AND (ClauseGuard more than 25 points below manual
                              OR at least one participant misled by wrong tags)
  KEEP THE PRODUCT DIRECTION  enough participants, neither condition met
  NOT ENOUGH PARTICIPANTS     fewer than 6 participants: no conclusion yet

Writes experiments/session08/decision_recheck.json and .md. Speed is reported, never decides.
"""
import argparse
import csv
import json
import re
import statistics
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RULE = 'docs/decisions/midpoint_rule.json'
LOCO = 'experiments/session05/threshold_cv.json'
BASELINE = 'experiments/session04/baseline/metrics.json'
SELECTED = 'artifacts/selected.json'
EVALUATED = 'experiments/session07/tuned/metrics.json'
OUT = 'experiments/session08/decision_recheck'
MIN_PARTICIPANTS = 6  # from the memo: "from Session 08 onward, with at least 6 participants"


class RecheckError(ValueError):
    pass


def read_json(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))


def trials(root, protocol):
    rows = []
    for path in sorted(Path(root, 'evidence').glob('session*/tasks.csv')):
        session = path.parent.name.replace('session', '')
        with path.open(newline='', encoding='utf-8') as f:
            for r in csv.DictReader(f):
                if r['protocol_version'] == protocol:
                    rows.append({**r, 'session': session})
    return rows


def success(r):
    return r['correct'] == '1' and float(r['seconds']) <= float(r['limit_seconds'])


def rate(rows):
    return round(100 * sum(success(r) for r in rows) / len(rows), 2) if rows else None


def run(root, misled, misled_source):
    root = Path(root)
    if misled is None or misled < 0:
        raise RecheckError('Give --misled: the number of participants misled by wrong tags (0 or more).')
    if not misled_source or not misled_source.strip() or '<<' in misled_source:
        raise RecheckError('Give --misled-source: which session notes you read to count misled participants.')
    rule = read_json(root / RULE)
    gap_limit = rule['max_success_gap_points_for_persevere_with_change']
    gate_min = rule['model_gate_min_macro_f1_gain_over_baseline']

    honest = read_json(root / LOCO)['leave_one_company_out_HONEST']['macro_f1']
    baseline = round(read_json(root / BASELINE)['macro_f1_8'], 4)
    identical = read_json(root / SELECTED)['artifact_sha256'] == read_json(root / EVALUATED)['model_id']
    gate = identical and honest - baseline >= gate_min

    rows = trials(root, rule['protocol'])
    if not rows:
        raise RecheckError(f"No {rule['protocol']} trials found under evidence/.")
    cg = [r for r in rows if r['condition'] == 'clauseguard']
    manual = [r for r in rows if r['condition'] == 'manual']
    people = sorted({r['participant_id'] for r in rows})
    cg_rate, manual_rate = rate(cg), rate(manual)
    gap = None if cg_rate is None or manual_rate is None else round(cg_rate - manual_rate, 2)
    enough = len(people) >= MIN_PARTICIPANTS
    worse = gap is not None and gap < -gap_limit

    if not gate:
        outcome = 'PIVOT'
    elif not enough:
        outcome = 'NOT ENOUGH PARTICIPANTS'
    elif worse or misled > 0:
        outcome = 'CHANGE INTERFACE OR JOB'
    else:
        outcome = 'KEEP THE PRODUCT DIRECTION'

    sessions = []
    for s in sorted({r['session'] for r in rows}):
        mine = [r for r in rows if r['session'] == s]
        c = [r for r in mine if r['condition'] == 'clauseguard']
        m = [r for r in mine if r['condition'] == 'manual']
        sessions.append({
            'session': s,
            'participants': sorted({r['participant_id'] for r in mine}),
            'clauseguard': f'{sum(success(r) for r in c)}/{len(c)}',
            'manual': f'{sum(success(r) for r in m)}/{len(m)}',
            'clauseguard_models': sorted({r['model_id'][:12] for r in c}),
        })
    return {
        'rule_source': 'docs/decisions/2026-10-06_midpoint_decision.md, section 5 ("What would change our mind")',
        'protocol': rule['protocol'],
        'model_gate': {'honest_macro_f1': honest, 'baseline_macro_f1': baseline,
                       'gain': round(honest - baseline, 4), 'required_gain': gate_min,
                       'app_runs_evaluated_model': identical, 'passed': bool(gate)},
        'participants': people,
        'participant_count': len(people),
        'required_participants': MIN_PARTICIPANTS,
        'clauseguard': {'trials': len(cg), 'successes': sum(map(success, cg)), 'success_percent': cg_rate,
                        'median_seconds': round(statistics.median(float(r['seconds']) for r in cg), 2) if cg else None},
        'manual': {'trials': len(manual), 'successes': sum(map(success, manual)), 'success_percent': manual_rate,
                   'median_seconds': round(statistics.median(float(r['seconds']) for r in manual), 2) if manual else None},
        'gap_points_clauseguard_minus_manual': gap,
        'max_gap_points_below_manual': gap_limit,
        'misled_by_wrong_tags': misled,
        'misled_source': misled_source.strip(),
        'per_session': sessions,
        'outcome': outcome,
        'note': 'A pre-committed decision heuristic, not a statistical test. Speed is reported but does not decide. '
                'Tasks differ in difficulty between sessions; pooled rates mix tasks and product versions.',
    }


def to_markdown(r):
    g, c, m = r['model_gate'], r['clauseguard'], r['manual']
    lines = ['# Re-check of the mid-semester decision rule (Session 08)', '',
             f"Rule: {r['rule_source']}. Protocol `{r['protocol']}` trials only.", '',
             '| Condition | Value | Needed | Met |', '|---|---|---|---|',
             f"| Model gate: honest macro-F1 gain over baseline, app runs the evaluated model | "
             f"{g['honest_macro_f1']} vs {g['baseline_macro_f1']} ({g['gain']:+.4f}); same model: {g['app_runs_evaluated_model']} | "
             f"+{g['required_gain']:.2f} and same model | {'yes' if g['passed'] else 'no'} |",
             f"| Outside participants | {r['participant_count']} ({', '.join(r['participants'])}) | at least {r['required_participants']} | "
             f"{'yes' if r['participant_count'] >= r['required_participants'] else 'no'} |",
             f"| ClauseGuard success minus manual success | {c['success_percent']}% - {m['success_percent']}% = "
             f"{r['gap_points_clauseguard_minus_manual']} points | not more than {r['max_gap_points_below_manual']} points below | "
             f"{'yes' if r['gap_points_clauseguard_minus_manual'] is not None and r['gap_points_clauseguard_minus_manual'] >= -r['max_gap_points_below_manual'] else 'no'} |",
             f"| Participants misled by wrong tags (from: {r['misled_source']}) | {r['misled_by_wrong_tags']} | 0 | "
             f"{'yes' if r['misled_by_wrong_tags'] == 0 else 'no'} |",
             '', f"**Outcome: {r['outcome']}**", '',
             '| Session | Participants | ClauseGuard | Manual | ClauseGuard model |', '|---|---|---:|---:|---|']
    for s in r['per_session']:
        lines.append(f"| {s['session']} | {', '.join(s['participants'])} | {s['clauseguard']} | {s['manual']} | "
                     f"{', '.join(s['clauseguard_models']) or '-'} |")
    lines += ['', f"Median seconds (reported, not deciding): ClauseGuard {c['median_seconds']}, manual {m['median_seconds']}.",
              '', r['note']]
    return '\n'.join(lines) + '\n'


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument('--misled', type=int, required=True,
                   help='participants who treated a wrong tag as true, counted from the session notes')
    p.add_argument('--misled-source', required=True, help='which notes you read, e.g. "evidence/session05-07/session_notes.md"')
    p.add_argument('--output', default=OUT, help='output path without extension')
    a = p.parse_args(argv)
    try:
        r = run(ROOT, a.misled, a.misled_source)
    except (RecheckError, FileNotFoundError, KeyError) as e:
        print(f'STOPPED: {e}', file=sys.stderr)
        return 1
    out = ROOT / a.output
    out.parent.mkdir(parents=True, exist_ok=True)
    out.with_suffix('.json').write_text(json.dumps(r, indent=2) + '\n', encoding='utf-8')
    out.with_suffix('.md').write_text(to_markdown(r), encoding='utf-8')
    print(f"Participants: {r['participant_count']} ({', '.join(r['participants'])})")
    print(f"ClauseGuard {r['clauseguard']['successes']}/{r['clauseguard']['trials']} ({r['clauseguard']['success_percent']}%), "
          f"manual {r['manual']['successes']}/{r['manual']['trials']} ({r['manual']['success_percent']}%), "
          f"gap {r['gap_points_clauseguard_minus_manual']} points; misled by wrong tags: {r['misled_by_wrong_tags']}")
    print(f"Model gate: {'passed' if r['model_gate']['passed'] else 'FAILED'} ({r['model_gate']['gain']:+.4f})")
    print(f"Outcome: {r['outcome']}")
    print(f'Wrote {a.output}.json and {a.output}.md')
    return 0


if __name__ == '__main__':
    sys.exit(main())
