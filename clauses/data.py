"""Pinned data retrieval without executable remote dataset loaders."""
import hashlib
import json
import tarfile
import urllib.request
from pathlib import Path
from .schema import LABELS

URL = 'https://zenodo.org/records/5532997/files/unfair_tos.tar.gz?download=1'
ARCHIVE_SHA256 = '934470d74b62139dfbfad4a13b75a32e4a4d26a680ab12eedfb7659cdf669d53'
EXPECTED_COUNTS = {'train': 5532, 'validation': 2275, 'test': 1607}
ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PATH = ROOT / 'data/unfair_tos.tar.gz'


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def fetch(path=DEFAULT_PATH):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists() and digest(path) == ARCHIVE_SHA256:
        return path
    temporary = path.with_suffix('.partial')
    req = urllib.request.Request(URL, headers={'User-Agent': 'ClauseGuard-course-project/0.1'})
    try:
        with urllib.request.urlopen(req, timeout=60) as response:
            temporary.write_bytes(response.read())
        if digest(temporary) != ARCHIVE_SHA256:
            raise ValueError('Dataset checksum mismatch. Keep the pinned release; inspect the download before replacing it.')
        temporary.replace(path)
    finally:
        temporary.unlink(missing_ok=True)
    return path


def load_split(split, path=DEFAULT_PATH):
    if split not in EXPECTED_COUNTS:
        raise ValueError('Choose train, validation, or test.')
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError('Dataset missing. Run: python -m clauses.cli data')
    if digest(path) != ARCHIVE_SHA256:
        raise ValueError('Dataset checksum differs from the pinned release.')
    # Read a named member, never extract arbitrary archive paths.
    with tarfile.open(path, 'r:gz') as archive:
        handle = archive.extractfile('unfair_tos.jsonl')
        if handle is None:
            raise ValueError('Expected dataset member is missing.')
        source_rows = [json.loads(line) for line in handle if line.strip()]
    source_split = 'val' if split == 'validation' else split
    rows = []
    for i, r in enumerate(source_rows):
        if r['data_type'] != source_split:
            continue
        if set(r['labels']) - set(LABELS):
            raise ValueError('Unknown source label.')
        rows.append({'id': f'{split}:{i:05d}', 'text': r['text'].strip(),
                     'labels': r['labels'], 'document_id': r['company'], 'split': split})
    if len(rows) != EXPECTED_COUNTS[split]:
        raise ValueError(f'Unexpected {split} size: {len(rows)}')
    return rows
