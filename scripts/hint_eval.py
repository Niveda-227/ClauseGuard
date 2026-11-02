"""Do the search words reach the clauses the model misses? (Session 09, validation split)

    python -m clauses.cli data        # once: the dataset is needed for the sentence text
    python scripts/hint_eval.py

The web app's "Check it yourself" panel (clauses/absence.py) lists, per category, the sentences that
are NOT flagged for that category but contain one of its search words. This script measures that
list on the validation split, with the product model's committed predictions
(experiments/session07/tuned/predictions.jsonl; the model and cut-offs did not change since then)
and the sentence text from the dataset.

Definitions:
  mark          a sentence that is not flagged for category k but contains a search word of k
  missed label  an annotator label that gets no flag

Two columns, as in scripts/cue_eval.py:
  optimistic  the product cut-offs in artifacts/selected.json, tuned on this same split
  honest      for each of the 10 companies, cut-offs tuned on the other 9 (leave-one-company-out)

Pre-set rule, written on Oct 27, 2026 before the first run (also in
docs/decisions/2026-10-28_cue_decision.md): the worth-a-look list is KEPT if, in the honest column,
  (a) the marks reach at least 40% of the missed labels, AND
  (b) the marks add at most 20 per 100 sentences.
Otherwise it is RECONSIDERED in Session 10. The search words were written before any validation
run and are never edited to change this result.

Checks that the prediction IDs and gold labels line up with load_split('validation') before
measuring. Writes experiments/session09/hint_eval.json and .md: counts only, no sentence text.
The test split is never read.
"""
import argparse
import hashlib
import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from clauses.absence import SEARCH_WORDS, search_hits  # noqa: E402
from clauses.schema import LABELS  # noqa: E402
from scripts.cue_eval import honest_cuts  # noqa: E402
from scripts.threshold_cv import load_predictions  # noqa: E402

PREDICTIONS = 'experiments/session07/tuned/predictions.jsonl'
METRICS = 'experiments/session07/tuned/metrics.json'
SELECTED = 'artifacts/selected.json'
OUT = 'experiments/session09/hint_eval'
MIN_COVERAGE = 0.40        # rule (a): share of missed labels that get a mark
MAX_MARKS_PER_100 = 20.0   # rule (b): marks per 100 sentences


class HintEvalError(ValueError):
    pass


def words_fingerprint():
    """SHA-256 of the search-word list, so the result names exactly the list it measured."""
    return hashlib.sha256(json.dumps(SEARCH_WORDS, sort_keys=True).encode('utf-8')).hexdigest()


def hit_matrix(texts):
    """n x 8 booleans: does sentence i contain a search word of category k?"""
    out = np.zeros((len(texts), len(LABELS)), dtype=bool)
    for i, text in enumerate(texts):
        for label in search_hits(text):
            out[i, LABELS.index(label)] = True
    return out


def measure(y, flagged, hits):
    gold = y.astype(bool)
    n = len(y)
    missed = gold & ~flagged
    marks = hits & ~flagged
    reached = marks & missed
    out = {
        'sentences': int(n),
        'annotator_labels': int(gold.sum()),
        'flags': int(flagged.sum()),
        'missed_labels': int(missed.sum()),
        'marks': int(marks.sum()),
        'marks_per_100_sentences': round(100 * float(marks.sum()) / n, 2),
        'sentences_with_any_mark_per_100': round(100 * float(marks.any(axis=1).sum()) / n, 2),
        'missed_labels_with_a_mark': int(reached.sum()),
        'share_of_missed_labels_with_a_mark': round(float(reached.sum()) / max(1, int(missed.sum())), 4),
        'percent_of_missed_labels_with_a_mark': round(100 * float(reached.sum()) / max(1, int(missed.sum())), 1),
        'marks_that_are_annotator_labels': int((marks & gold).sum()),
        'percent_of_marks_that_are_annotator_labels': round(100 * float((marks & gold).sum()) / max(1, int(marks.sum())), 1),
    }
    out['per_category'] = {
        label: {
            'missed_labels': int(missed[:, k].sum()),
            'marks': int(marks[:, k].sum()),
            'missed_labels_with_a_mark': int(reached[:, k].sum()),
        } for k, label in enumerate(LABELS)
    }
    return out


def validation_texts(rows, split_rows):
    """Sentence text for each prediction, after checking IDs and gold labels against the dataset."""
    by_id = {r['id']: r for r in split_rows}
    if len(by_id) != len(rows) or set(by_id) != {r['id'] for r in rows}:
        raise HintEvalError('The prediction IDs do not match the validation split of the dataset.')
    texts = []
    for r in rows:
        source = by_id[r['id']]
        if sorted(source['labels']) != sorted(r['gold']) or source['document_id'] != r['document_id']:
            raise HintEvalError(f"Gold labels or company differ from the dataset for {r['id']}.")
        texts.append(source['text'])
    return texts


def run(root=ROOT, split_rows=None):
    root = Path(root)
    y, scores, groups = load_predictions(root / PREDICTIONS)
    rows = [json.loads(l) for l in (root / PREDICTIONS).read_text(encoding='utf-8').splitlines() if l.strip()]
    selected = json.loads((root / SELECTED).read_text(encoding='utf-8'))
    metrics = json.loads((root / METRICS).read_text(encoding='utf-8'))
    if metrics.get('model_id') != selected.get('artifact_sha256'):
        raise HintEvalError('The predictions are not from the model the app runs (artifacts/selected.json).')
    product_cuts = np.asarray(selected['thresholds'], dtype=float)
    expected = [[l for l, s, t in zip(LABELS, r['scores'], product_cuts) if s > t] for r in rows]
    if expected != [r['predicted'] for r in rows]:
        raise HintEvalError('Stored predictions do not match scores > product cut-offs.')
    if split_rows is None:
        from clauses.data import load_split
        split_rows = load_split('validation')
    hits = hit_matrix(validation_texts(rows, split_rows))

    optimistic = measure(y, scores > product_cuts, hits)
    honest = measure(y, scores > honest_cuts(y, scores, groups), hits)
    a = honest['share_of_missed_labels_with_a_mark'] >= MIN_COVERAGE
    b = honest['marks_per_100_sentences'] <= MAX_MARKS_PER_100
    return {
        'source': PREDICTIONS,
        'model_id': selected['artifact_sha256'],
        'search_words': 'clauses/absence.py SEARCH_WORDS',
        'search_words_sha256': words_fingerprint(),
        'optimistic': optimistic,
        'honest': honest,
        'rule': (f'KEEP if, honest column: marks reach at least {int(MIN_COVERAGE * 100)}% of missed labels '
                 f'AND add at most {MAX_MARKS_PER_100:g} per 100 sentences'),
        'min_coverage': MIN_COVERAGE,
        'max_marks_per_100_sentences': MAX_MARKS_PER_100,
        'rule_a_coverage_passed': bool(a),
        'rule_b_volume_passed': bool(b),
        'coverage_result': 'passed' if a else 'failed',
        'volume_result': 'passed' if b else 'failed',
        'decision': 'KEEP the worth-a-look list' if a and b else 'RECONSIDER the worth-a-look list in Session 10',
        'note': ('Validation split only; the test split is never read. No sentence text is stored. UNFAIR-ToS '
                 'labels only potentially unfair clauses, so many marks are on-topic but fair sentences.'),
        'test_split_read': False,
    }


def to_markdown(r):
    opt, hon = r['optimistic'], r['honest']
    rows = [
        ('Annotator labels', 'annotator_labels'),
        ('Flags', 'flags'),
        ('Missed labels (annotator label, no flag)', 'missed_labels'),
        ('Marks (not flagged, contains a search word)', 'marks'),
        ('Marks per 100 sentences', 'marks_per_100_sentences'),
        ('Sentences with any mark, per 100', 'sentences_with_any_mark_per_100'),
        ('Missed labels with a mark', 'missed_labels_with_a_mark'),
        ('Percent of missed labels with a mark', 'percent_of_missed_labels_with_a_mark'),
        ('Marks that are annotator labels', 'marks_that_are_annotator_labels'),
        ('Percent of marks that are annotator labels', 'percent_of_marks_that_are_annotator_labels'),
    ]
    lines = ['# Do the search words reach the clauses the model misses? (Session 09)', '',
             f"Product model `{r['model_id'][:12]}` on the validation split ({opt['sentences']:,} sentences). "
             f"Search words: `clauses/absence.py` (SHA-256 of the list `{r['search_words_sha256'][:12]}`), written "
             'before any validation run. The test split is not read.', '',
             '| | Product cut-offs (optimistic) | Leave-one-company-out (honest) |', '|---|---:|---:|']
    lines += [f'| {name} | {opt[key]} | {hon[key]} |' for name, key in rows]
    lines += ['', '**Per category (honest column):**', '',
              '| Category | Missed labels | Marks | Missed labels with a mark |', '|---|---:|---:|---:|']
    for label, c in hon['per_category'].items():
        lines.append(f"| {label} | {c['missed_labels']} | {c['marks']} | {c['missed_labels_with_a_mark']} |")
    lines += ['', f"Rule set before running: {r['rule']}.", '',
              f"**Result:** {r['decision']} (coverage {'passed' if r['rule_a_coverage_passed'] else 'failed'}, "
              f"volume {'passed' if r['rule_b_volume_passed'] else 'failed'}).", '', r['note']]
    return '\n'.join(lines) + '\n'


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.parse_args(argv)
    try:
        r = run(ROOT)
    except (HintEvalError, FileNotFoundError, KeyError, ValueError) as e:
        print(f'STOPPED: {e}', file=sys.stderr)
        return 1
    out = ROOT / OUT
    out.parent.mkdir(parents=True, exist_ok=True)
    out.with_suffix('.json').write_text(json.dumps(r, indent=2) + '\n', encoding='utf-8')
    out.with_suffix('.md').write_text(to_markdown(r), encoding='utf-8')
    for name in ('optimistic', 'honest'):
        c = r[name]
        print(f"{name:10s}: missed labels {c['missed_labels']}, marks {c['marks']} ({c['marks_per_100_sentences']} per 100 sentences), "
              f"missed labels with a mark {c['missed_labels_with_a_mark']} ({c['percent_of_missed_labels_with_a_mark']}%), "
              f"marks that are annotator labels {c['percent_of_marks_that_are_annotator_labels']}%")
    print(f"Result: {r['decision']} (coverage {'passed' if r['rule_a_coverage_passed'] else 'failed'}, "
          f"volume {'passed' if r['rule_b_volume_passed'] else 'failed'})")
    print(f'Wrote {OUT}.json and {OUT}.md (counts only, no sentence text)')
    return 0


if __name__ == '__main__':
    sys.exit(main())
