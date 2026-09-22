"""Reproduce Session 04 technical checks without exposing the final test split."""
import hashlib
import importlib.metadata
import json
import platform
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from clauses import data, model
from clauses.evaluate import evaluate
from clauses.export import render_html
from clauses.schema import LABELS


def main():
    out = ROOT / 'experiments/session04'
    out.mkdir(parents=True, exist_ok=True)
    started = datetime.now(timezone.utc).isoformat()
    data.fetch()
    test = subprocess.run([sys.executable, '-m', 'unittest', 'discover', '-s', 'tests', '-v'],
                          cwd=ROOT, capture_output=True, text=True)
    (out/'test_results.txt').write_text(test.stdout + test.stderr, encoding='utf-8')
    if test.returncode:
        print(test.stdout + test.stderr)
        return test.returncode
    rows = data.load_split('validation')
    results = {}
    for variant in ('baseline', 'balanced', 'hybrid'):
        bundle = model.load(ROOT / f'artifacts/{variant}.joblib')
        results[variant] = evaluate(bundle, rows, out/variant)
    selected = model.load(model.DEFAULT_MODEL)
    if selected['model_id'] != results['hybrid']['model_id']:
        raise ValueError('Selected product artifact differs from evaluated hybrid artifact.')
    text = (ROOT/'examples/fictional_terms.txt').read_text(encoding='utf-8')
    demo = model.analyze(text, selected)
    (ROOT/'examples/fictional_analysis.json').write_text(json.dumps(demo, indent=2)+'\n', encoding='utf-8')
    (ROOT/'examples/fictional_analysis.html').write_text(render_html(demo), encoding='utf-8')
    predictions = [json.loads(line) for line in (out/'hybrid/predictions.jsonl').read_text().splitlines()]
    errors = []
    for label in LABELS:
        fp = [r['id'] for r in predictions if label in r['predicted'] and label not in r['gold']]
        fn = [r['id'] for r in predictions if label in r['gold'] and label not in r['predicted']]
        errors.append({'label': label, 'false_positives': len(fp), 'false_negatives': len(fn),
                       'false_positive_ids': fp[:5], 'false_negative_ids': fn[:5]})
    (out/'error_analysis.json').write_text(json.dumps(errors, indent=2)+'\n')
    record = {'started_at_utc': started, 'completed_at_utc': datetime.now(timezone.utc).isoformat(),
              'python': platform.python_version(), 'platform': platform.platform(),
              'packages': {k: importlib.metadata.version(k) for k in ('numpy','scipy','scikit-learn','joblib')},
              'dataset_sha256': data.digest(data.DEFAULT_PATH), 'validation_sentences': len(rows),
              'validation_documents': sorted({r['document_id'] for r in rows}),
              'selected_model_id': selected['model_id'], 'model_original_created_utc': selected['manifest']['created_utc'],
              'test_suite_exit_code': test.returncode, 'final_test_evaluated': False,
              'gui_visual_tested': False, 'outside_user_session_claimed': False,
              'note': 'AI-assisted local technical verification. No GitHub merge or student contribution is inferred.'}
    (out/'verification.json').write_text(json.dumps(record, indent=2)+'\n')
    print(json.dumps({'verified': True, 'outputs': str(out), 'metrics': {
        k: {m: v[m] for m in ('macro_f1_8','micro_f1_8','lexglue_macro_f1_9','lexglue_micro_f1_9')} for k,v in results.items()}}, indent=2))
    return 0


if __name__ == '__main__':
    sys.exit(main())
