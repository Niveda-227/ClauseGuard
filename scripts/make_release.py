"""Freeze the product as release 1.0.0 (Session 12, Hemanth). Run it once, on the release branch:

    python scripts/make_release.py

It writes RELEASE.json (the fingerprint of every product file: the app, the web app, the model and
its manifest, the pinned packages) and experiments/session12/release_summary.json (the facts the
notes and the report quote). It refuses if the test split has already been read
(experiments/test_exposure.jsonl exists): the freeze must come first. Running it again on the same
files changes nothing. After the release is merged, scripts/check_release.py checks any folder
against RELEASE.json.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from scripts.release_files import LEDGER, MODEL, fingerprint, model_sha256, product_files  # noqa: E402

VERSION = '1.0.0'
TAG = 'v1.0.0'
RELEASE = 'RELEASE.json'
SUMMARY = 'experiments/session12/release_summary.json'


def build(root):
    root = Path(root)
    if (root / LEDGER).exists():
        raise ValueError(f'{LEDGER} exists: the test split was already read. The release must be frozen before that.')
    manifest = json.loads((root / 'artifacts/selected.json').read_text(encoding='utf-8'))
    model = model_sha256(root)
    if manifest['artifact_sha256'] != model:
        raise ValueError(f'{MODEL} is not the model named in artifacts/selected.json.')
    files = {rel: fingerprint(root / rel) for rel in product_files(root)}
    pins = [l.strip() for l in (root / 'requirements.txt').read_text(encoding='utf-8').splitlines() if l.strip()]
    release = {
        'name': 'ClauseGuard', 'version': VERSION, 'tag': TAG,
        'model_sha256': model,
        'variant': manifest['variant'], 'cut_offs': dict(zip(manifest['labels'], [round(c, 2) for c in manifest['thresholds']])),
        'dataset_sha256': manifest['dataset_sha256'],
        'python': '3.12', 'packages': pins,
        'product_files': files,
        'note': 'Frozen in Session 12, before the test split was read. scripts/check_release.py checks a folder against this file.',
    }
    summary = {
        'version': VERSION, 'tag': TAG, 'model_sha256': model, 'model_short': model[:12],
        'product_files': len(files), 'dataset_sha256': manifest['dataset_sha256'],
        'packages': pins, 'test_split_read_before_freeze': False,
        'summary': f'release {VERSION}: {len(files)} product files, model {model[:12]}',
    }
    return release, summary


def main():
    try:
        release, summary = build(ROOT)
    except (ValueError, OSError, KeyError) as e:
        print(f'STOPPED: {e}')
        return 1
    for rel, data in ((RELEASE, release), (SUMMARY, summary)):
        path = ROOT / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(data, indent=2) + '\n', encoding='utf-8')
    print(f"Release {release['version']} (tag {release['tag']}): {summary['product_files']} product files, "
          f"model {release['model_sha256']}")
    print(f'Wrote {RELEASE} and {SUMMARY}')
    return 0


if __name__ == '__main__':
    sys.exit(main())
