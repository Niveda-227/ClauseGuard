"""Is this folder release 1.0.0? (Session 12; run it before every demo, study session and the test run.)

    python scripts/check_release.py

It compares every product file (the app, the web app, the model and its manifest, the pinned
packages) with the fingerprints in RELEASE.json. It changes nothing. The last line is
"THIS IS RELEASE 1.0.0" or starts with "NOT RELEASE 1.0.0"; the exit code is 0 or 1.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from scripts.release_files import MODEL, fingerprint, model_sha256, product_files  # noqa: E402


def check(root):
    """Return (ok, lines)."""
    root = Path(root)
    path = root / 'RELEASE.json'
    if not path.exists():
        return False, ['FAIL  RELEASE.json is missing (the release PR is not merged on this branch)']
    release = json.loads(path.read_text(encoding='utf-8'))
    lines, ok = [], True
    model = model_sha256(root) if (root / MODEL).exists() else None
    if model == release['model_sha256']:
        lines.append(f"PASS  model {MODEL} {model[:12]} (as released)")
    else:
        ok = False
        lines.append(f"FAIL  model {MODEL} is not the released model {release['model_sha256'][:12]}")
    expected = release['product_files']
    now = product_files(root)
    changed = [rel for rel in expected if rel not in now or fingerprint(root / rel) != expected[rel]]
    added = [rel for rel in now if rel not in expected]
    if changed or added:
        ok = False
        if changed:
            lines.append('FAIL  changed or missing since the release: ' + ', '.join(changed))
        if added:
            lines.append('FAIL  new product files since the release: ' + ', '.join(added))
    else:
        lines.append(f'PASS  {len(expected)} product files as released')
    version = release['version']
    lines.append(f'THIS IS RELEASE {version}' if ok else f'NOT RELEASE {version}: do not demo, run a study or read the test split on this folder')
    return ok, lines


def main():
    ok, lines = check(ROOT)
    print('\n'.join(lines))
    return 0 if ok else 1


if __name__ == '__main__':
    sys.exit(main())
