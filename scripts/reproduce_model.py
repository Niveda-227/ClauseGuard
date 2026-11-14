"""Rebuild the product model from a clean clone and check it is the model we report (Session 11).

    python -m clauses.cli data             # once: the dataset is needed
    python scripts/reproduce_model.py      # about 10 to 30 seconds
    python scripts/reproduce_model.py --save private/reproduced.joblib   # optional: keep the rebuilt model

It trains the shipped configuration with the product code (clauses.model.train, variant hybrid,
seed 641) on the train split only, applies the product cut-offs from artifacts/selected.json, and
checks three things:
  1. its validation scores equal the committed scores of the product model
     (experiments/session07/tuned/predictions.jsonl) to within one millionth;
  2. it flags exactly the same categories on every validation sentence;
  3. it flags the fictional demo document exactly as the demo was rehearsed (scripts/demo_check.py).

It also records the fingerprints that identify this release: the dataset archive, the training
companies, the cut-offs, the product artifact, and a SHA-256 over the validation flags.
Writes experiments/session11/reproduce.json and .md (no sentence text, no machine names, no times),
so a second run writes identical files. The test split is never read. --save writes the rebuilt
bundle to a git-ignored path only (for the Session 12 freeze); it is never committed.
"""
import argparse
import hashlib
import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from clauses.data import ARCHIVE_SHA256  # noqa: E402
from clauses.model import analyze, train  # noqa: E402
from clauses.schema import LABELS  # noqa: E402
from scripts.demo_check import DEMO_DOC, EXPECTED_DEMO_LABELS  # noqa: E402
from scripts.threshold_cv import load_predictions  # noqa: E402

SELECTED = 'artifacts/selected.json'
PREDICTIONS = 'experiments/session07/tuned/predictions.jsonl'
OUT = 'experiments/session11/reproduce'
TOLERANCE = 1e-6


class ReproduceError(ValueError):
    pass


def flags_fingerprint(scores, cuts):
    """SHA-256 over the flagged category names of every sentence, in order."""
    flags = [[l for l, s, t in zip(LABELS, row, cuts) if s > t] for row in scores]
    return hashlib.sha256(json.dumps(flags).encode('utf-8')).hexdigest()


def run(root=ROOT, train_rows=None, val_rows=None):
    root = Path(root)
    selected = json.loads((root / SELECTED).read_text(encoding='utf-8'))
    cuts = list(selected['thresholds'])
    y_ref, ref_scores, _ = load_predictions(root / PREDICTIONS)
    ref_ids = [json.loads(l)['id'] for l in (root / PREDICTIONS).read_text(encoding='utf-8').splitlines() if l.strip()]
    if train_rows is None or val_rows is None:
        from clauses.data import load_split
        train_rows, val_rows = load_split('train'), load_split('validation')
    if [r['id'] for r in val_rows] != ref_ids:
        raise ReproduceError('The validation rows do not match the committed predictions.')
    bundle = train(train_rows, 'hybrid', 641)
    bundle['manifest']['thresholds'] = cuts
    bundle['manifest']['threshold_source'] = selected['threshold_source']
    scores = np.asarray(bundle['pipeline'].predict_proba([r['text'] for r in val_rows]))
    diff = float(np.abs(scores - ref_scores).max())
    same_flags = bool(np.array_equal(scores > np.asarray(cuts), ref_scores > np.asarray(cuts)))
    demo = analyze((root / DEMO_DOC).read_text(encoding='utf-8'), bundle)
    demo_labels = [s['labels'] for s in demo['sentences']]
    checks = {
        'validation_scores_within_one_millionth': diff <= TOLERANCE,
        'same_validation_flags': same_flags,
        'demo_document_flags_as_rehearsed': demo_labels == EXPECTED_DEMO_LABELS,
        'train_count_matches_manifest': len(train_rows) == selected['train_count'],
        'training_companies_match_manifest': sorted({r['document_id'] for r in train_rows}) == selected['train_documents'],
        'dataset_matches_manifest': ARCHIVE_SHA256 == selected['dataset_sha256'],
    }
    result = {
        'reproduced': all(checks.values()),
        'result_text': 'REPRODUCED' if all(checks.values()) else 'NOT REPRODUCED',
        'checks_passed_text': f'{sum(checks.values())} of {len(checks)}',
        'checks': checks,
        'configuration': {'variant': 'hybrid', 'seed': 641, 'features': 'word 1-2-grams + character 3-5-grams (TF-IDF)',
                          'classifier': 'one logistic regression per category (liblinear, C 1.0, balanced class weights)'},
        'fingerprints': {
            'dataset_sha256': ARCHIVE_SHA256,
            'product_artifact_sha256': selected['artifact_sha256'],
            'training_sentences': len(train_rows),
            'training_companies': len({r['document_id'] for r in train_rows}),
            'validation_sentences': len(val_rows),
            'cut_offs': {l: round(float(c), 2) for l, c in zip(LABELS, cuts)},
            'validation_flags_sha256': flags_fingerprint(scores, cuts),
        },
        'largest_score_difference_below_one_millionth': diff <= TOLERANCE,
        'test_split_read': False,
        'note': 'The rebuilt model is compared by its outputs, not by its file bytes: a saved joblib file contains a '
                'creation time and so never has the same SHA-256 twice.',
    }
    return result, bundle


def to_markdown(r):
    f = r['fingerprints']
    yes = lambda v: 'yes' if v else 'NO'  # noqa: E731
    lines = ['# Rebuilding the product model from a clean clone (Session 11)', '',
             f"**Reproduced: {yes(r['reproduced'])}.** The shipped configuration ({r['configuration']['features']}; "
             f"{r['configuration']['classifier']}; seed {r['configuration']['seed']}) was trained on the train split only "
             'with the product code and given the product cut-offs.', '', '| Check | Passed |', '|---|---|']
    names = {'validation_scores_within_one_millionth': 'Validation scores equal the product model\'s (within one millionth)',
             'same_validation_flags': 'Same flags on every validation sentence',
             'demo_document_flags_as_rehearsed': 'Demo document flagged exactly as rehearsed',
             'train_count_matches_manifest': 'Training sentences match the model manifest',
             'training_companies_match_manifest': 'Training companies match the model manifest',
             'dataset_matches_manifest': 'Dataset archive matches the model manifest'}
    for k, v in r['checks'].items():
        lines.append(f'| {names[k]} | {yes(v)} |')
    lines += ['', '## Fingerprints of this release', '',
              f"- Dataset archive SHA-256: `{f['dataset_sha256']}`",
              f"- Product model file (`artifacts/selected.joblib`) SHA-256: `{f['product_artifact_sha256']}`",
              f"- Training data: {f['training_sentences']} sentences from {f['training_companies']} companies; validation: "
              f"{f['validation_sentences']} sentences",
              '- Cut-offs: ' + ', '.join(f'{l} {c:.2f}' for l, c in f['cut_offs'].items()),
              f"- SHA-256 over the validation flags: `{f['validation_flags_sha256']}`", '', r['note'],
              'The test split was not read.']
    return '\n'.join(lines) + '\n'


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument('--save', help='also save the rebuilt model to this path inside private/ (git-ignored)')
    a = p.parse_args(argv)
    if a.save and not Path(a.save).as_posix().startswith('private/'):
        p.error('--save must be a path inside private/ (git-ignored), for example private/reproduced.joblib')
    try:
        r, bundle = run(ROOT)
    except (ReproduceError, ValueError, OSError, FileNotFoundError) as e:
        print(f'STOPPED: {e}', file=sys.stderr)
        return 1
    out = ROOT / OUT
    out.parent.mkdir(parents=True, exist_ok=True)
    out.with_suffix('.json').write_text(json.dumps(r, indent=2) + '\n', encoding='utf-8')
    out.with_suffix('.md').write_text(to_markdown(r), encoding='utf-8')
    for k, v in r['checks'].items():
        print(f"{'PASS' if v else 'FAIL'}  {k.replace('_', ' ')}")
    print(f"Validation flags fingerprint: {r['fingerprints']['validation_flags_sha256']}")
    if a.save:
        from clauses.model import save
        save(bundle, ROOT / a.save)
        print(f'Saved the rebuilt model to {a.save} (git-ignored; never commit it)')
    print('REPRODUCED' if r['reproduced'] else 'NOT REPRODUCED: stop and post this output in the team chat')
    print(f'Wrote {OUT}.json and {OUT}.md')
    return 0 if r['reproduced'] else 1


if __name__ == '__main__':
    sys.exit(main())
