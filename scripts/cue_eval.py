"""What the Session 08 review cues show on the validation split (no dataset download needed).

    python scripts/cue_eval.py

Session 08 added two cues to what users see (clauses/cues.py, margin 0.05, fixed in advance):
  uncertain  a flag whose score is less than 0.05 above its category's cut-off
  possible   a category whose score is less than 0.05 below its cut-off (not flagged)

This script measures, on the committed validation predictions of the product model
(experiments/session07/tuned/predictions.jsonl; the model and cut-offs did not change in Session 08):
  - how many possible cues appear (per 100 sentences), and how many of them are annotator labels
  - how many of the annotator labels that get NO flag ("missed labels") a possible cue points to
  - whether uncertain flags are wrong more often than the other flags

Two columns, as in Session 07:
  product cut-offs     the cut-offs in artifacts/selected.json, tuned on this same split (optimistic)
  leave-one-company-out  for each of the 10 companies, cut-offs tuned on the other 9 (honest estimate)

Pre-set rule, written before this script was first run: the cue display is KEPT if, in the
honest column at margin 0.05,
  (a) possible cues point to at least 10% of the missed labels, AND
  (b) possible cues add at most 5 per 100 sentences.
Margins 0.03 and 0.10 are shown for sensitivity only; they are never used to pick a margin.

Writes experiments/session08/cue_eval.json and .md (counts only, no sentence text). The test split
is never read.
"""
import argparse
import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from clauses.cues import MARGIN  # noqa: E402
from clauses.schema import LABELS  # noqa: E402
from scripts.threshold_cv import best_threshold, decide, load_predictions  # noqa: E402

PREDICTIONS = 'experiments/session07/tuned/predictions.jsonl'
METRICS = 'experiments/session07/tuned/metrics.json'
SELECTED = 'artifacts/selected.json'
OUT = 'experiments/session08/cue_eval'
SENSITIVITY = [0.03, 0.10]
MIN_COVERAGE = 0.10          # rule (a): share of missed labels a possible cue points to
MAX_POSSIBLE_PER_100 = 5.0   # rule (b): possible cues per 100 sentences


class CueEvalError(ValueError):
    pass


def cues(scores, cuts, margin):
    """Boolean matrices (uncertain, possible) with the same rule as clauses/cues.py."""
    cuts = np.asarray(cuts, dtype=float)
    flagged = scores > cuts
    uncertain = flagged & (scores - cuts < margin)
    possible = ~flagged & (cuts - scores < margin)
    return flagged, uncertain, possible


def measure(y, flagged, uncertain, possible):
    gold = y.astype(bool)
    n = len(y)
    missed = gold & ~flagged
    wrong = flagged & ~gold
    confident = flagged & ~uncertain
    out = {
        'sentences': int(n),
        'annotator_labels': int(gold.sum()),
        'flags': int(flagged.sum()),
        'missed_labels': int(missed.sum()),
        'possible_cues': int(possible.sum()),
        'possible_cues_per_100_sentences': round(100 * float(possible.sum()) / n, 2),
        'possible_cues_that_are_annotator_labels': int((possible & gold).sum()),
        'missed_labels_with_a_possible_cue': int((possible & missed).sum()),
        'share_of_missed_labels_with_a_possible_cue': round(float((possible & missed).sum()) / max(1, int(missed.sum())), 4),
        'sentences_with_any_cue_per_100': round(100 * float((possible | uncertain).any(axis=1).sum()) / n, 2),
        'uncertain_flags': int(uncertain.sum()),
        'wrong_share_of_uncertain_flags': round(float((uncertain & wrong).sum()) / max(1, int(uncertain.sum())), 4),
        'wrong_share_of_other_flags': round(float((confident & wrong).sum()) / max(1, int(confident.sum())), 4),
    }
    out['per_category'] = {
        label: {
            'missed_labels': int(missed[:, k].sum()),
            'possible_cues': int(possible[:, k].sum()),
            'missed_labels_with_a_possible_cue': int((possible[:, k] & missed[:, k]).sum()),
            'uncertain_flags': int(uncertain[:, k].sum()),
        } for k, label in enumerate(LABELS)
    }
    return out


def honest_cuts(y, scores, groups):
    """Per sentence, the cut-offs tuned without that sentence's company (leave-one-company-out)."""
    cuts = np.zeros_like(scores)
    for company in sorted(set(groups)):
        test = groups == company
        train = ~test
        cuts[test] = [best_threshold(y[train, k], scores[train, k]) for k in range(len(LABELS))]
    return cuts


def run(root=ROOT):
    root = Path(root)
    y, scores, groups = load_predictions(root / PREDICTIONS)
    selected = json.loads((root / SELECTED).read_text(encoding='utf-8'))
    metrics = json.loads((root / METRICS).read_text(encoding='utf-8'))
    if metrics.get('model_id') != selected.get('artifact_sha256'):
        raise CueEvalError('The predictions are not from the model the app runs (artifacts/selected.json).')
    product_cuts = np.asarray(selected['thresholds'], dtype=float)
    rows = [json.loads(l) for l in (root / PREDICTIONS).read_text(encoding='utf-8').splitlines() if l.strip()]
    expected = [[l for l, s, t in zip(LABELS, r['scores'], product_cuts) if s > t] for r in rows]
    if expected != [r['predicted'] for r in rows]:
        raise CueEvalError('Stored predictions do not match scores > product cut-offs.')

    loco = honest_cuts(y, scores, groups)
    columns = {}
    for margin in [MARGIN] + SENSITIVITY:
        columns[f'{margin:.2f}'] = {
            'product_cut_offs_OPTIMISTIC': measure(y, *cues(scores, product_cuts, margin)),
            'leave_one_company_out_HONEST': measure(y, *cues(scores, loco, margin)),
        }
    honest = columns[f'{MARGIN:.2f}']['leave_one_company_out_HONEST']
    a = honest['share_of_missed_labels_with_a_possible_cue'] >= MIN_COVERAGE
    b = honest['possible_cues_per_100_sentences'] <= MAX_POSSIBLE_PER_100
    return {
        'source': PREDICTIONS,
        'model_id': selected['artifact_sha256'],
        'product_margin': MARGIN,
        'margins': columns,
        'rule': (f'KEEP if, honest column at margin {MARGIN}: possible cues point to at least '
                 f'{int(MIN_COVERAGE * 100)}% of missed labels AND add at most {MAX_POSSIBLE_PER_100:g} per 100 sentences'),
        'rule_a_coverage_passed': bool(a),
        'rule_b_volume_passed': bool(b),
        'decision': 'KEEP the cue display' if a and b else 'RECONSIDER the cue display in Session 09',
        'note': 'Validation split only; the test split is never read. Margins other than the product margin are '
                'sensitivity checks, not candidates. No sentence text is stored.',
        'test_split_read': False,
    }


def to_markdown(r):
    m = r['margins'][f"{r['product_margin']:.2f}"]
    opt, hon = m['product_cut_offs_OPTIMISTIC'], m['leave_one_company_out_HONEST']
    rows = [
        ('Annotator labels', 'annotator_labels'),
        ('Flags', 'flags'),
        ('Missed labels (annotator label, no flag)', 'missed_labels'),
        ('Possible cues', 'possible_cues'),
        ('Possible cues per 100 sentences', 'possible_cues_per_100_sentences'),
        ('Possible cues that are annotator labels', 'possible_cues_that_are_annotator_labels'),
        ('Missed labels with a possible cue', 'missed_labels_with_a_possible_cue'),
        ('Share of missed labels with a possible cue', 'share_of_missed_labels_with_a_possible_cue'),
        ('Sentences with any cue, per 100', 'sentences_with_any_cue_per_100'),
        ('Uncertain flags', 'uncertain_flags'),
        ('Wrong share of uncertain flags', 'wrong_share_of_uncertain_flags'),
        ('Wrong share of the other flags', 'wrong_share_of_other_flags'),
    ]
    lines = ['# Review cues near a cut-off: what they show (Session 08)', '',
             f"Product model `{r['model_id'][:12]}` on the validation split ({opt['sentences']:,} sentences). "
             f"Margin {r['product_margin']} (`clauses/cues.py`, fixed in advance). The test split is not read.", '',
             '| | Product cut-offs (optimistic) | Leave-one-company-out (honest) |', '|---|---:|---:|']
    lines += [f'| {name} | {opt[key]} | {hon[key]} |' for name, key in rows]
    lines += ['', '**Per category (honest column):**', '',
              '| Category | Missed labels | Possible cues | Missed labels with a possible cue | Uncertain flags |',
              '|---|---:|---:|---:|---:|']
    for label, c in hon['per_category'].items():
        lines.append(f"| {label} | {c['missed_labels']} | {c['possible_cues']} | {c['missed_labels_with_a_possible_cue']} | {c['uncertain_flags']} |")
    lines += ['', '**Sensitivity only (honest column; never used to choose the margin):**', '',
              '| Margin | Possible cues per 100 sentences | Share of missed labels with a possible cue |', '|---:|---:|---:|']
    for key, col in r['margins'].items():
        h = col['leave_one_company_out_HONEST']
        lines.append(f"| {key} | {h['possible_cues_per_100_sentences']} | {h['share_of_missed_labels_with_a_possible_cue']} |")
    lines += ['', f"Rule set before running: {r['rule']}.", '',
              f"**Result:** {r['decision']} (coverage {'passed' if r['rule_a_coverage_passed'] else 'failed'}, "
              f"volume {'passed' if r['rule_b_volume_passed'] else 'failed'}).", '', r['note']]
    return '\n'.join(lines) + '\n'


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.parse_args(argv)
    try:
        r = run(ROOT)
    except (CueEvalError, FileNotFoundError, KeyError, ValueError) as e:
        print(f'STOPPED: {e}', file=sys.stderr)
        return 1
    out = ROOT / OUT
    out.parent.mkdir(parents=True, exist_ok=True)
    out.with_suffix('.json').write_text(json.dumps(r, indent=2) + '\n', encoding='utf-8')
    out.with_suffix('.md').write_text(to_markdown(r), encoding='utf-8')
    hon = r['margins'][f"{r['product_margin']:.2f}"]['leave_one_company_out_HONEST']
    print(f"Honest column, margin {r['product_margin']}: {hon['possible_cues_per_100_sentences']} possible cues per 100 sentences; "
          f"{hon['missed_labels_with_a_possible_cue']} of {hon['missed_labels']} missed labels have a possible cue "
          f"({100 * hon['share_of_missed_labels_with_a_possible_cue']:.1f}%).")
    print(f"Uncertain flags wrong: {100 * hon['wrong_share_of_uncertain_flags']:.1f}%  vs other flags: "
          f"{100 * hon['wrong_share_of_other_flags']:.1f}%")
    print(f"Result: {r['decision']}")
    print(f'Wrote {OUT}.json and {OUT}.md (counts only, no sentence text)')
    return 0


if __name__ == '__main__':
    sys.exit(main())
