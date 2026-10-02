"""Every number for the Session 06 mid-semester presentation, computed from committed files.

    python scripts/midpoint_facts.py

Reads (nothing is typed in by hand):
  - experiments/session04/{baseline,balanced,hybrid}/metrics.json   validation results
  - experiments/session04/hybrid/predictions.jsonl                   flag rates
  - experiments/session05/threshold_cv.json                          threshold experiment (NOT shipped)
  - artifacts/selected.joblib                                        the model the app runs
  - experiments/session06/demo_check.json   (optional)               cost to serve (Hemanth)
  - evidence/session05/tasks.csv, evidence/session06/tasks.csv       outside-user task tests
  - docs/decisions/midpoint_rule.json                                the pre-registered decision rule (Ameer)

Writes to reports/midpoint/:
  facts.json          all values, plus a flat "tokens" map used by scripts/build_slides.py
  metrics.md          readable tables with sources
  figures/*.svg       metric vs baseline, per-category F1, user task results

The final test split is never read. Refuses to run if the three models were not
evaluated on the same validation sentences or if the app's model is not the evaluated one.
"""
import argparse
import csv
import hashlib
import json
import statistics
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MODELS = [('baseline', 'Unigram baseline'), ('balanced', 'Balanced 1-2-gram'), ('hybrid', 'Hybrid (shipped)')]
OUTCOME_TEXT = {
    'PIVOT': 'Pivot',
    'PERSEVERE_WITH_CHANGE': 'Persevere with change',
    'PERSEVERE': 'Persevere',
    'PROVISIONAL_PERSEVERE': 'Provisional persevere (not enough users yet)',
}


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def read_json(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))


def fmt(x, digits=4):
    return 'not measured' if x is None else f'{x:.{digits}f}'


# ---------------------------------------------------------------- model facts
def model_facts(root, rule):
    root = Path(root)
    metrics = {k: read_json(root / f'experiments/session04/{k}/metrics.json') for k, _ in MODELS}
    for k, m in metrics.items():
        if m.get('split') != 'validation':
            raise ValueError(f'{k} metrics are not validation metrics; the test split must not be used before Session 12.')
    if len({m['n'] for m in metrics.values()}) != 1 or len({m['dataset_sha256'] for m in metrics.values()}) != 1:
        raise ValueError('The three models were not evaluated on the same data. Not comparable.')
    ids = {}
    for k, _ in MODELS:
        p = root / f'experiments/session04/{k}/predictions.jsonl'
        if p.exists():
            ids[k] = [json.loads(line)['id'] for line in p.read_text(encoding='utf-8').splitlines() if line.strip()]
    if len({tuple(v) for v in ids.values()}) > 1:
        raise ValueError('Prediction files cover different sentences. Not comparable.')

    shipped = sha256(root / 'artifacts/selected.joblib')
    identity = {
        'app_model_sha256': shipped,
        'evaluated_hybrid_model_id': metrics['hybrid']['model_id'],
        'rule_shipped_model_sha256': rule['shipped_model_sha256'],
    }
    identical = len(set(identity.values())) == 1
    if not identical:
        raise ValueError('The model the app runs is not the model whose numbers we report: ' + json.dumps(identity))

    rows = [json.loads(line) for line in (root / 'experiments/session04/hybrid/predictions.jsonl')
            .read_text(encoding='utf-8').splitlines() if line.strip()]
    if any(r['id'].startswith('test:') for r in rows):
        raise ValueError('Test-split predictions found. They must not be used before Session 12.')
    flags = sum(len(r['predicted']) for r in rows)
    gold = sum(len(r['gold']) for r in rows)
    wrong = sum(1 for r in rows for label in r['predicted'] if label not in r['gold'])
    companies = sorted({r['document_id'] for r in rows})

    per = []
    tcv_path = root / 'experiments/session05/threshold_cv.json'
    tcv = read_json(tcv_path) if tcv_path.exists() else None
    for label, v in metrics['hybrid']['per_label'].items():
        if label == 'No category':
            continue
        entry = {'category': label, 'support': v['support'], 'precision': v['precision'], 'recall': v['recall'], 'f1': v['f1']}
        if tcv:
            loco = tcv['leave_one_company_out_HONEST']
            entry['f1_loco_not_shipped'] = loco['per_label'][label]['f1']
            entry['loco_threshold_range'] = loco['threshold_range_across_folds'][label]
        per.append(entry)
    weakest = min(per, key=lambda e: e['f1'])
    out = {
        'identity': identity,
        'identical': identical,
        'variant': metrics['hybrid']['variant'],
        'threshold_source': metrics['hybrid']['threshold_source'],
        'validation_sentences': metrics['hybrid']['n'],
        'validation_companies': len(companies),
        'dataset_sha256': metrics['hybrid']['dataset_sha256'],
        'macro_f1': {k: metrics[k]['macro_f1_8'] for k, _ in MODELS},
        'micro_f1': {k: metrics[k]['micro_f1_8'] for k, _ in MODELS},
        'gain_over_baseline': metrics['hybrid']['macro_f1_8'] - metrics['baseline']['macro_f1_8'],
        'per_category': per,
        'weakest': weakest,
        'flags_per_100': 100 * flags / len(rows),
        'gold_flags_per_100': 100 * gold / len(rows),
        'flags': flags,
        'wrong_flags': wrong,
        'wrong_flag_share': wrong / flags if flags else None,
        'threshold_experiment': None,
    }
    if tcv:
        out['threshold_experiment'] = {
            'shipped': False,
            'source': 'experiments/session05/threshold_cv.json',
            'fixed_macro_f1': tcv['fixed_0_5']['macro_f1'],
            'loco_macro_f1': tcv['leave_one_company_out_HONEST']['macro_f1'],
            'loco_flags_per_100': tcv['leave_one_company_out_HONEST']['flags_per_100_sentences'],
        }
    return out


# ----------------------------------------------------------------- user facts
def load_trials(root, rule):
    trials, missing = [], []
    for rel in rule['evidence_files']:
        p = Path(root) / rel
        if not p.exists():
            missing.append(rel)
            continue
        with p.open(newline='', encoding='utf-8') as f:
            for r in csv.DictReader(f):
                r['session'] = Path(rel).parent.name
                trials.append(r)
    return trials, missing


def user_facts(trials, rule):
    kept, excluded = [], []
    for r in trials:
        if r['protocol_version'] != rule['protocol']:
            excluded.append((r, f"protocol {r['protocol_version']}"))
        elif r['condition'] == 'clauseguard' and r['model_id'] != rule['shipped_model_sha256']:
            excluded.append((r, 'ClauseGuard trial ran a different model'))
        else:
            kept.append(r)
    seen = {}
    for r in kept:
        key = (r['participant_id'], r['task_id'], r['condition'])
        if key in seen:
            raise ValueError(f'Duplicate trial {key} in {seen[key]} and {r["session"]}. A participant repeated a task.')
        seen[key] = r['session']

    def ok(r):
        return r['correct'] == '1' and float(r['seconds']) <= float(r['limit_seconds'])

    by = {}
    for cond in ('clauseguard', 'manual'):
        rr = [r for r in kept if r['condition'] == cond]
        succ = sum(ok(r) for r in rr)
        by[cond] = {
            'trials': len(rr),
            'participants': len({r['participant_id'] for r in rr}),
            'successes': succ,
            'success_pct': 100 * succ / len(rr) if rr else None,
            'median_seconds': statistics.median(float(r['seconds']) for r in rr) if rr else None,
        }
    task = rule['over_tagging_task']
    c1 = [r for r in kept if r['task_id'] == task and r['condition'] == 'clauseguard']
    sessions = {}
    for r in kept:
        sessions.setdefault(r['session'], set()).add(r['participant_id'])
    return {
        'protocol': rule['protocol'],
        'participants': len({r['participant_id'] for r in kept}),
        'participants_by_session': {k: len(v) for k, v in sorted(sessions.items())},
        'trials': len(kept),
        'by_condition': by,
        'over_tagged_task': task,
        'over_tagged_with_clauseguard': {'trials': len(c1), 'successes': sum(ok(r) for r in c1)},
        'excluded': [{'session': r['session'], 'participant': r['participant_id'], 'task': r['task_id'],
                      'reason': why} for r, why in excluded],
        'per_trial': [{'session': r['session'], 'participant': r['participant_id'], 'task': r['task_id'],
                       'condition': r['condition'], 'correct': r['correct'] == '1',
                       'seconds': float(r['seconds'])} for r in kept],
    }


# ---------------------------------------------------------------- the rule
def evaluate_rule(rule, model, users):
    checks = []
    gain = model['gain_over_baseline']
    gate = model['identical'] and gain >= rule['model_gate_min_macro_f1_gain_over_baseline']
    checks.append({'condition': f"Model gate: shipped macro-F1 gain over baseline >= "
                                f"{rule['model_gate_min_macro_f1_gain_over_baseline']:.2f} and app model = evaluated model",
                   'value': f'{gain:+.4f}', 'met': gate})
    n = users['participants']
    enough = n >= rule['min_outside_participants_for_user_decision']
    checks.append({'condition': f"At least {rule['min_outside_participants_for_user_decision']} outside participants "
                                f"({rule['protocol']})", 'value': str(n), 'met': enough})
    cg = users['by_condition']['clauseguard']['success_pct']
    man = users['by_condition']['manual']['success_pct']
    gap = None if cg is None or man is None else man - cg
    checks.append({'condition': 'ClauseGuard success rate >= manual success rate',
                   'value': 'not measured' if gap is None else f'ClauseGuard {cg:.0f}% vs manual {man:.0f}%',
                   'met': None if gap is None else gap <= 0})
    c1 = users['over_tagged_with_clauseguard']
    c1_fail = c1['trials'] - c1['successes'] > 0
    checks.append({'condition': f"Nobody failed over-tagged task {users['over_tagged_task']} with ClauseGuard",
                   'value': f"{c1['successes']}/{c1['trials']} correct" if c1['trials'] else 'not tested',
                   'met': None if not c1['trials'] else not c1_fail})
    if not gate:
        outcome, reason = 'PIVOT', 'The shipped model does not clear the model gate.'
    elif not enough:
        outcome, reason = 'PROVISIONAL_PERSEVERE', (f'Only {n} outside participant(s) under {rule["protocol"]}; '
                                                    f'the rule needs {rule["min_outside_participants_for_user_decision"]}.')
    elif gap is None:
        outcome, reason = 'PROVISIONAL_PERSEVERE', 'No trials in one of the two conditions.'
    elif gap > rule['max_success_gap_points_for_persevere_with_change']:
        outcome, reason = 'PIVOT', f'ClauseGuard success rate is {gap:.0f} points below manual.'
    elif gap > 0 or c1_fail:
        why = []
        if gap > 0:
            why.append(f'ClauseGuard success rate is {gap:.0f} points below manual')
        if c1_fail:
            why.append(f"{c1['trials'] - c1['successes']} participant(s) failed the over-tagged task with ClauseGuard")
        outcome, reason = 'PERSEVERE_WITH_CHANGE', '; '.join(why) + '.'
    else:
        outcome, reason = 'PERSEVERE', 'Model gate passed, enough participants, ClauseGuard success >= manual, nobody failed the over-tagged task.'
    return {'rule_id': rule['rule_id'], 'outcome': outcome, 'outcome_text': OUTCOME_TEXT[outcome],
            'reason': reason, 'checks': checks}


# ---------------------------------------------------------------- figures
def _svg(width, height, body, title):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" '
            f'font-family="Helvetica, Arial, sans-serif" role="img" aria-label="{title}">'
            f'<rect width="100%" height="100%" fill="#ffffff"/>'
            f'<text x="20" y="30" font-size="20" font-weight="bold" fill="#1d1d1f">{title}</text>{body}</svg>\n')


def fig_metric(model):
    bars = [(label, model['macro_f1'][k], '#2f6fb2' if k == 'hybrid' else '#9fb4c9') for k, label in MODELS]
    te = model['threshold_experiment']
    if te:
        bars.append(('Per-category thresholds (not shipped)', te['loco_macro_f1'], '#d9d9d9'))
    w, h, x0, y0, plot_h = 820, 430, 70, 370, 300
    bw = 140
    body = [f'<line x1="{x0}" y1="{y0}" x2="{w - 20}" y2="{y0}" stroke="#555"/>']
    for t in (0, 0.25, 0.5, 0.75, 1.0):
        y = y0 - t * plot_h
        body.append(f'<line x1="{x0}" y1="{y:.1f}" x2="{w - 20}" y2="{y:.1f}" stroke="#eee"/>'
                    f'<text x="{x0 - 8}" y="{y + 4:.1f}" font-size="12" text-anchor="end" fill="#555">{t:.2f}</text>')
    for i, (label, v, color) in enumerate(bars):
        x = x0 + 30 + i * (bw + 45)
        bh = v * plot_h
        dash = ' stroke="#777" stroke-dasharray="5,4"' if 'not shipped' in label else ''
        body.append(f'<rect x="{x}" y="{y0 - bh:.1f}" width="{bw}" height="{bh:.1f}" fill="{color}"{dash}/>'
                    f'<text x="{x + bw / 2}" y="{y0 - bh - 8:.1f}" font-size="16" font-weight="bold" text-anchor="middle">{v:.4f}</text>'
                    f'<text x="{x + bw / 2}" y="{y0 + 20}" font-size="12" text-anchor="middle">{label.split(" (")[0]}</text>')
        if '(' in label:
            body.append(f'<text x="{x + bw / 2}" y="{y0 + 36}" font-size="12" text-anchor="middle">({label.split(" (")[1]}</text>')
    body.append(f'<text x="20" y="52" font-size="13" fill="#555">Macro-F1 over 8 categories, validation split '
                f'({model["validation_sentences"]:,} sentences, {model["validation_companies"]} companies). Test split untouched.</text>')
    return _svg(w, h, ''.join(body), 'Shipped model vs baseline')


def fig_categories(model):
    per = model['per_category']
    w, row_h, x0 = 820, 34, 230
    h = 75 + row_h * len(per) + 15
    scale = (w - x0 - 80)
    body = [f'<text x="20" y="52" font-size="13" fill="#555">Validation F1 per category. Dark = shipped (fixed 0.5); '
            f'light = per-category thresholds, not shipped.</text>']
    for i, e in enumerate(sorted(per, key=lambda e: e['f1'])):
        y = 75 + i * row_h
        body.append(f'<text x="{x0 - 10}" y="{y + 15}" font-size="13" text-anchor="end">{e["category"]} (n={e["support"]})</text>'
                    f'<rect x="{x0}" y="{y}" width="{e["f1"] * scale:.1f}" height="13" fill="#2f6fb2"/>'
                    f'<text x="{x0 + e["f1"] * scale + 6:.1f}" y="{y + 11}" font-size="11">{e["f1"]:.3f}</text>')
        if 'f1_loco_not_shipped' in e:
            v = e['f1_loco_not_shipped']
            body.append(f'<rect x="{x0}" y="{y + 15}" width="{v * scale:.1f}" height="11" fill="#c9d3dd"/>'
                        f'<text x="{x0 + v * scale + 6:.1f}" y="{y + 25}" font-size="10" fill="#555">{v:.3f}</text>')
    return _svg(w, h, ''.join(body), 'Where the model fails: F1 by category')


def fig_users(users):
    w, h, x0, y0, plot_h = 820, 400, 70, 330, 220
    body = [f'<line x1="{x0}" y1="{y0}" x2="{w - 20}" y2="{y0}" stroke="#555"/>',
            f'<text x="20" y="52" font-size="13" fill="#555">Outside participants: {users["participants"]} · protocol '
            f'{users["protocol"]} · success = right sentence and meaning within 180 s</text>']
    for i, (cond, label, color) in enumerate([('manual', 'Manual (text editor)', '#9fb4c9'),
                                              ('clauseguard', 'ClauseGuard', '#2f6fb2')]):
        c = users['by_condition'][cond]
        x = x0 + 80 + i * 330
        if not c['trials']:
            body.append(f'<text x="{x + 90}" y="{y0 - 20}" font-size="14" text-anchor="middle">no trials</text>')
        else:
            bh = c['success_pct'] / 100 * plot_h
            body.append(f'<rect x="{x}" y="{y0 - bh:.1f}" width="180" height="{bh:.1f}" fill="{color}"/>'
                        f'<text x="{x + 90}" y="{y0 - bh - 10:.1f}" font-size="18" font-weight="bold" text-anchor="middle">'
                        f'{c["successes"]}/{c["trials"]} correct</text>'
                        f'<text x="{x + 90}" y="{y0 + 40}" font-size="13" text-anchor="middle" fill="#555">'
                        f'median {c["median_seconds"]:.1f} s</text>')
        body.append(f'<text x="{x + 90}" y="{y0 + 20}" font-size="14" text-anchor="middle">{label}</text>')
    return _svg(w, h, ''.join(body), 'What outside users did with it')


# ---------------------------------------------------------------- outputs
def tokens(model, users, rule_eval, cost):
    t = {}
    t['MODEL_SHA12'] = model['identity']['app_model_sha256'][:12]
    t['THRESHOLD_SOURCE'] = model['threshold_source']
    t['VAL_SENTENCES'] = f"{model['validation_sentences']:,}"
    t['VAL_COMPANIES'] = str(model['validation_companies'])
    t['BASELINE_MACRO_F1'] = fmt(model['macro_f1']['baseline'])
    t['BALANCED_MACRO_F1'] = fmt(model['macro_f1']['balanced'])
    t['HYBRID_MACRO_F1'] = fmt(model['macro_f1']['hybrid'])
    t['HYBRID_MICRO_F1'] = fmt(model['micro_f1']['hybrid'])
    t['GAIN_OVER_BASELINE'] = f"{model['gain_over_baseline']:+.4f}"
    w = model['weakest']
    t['WEAKEST_CATEGORY'], t['WEAKEST_F1'], t['WEAKEST_SUPPORT'] = w['category'], f"{w['f1']:.3f}", str(w['support'])
    t['MODEL_FLAGS_PER_100'] = f"{model['flags_per_100']:.1f}"
    t['GOLD_FLAGS_PER_100'] = f"{model['gold_flags_per_100']:.1f}"
    t['WRONG_FLAGS'], t['TOTAL_FLAGS'] = str(model['wrong_flags']), str(model['flags'])
    t['WRONG_FLAG_PCT'] = f"{100 * model['wrong_flag_share']:.0f}%"
    te = model['threshold_experiment'] or {}
    t['LOCO_MACRO_F1'] = fmt(te.get('loco_macro_f1'))
    t['LOCO_FLAGS_PER_100'] = 'not measured' if 'loco_flags_per_100' not in te else f"{te['loco_flags_per_100']:.1f}"
    t['PARTICIPANTS'] = str(users['participants'])
    for s in ('session05', 'session06'):
        t[f'PARTICIPANTS_S{s[-2:]}'] = str(users['participants_by_session'].get(s, 0))
    for cond, key in (('clauseguard', 'CG'), ('manual', 'MANUAL')):
        c = users['by_condition'][cond]
        t[f'{key}_TRIALS'], t[f'{key}_SUCCESSES'] = str(c['trials']), str(c['successes'])
        t[f'{key}_SUCCESS_PCT'] = 'not measured' if c['success_pct'] is None else f"{c['success_pct']:.0f}%"
        t[f'{key}_MEDIAN_S'] = 'not measured' if c['median_seconds'] is None else f"{c['median_seconds']:.1f} s"
    c1 = users['over_tagged_with_clauseguard']
    t['C1_CG_TRIALS'], t['C1_CG_SUCCESSES'] = str(c1['trials']), str(c1['successes'])
    t['EXCLUDED_TRIALS'] = str(len(users['excluded']))
    t['RULE_OUTCOME'] = rule_eval['outcome_text']
    t['RULE_REASON'] = rule_eval['reason']
    t['RULE_TABLE'] = '\n'.join(['| Rule condition | Value | Met? |', '|---|---|---|'] + [
        f"| {c['condition']} | {c['value']} | {'n/a' if c['met'] is None else ('yes' if c['met'] else 'no')} |"
        for c in rule_eval['checks']])
    t['USER_TABLE'] = '\n'.join(['| | Manual (text editor) | ClauseGuard |', '|---|---|---|',
                                 f"| Correct within 180 s | {t['MANUAL_SUCCESSES']}/{t['MANUAL_TRIALS']} | {t['CG_SUCCESSES']}/{t['CG_TRIALS']} |",
                                 f"| Median time (all trials) | {t['MANUAL_MEDIAN_S']} | {t['CG_MEDIAN_S']} |"])
    t['COST_MS_PER_SENTENCE'] = 'not measured' if not cost else f"{cost['cost_to_serve']['ms_per_sentence_long_document']:.3f} ms"
    t['COST_DEMO_SECONDS'] = 'not measured' if not cost else f"{cost['cost_to_serve']['demo_document_median_seconds']:.3f} s"
    t['COST_LOAD_SECONDS'] = 'not measured' if not cost else f"{cost['cost_to_serve']['model_load_seconds']:.2f} s"
    t['DEMO_CHECK_DATE'] = 'not run' if not cost else cost['checked_utc'][:10]
    return t


def metrics_md(facts):
    m, u, r, t = facts['model'], facts['users'], facts['rule'], facts['tokens']
    lines = ['# Mid-semester numbers (Session 06)', '',
             f"Generated {facts['generated_utc']} by `python scripts/midpoint_facts.py` from commit `{facts['git_commit']}`. "
             'Every value is computed from committed files; nothing is typed in by hand.', '',
             '## 1. Shipped model vs baseline (validation)', '',
             f"The app runs model `{t['MODEL_SHA12']}` ({m['variant']}, thresholds `{m['threshold_source']}`). "
             'It is byte-identical to the evaluated hybrid model, so the numbers below are for the model in the demo.', '',
             '| Model | Macro-F1 | Micro-F1 |', '|---|---:|---:|']
    for k, label in MODELS:
        lines.append(f"| {label} | {m['macro_f1'][k]:.4f} | {m['micro_f1'][k]:.4f} |")
    lines += ['', f"Validation: {t['VAL_SENTENCES']} sentences from {t['VAL_COMPANIES']} companies not seen in training. "
              'Test split untouched. Sources: `experiments/session04/*/metrics.json`.', '',
              '## 2. Where it fails', '',
              f"- Over-flagging: {t['MODEL_FLAGS_PER_100']} flags per 100 sentences vs {t['GOLD_FLAGS_PER_100']} marked by annotators; "
              f"{t['WRONG_FLAGS']} of {t['TOTAL_FLAGS']} flags ({t['WRONG_FLAG_PCT']}) are a category the annotators did not assign.",
              f"- Weakest category: {t['WEAKEST_CATEGORY']}, F1 {t['WEAKEST_F1']} on {t['WEAKEST_SUPPORT']} sentences.", '',
              '| Category | Support | Precision | Recall | F1 (shipped) | F1 per-category thresholds (not shipped) |',
              '|---|---:|---:|---:|---:|---:|']
    for e in sorted(m['per_category'], key=lambda e: e['f1']):
        lines.append(f"| {e['category']} | {e['support']} | {e['precision']:.3f} | {e['recall']:.3f} | {e['f1']:.3f} | "
                     f"{e.get('f1_loco_not_shipped', float('nan')):.3f} |")
    if m['threshold_experiment']:
        lines += ['', f"Threshold experiment (Session 05, leave-one-company-out): macro-F1 {t['LOCO_MACRO_F1']}, "
                  f"{t['LOCO_FLAGS_PER_100']} flags per 100 sentences. **Not shipped**; planned for Session 07."]
    lines += ['', '## 3. Outside users (protocol ' + u['protocol'] + ')', '',
              f"Participants: {t['PARTICIPANTS']} (Session 05: {t['PARTICIPANTS_S05']}, Session 06: {t['PARTICIPANTS_S06']}). "
              f"Excluded trials: {t['EXCLUDED_TRIALS']}.", '', t['USER_TABLE'], '',
              f"Over-tagged task {u['over_tagged_task']} with ClauseGuard: {t['C1_CG_SUCCESSES']}/{t['C1_CG_TRIALS']} correct.", '',
              'Every trial:', '', '| Session | Participant | Task | Condition | Correct | Seconds |', '|---|---|---|---|---|---:|']
    for p in u['per_trial']:
        lines.append(f"| {p['session']} | {p['participant']} | {p['task']} | {p['condition']} | {'yes' if p['correct'] else 'no'} | {p['seconds']:.1f} |")
    lines += ['', 'Sources: ' + ', '.join(f'`{x}`' for x in facts['sources']['evidence_files_found']) + '.',
              'C1 and D1 differ in difficulty, so manual vs ClauseGuard is not a matched comparison.', '',
              '## 4. Pre-registered decision rule', '', f"Rule: `docs/decisions/midpoint_rule.json`. **Outcome: {t['RULE_OUTCOME']}.** {t['RULE_REASON']}", '',
              t['RULE_TABLE'], '', '## 5. Cost to serve', '',
              f"Measured on a team laptop on {t['DEMO_CHECK_DATE']}: model load {t['COST_LOAD_SECONDS']}, demo document {t['COST_DEMO_SECONDS']}, "
              f"{t['COST_MS_PER_SENTENCE']} per sentence on a long document. No network or API calls. Source: `experiments/session06/demo_check.json`.", '']
    return '\n'.join(lines)


def build(root=ROOT):
    root = Path(root)
    rule_path = root / 'docs/decisions/midpoint_rule.json'
    if not rule_path.exists():
        raise ValueError('docs/decisions/midpoint_rule.json is missing. Ameer\'s rule must be merged first.')
    rule = read_json(rule_path)
    model = model_facts(root, rule)
    trials, missing = load_trials(root, rule)
    users = user_facts(trials, rule)
    rule_eval = evaluate_rule(rule, model, users)
    cost_path = root / 'experiments/session06/demo_check.json'
    cost = read_json(cost_path) if cost_path.exists() else None
    try:
        commit = subprocess.run(['git', 'rev-parse', '--short', 'HEAD'], cwd=root, capture_output=True,
                                text=True, check=True).stdout.strip()
    except (OSError, subprocess.CalledProcessError):
        commit = 'unknown'
    facts = {
        'generated_utc': datetime.now(timezone.utc).isoformat(timespec='seconds'),
        'git_commit': commit,
        'sources': {'evidence_files_found': [x for x in rule['evidence_files'] if x not in missing],
                    'evidence_files_missing': missing,
                    'cost': 'experiments/session06/demo_check.json' if cost else None},
        'model': model, 'users': users, 'rule': rule_eval,
        'cost_to_serve': cost['cost_to_serve'] if cost else None,
    }
    facts['tokens'] = tokens(model, users, rule_eval, cost)
    return facts


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument('--out-dir', default='reports/midpoint')
    a = p.parse_args(argv)
    try:
        facts = build()
    except (ValueError, KeyError, OSError) as e:
        print(f'STOPPED: {e}', file=sys.stderr)
        return 1
    out = ROOT / a.out_dir
    (out / 'figures').mkdir(parents=True, exist_ok=True)
    (out / 'facts.json').write_text(json.dumps(facts, indent=2) + '\n', encoding='utf-8')
    (out / 'metrics.md').write_text(metrics_md(facts), encoding='utf-8')
    (out / 'figures/metric_vs_baseline.svg').write_text(fig_metric(facts['model']), encoding='utf-8')
    (out / 'figures/per_category_f1.svg').write_text(fig_categories(facts['model']), encoding='utf-8')
    (out / 'figures/user_tasks.svg').write_text(fig_users(facts['users']), encoding='utf-8')
    t = facts['tokens']
    print(f"Model {t['MODEL_SHA12']} (the app's model = the evaluated model)")
    print(f"Validation macro-F1: shipped {t['HYBRID_MACRO_F1']} vs baseline {t['BASELINE_MACRO_F1']} ({t['GAIN_OVER_BASELINE']})")
    print(f"Flags per 100 sentences: model {t['MODEL_FLAGS_PER_100']}, annotators {t['GOLD_FLAGS_PER_100']}; wrong flags {t['WRONG_FLAG_PCT']}")
    print(f"Outside participants: {t['PARTICIPANTS']} (S05 {t['PARTICIPANTS_S05']}, S06 {t['PARTICIPANTS_S06']})")
    print(f"  Manual:      {t['MANUAL_SUCCESSES']}/{t['MANUAL_TRIALS']} correct, median {t['MANUAL_MEDIAN_S']}")
    print(f"  ClauseGuard: {t['CG_SUCCESSES']}/{t['CG_TRIALS']} correct, median {t['CG_MEDIAN_S']}")
    print(f"  C1 (over-tagged) with ClauseGuard: {t['C1_CG_SUCCESSES']}/{t['C1_CG_TRIALS']} correct")
    for m in facts['sources']['evidence_files_missing']:
        print(f'  (not found yet: {m})')
    print(f"Rule outcome: {t['RULE_OUTCOME']} - {t['RULE_REASON']}")
    print(f"Cost: {t['COST_MS_PER_SENTENCE']} per sentence (demo check {t['DEMO_CHECK_DATE']})")
    print(f'Wrote {a.out_dir}/facts.json, metrics.md and figures/*.svg')
    return 0


if __name__ == '__main__':
    sys.exit(main())
