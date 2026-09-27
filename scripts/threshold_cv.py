"""Leave-one-company-out estimate of per-category threshold tuning.

The model's built-in tune() picks thresholds on the validation split and then scoring
on that same split makes the gain look better than it is. This script gives an honest
estimate from the committed validation predictions (no dataset download needed):

  for each of the 10 validation companies:
      tune one threshold per category on the other 9 companies
      apply those thresholds to the held-out company
  pool the held-out predictions and compute F1

It reports three numbers side by side: fixed 0.5 (what ships today), tuned-and-scored
in-sample (optimistic), and leave-one-company-out (the honest estimate).
The final test split is never read.
"""
import argparse
import json
import sys
from pathlib import Path

import numpy as np
from sklearn.metrics import f1_score, precision_score, recall_score

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from clauses.schema import LABELS  # noqa: E402

GRID = np.round(np.arange(0.10, 0.91, 0.05), 2)


def load_predictions(path):
    rows = [json.loads(line) for line in Path(path).read_text(encoding='utf-8').splitlines() if line.strip()]
    if not rows:
        raise ValueError('No predictions found.')
    if any(not r['id'].startswith('validation:') for r in rows):
        raise ValueError('Only validation predictions are allowed. The test split must stay untouched.')
    y = np.array([[int(l in r['gold']) for l in LABELS] for r in rows], dtype=int)
    scores = np.array([r['scores'] for r in rows], dtype=float)
    groups = np.array([r['document_id'] for r in rows])
    return y, scores, groups


def best_threshold(y_col, s_col):
    """Same rule as clauses.model.tune: maximise F1, prefer the higher threshold on ties."""
    results = [(f1_score(y_col, s_col > t, zero_division=0), float(t)) for t in GRID]
    return max(results)[1]


def decide(scores, thresholds):
    # Same strict comparison as clauses.model.predict_rows.
    return (scores > np.asarray(thresholds)).astype(int)


def per_label(y, pred):
    out = {}
    for k, label in enumerate(LABELS):
        out[label] = {
            'support': int(y[:, k].sum()),
            'precision': round(float(precision_score(y[:, k], pred[:, k], zero_division=0)), 4),
            'recall': round(float(recall_score(y[:, k], pred[:, k], zero_division=0)), 4),
            'f1': round(float(f1_score(y[:, k], pred[:, k], zero_division=0)), 4),
        }
    return out


def summary(y, pred):
    return {
        'macro_f1': round(float(f1_score(y, pred, average='macro', zero_division=0)), 4),
        'micro_f1': round(float(f1_score(y, pred, average='micro', zero_division=0)), 4),
        'flags_per_100_sentences': round(100 * float(pred.sum()) / len(pred), 2),
        'per_label': per_label(y, pred),
    }


def run(path):
    y, scores, groups = load_predictions(path)
    companies = sorted(set(groups))
    if len(companies) < 3:
        raise ValueError('Need at least 3 companies for leave-one-company-out.')

    fixed = decide(scores, [0.5] * len(LABELS))
    in_sample_t = [best_threshold(y[:, k], scores[:, k]) for k in range(len(LABELS))]
    in_sample = decide(scores, in_sample_t)

    held_out = np.zeros_like(y)
    fold_thresholds = {}
    for company in companies:
        test = groups == company
        train = ~test
        t = [best_threshold(y[train, k], scores[train, k]) for k in range(len(LABELS))]
        fold_thresholds[company] = t
        held_out[test] = decide(scores[test], t)

    spread = {label: [min(f[k] for f in fold_thresholds.values()), max(f[k] for f in fold_thresholds.values())]
              for k, label in enumerate(LABELS)}
    return {
        'source': str(path),
        'sentences': int(len(y)),
        'companies': companies,
        'fixed_0_5': summary(y, fixed),
        'tuned_in_sample_OPTIMISTIC': {**summary(y, in_sample), 'thresholds': dict(zip(LABELS, in_sample_t))},
        'leave_one_company_out_HONEST': {**summary(y, held_out), 'threshold_range_across_folds': spread},
        'note': 'Validation predictions only. In-sample tuning is optimistic by construction; '
                'the leave-one-company-out row is the estimate to report.',
    }


def to_markdown(r):
    fx, ins, cv = r['fixed_0_5'], r['tuned_in_sample_OPTIMISTIC'], r['leave_one_company_out_HONEST']
    lines = [
        '# Per-category threshold experiment (Session 05)', '',
        f"Source: `{r['source']}` · {r['sentences']} validation sentences · {len(r['companies'])} companies.",
        'Final test split not read.', '',
        '| Decision rule | Macro-F1 | Micro-F1 | Flags per 100 sentences |',
        '|---|---:|---:|---:|',
        f"| Fixed 0.5 (ships today) | {fx['macro_f1']:.4f} | {fx['micro_f1']:.4f} | {fx['flags_per_100_sentences']} |",
        f"| Tuned and scored on the same data (optimistic) | {ins['macro_f1']:.4f} | {ins['micro_f1']:.4f} | {ins['flags_per_100_sentences']} |",
        f"| **Leave-one-company-out (honest)** | **{cv['macro_f1']:.4f}** | **{cv['micro_f1']:.4f}** | {cv['flags_per_100_sentences']} |",
        '', '## Per category: fixed 0.5 vs leave-one-company-out', '',
        '| Category | Support | P (0.5) | R (0.5) | F1 (0.5) | P (LOCO) | R (LOCO) | F1 (LOCO) | Threshold range across folds |',
        '|---|---:|---:|---:|---:|---:|---:|---:|---|',
    ]
    for label in LABELS:
        a, b = fx['per_label'][label], cv['per_label'][label]
        lo, hi = cv['threshold_range_across_folds'][label]
        lines.append(f"| {label} | {a['support']} | {a['precision']:.3f} | {a['recall']:.3f} | {a['f1']:.3f} | "
                     f"{b['precision']:.3f} | {b['recall']:.3f} | {b['f1']:.3f} | {lo:.2f}–{hi:.2f} |")
    lines += ['', 'A wide threshold range across folds means the tuned value depends on which companies it was tuned on, '
              'so it may not transfer to unseen documents.']
    return '\n'.join(lines) + '\n'


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument('--predictions', default='experiments/session04/hybrid/predictions.jsonl')
    p.add_argument('--out-dir', default='experiments/session05')
    a = p.parse_args()
    try:
        result = run(a.predictions)
    except (ValueError, OSError, KeyError) as e:
        p.exit(2, f'Experiment not run: {e}\n')
    out = Path(a.out_dir); out.mkdir(parents=True, exist_ok=True)
    (out / 'threshold_cv.json').write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
    (out / 'threshold_cv.md').write_text(to_markdown(result), encoding='utf-8')
    fx, ins, cv = result['fixed_0_5'], result['tuned_in_sample_OPTIMISTIC'], result['leave_one_company_out_HONEST']
    print(f"Fixed 0.5 macro-F1:                 {fx['macro_f1']:.4f}")
    print(f"Tuned in-sample macro-F1 (optimistic): {ins['macro_f1']:.4f}")
    print(f"Leave-one-company-out macro-F1:      {cv['macro_f1']:.4f}")
    print(f"Wrote {out / 'threshold_cv.json'} and {out / 'threshold_cv.md'}")


if __name__ == '__main__':
    main()
