"""Which model configuration should the final release use? (Session 11, validation split only)

    python -m clauses.cli data        # once: the dataset is needed
    python scripts/ablation.py        # about 2 to 5 minutes

Trains 6 models on the train split (features: word, char or hybrid; class weighting: balanced or
none) and scores each with two kinds of cut-offs (one per category, or fixed 0.5): 12
configurations. The score that decides is the HONEST validation macro-F1: leave-one-company-out
for per-category cut-offs (each company's cut-offs are tuned on the other nine), plain for 0.5.

The rule (docs/decisions/final_model_rule.json) was frozen before this script was first run and was
merged on main before this script was added; this script reads it and never changes it. Before
measuring, it checks that the retrained shipped configuration (hybrid, balanced) reproduces the
committed validation scores of the product model (experiments/session07/tuned/predictions.jsonl);
if not, it stops.

Also reported, deciding nothing: micro-F1, flags per 100 sentences, and macro-F1 on the Session 10
fresh documents (strict answers; those labels were not made independently).

Writes experiments/session11/ablation.json and .md (no sentence text). The test split is never read.
Training seconds are printed only (they differ on every laptop), so a second run writes identical files.
"""
import argparse
import json
import sys
import time
from pathlib import Path

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.multiclass import OneVsRestClassifier
from sklearn.pipeline import FeatureUnion, Pipeline

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from clauses.model import targets  # noqa: E402
from clauses.schema import LABELS  # noqa: E402
from scripts.cue_eval import honest_cuts  # noqa: E402
from scripts.threshold_cv import best_threshold, load_predictions, summary  # noqa: E402

RULE = 'docs/decisions/final_model_rule.json'
PREDICTIONS = 'experiments/session07/tuned/predictions.jsonl'
SELECTED = 'artifacts/selected.json'
OUT = 'experiments/session11/ablation'
FEATURES = ('word', 'char', 'hybrid')
WEIGHTS = ('balanced', 'none')
CUTS = ('per_category', 'fixed_0.5')
SEED = 641
SANITY_TOLERANCE = 1e-6


class AblationError(ValueError):
    pass


def name(features, weight, cuts):
    return f'{features} / {weight} / {cuts}'


def make(features, weight, seed=SEED):
    """The same pieces as clauses.model.make_pipeline('hybrid'), switched on or off."""
    word = TfidfVectorizer(ngram_range=(1, 2), min_df=2, max_features=30000, sublinear_tf=True, dtype=np.float64)
    char = TfidfVectorizer(analyzer='char_wb', ngram_range=(3, 5), min_df=3, max_features=25000, sublinear_tf=True)
    feats = {'word': word, 'char': char, 'hybrid': FeatureUnion([('word', word), ('char', char)])}[features]
    clf = OneVsRestClassifier(LogisticRegression(C=1.0, class_weight='balanced' if weight == 'balanced' else None,
                                                 solver='liblinear', max_iter=1000, random_state=seed), n_jobs=1)
    return Pipeline([('features', feats), ('classifier', clf)])


def simplicity(c):
    """Lower is simpler (the rule's order): features, then cut-offs, then weighting."""
    return (0 if c['features'] in ('word', 'char') else 1, 0 if c['cut_offs'] == 'fixed_0.5' else 1,
            0 if c['class_weight'] == 'none' else 1)


def decide(configs, rule):
    r = rule['rule']
    shipped = rule['shipped']
    ship = next(c for c in configs if (c['features'], c['class_weight'], c['cut_offs'])
                == (shipped['features'], shipped['class_weight'], shipped['cut_offs']))
    best = max(c['honest_macro_f1'] for c in configs)
    gain = round(best - ship['honest_macro_f1'], 4)
    other = max((c for c in configs if c is not ship), key=lambda c: c['honest_macro_f1'])
    base = {'best_other': other['name'], 'best_other_honest_macro_f1': other['honest_macro_f1'],
            'shipped_honest_macro_f1': ship['honest_macro_f1'], 'gain_of_best_over_shipped': gain,
            'min_gain': r['min_gain']}
    if gain < r['min_gain'] - 1e-9:
        return {'result': r['if_keep'], 'chosen': ship['name'], 'switch': False, **base}
    near = [c for c in configs if c['honest_macro_f1'] >= best - r['tie_margin'] - 1e-9]
    chosen = min(near, key=lambda c: (simplicity(c), -c['honest_macro_f1']))
    return {'result': r['if_switch'].format(name=chosen['name']), 'chosen': chosen['name'], 'switch': True, **base}


def fresh_macro(root, scores_fn, cuts):
    """Strict macro-F1 on the Session 10 fresh documents, or None if the labels are not there."""
    try:
        from clauses.labelling import documents, load_document
        from scripts.label_agreement import gold
        answers = gold(root, 'strict')
    except Exception:  # noqa: BLE001  (the fresh labels are reported only; missing labels must not stop the ablation)
        return None
    texts, y = [], []
    for doc_id in documents(root):
        _, _, sentences = load_document(doc_id, root)
        texts += [s.text for s in sentences]
        y += [[int(l in a) for l in LABELS] for a in answers[doc_id]]
    y = np.array(y, dtype=bool)
    pred = scores_fn(texts) > np.asarray(cuts)
    f1s = []
    for k in range(len(LABELS)):
        if y[:, k].any():
            tp, fp, fn = int((y[:, k] & pred[:, k]).sum()), int((~y[:, k] & pred[:, k]).sum()), int((y[:, k] & ~pred[:, k]).sum())
            f1s.append(2 * tp / (2 * tp + fp + fn))
    return round(sum(f1s) / len(f1s), 4)


def run(root=ROOT, train_rows=None, val_rows=None, say=print):
    root = Path(root)
    rule = json.loads((root / RULE).read_text(encoding='utf-8'))
    y_ref, ref_scores, groups_ref = load_predictions(root / PREDICTIONS)
    ref_ids = [json.loads(l)['id'] for l in (root / PREDICTIONS).read_text(encoding='utf-8').splitlines() if l.strip()]
    if train_rows is None or val_rows is None:
        from clauses.data import load_split
        train_rows, val_rows = load_split('train'), load_split('validation')
    if [r['id'] for r in val_rows] != ref_ids:
        raise AblationError('The validation rows do not match the committed predictions (order or IDs differ).')
    y = targets(val_rows).astype(int)
    if not np.array_equal(y, y_ref):
        raise AblationError('The validation labels do not match the committed predictions.')
    groups = np.array([r['document_id'] for r in val_rows])
    product_cuts = json.loads((root / SELECTED).read_text(encoding='utf-8'))['thresholds']
    train_texts, val_texts = [r['text'] for r in train_rows], [r['text'] for r in val_rows]
    y_train = targets(train_rows)

    configs, sanity = [], None
    for features in FEATURES:
        for weight in WEIGHTS:
            started = time.perf_counter()
            model = make(features, weight).fit(train_texts, y_train)
            say(f'trained {features} / {weight} in {time.perf_counter() - started:.0f} s')
            scores = np.asarray(model.predict_proba(val_texts))
            if (features, weight) == ('hybrid', 'balanced'):
                diff = float(np.abs(scores - ref_scores).max())
                same_flags = bool(np.array_equal(scores > np.asarray(product_cuts), ref_scores > np.asarray(product_cuts)))
                sanity = {'scores_within_one_millionth': bool(diff <= SANITY_TOLERANCE),
                          'same_flags_with_product_cut_offs': same_flags,
                          'passed': bool(diff <= SANITY_TOLERANCE and same_flags)}
                if not sanity['passed']:
                    raise AblationError(f'The retrained shipped configuration does not reproduce the product model '
                                        f'(largest score difference {diff:.2e}). Check the package versions.')
            tuned_in_sample = [best_threshold(y[:, k], scores[:, k]) for k in range(len(LABELS))]
            for cuts in CUTS:
                pred = (scores > honest_cuts(y, scores, groups)) if cuts == 'per_category' else (scores > 0.5)
                s = summary(y, pred.astype(int))
                fresh = fresh_macro(root, lambda t, m=model: np.asarray(m.predict_proba(t)),
                                    tuned_in_sample if cuts == 'per_category' else [0.5] * len(LABELS))
                configs.append({'name': name(features, weight, cuts), 'features': features, 'class_weight': weight,
                                'cut_offs': cuts, 'honest_macro_f1': s['macro_f1'], 'micro_f1': s['micro_f1'],
                                'flags_per_100_sentences': s['flags_per_100_sentences'],
                                'per_category_f1': {l: v['f1'] for l, v in s['per_label'].items()},
                                'fresh_strict_macro_f1': fresh,
                                'fresh_text': 'not available' if fresh is None else f'{fresh:.4f}'})
    decision = decide(configs, rule)
    shipped = next(c for c in configs if c['name'] == name('hybrid', 'balanced', 'per_category'))
    ranked = sorted(configs, key=lambda c: -c['honest_macro_f1'])
    return {
        'rule_file': RULE,
        'split': 'validation',
        'sentences': int(len(y)),
        'companies': int(len(set(groups))),
        'test_split_read': False,
        'sanity_check': sanity,
        'configurations': configs,
        'ranking': [c['name'] for c in ranked],
        'shipped': {'name': shipped['name'], 'honest_macro_f1': shipped['honest_macro_f1']},
        'best': {'name': ranked[0]['name'], 'honest_macro_f1': ranked[0]['honest_macro_f1']},
        'decision': decision,
        'summary': (f"best {ranked[0]['name']} {ranked[0]['honest_macro_f1']:.4f}; shipped {shipped['honest_macro_f1']:.4f}; "
                    f"gain {decision['gain_of_best_over_shipped']:.4f} (a switch needs at least {decision['min_gain']:.2f})"),
        'note': 'Validation split only; honest = leave-one-company-out for per-category cut-offs. Choosing among 12 '
                'configurations on one split flatters the best one; the Session 12 test-split run is the unbiased number. '
                'Fresh-document macro-F1 is reported only: those labels were not made independently.',
    }


def to_markdown(r):
    lines = ['# Ablation: which configuration should the final release use? (Session 11)', '',
             f"Validation split only ({r['sentences']} sentences, {r['companies']} companies); test split not read. "
             f"Rule: [{r['rule_file']}](../../{r['rule_file']}), frozen before this script was first run, never changed after.", '',
             "Sanity check: the retrained shipped configuration reproduces the product model's validation scores "
             f"(within one millionth: {'yes' if r['sanity_check']['scores_within_one_millionth'] else 'no'}; same flags: "
             f"{'yes' if r['sanity_check']['same_flags_with_product_cut_offs'] else 'no'}).", '',
             '| Rank | Features | Class weighting | Cut-offs | Honest macro-F1 | Micro-F1 | Flags per 100 | Fresh docs macro-F1 (reported only) |',
             '|---:|---|---|---|---:|---:|---:|---:|']
    by_name = {c['name']: c for c in r['configurations']}
    for i, n in enumerate(r['ranking'], start=1):
        c = by_name[n]
        mark = ' (shipped)' if n == r['shipped']['name'] else ''
        lines.append(f"| {i} | {c['features']}{mark} | {c['class_weight']} | {c['cut_offs']} | {c['honest_macro_f1']:.4f} | "
                     f"{c['micro_f1']:.4f} | {c['flags_per_100_sentences']:.2f} | {c['fresh_text']} |")
    lines += ['', '## Per category (honest F1)', '', '| Configuration | ' + ' | '.join(LABELS) + ' |',
              '|---|' + '---:|' * len(LABELS)]
    for n in r['ranking']:
        c = by_name[n]
        lines.append(f"| {n} | " + ' | '.join(f"{c['per_category_f1'][l]:.3f}" for l in LABELS) + ' |')
    d = r['decision']
    lines += ['', '## The pre-set rule', '', f"- {r['summary']}.", f"- **Result: {d['result']}.**", '', r['note']]
    return '\n'.join(lines) + '\n'


def main(argv=None):
    argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter).parse_args(argv)
    try:
        r = run(ROOT)
    except (AblationError, ValueError, OSError, FileNotFoundError) as e:
        print(f'STOPPED: {e}', file=sys.stderr)
        return 1
    out = ROOT / OUT
    out.parent.mkdir(parents=True, exist_ok=True)
    out.with_suffix('.json').write_text(json.dumps(r, indent=2) + '\n', encoding='utf-8')
    out.with_suffix('.md').write_text(to_markdown(r), encoding='utf-8')
    print('Sanity check passed: the retrained shipped configuration reproduces the product model.')
    print(r['summary'])
    print(f"Result: {r['decision']['result']}")
    print(f'Wrote {OUT}.json and {OUT}.md (no sentence text; test split not read)')
    return 0


if __name__ == '__main__':
    sys.exit(main())
