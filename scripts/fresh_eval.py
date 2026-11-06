"""Does the shipped model hold up on fresh real Terms of Service? (Session 10)

    python scripts/fresh_eval.py

Runs the product model (artifacts/selected.joblib, the cut-offs in artifacts/selected.json) on the
three fresh documents in examples/fresh/ and compares it with the two annotators' labels in
data/fresh_labels/ (see scripts/label_agreement.py):

  strict   a category counts for a sentence only when BOTH annotators gave it. The rules use this.
  lenient  it counts when EITHER annotator gave it. Reported only; it decides nothing.

Definitions (the same as in Sessions 07-09):
  flag          the model's score for a category is above its cut-off
  wrong tag     a flag the answer set does not have;  missed label: an answer with no flag
  macro-F1      the mean of the per-category F1 over the categories that have at least one answer
                (a category nobody labelled has no F1 and is left out, as fixed in the rule)
  possible cue  not flagged, and the score is less than the margin below the cut-off (clauses/cues.py)
  mark          not flagged, but the sentence has a search word of the category (clauses/absence.py)
  zero-flag-only marks   marks kept only for categories with no flag anywhere in that document

The three rules were fixed on 2026-11-04 before any label existed (docs/decisions/fresh_rule.json);
this script reads them from that file and never changes them. The validation figure it compares
with is experiments/session07/threshold_ship_eval.json (honest, leave-one-company-out).

It also checks that no fresh company is one of the 50 UNFAIR-ToS companies (names only).
Writes experiments/session10/fresh_eval.json and .md: counts, sentence numbers and scores only,
no sentence text. Needs no dataset download.
"""
import argparse
import json
import re
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from clauses.absence import search_hits  # noqa: E402
from clauses.labelling import documents, load_document  # noqa: E402
from clauses.model import DEFAULT_MODEL, load, predict_rows  # noqa: E402
from clauses.schema import LABELS  # noqa: E402
from scripts.label_agreement import gold  # noqa: E402

RULE = 'docs/decisions/fresh_rule.json'
SELECTED = 'artifacts/selected.json'
OUT = 'experiments/session10/fresh_eval'
MARGINS = (0.05, 0.10)
# The 20 validation and test companies of UNFAIR-ToS (the 30 training companies are in
# artifacts/selected.json). Names only: tests/test_fresh_eval.py checks the validation names against
# the dataset; the test split itself is never read (it stays unread until Session 12).
VALIDATION_COMPANIES = ('Airbnb', 'Crowdtangle', 'Fitbit', 'Headspace', 'LindenLab', 'Nintendo', 'Oculus',
                        'Supercell', 'TripAdvisor', 'Vimeo')
TEST_COMPANIES = ('Academia', 'Amazon', 'Duolingo', 'Evernote', 'LinkedIn', 'Netflix', 'Snap', 'Twitter', 'Uber',
                  'eBay')


class FreshEvalError(ValueError):
    pass


def norm(name):
    return re.sub(r'[^a-z0-9]', '', name.lower())


def company_overlap(root=ROOT):
    """Fresh documents whose company or ID matches an UNFAIR-ToS company (should be empty)."""
    selected = json.loads((Path(root) / SELECTED).read_text(encoding='utf-8'))
    known = {norm(c) for c in list(selected['train_documents']) + list(VALIDATION_COMPANIES) + list(TEST_COMPANIES)}
    out = []
    for doc_id, d in documents(root).items():
        words = {norm(doc_id)} | {norm(w) for w in re.split(r'[\s()]+', d['company']) if w}
        if words & known or d.get('in_unfair_tos') is not False:
            out.append(doc_id)
    return out


def f1(tp, fp, fn):
    return round(2 * tp / (2 * tp + fp + fn), 4) if (2 * tp + fp + fn) else None


def possible(scores, flagged, cuts, margin):
    return ~flagged & (cuts - scores < margin)


def measure(y, flagged, scores, cuts, hits, doc_index):
    """All counts for one answer set. y, flagged, hits: n x 8 booleans; doc_index: document number per row."""
    n = len(y)
    missed = y & ~flagged
    out = {'sentences': int(n), 'answer_labels': int(y.sum()), 'flags': int(flagged.sum()),
           'correct_tags': int((y & flagged).sum()), 'wrong_tags': int((~y & flagged).sum()),
           'missed_labels': int(missed.sum()), 'flags_per_100_sentences': round(100 * int(flagged.sum()) / n, 2)}
    per = {}
    for k, label in enumerate(LABELS):
        tp, fp, fn = int((y[:, k] & flagged[:, k]).sum()), int((~y[:, k] & flagged[:, k]).sum()), int(missed[:, k].sum())
        per[label] = {'answers': int(y[:, k].sum()), 'flags': int(flagged[:, k].sum()), 'correct_tags': tp,
                      'wrong_tags': fp, 'missed_labels': fn, 'f1': f1(tp, fp, fn) if y[:, k].any() else None}
        per[label]['f1_text'] = num(per[label]['f1'])
    out['per_category'] = per
    used = [label for label in LABELS if per[label]['answers'] > 0]
    if not used:
        raise FreshEvalError('The answer set has no label at all, so macro-F1 is not defined.')
    out['categories_in_macro_f1'] = used
    out['macro_f1'] = round(sum(per[l]['f1'] for l in used) / len(used), 4)
    out['micro_f1'] = f1(out['correct_tags'], out['wrong_tags'], out['missed_labels'])
    out['wrong_tag_share'] = round(out['wrong_tags'] / out['flags'], 4) if out['flags'] else None

    def reach(extra, name):
        got, total = int((extra & missed).sum()), int(missed.sum())
        return {name: int(extra.sum()), f'{name}_per_100_sentences': round(100 * int(extra.sum()) / n, 2),
                'missed_labels_reached': got,
                'share_of_missed_labels_reached': round(got / total, 4) if total else None,
                'percent_of_missed_labels_reached': round(100 * got / total, 1) if total else None,
                'that_are_answers': int((extra & y).sum()),
                'reached_text': f'{got} of {total} (' + (f'{100 * got / total:.1f}%' if total else 'not defined') + ')'}

    out['possible_cues'] = {f'{m:.2f}': reach(possible(scores, flagged, cuts, m), 'cues') for m in MARGINS}
    marks = hits & ~flagged
    zero = np.zeros_like(flagged)
    for d in np.unique(doc_index):
        rows = doc_index == d
        zero[rows] = ~flagged[rows].any(axis=0)
    out['marks_all'] = reach(marks, 'marks')
    out['marks_zero_flag_only'] = reach(marks & zero, 'marks')
    return out


def errors(y, flagged, scores, cuts, sentence_numbers):
    """Every wrong tag and missed label: document, sentence number (from 1), category, score, cut-off."""
    out = []
    for i, k in zip(*np.nonzero(y ^ flagged)):
        doc_id, number = sentence_numbers[i]
        out.append({'document': doc_id, 'sentence': number, 'category': LABELS[k],
                    'kind': 'wrong tag' if flagged[i, k] else 'missed label',
                    'score': round(float(scores[i, k]), 3), 'cut_off': round(float(cuts[k]), 2)})
    return out


def decide(rule, strict, reference):
    r = rule['rules']
    shift = r['domain_shift']
    drop = round(reference - strict['macro_f1'], 4)
    ok = bool(drop <= shift['max_drop'] + 1e-9)
    out = {'domain_shift': {'fresh_macro_f1': strict['macro_f1'], 'validation_macro_f1': reference, 'drop': drop,
                            'max_drop': shift['max_drop'], 'passed': ok,
                            'result': shift['if_pass'] if ok else shift['if_fail'],
                            'summary': f"fresh macro-F1 {strict['macro_f1']:.4f} against {reference:.4f} on validation, "
                                       f"a drop of {drop:.4f} (the limit is {shift['max_drop']:.2f})"}}
    for name, block in (('cue_margin', strict['possible_cues']['0.10']), ('zero_flag_marks', strict['marks_zero_flag_only'])):
        spec = r[name]
        share = block['share_of_missed_labels_reached']
        per_100 = block['cues_per_100_sentences' if name == 'cue_margin' else 'marks_per_100_sentences']
        a = bool(share is not None and share >= spec['min_coverage'] - 1e-9)
        b = bool(per_100 <= spec['max_per_100'] + 1e-9)
        out[name] = {'share_of_missed_labels_reached': share, 'per_100_sentences': per_100,
                     'min_coverage': spec['min_coverage'], 'max_per_100': spec['max_per_100'],
                     'coverage_passed': a, 'volume_passed': b, 'passed': a and b,
                     'result': spec['if_pass'] if a and b else spec['if_fail']}
        limits = f"needs at least {100 * spec['min_coverage']:.0f}% and at most {spec['max_per_100']:.0f} per 100"
        if share is None:
            out[name]['note'] = 'No missed labels, so coverage cannot be measured; the rule keeps the current setting.'
            out[name]['summary'] = f'no missed labels, so coverage cannot be measured; {per_100:.2f} per 100 sentences ({limits})'
        else:
            out[name]['summary'] = (f"reach {100 * share:.1f}% of the missed labels ({block['missed_labels_reached']} of "
                                    f"{strict['missed_labels']}), {per_100:.2f} per 100 sentences ({limits})")
    return out


def run(root=ROOT, model_path=DEFAULT_MODEL):
    root = Path(root)
    overlap = company_overlap(root)
    if overlap:
        raise FreshEvalError(f'These documents are not fresh (company in UNFAIR-ToS or not marked): {overlap}')
    selected = json.loads((root / SELECTED).read_text(encoding='utf-8'))
    bundle = load(model_path)
    if bundle['model_id'] != selected['artifact_sha256']:
        raise FreshEvalError('The model file is not the one in artifacts/selected.json.')
    cuts = np.asarray(bundle['manifest']['thresholds'], dtype=float)
    if not np.allclose(cuts, selected['thresholds']):
        raise FreshEvalError('The model cut-offs differ from artifacts/selected.json.')
    rule = json.loads((root / RULE).read_text(encoding='utf-8'))
    ref_meta = rule['validation_reference']
    value = json.loads((root / ref_meta['source']).read_text(encoding='utf-8'))
    for part in ref_meta['key'].split('.'):
        value = value[part]
    reference = float(value)

    answer_sets = {mode: gold(root, mode) for mode in ('strict', 'lenient')}
    texts, numbers, doc_index, per_doc = [], [], [], {}
    for d, doc_id in enumerate(documents(root)):
        _, _, sentences = load_document(doc_id, root)
        if len(sentences) != len(answer_sets['strict'][doc_id]):
            raise FreshEvalError(f'{doc_id}: the labels do not cover every sentence.')
        texts += [s.text for s in sentences]
        numbers += [(doc_id, i + 1) for i in range(len(sentences))]
        doc_index += [d] * len(sentences)
        per_doc[doc_id] = len(sentences)
    scores, pred = predict_rows(bundle, texts)
    flagged = pred.astype(bool)
    hits = np.zeros_like(flagged)
    for i, t in enumerate(texts):
        for label in search_hits(t):
            hits[i, LABELS.index(label)] = True
    doc_index = np.asarray(doc_index)

    def matrix(mode):
        y = np.zeros_like(flagged)
        i = 0
        for doc_id in per_doc:
            for labels in answer_sets[mode][doc_id]:
                for label in labels:
                    y[i, LABELS.index(label)] = True
                i += 1
        return y

    results = {mode: measure(matrix(mode), flagged, scores, cuts, hits, doc_index) for mode in answer_sets}
    return {
        'model_id': bundle['model_id'],
        'cut_offs': [round(float(c), 2) for c in cuts],
        'documents': per_doc,
        'sentences': len(texts),
        'company_overlap_with_unfair_tos': overlap,
        'rule_file': RULE,
        'validation_reference': {'source': ref_meta['source'], 'key': ref_meta['key'], 'macro_f1': reference},
        'strict': results['strict'],
        'lenient': results['lenient'],
        'rules': decide(rule, results['strict'], reference),
        'errors_strict': errors(matrix('strict'), flagged, scores, cuts, numbers),
        'note': 'Counts, sentence numbers (from 1) and scores only, no sentence text. The rules use the strict answer '
                'set; lenient is reported only. Three documents and two team annotators: a small check. The *_text and '
                'summary fields give the same values as text for the report.',
    }


def pct(x):
    return 'not defined' if x is None else f'{100 * x:.1f}%'


def num(x, d=2):
    return 'not defined' if x is None else f'{x:.{d}f}'


def to_markdown(r):
    s, l, rules = r['strict'], r['lenient'], r['rules']
    lines = ['# The shipped model on fresh real Terms of Service (Session 10)', '',
             f"Model `{r['model_id'][:12]}`, product cut-offs. {len(r['documents'])} documents "
             f"({', '.join(f'{k} {v}' for k, v in r['documents'].items())} sentences), {r['sentences']} sentences. "
             'No company is in UNFAIR-ToS. Answers: two team annotators (see `label_agreement.md`).', '',
             '## Overall', '', '| | Strict (both annotators) | Lenient (either) |', '|---|---:|---:|']
    for name, key, d in (('Macro-F1 (categories with an answer)', 'macro_f1', 4), ('Micro-F1', 'micro_f1', 4),
                         ('Answer labels', 'answer_labels', 0), ('Flags', 'flags', 0), ('Correct tags', 'correct_tags', 0),
                         ('Wrong tags', 'wrong_tags', 0), ('Missed labels', 'missed_labels', 0),
                         ('Flags per 100 sentences', 'flags_per_100_sentences', 2)):
        lines.append(f'| {name} | {num(s[key], d)} | {num(l[key], d)} |')
    lines += ['', f"Validation macro-F1 (honest, Session 07): {r['validation_reference']['macro_f1']:.4f}. "
              f"Categories in the strict macro-F1: {', '.join(s['categories_in_macro_f1'])}.", '',
              '## Per category (strict)', '', '| Category | Answers | Flags | Correct | Wrong | Missed | F1 |',
              '|---|---:|---:|---:|---:|---:|---:|']
    for label, c in s['per_category'].items():
        lines.append(f"| {label} | {c['answers']} | {c['flags']} | {c['correct_tags']} | {c['wrong_tags']} | "
                     f"{c['missed_labels']} | {num(c['f1'])} |")
    lines += ['', '## Help for missed clauses (strict)', '',
              '| What the user sees | How many | Per 100 sentences | Missed labels reached |', '|---|---:|---:|---:|']
    for m in ('0.05', '0.10'):
        c = s['possible_cues'][m]
        lines.append(f"| Possible cues, margin {m} | {c['cues']} | {c['cues_per_100_sentences']:.2f} | "
                     f"{c['missed_labels_reached']} of {s['missed_labels']} ({pct(c['share_of_missed_labels_reached'])}) |")
    for name, key in (('Worth-a-look marks, all', 'marks_all'), ('Worth-a-look marks, zero-flag categories only', 'marks_zero_flag_only')):
        c = s[key]
        lines.append(f"| {name} | {c['marks']} | {c['marks_per_100_sentences']:.2f} | "
                     f"{c['missed_labels_reached']} of {s['missed_labels']} ({pct(c['share_of_missed_labels_reached'])}) |")
    ds = rules['domain_shift']
    lines += ['', '## The three pre-set rules (strict answers)', '',
              f"- **Domain shift:** fresh macro-F1 {ds['fresh_macro_f1']:.4f} against {ds['validation_macro_f1']:.4f}, "
              f"a drop of {ds['drop']:.4f} (the limit is {ds['max_drop']:.2f}). Result: **{ds['result']}**."]
    for name, title in (('cue_margin', 'Cue margin 0.10'), ('zero_flag_marks', 'Zero-flag-only marks')):
        x = rules[name]
        lines.append(f"- **{title}:** reach {pct(x['share_of_missed_labels_reached'])} of missed labels (needs at least "
                     f"{100 * x['min_coverage']:.0f}%), {x['per_100_sentences']:.2f} per 100 sentences (at most "
                     f"{x['max_per_100']:g}). Result: **{x['result']}**." + (f" {x['note']}" if 'note' in x else ''))
    lines += ['', '## Every error (strict)', '', '| Document | Sentence | Category | Kind | Score | Cut-off |',
              '|---|---:|---|---|---:|---:|']
    for e in r['errors_strict']:
        lines.append(f"| {e['document']} | {e['sentence']} | {e['category']} | {e['kind']} | {e['score']:.3f} | {e['cut_off']:.2f} |")
    lines += ['', r['note']]
    return '\n'.join(lines) + '\n'


def main(argv=None):
    argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter).parse_args(argv)
    try:
        r = run(ROOT)
    except (FreshEvalError, ValueError, OSError) as e:
        print(f'STOPPED: {e}', file=sys.stderr)
        return 1
    out = ROOT / OUT
    out.parent.mkdir(parents=True, exist_ok=True)
    out.with_suffix('.json').write_text(json.dumps(r, indent=2) + '\n', encoding='utf-8')
    out.with_suffix('.md').write_text(to_markdown(r), encoding='utf-8')
    s = r['strict']
    print(f"Strict: macro-F1 {s['macro_f1']:.4f} (validation {r['validation_reference']['macro_f1']:.4f}), "
          f"{s['wrong_tags']} wrong tags, {s['missed_labels']} missed labels.")
    for name, x in r['rules'].items():
        print(f"{name}: {x['result']}")
    print(f'Wrote {OUT}.json and {OUT}.md (no sentence text)')
    return 0


if __name__ == '__main__':
    sys.exit(main())
