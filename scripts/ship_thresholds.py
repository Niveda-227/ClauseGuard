"""Ship per-category thresholds (Session 07): build, evaluate and (with --promote) install the tuned model.

    python scripts/ship_thresholds.py             # build + evaluate; the app is NOT changed
    python scripts/ship_thresholds.py --promote   # also make the tuned model the product model

What it does, in order (stops at the first problem):
  1. Loads the evaluated hybrid model, artifacts/hybrid.joblib, and checks it is the model whose
     Session 04 validation metrics we report (fingerprint = experiments/session04/hybrid/metrics.json).
  2. Tunes one threshold per category on the validation split with the project's own
     clauses.model.tune() (grid 0.10-0.90, ties go to the higher threshold).
  3. Checks the thresholds equal the in-sample thresholds of the Session 05 experiment
     (experiments/session05/threshold_cv.json). Same model + same data must give the same answer.
  4. Saves artifacts/tuned.joblib and artifacts/tuned.json. Only the thresholds change.
  5. Evaluates the tuned model on validation into experiments/session07/tuned/ and checks its
     scores equal the Session 04 hybrid scores (same pipeline, only the cut-offs moved).
  6. With --promote: copies tuned.joblib/tuned.json over artifacts/selected.joblib/selected.json.
  7. Writes experiments/session07/tuned/ship_record.json.

Honesty note written into the record: the validation numbers of the tuned model are optimistic,
because its thresholds were chosen on that same validation split. The estimate to report is the
leave-one-company-out result from experiments/session05/threshold_cv.json. The test split is never read.
"""
import argparse
import hashlib
import json
import platform
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

BASE = 'artifacts/hybrid.joblib'
BASE_METRICS = 'experiments/session04/hybrid/metrics.json'
BASE_PREDICTIONS = 'experiments/session04/hybrid/predictions.jsonl'
EXPERIMENT = 'experiments/session05/threshold_cv.json'
TUNED = 'artifacts/tuned.joblib'
OUT_DIR = 'experiments/session07/tuned'
SCORE_TOLERANCE = 1e-6


class ShipError(ValueError):
    pass


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def read_json(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))


def check_base(root):
    base_sha = sha256(root / BASE)
    reported = read_json(root / BASE_METRICS)['model_id']
    if base_sha != reported:
        raise ShipError(f'{BASE} is not the model whose Session 04 metrics we report ({base_sha[:12]} vs {reported[:12]}).')
    return base_sha


def compare_thresholds(tuned, expected, labels):
    """Return a list of differences between tuned thresholds and the Session 05 in-sample thresholds."""
    diffs = []
    for label, value in zip(labels, tuned):
        want = expected.get(label)
        if want is None or abs(float(value) - float(want)) > 1e-9:
            diffs.append(f'{label}: tuned {value} vs experiment {want}')
    return diffs


def max_score_difference(path_a, path_b):
    """Largest absolute score difference between two prediction files over the same sentences."""
    def read(p):
        return {r['id']: r['scores'] for r in (json.loads(l) for l in Path(p).read_text(encoding='utf-8').splitlines() if l.strip())}
    a, b = read(path_a), read(path_b)
    if set(a) != set(b):
        raise ShipError('The two prediction files cover different sentences.')
    if any(i.startswith('test:') for i in a):
        raise ShipError('Test-split predictions found. The test split must stay untouched until Session 12.')
    return max(abs(x - y) for i in a for x, y in zip(a[i], b[i]))


def promote(root, tuned_joblib, tuned_json):
    shutil.copyfile(tuned_joblib, root / 'artifacts/selected.joblib')
    shutil.copyfile(tuned_json, root / 'artifacts/selected.json')
    if sha256(root / 'artifacts/selected.joblib') != sha256(tuned_joblib):
        raise ShipError('Copy failed: selected.joblib does not match tuned.joblib.')


def build(root=ROOT, rows=None, do_promote=False, expected=None, base_predictions=None):
    """Run steps 1-7. `rows` and `expected` can be injected by tests; normally they are loaded."""
    from clauses import model
    from clauses.evaluate import evaluate
    from clauses.schema import LABELS
    root = Path(root)
    base_sha = check_base(root)
    if rows is None:
        from clauses.data import load_split
        rows = load_split('validation')
    if any(r['split'] != 'validation' for r in rows):
        raise ShipError('Thresholds may only be tuned on the validation split.')

    bundle = model.load(root / BASE)
    bundle.pop('model_id', None)  # the fingerprint belongs to the file, not inside it
    bundle = model.tune(bundle, rows)
    thresholds = [float(t) for t in bundle['manifest']['thresholds']]
    if expected is None:
        expected = read_json(root / EXPERIMENT)['tuned_in_sample_OPTIMISTIC']['thresholds']
    diffs = compare_thresholds(thresholds, expected, LABELS)
    if diffs:
        raise ShipError('Thresholds differ from the Session 05 experiment: ' + '; '.join(diffs))

    bundle['manifest'].update({
        'base_artifact_sha256': base_sha,
        'threshold_note': 'Per-category thresholds tuned on the full validation split (Session 07). '
                          'Validation scores of this model are optimistic; report the leave-one-company-out '
                          'estimate from experiments/session05/threshold_cv.json.',
    })
    tuned_path = root / TUNED
    manifest = model.save(bundle, tuned_path)
    tuned_sha = manifest['artifact_sha256']

    out = root / OUT_DIR
    result = evaluate(model.load(tuned_path), rows, out)
    diff = max_score_difference(base_predictions or root / BASE_PREDICTIONS, out / 'predictions.jsonl')
    if diff > SCORE_TOLERANCE:
        raise ShipError(f'Scores differ from the Session 04 hybrid model by {diff:.2e}; this is not the same pipeline.')

    loco = None
    exp_path = root / EXPERIMENT
    if exp_path.exists():
        cv = read_json(exp_path)['leave_one_company_out_HONEST']
        loco = {'macro_f1': cv['macro_f1'], 'micro_f1': cv['micro_f1'],
                'flags_per_100_sentences': cv['flags_per_100_sentences'], 'source': EXPERIMENT}

    if do_promote:
        promote(root, tuned_path, tuned_path.with_suffix('.json'))

    record = {
        'shipped_utc': datetime.now(timezone.utc).isoformat(timespec='seconds'),
        'base_model_sha256': base_sha,
        'tuned_model_sha256': tuned_sha,
        'thresholds': dict(zip(LABELS, thresholds)),
        'promoted_to_product': bool(do_promote),
        'validation_in_sample_OPTIMISTIC': {
            'macro_f1': round(result['macro_f1_8'], 4), 'micro_f1': round(result['micro_f1_8'], 4),
            'note': 'Thresholds were tuned on this same split, so these numbers overstate performance.'},
        'honest_estimate_leave_one_company_out': loco,
        'max_score_difference_vs_session04': diff,
        'environment': {'python': platform.python_version(), 'sklearn': __import__('sklearn').__version__},
        'test_split_evaluated': False,
    }
    (out / 'ship_record.json').write_text(json.dumps(record, indent=2) + '\n', encoding='utf-8')
    return record


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument('--promote', action='store_true', help='Make the tuned model the product model.')
    a = p.parse_args(argv)
    try:
        r = build(do_promote=a.promote)
    except (ValueError, FileNotFoundError) as e:  # ShipError is a ValueError; so is a dataset checksum error
        print(f'STOPPED: {e}', file=sys.stderr)
        return 1
    print('Thresholds (tuned on validation, identical to the Session 05 experiment):')
    for label, t in r['thresholds'].items():
        print(f'  {label:<25} {t:.2f}')
    print(f"Base model   {r['base_model_sha256'][:12]}  (fixed 0.5)")
    print(f"Tuned model  {r['tuned_model_sha256'][:12]}  -> artifacts/tuned.joblib")
    ins = r['validation_in_sample_OPTIMISTIC']
    print(f"Validation macro-F1 {ins['macro_f1']:.4f} (OPTIMISTIC: tuned on the same data)")
    if r['honest_estimate_leave_one_company_out']:
        print(f"Honest estimate (leave-one-company-out): macro-F1 {r['honest_estimate_leave_one_company_out']['macro_f1']:.4f}")
    print(f"Scores identical to Session 04 (max difference {r['max_score_difference_vs_session04']:.1e})")
    if r['promoted_to_product']:
        print('PROMOTED: artifacts/selected.joblib is now the tuned model. The app uses it from the next start.')
    else:
        print('Not promoted. Run again with --promote to make it the product model.')
    print(f'Wrote {OUT_DIR}/metrics.json, predictions.jsonl, ship_record.json')
    return 0


if __name__ == '__main__':
    sys.exit(main())
