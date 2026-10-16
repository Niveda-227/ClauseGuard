"""What did shipping per-category thresholds actually change? (Session 07)

    python scripts/compare_thresholds.py

Compares the old product model (fixed 0.5 thresholds) with the new product model
(per-category thresholds) on the same 2,275 validation sentences, from committed files only:

  experiments/session04/hybrid/predictions.jsonl    old product, fixed 0.5
  experiments/session07/tuned/predictions.jsonl     new product, per-category thresholds
  experiments/session07/tuned/metrics.json          evaluation of the new product file
  experiments/session05/threshold_cv.json           leave-one-company-out (honest) estimate
  artifacts/selected.json, artifacts/tuned.json     what the app runs, and its thresholds

Checks first (stops if any fails): same sentences; identical scores (only the cut-offs moved);
the app's model is the evaluated tuned model; its thresholds equal the Session 05 experiment;
no test-split rows.

Then reports, for both models: correct tags, wrong tags (false positives), missed labels
(false negatives), flags per 100 sentences, macro/micro-F1, per category. Because the new
thresholds were chosen on this same validation split, the new model's numbers here are
OPTIMISTIC. The same counts are also computed leave-one-company-out (tune on 9 companies,
apply to the 10th), which is the estimate to report.

Writes experiments/session07/threshold_ship_eval.json and .md. The test split is never read.
"""
import argparse
import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from clauses.schema import LABELS  # noqa: E402
from scripts.threshold_cv import best_threshold, decide, summary  # noqa: E402

OLD = 'experiments/session04/hybrid/predictions.jsonl'
NEW = 'experiments/session07/tuned/predictions.jsonl'
NEW_METRICS = 'experiments/session07/tuned/metrics.json'
EXPERIMENT = 'experiments/session05/threshold_cv.json'
OUT = 'experiments/session07/threshold_ship_eval'
TOLERANCE = 1e-6


class CompareError(ValueError):
    pass


def read_json(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))


def read_predictions(path):
    rows = [json.loads(l) for l in Path(path).read_text(encoding='utf-8').splitlines() if l.strip()]
    if not rows:
        raise CompareError(f'{path} is empty.')
    if any(not r['id'].startswith('validation:') for r in rows):
        raise CompareError('Only validation predictions are allowed; the test split stays untouched.')
    return rows


def counts(y, pred):
    out = {'correct_tags': int(((pred == 1) & (y == 1)).sum()),
           'wrong_tags': int(((pred == 1) & (y == 0)).sum()),
           'missed_labels': int(((pred == 0) & (y == 1)).sum()),
           'flags': int(pred.sum())}
    out['wrong_tag_share'] = round(out['wrong_tags'] / out['flags'], 4) if out['flags'] else None
    return out


def per_category(y, pred):
    s = summary(y, pred)['per_label']
    for k, label in enumerate(LABELS):
        s[label].update({'wrong_tags': int(((pred[:, k] == 1) & (y[:, k] == 0)).sum()),
                         'missed_labels': int(((pred[:, k] == 0) & (y[:, k] == 1)).sum())})
    return s


def leave_one_company_out(y, scores, groups):
    held = np.zeros_like(y)
    for company in sorted(set(groups)):
        test = groups == company
        t = [best_threshold(y[~test, k], scores[~test, k]) for k in range(len(LABELS))]
        held[test] = decide(scores[test], t)
    return held


def compare(root=ROOT):
    root = Path(root)
    old_rows, new_rows = read_predictions(root / OLD), read_predictions(root / NEW)
    if [r['id'] for r in old_rows] != [r['id'] for r in new_rows]:
        raise CompareError('The two prediction files cover different sentences.')
    y = np.array([[int(l in r['gold']) for l in LABELS] for r in old_rows])
    old_scores = np.array([r['scores'] for r in old_rows], dtype=float)
    new_scores = np.array([r['scores'] for r in new_rows], dtype=float)
    diff = float(np.abs(old_scores - new_scores).max())
    if diff > TOLERANCE:
        raise CompareError(f'Scores differ by {diff:.2e}: the two models are not the same pipeline.')

    product = read_json(root / 'artifacts/selected.json')['artifact_sha256']
    evaluated = read_json(root / NEW_METRICS)['model_id']
    if product != evaluated:
        raise CompareError(f'The app runs {product[:12]} but the tuned evaluation is of {evaluated[:12]}.')
    thresholds = read_json(root / 'artifacts/tuned.json')['thresholds']
    experiment = read_json(root / EXPERIMENT)
    planned = experiment['tuned_in_sample_OPTIMISTIC']['thresholds']
    if any(abs(t - planned[l]) > 1e-9 for t, l in zip(thresholds, LABELS)):
        raise CompareError('Shipped thresholds differ from the Session 05 experiment.')

    old_pred = np.array([[int(l in r['predicted']) for l in LABELS] for r in old_rows])
    new_pred = np.array([[int(l in r['predicted']) for l in LABELS] for r in new_rows])
    if not np.array_equal(new_pred, decide(new_scores, thresholds)):
        raise CompareError('New predictions do not follow the shipped thresholds.')
    groups = np.array([r['document_id'] for r in old_rows])
    loco = leave_one_company_out(y, new_scores, groups)

    def block(pred):
        s = summary(y, pred)
        return {'macro_f1': s['macro_f1'], 'micro_f1': s['micro_f1'],
                'flags_per_100_sentences': s['flags_per_100_sentences'], **counts(y, pred),
                'per_category': per_category(y, pred)}

    return {
        'sentences': int(len(y)), 'companies': int(len(set(groups))),
        'gold_labels': int(y.sum()), 'gold_labels_per_100_sentences': round(100 * float(y.sum()) / len(y), 2),
        'old_product_fixed_0_5': {'model_id': read_json(root / 'experiments/session04/hybrid/metrics.json')['model_id'],
                                  **block(old_pred)},
        'new_product_tuned_OPTIMISTIC': {'model_id': product, 'thresholds': dict(zip(LABELS, thresholds)), **block(new_pred)},
        'new_product_leave_one_company_out_HONEST': block(loco),
        'checks': {'same_sentences': True, 'max_score_difference': diff, 'app_runs_evaluated_tuned_model': True,
                   'thresholds_match_session05_experiment': True, 'test_split_read': False},
        'note': 'Validation split only. The tuned numbers are optimistic (thresholds chosen on this split); '
                'the leave-one-company-out block is the estimate to report.',
    }


def to_markdown(r):
    o, n, h = r['old_product_fixed_0_5'], r['new_product_tuned_OPTIMISTIC'], r['new_product_leave_one_company_out_HONEST']
    lines = ['# What shipping per-category thresholds changed (Session 07)', '',
             f"{r['sentences']:,} validation sentences from {r['companies']} companies; {r['gold_labels']} labels marked by the annotators "
             f"({r['gold_labels_per_100_sentences']} per 100 sentences). Test split not read. "
             f"Scores identical between the two models (max difference {r['checks']['max_score_difference']:.1e}); only the thresholds changed.", '',
             '| | Old product (fixed 0.5) | New product, tuned on this split (optimistic) | New product, leave-one-company-out (honest) |',
             '|---|---:|---:|---:|']
    for key, name in (('macro_f1', 'Macro-F1'), ('micro_f1', 'Micro-F1'), ('flags_per_100_sentences', 'Flags per 100 sentences'),
                      ('correct_tags', 'Correct tags'), ('wrong_tags', 'Wrong tags'), ('missed_labels', 'Missed labels')):
        fmt = (lambda v: f'{v:.4f}') if 'f1' in key else (lambda v: f'{v}')
        lines.append(f'| {name} | {fmt(o[key])} | {fmt(n[key])} | **{fmt(h[key])}** |')
    lines += ['', '## Per category (old vs honest estimate)', '',
              '| Category | Threshold | Support | Precision | Recall | Wrong tags | Missed labels |', '|---|---:|---:|---|---|---|---|']
    for label in LABELS:
        a, b = o['per_category'][label], h['per_category'][label]
        lines.append(f"| {label} | {n['thresholds'][label]:.2f} | {a['support']} | {a['precision']:.3f} → {b['precision']:.3f} | "
                     f"{a['recall']:.3f} → {b['recall']:.3f} | {a['wrong_tags']} → {b['wrong_tags']} | {a['missed_labels']} → {b['missed_labels']} |")
    lines += ['', f"New product model: `{n['model_id']}`. Old product model: `{o['model_id']}`.", '',
              'Read the honest column. Fewer wrong tags came with more missed labels: a sentence the old model flagged '
              'correctly may now have no flag, which is why "no flag" must never be read as "safe".']
    return '\n'.join(lines) + '\n'


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.parse_args(argv)
    try:
        r = compare()
    except (CompareError, FileNotFoundError, KeyError) as e:
        print(f'STOPPED: {e}', file=sys.stderr)
        return 1
    out = ROOT / OUT
    out.parent.mkdir(parents=True, exist_ok=True)
    out.with_suffix('.json').write_text(json.dumps(r, indent=2) + '\n', encoding='utf-8')
    out.with_suffix('.md').write_text(to_markdown(r), encoding='utf-8')
    o, n, h = r['old_product_fixed_0_5'], r['new_product_tuned_OPTIMISTIC'], r['new_product_leave_one_company_out_HONEST']
    print('Checks passed: same sentences, identical scores, app runs the evaluated tuned model, thresholds = Session 05 experiment.')
    print(f"{'':28}{'old 0.5':>10}{'tuned*':>10}{'honest':>10}")
    for key in ('macro_f1', 'flags_per_100_sentences', 'correct_tags', 'wrong_tags', 'missed_labels'):
        print(f'{key:28}{o[key]:>10}{n[key]:>10}{h[key]:>10}')
    print('* tuned on this same split: optimistic. Report the honest column.')
    print(f'Wrote {OUT}.json and {OUT}.md')
    return 0


if __name__ == '__main__':
    sys.exit(main())
