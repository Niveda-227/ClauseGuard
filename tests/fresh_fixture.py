"""Shared test helper for Session 10: a temporary repo copy with made-up label files.

The labels made here are fake (chosen by a rule in the test), used only to test the scripts.
"""
import json
import shutil
import tempfile
from pathlib import Path

from clauses.labelling import documents, label_path, load_document, new_record, save

ROOT = Path(__file__).resolve().parents[1]


def temp_root():
    root = Path(tempfile.mkdtemp())
    (root / 'examples').mkdir()
    shutil.copytree(ROOT / 'examples/fresh', root / 'examples/fresh')
    return root


def write_labels(root, annotator, choose, folder='private/labels'):
    """choose(doc_id, sentence_index, sentence_text) -> list of category names (or None for unsure)."""
    for doc_id in documents(root):
        doc, _, sentences = load_document(doc_id, root)
        rec = new_record(doc, annotator)
        for i, s in enumerate(sentences):
            labels = choose(doc_id, i, s.text)
            rec['sentences'].append({'sentence_id': i, 'start': s.start, 'end': s.end,
                                     'labels': labels or [], 'unsure': labels is None})
        rec['complete'] = True
        rec['finished_utc'] = rec['started_utc']
        rec['seconds_active'] = 60.0
        save(rec, label_path(annotator, doc_id, root, folder))


def edit_label_file(root, annotator, doc_id, change, folder='private/labels'):
    path = label_path(annotator, doc_id, root, folder)
    rec = json.loads(path.read_text())
    change(rec)
    path.write_text(json.dumps(rec, indent=2) + '\n')
