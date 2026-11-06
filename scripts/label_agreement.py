"""How much do the two annotators agree on the fresh Terms of Service? (Session 10)

    python scripts/label_agreement.py

Reads data/fresh_labels/A1/ and data/fresh_labels/A2/ (both must be complete; see
scripts/check_labels.py). For each of the eight categories, over all 376 sentences of the
three documents, it counts how often each annotator gave the category and how often both did,
and computes Cohen's kappa: agreement corrected for the agreement two annotators would reach by
chance (1 = perfect, 0 = no better than chance; it is not defined when neither annotator ever
gave the category). It also reports the pooled kappa over all categories and sentences.

It defines the two answer sets the evaluation uses (docs/decisions/2026-11-04_fresh_documents_rule.md):
  strict   a category counts for a sentence only when BOTH annotators gave it (decides the rules)
  lenient  it counts when EITHER annotator gave it (reported only)

Writes experiments/session10/label_agreement.json and .md: counts only, no sentence text.
"""
import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from clauses.labelling import documents, label_path  # noqa: E402
from clauses.schema import LABELS  # noqa: E402
from scripts.check_labels import PUBLISHED, check  # noqa: E402

OUT = 'experiments/session10/label_agreement'
PAIR = ('A1', 'A2')


class AgreementError(ValueError):
    pass


def load_labels(annotator, root=ROOT):
    """{doc_id: [set of categories per sentence]} for one annotator's published labels."""
    problems, _ = check(annotator, root, PUBLISHED)
    if any('missing' in p for p in problems) and all('missing' in p for p in problems):
        raise AgreementError(f'{annotator} labels are not in {PUBLISHED}/{annotator}/ yet.')
    if problems:
        raise AgreementError(f'{annotator} labels are not complete or not valid: {problems[0]}')
    out = {}
    for doc_id in documents(root):
        rec = json.loads(label_path(annotator, doc_id, root, PUBLISHED).read_text(encoding='utf-8'))
        out[doc_id] = [set(x['labels']) for x in rec['sentences']]
    return out


def gold(root=ROOT, mode='strict'):
    """{doc_id: [set of categories per sentence]}: strict = both annotators, lenient = either."""
    if mode not in ('strict', 'lenient'):
        raise ValueError('mode must be strict or lenient')
    a, b = (load_labels(x, root) for x in PAIR)
    return {d: [(x & y) if mode == 'strict' else (x | y) for x, y in zip(a[d], b[d])] for d in a}


def kappa(pairs):
    """Cohen's kappa for a list of (bool, bool), or None when it is not defined."""
    n = len(pairs)
    if n == 0:
        return None
    agree = sum(x == y for x, y in pairs) / n
    p1 = sum(x for x, _ in pairs) / n
    p2 = sum(y for _, y in pairs) / n
    expected = p1 * p2 + (1 - p1) * (1 - p2)
    if expected == 1:
        return None
    return round((agree - expected) / (1 - expected), 4)


def run(root=ROOT):
    a, b = (load_labels(x, root) for x in PAIR)
    docs = list(a)
    per_category, pooled = {}, []
    for label in LABELS:
        pairs = [(label in x, label in y) for d in docs for x, y in zip(a[d], b[d])]
        pooled += pairs
        per_category[label] = {
            'A1': sum(x for x, _ in pairs), 'A2': sum(y for _, y in pairs), 'both': sum(x and y for x, y in pairs),
            'either': sum(x or y for x, y in pairs), 'kappa': kappa(pairs),
        }
        per_category[label]['kappa_text'] = fmt(per_category[label]['kappa'])
    sentences = sum(len(a[d]) for d in docs)
    minutes = {x: check(x, root, PUBLISHED)[1]['seconds_active'] for x in PAIR}
    disagree = sum(x != y for d in docs for x, y in zip(a[d], b[d]))
    return {
        'documents': docs,
        'sentences': sentences,
        'annotators': {'A1': 'Hemanth (hreddy14)', 'A2': 'Jayakrishna (Jayakrishna-Reddy)'},
        'per_category': per_category,
        'pooled_kappa': kappa(pooled),
        'pooled_kappa_text': fmt(kappa(pooled)),
        'sentences_with_any_disagreement': disagree,
        'percent_sentences_with_any_disagreement': round(100 * disagree / sentences, 1),
        'minutes_labelling': {x: round(v / 60) for x, v in minutes.items()},
        'strict_labels': sum(c['both'] for c in per_category.values()),
        'lenient_labels': sum(c['either'] for c in per_category.values()),
        'note': 'Counts only, no sentence text. Strict = both annotators; lenient = either. Kappa is not defined (null) '
                'for a category neither annotator ever gave. The *_text fields give the same values as text for the report.',
    }


def fmt(k):
    return 'not defined' if k is None else f'{k:.2f}'


def to_markdown(r):
    lines = ['# Agreement between the two annotators on the fresh Terms of Service (Session 10)', '',
             f"{len(r['documents'])} documents ({', '.join(r['documents'])}), {r['sentences']} sentences. "
             f"A1 = {r['annotators']['A1']}, A2 = {r['annotators']['A2']}. Labelled independently with "
             '`docs/LABELLING_GUIDE.md`.', '',
             '| Category | A1 | A2 | Both (strict) | Either (lenient) | Cohen\'s kappa |', '|---|---:|---:|---:|---:|---:|']
    for label, c in r['per_category'].items():
        lines.append(f"| {label} | {c['A1']} | {c['A2']} | {c['both']} | {c['either']} | {fmt(c['kappa'])} |")
    lines += ['', f"Pooled kappa over all categories and sentences: {fmt(r['pooled_kappa'])}. "
              f"Sentences where the annotators gave different categories: {r['sentences_with_any_disagreement']} "
              f"({r['percent_sentences_with_any_disagreement']}%). Strict labels: {r['strict_labels']}; lenient labels: "
              f"{r['lenient_labels']}.", '', r['note']]
    return '\n'.join(lines) + '\n'


def main(argv=None):
    argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter).parse_args(argv)
    try:
        r = run(ROOT)
    except (AgreementError, ValueError, OSError) as e:
        print(f'STOPPED: {e}', file=sys.stderr)
        return 1
    out = ROOT / OUT
    out.parent.mkdir(parents=True, exist_ok=True)
    out.with_suffix('.json').write_text(json.dumps(r, indent=2) + '\n', encoding='utf-8')
    out.with_suffix('.md').write_text(to_markdown(r), encoding='utf-8')
    print(f"Pooled kappa {fmt(r['pooled_kappa'])}; strict labels {r['strict_labels']}, lenient labels {r['lenient_labels']}; "
          f"{r['sentences_with_any_disagreement']} of {r['sentences']} sentences with a disagreement.")
    print(f'Wrote {OUT}.json and {OUT}.md (counts only, no sentence text)')
    return 0


if __name__ == '__main__':
    sys.exit(main())
