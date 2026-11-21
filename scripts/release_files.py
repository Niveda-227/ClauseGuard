"""The product files of a ClauseGuard release, and their fingerprints (Session 12).

Shared by scripts/make_release.py (writes RELEASE.json once, at the freeze) and
scripts/check_release.py (checks that a folder is still that release).
"""
import hashlib
from pathlib import Path

PRODUCT_GLOBS = ['app.py', 'requirements.txt', 'clauses/*.py', 'webapp/*.py', 'webapp/static/*',
                 'artifacts/selected.joblib', 'artifacts/selected.json']
TEXT_SUFFIXES = {'.py', '.txt', '.json', '.html', '.css', '.js', '.svg', '.md'}
MODEL = 'artifacts/selected.joblib'
LEDGER = 'experiments/test_exposure.jsonl'


def fingerprint(path):
    """SHA-256 of a file; text files with Windows line endings get the same fingerprint as on macOS."""
    data = Path(path).read_bytes()
    if Path(path).suffix in TEXT_SUFFIXES:
        data = data.replace(b'\r\n', b'\n')
    return hashlib.sha256(data).hexdigest()


def product_files(root):
    root = Path(root)
    found = set()
    for pattern in PRODUCT_GLOBS:
        for p in root.glob(pattern):
            # Hidden files (for example macOS .DS_Store) are never product files.
            if p.is_file() and '__pycache__' not in p.parts and not p.name.startswith('.'):
                found.add(p.relative_to(root).as_posix())
    return sorted(found)


def model_sha256(root):
    """The model ID, exactly as clauses.model computes it (raw bytes of the artifact)."""
    return hashlib.sha256((Path(root) / MODEL).read_bytes()).hexdigest()
