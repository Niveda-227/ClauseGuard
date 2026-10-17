"""Heading and short-fragment filter: a TRIAL, not a product change (Session 07).

    python scripts/fragment_trial.py

The mid-semester decision memo (docs/decisions/2026-10-06_midpoint_decision.md, section 5)
promised to "trial a filter for headings and short fragments that receive tags". This script
measures what such a filter WOULD do to the product's validation predictions. It changes nothing
in the app.

Candidate filters (fixed before looking at any result; listed in CANDIDATES below):
  fewer_than_N_words  the sentence has fewer than N words (N = 3, 4, 5, 6)
  no_lowercase        the sentence has letters but none in lower case (an ALL-CAPS heading)
  short_no_end_mark   8 words or fewer AND it does not end with . ! ? ; or :

For each candidate it counts, on the 2,275 validation sentences:
  - sentences the filter would hide from tagging
  - product flags on those sentences: how many are wrong tags (removed: good) and how many are
    correct tags (removed: bad)
  - annotator labels on those sentences (they could never be flagged again)

Pre-set rule (written before running): a candidate PASSES if it removes at least 5 wrong tags AND
no annotator label sits on any sentence it hides. If several pass, the recommendation is the one
that removes the most wrong tags (ties: the candidate listed first). Because the candidates are
compared on the same validation split, the counts are optimistic; a passing filter is a candidate
for Session 08, to be re-checked on new documents, not a proven improvement.

Reads the validation split (needs the dataset: python -m clauses.cli data) and
experiments/session07/tuned/predictions.jsonl. Writes experiments/session07/fragment_trial.json
and .md with counts only: no sentence text leaves this script. The test split is never read.
"""
import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

PREDICTIONS = 'experiments/session07/tuned/predictions.jsonl'
OUT = 'experiments/session07/fragment_trial'
MIN_WRONG_REMOVED = 5
END_MARKS = ('.', '!', '?', ';', ':')


class TrialError(ValueError):
    pass


def words(text):
    return len(text.split())


def fewer_than(n):
    return lambda text: words(text) < n


def no_lowercase(text):
    letters = [c for c in text if c.isalpha()]
    return bool(letters) and not any(c.islower() for c in letters)


def short_no_end_mark(text):
    stripped = text.strip().rstrip('"\')]')
    return words(text) <= 8 and not stripped.endswith(END_MARKS)


CANDIDATES = [
    ('fewer_than_3_words', 'fewer than 3 words', fewer_than(3)),
    ('fewer_than_4_words', 'fewer than 4 words', fewer_than(4)),
    ('fewer_than_5_words', 'fewer than 5 words', fewer_than(5)),
    ('fewer_than_6_words', 'fewer than 6 words', fewer_than(6)),
    ('no_lowercase', 'letters but no lower case (ALL-CAPS heading)', no_lowercase),
    ('short_no_end_mark', '8 words or fewer and no . ! ? ; : at the end', short_no_end_mark),
]


def read_predictions(path):
    rows = [json.loads(l) for l in Path(path).read_text(encoding='utf-8').splitlines() if l.strip()]
    if not rows:
        raise TrialError(f'{path} is empty.')
    if any(not r['id'].startswith('validation:') for r in rows):
        raise TrialError('Only validation predictions are allowed; the test split stays untouched.')
    return rows


def join(rows, predictions):
    """Pair every validation sentence with the product's prediction for it."""
    by_id = {p['id']: p for p in predictions}
    if set(by_id) != {r['id'] for r in rows}:
        raise TrialError('The predictions do not cover exactly the validation sentences.')
    pairs = []
    for r in rows:
        p = by_id[r['id']]
        if sorted(p['gold']) != sorted(r['labels']):
            raise TrialError(f"{r['id']}: labels in the predictions file differ from the dataset.")
        pairs.append((r['text'], set(r['labels']), set(p['predicted'])))
    return pairs


def measure(pairs, rule):
    hidden = [(gold, pred) for text, gold, pred in pairs if rule(text)]
    return {
        'sentences_hidden': len(hidden),
        'flags_removed': sum(len(pred) for _, pred in hidden),
        'wrong_tags_removed': sum(len(pred - gold) for gold, pred in hidden),
        'correct_tags_removed': sum(len(pred & gold) for gold, pred in hidden),
        'annotator_labels_on_hidden_sentences': sum(len(gold) for gold, _ in hidden),
    }


def run(rows, predictions):
    pairs = join(rows, predictions)
    total_flags = sum(len(pred) for _, _, pred in pairs)
    total_wrong = sum(len(pred - gold) for _, gold, pred in pairs)
    results = []
    for key, description, rule in CANDIDATES:
        m = measure(pairs, rule)
        m.update({'candidate': key, 'description': description,
                  'passes': m['wrong_tags_removed'] >= MIN_WRONG_REMOVED and m['annotator_labels_on_hidden_sentences'] == 0})
        results.append(m)
    passing = [r for r in results if r['passes']]
    best = max(passing, key=lambda r: r['wrong_tags_removed']) if passing else None  # max keeps the first on ties
    lengths = [words(t) for t, _, _ in pairs]
    return {
        'sentences': len(pairs),
        'product_flags': total_flags,
        'product_wrong_tags': total_wrong,
        'sentences_under_6_words': sum(1 for n in lengths if n < 6),
        'candidates': results,
        'rule': f'PASS = removes at least {MIN_WRONG_REMOVED} wrong tags AND no annotator label on any hidden sentence',
        'recommendation': best['candidate'] if best else None,
        'note': 'Validation split only; counts are optimistic because the candidates are compared on the same split. '
                'Not shipped: a passing filter is a Session 08 candidate. No sentence text is stored.',
        'test_split_read': False,
    }


def to_markdown(r):
    lines = ['# Heading and short-fragment filter: trial (Session 07)', '',
             f"Product model (per-category thresholds) on {r['sentences']:,} validation sentences: "
             f"{r['product_flags']} flags, {r['product_wrong_tags']} of them wrong tags. "
             f"{r['sentences_under_6_words']} sentences have fewer than 6 words. Not shipped; the app is unchanged.", '',
             f"Rule set before running: {r['rule']}.", '',
             '| Candidate filter | Sentences hidden | Flags removed | Wrong tags removed | Correct tags removed | Annotator labels on hidden sentences | Passes |',
             '|---|---:|---:|---:|---:|---:|---|']
    for c in r['candidates']:
        lines.append(f"| {c['description']} | {c['sentences_hidden']} | {c['flags_removed']} | {c['wrong_tags_removed']} | "
                     f"{c['correct_tags_removed']} | {c['annotator_labels_on_hidden_sentences']} | {'yes' if c['passes'] else 'no'} |")
    rec = r['recommendation']
    lines += ['', f"**Result:** {'candidate for Session 08: ' + rec if rec else 'no candidate passes the rule; do not ship a fragment filter'}.", '',
              r['note']]
    return '\n'.join(lines) + '\n'


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.parse_args(argv)
    try:
        from clauses.data import load_split
        r = run(load_split('validation'), read_predictions(ROOT / PREDICTIONS))
    except (TrialError, FileNotFoundError, ValueError, KeyError) as e:
        print(f'STOPPED: {e}', file=sys.stderr)
        return 1
    out = ROOT / OUT
    out.parent.mkdir(parents=True, exist_ok=True)
    out.with_suffix('.json').write_text(json.dumps(r, indent=2) + '\n', encoding='utf-8')
    out.with_suffix('.md').write_text(to_markdown(r), encoding='utf-8')
    print(f"{r['product_flags']} product flags on {r['sentences']} validation sentences, {r['product_wrong_tags']} wrong tags.")
    print(f"{'candidate':24}{'hidden':>8}{'wrong-':>8}{'correct-':>10}{'labels':>8}  passes")
    for c in r['candidates']:
        print(f"{c['candidate']:24}{c['sentences_hidden']:>8}{c['wrong_tags_removed']:>8}{c['correct_tags_removed']:>10}"
              f"{c['annotator_labels_on_hidden_sentences']:>8}  {'yes' if c['passes'] else 'no'}")
    print(f"Recommendation: {r['recommendation'] or 'none passes; do not ship a fragment filter'}")
    print(f'Wrote {OUT}.json and {OUT}.md (counts only, no sentence text)')
    return 0


if __name__ == '__main__':
    sys.exit(main())
