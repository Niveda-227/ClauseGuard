"""Check an annotator's labels of the fresh Terms of Service, and publish them for a PR (Session 10).

    python scripts/check_labels.py --annotator A1              # check private/labels/A1/ (your laptop only)
    python scripts/check_labels.py --annotator A1 --publish    # check, then copy into data/fresh_labels/A1/
    python scripts/check_labels.py --annotator A1 --folder data/fresh_labels   # check the published copy

For every document in examples/fresh/manifest.json it checks that the label file exists, is for
that exact document (SHA-256), is complete, has every sentence once in order with the offsets the
product's sentence splitter gives, and uses only the eight category names. It prints the counts
and the fingerprint (SHA-256 over the three files): post that fingerprint in the team chat as
soon as you finish, before the other annotator's labels are on main.

--publish copies the checked files unchanged, so the fingerprint stays the same, and writes
experiments/session10/labels_<annotator>.json (counts, minutes and the fingerprint; no sentence
text) for your notes. It refuses to overwrite a published file that differs. It never commits
or pushes.
"""
import argparse
import json
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from clauses.labelling import ANNOTATORS, FORMAT, PRIVATE, fingerprint, label_path, load_document, documents  # noqa: E402
from clauses.schema import LABELS  # noqa: E402

PUBLISHED = 'data/fresh_labels'
SUMMARY = 'experiments/session10/labels_{}.json'


def check(annotator, root=ROOT, folder=PRIVATE):
    """(problems, counts) for one annotator's label files."""
    root = Path(root)
    problems, counts = [], {'sentences': 0, 'labelled_sentences': 0, 'unsure': 0, 'seconds_active': 0.0,
                            'per_category': {l: 0 for l in LABELS}, 'per_document': {}}
    for doc_id in documents(root):
        path = label_path(annotator, doc_id, root, folder)
        if not path.exists():
            problems.append(f'{doc_id}: {path.relative_to(root)} is missing')
            continue
        try:
            rec = json.loads(path.read_text(encoding='utf-8'))
        except json.JSONDecodeError:
            problems.append(f'{doc_id}: not valid JSON')
            continue
        doc, _, sentences = load_document(doc_id, root)
        if rec.get('format') != FORMAT or rec.get('doc_id') != doc_id or rec.get('annotator') != annotator:
            problems.append(f'{doc_id}: wrong format, document or annotator in the file')
            continue
        if rec.get('doc_sha256') != doc['sha256']:
            problems.append(f'{doc_id}: labels were made for another version of the document')
        if not rec.get('complete') or len(rec.get('sentences', [])) != len(sentences):
            problems.append(f'{doc_id}: not complete ({len(rec.get("sentences", []))} of {len(sentences)} sentences)')
        for i, (item, s) in enumerate(zip(rec.get('sentences', []), sentences)):
            if (item.get('sentence_id'), item.get('start'), item.get('end')) != (i, s.start, s.end):
                problems.append(f'{doc_id}: sentence {i + 1} does not match the document')
                break
            bad = [l for l in item.get('labels', []) if l not in LABELS]
            if bad or len(set(item.get('labels', []))) != len(item.get('labels', [])):
                problems.append(f'{doc_id}: sentence {i + 1} has unknown or repeated categories')
            if item.get('unsure') and item.get('labels'):
                problems.append(f'{doc_id}: sentence {i + 1} is marked unsure but has categories')
        items = rec.get('sentences', [])
        counts['sentences'] += len(items)
        counts['labelled_sentences'] += sum(bool(x.get('labels')) for x in items)
        counts['unsure'] += sum(bool(x.get('unsure')) for x in items)
        counts['seconds_active'] = round(counts['seconds_active'] + float(rec.get('seconds_active', 0.0)), 1)
        for x in items:
            for l in x.get('labels', []):
                if l in counts['per_category']:
                    counts['per_category'][l] += 1
        counts['per_document'][doc_id] = {'sentences': len(items), 'labelled_sentences': sum(bool(x.get('labels')) for x in items)}
    return problems, counts


def summary(annotator, counts, fp):
    """The counts-only summary written next to the results."""
    return {'annotator': annotator, 'fingerprint': fp, 'sentences': counts['sentences'],
            'labelled_sentences': counts['labelled_sentences'], 'unsure': counts['unsure'],
            'minutes_labelling': round(counts['seconds_active'] / 60), 'per_category': counts['per_category'],
            'per_document': counts['per_document'],
            'note': 'Counts only, no sentence text. minutes_labelling is the time between showing a sentence and '
                    'the answer, capped at 5 minutes per sentence.'}


def publish(annotator, root=ROOT):
    """Copy the checked private files into data/fresh_labels/<annotator>/ and write the summary. Returns the paths."""
    root = Path(root)
    problems, counts = check(annotator, root, PRIVATE)
    if problems:
        raise ValueError(f'the labels do not pass the check: {problems[0]}')
    copied = []
    for doc_id in documents(root):
        src = label_path(annotator, doc_id, root, PRIVATE)
        dst = label_path(annotator, doc_id, root, PUBLISHED)
        if dst.exists() and dst.read_bytes() != src.read_bytes():
            raise ValueError(f'{dst.relative_to(root)} already exists with different labels. Not overwriting it.')
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(src, dst)
        copied.append(dst.relative_to(root).as_posix())
    out = root / SUMMARY.format(annotator)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(summary(annotator, counts, fingerprint(annotator, root, PUBLISHED)), indent=2) + '\n',
                   encoding='utf-8')
    copied.append(out.relative_to(root).as_posix())
    return copied


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument('--annotator', required=True, choices=ANNOTATORS)
    p.add_argument('--folder', default=PRIVATE, help=f'where the label files are (default {PRIVATE})')
    p.add_argument('--publish', action='store_true', help=f'after the check, copy them into {PUBLISHED}/')
    a = p.parse_args(argv)
    try:
        problems, counts = check(a.annotator, ROOT, a.folder)
    except (ValueError, OSError) as e:
        print(f'LABELS NOT OK: {e}')
        return 1
    for doc_id, c in counts['per_document'].items():
        print(f"{doc_id:12s} {c['sentences']:4d} sentences, {c['labelled_sentences']:3d} with a category")
    print('Per category: ' + ', '.join(f'{l} {n}' for l, n in counts['per_category'].items()))
    print(f"Unsure: {counts['unsure']}. Time spent labelling: {round(counts['seconds_active'] / 60)} minutes.")
    if problems:
        print('LABELS NOT OK:')
        for x in problems:
            print('  - ' + x)
        return 1
    print(f'Fingerprint {a.annotator}: {fingerprint(a.annotator, ROOT, a.folder)}')
    if a.publish:
        if a.folder != PRIVATE:
            print('--publish copies from private/labels only.')
            return 1
        try:
            for path in publish(a.annotator, ROOT):
                print(f'published {path}')
        except ValueError as e:
            print(f'NOT PUBLISHED: {e}')
            return 1
    print('LABELS OK')
    return 0


if __name__ == '__main__':
    sys.exit(main())
