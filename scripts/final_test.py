"""Read the UNFAIR-ToS test split ONCE with the frozen release, and report it (Session 12, Jayakrishna).

    python scripts/final_test.py

It runs only if all of these hold, and otherwise stops before opening the test split:
  - this folder is release 1.0.0 (scripts/check_release.py),
  - the rule docs/decisions/final_test_rule.json is on main,
  - the test split has never been read (experiments/test_exposure.jsonl does not exist),
  - the dataset file is the pinned one.
It then writes one line to experiments/test_exposure.jsonl (so the reading is recorded even if
something fails afterwards), reads the test split, scores the released model with its shipped
cut-offs (nothing is tuned), and writes experiments/session12/test_eval.json and test_eval.md:
macro-F1 and the other measures on the test split next to the honest and optimistic validation
numbers, and the result of the pre-set rule. Counts and scores only: no sentence text.

It is meant to run exactly once. To check the record afterwards WITHOUT reading the test split
again, use scripts/check_final_test.py.
"""
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from scripts.check_release import check as check_release  # noqa: E402
from scripts.release_files import LEDGER  # noqa: E402

RULE = 'docs/decisions/final_test_rule.json'
OUT_JSON = 'experiments/session12/test_eval.json'
OUT_MD = 'experiments/session12/test_eval.md'
VALIDATION = 'experiments/session07/threshold_ship_eval.json'


class Stop(Exception):
    pass


def lookup(root, rel, key):
    data = json.loads((Path(root) / rel).read_text(encoding='utf-8'))
    for part in key.split('.'):
        data = data[part]
    return data


def decide(test_macro, honest, rule):
    diff = round(test_macro - honest, 4)
    r = rule['rule']
    if abs(diff) <= r['margin']:
        return diff, r['if_within']
    return diff, (r['if_below'] if diff < 0 else r['if_above'])


def run(root, rows, bundle):
    """Score the released model on `rows` (the test split in real use) and build the result."""
    import numpy as np
    from clauses.evaluate import metrics
    from clauses.model import predict_rows, targets
    from clauses.schema import LABELS
    root = Path(root)
    rule = json.loads((root / RULE).read_text(encoding='utf-8'))
    release = json.loads((root / 'RELEASE.json').read_text(encoding='utf-8'))
    if bundle['model_id'] != release['model_sha256'] or bundle['model_id'] != rule['model']['model_sha256']:
        raise Stop('the loaded model is not the released model named in the rule')
    gold = targets(rows)
    _, pred = predict_rows(bundle, [r['text'] for r in rows])
    m = metrics(gold, pred)
    n = len(rows)
    flags, correct = int(pred.sum()), int((pred & gold).sum())
    honest = lookup(root, VALIDATION, rule['compare_with']['honest_validation_macro_f1']['key'])
    optimistic = lookup(root, VALIDATION, rule['compare_with']['optimistic_validation_macro_f1']['key'])
    honest_cat = lookup(root, VALIDATION, 'new_product_leave_one_company_out_HONEST.per_category')
    test_macro = round(m['macro_f1_8'], 4)
    diff, result = decide(test_macro, honest, rule)
    per_category = {}
    for label in LABELS:
        p = m['per_label'][label]
        per_category[label] = {'support': p['support'], 'precision': round(p['precision'], 4), 'recall': round(p['recall'], 4),
                               'f1': round(p['f1'], 4), 'honest_validation_f1': honest_cat[label]['f1']}
    return {
        'split': 'test', 'sentences': n, 'companies': len({r['document_id'] for r in rows}),
        'release': release['version'], 'model_sha256': bundle['model_id'],
        'test_macro_f1': test_macro, 'test_micro_f1': round(m['micro_f1_8'], 4),
        'flags_per_100_sentences': round(100 * flags / n, 2), 'flags': flags,
        'correct_tags': correct, 'wrong_tags': flags - correct, 'missed_labels': int(gold.sum()) - correct,
        'gold_labels': int(gold.sum()),
        'honest_validation_macro_f1': honest, 'optimistic_validation_macro_f1': optimistic,
        'difference_from_honest_validation': diff, 'margin': rule['rule']['margin'], 'result': result,
        'summary': f'test macro-F1 {test_macro:.4f}; honest validation {honest:.4f}; difference {diff:+.4f} (margin {rule["rule"]["margin"]})',
        'per_category': per_category,
        'cut_offs': release['cut_offs'],
        'rule_file': RULE,
        'note': 'Read once with the frozen release and its shipped cut-offs; nothing was tuned on the test split. Counts and scores only.',
    }


def to_markdown(r):
    lines = ['# The one-time test-split result (Session 12)', '',
             f"Release {r['release']}, model `{r['model_sha256']}`, shipped cut-offs. Test split: {r['sentences']} sentences "
             f"from {r['companies']} companies, read once by `scripts/final_test.py` (see `experiments/test_exposure.jsonl`). "
             f"Rule: [{r['rule_file']}](../../{r['rule_file']}).", '',
             '| Measure | Test split | Honest validation | Optimistic validation |', '|---|---:|---:|---:|',
             f"| Macro-F1 (8 categories) | {r['test_macro_f1']:.4f} | {r['honest_validation_macro_f1']:.4f} | {r['optimistic_validation_macro_f1']:.4f} |",
             f"| Micro-F1 | {r['test_micro_f1']:.4f} | | |",
             f"| Flags per 100 sentences | {r['flags_per_100_sentences']:.2f} | | |",
             f"| Correct tags / wrong tags / missed labels | {r['correct_tags']} / {r['wrong_tags']} / {r['missed_labels']} | | |", '',
             f"**The pre-set rule:** {r['summary']}. **Result: {r['result']}.**", '',
             '## By category', '',
             '| Category | Test support | Test precision | Test recall | Test F1 | Honest validation F1 |', '|---|---:|---:|---:|---:|---:|']
    for label, c in r['per_category'].items():
        lines.append(f"| {label} | {c['support']} | {c['precision']:.4f} | {c['recall']:.4f} | {c['f1']:.4f} | {c['honest_validation_f1']:.4f} |")
    lines += ['', r['note'], '']
    return '\n'.join(lines)


def preconditions(root):
    root = Path(root)
    ok, lines = check_release(root)
    if not ok:
        raise Stop('this folder is not the release: ' + lines[-1])
    if not (root / RULE).exists():
        raise Stop(f'{RULE} is missing (Ameer\'s PR is not merged on this branch)')
    ledger = root / LEDGER
    if ledger.exists() and ledger.read_text(encoding='utf-8').strip():
        first = json.loads(ledger.read_text(encoding='utf-8').splitlines()[0])
        raise Stop(f"the test split was already read ({first.get('at')}). It is read only once; do not run this again.")
    from clauses.data import ARCHIVE_SHA256, DEFAULT_PATH, digest
    if not Path(DEFAULT_PATH).exists() or digest(DEFAULT_PATH) != ARCHIVE_SHA256:
        raise Stop('the dataset file is missing or not the pinned one: run python -m clauses.cli data first')


def execute(root, load_rows):
    """The one run: preconditions, the exposure record, the scoring, the two result files.
    `load_rows` returns the rows to score; in real use it reads the test split."""
    from clauses.model import load
    root = Path(root)
    preconditions(root)
    bundle = load(root / 'artifacts/selected.joblib')
    rule = json.loads((root / RULE).read_text(encoding='utf-8'))
    if bundle['model_id'] != rule['model']['model_sha256']:
        raise Stop('the model file is not the released model named in the rule')
    ledger = root / LEDGER
    ledger.parent.mkdir(parents=True, exist_ok=True)
    with ledger.open('a', encoding='utf-8') as f:
        f.write(json.dumps({'at': datetime.now(timezone.utc).isoformat(timespec='seconds'), 'model_id': bundle['model_id'],
                            'release': '1.0.0', 'output': OUT_JSON, 'by': 'scripts/final_test.py'}) + '\n')
    result = run(root, load_rows(), bundle)
    out = root / OUT_JSON
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
    (root / OUT_MD).write_text(to_markdown(result), encoding='utf-8')
    return result


def main():
    from clauses.data import load_split
    try:
        result = execute(ROOT, lambda: load_split('test'))
    except Stop as e:
        print(f'STOPPED: {e}')
        return 1
    print(f"Test split read once: {result['sentences']} sentences, {result['companies']} companies (recorded in {LEDGER})")
    print(result['summary'])
    print(f"Result: {result['result']}")
    print(f'Wrote {OUT_JSON} and {OUT_MD} (no sentence text)')
    return 0


if __name__ == '__main__':
    sys.exit(main())
