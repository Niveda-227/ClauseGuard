"""Label the fresh Terms of Service, one sentence at a time (Session 10).

    python -m clauses.labelling --doc basecamp --annotator A1     # label (or continue) one document
    python -m clauses.labelling --status --annotator A1           # progress and, when done, the fingerprint

The documents are the ones in examples/fresh/manifest.json. Each sentence is shown exactly as the
app splits the document (clauses/text.py), with the sentence before it for context. Type the
numbers of every category the sentence itself states (for example 3 or 1,5), Enter for none,
? for unsure (saved with no category), b to go back one sentence, h for the category list, and
q to save and stop. The file is saved after every answer, so the next run continues where you
stopped.

Labels are written to private/labels/<annotator>/<doc_id>.json. private/ is git-ignored: the
labels stay on your laptop until scripts/check_labels.py --publish copies them into
data/fresh_labels/ for your PR. Follow docs/LABELLING_GUIDE.md, and never open the other
annotator's labels before you have posted your own fingerprint.
"""
import argparse
import hashlib
import json
import re
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

from .schema import LABELS
from .text import segment

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = 'examples/fresh/manifest.json'
PRIVATE = 'private/labels'
FORMAT = 'clauseguard-labels-v1'
ANNOTATORS = ('A1', 'A2')
ANSWER = re.compile(r'^[1-8](\s*,\s*[1-8])*$')


def now():
    return datetime.now(timezone.utc).isoformat(timespec='seconds')


def documents(root=ROOT):
    """{doc_id: manifest entry} for the fresh documents."""
    data = json.loads((Path(root) / MANIFEST).read_text(encoding='utf-8'))
    return {d['doc_id']: d for d in data['documents']}


def load_document(doc_id, root=ROOT):
    """(manifest entry, text, sentences) after checking the file is the one in the manifest."""
    docs = documents(root)
    if doc_id not in docs:
        raise ValueError(f'Unknown document {doc_id!r}. Choose one of: {", ".join(docs)}.')
    doc = docs[doc_id]
    path = Path(root) / doc['file']
    data = path.read_bytes()
    if hashlib.sha256(data).hexdigest() != doc['sha256']:
        raise ValueError(f'{doc["file"]} is not the document in the manifest (SHA-256 differs). Do not label it.')
    text = data.decode('utf-8')
    sentences = segment(text)
    if len(sentences) != doc['sentences']:
        raise ValueError(f'{doc["file"]} splits into {len(sentences)} sentences, the manifest says {doc["sentences"]}.')
    return doc, text, sentences


def label_path(annotator, doc_id, root=ROOT, folder=PRIVATE):
    return Path(root) / folder / annotator / f'{doc_id}.json'


def new_record(doc, annotator):
    return {'format': FORMAT, 'doc_id': doc['doc_id'], 'doc_sha256': doc['sha256'], 'annotator': annotator,
            'guide': 'docs/LABELLING_GUIDE.md', 'total_sentences': doc['sentences'], 'complete': False,
            'started_utc': now(), 'finished_utc': None, 'seconds_active': 0.0, 'sentences': []}


def save(record, path):
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix('.partial')
    tmp.write_text(json.dumps(record, indent=2) + '\n', encoding='utf-8')
    tmp.replace(path)


def parse_answer(raw):
    """('labels', [names]) | ('unsure', []) | ('back'|'help'|'quit', None) | ('bad', None)."""
    raw = raw.strip().lower()
    if raw == '':
        return 'labels', []
    if raw in ('?', 'b', 'h', 'q'):
        return {'?': ('unsure', []), 'b': ('back', None), 'h': ('help', None), 'q': ('quit', None)}[raw]
    if ANSWER.fullmatch(raw):
        numbers = sorted({int(x) for x in re.split(r'\s*,\s*', raw)})
        return 'labels', [LABELS[n - 1] for n in numbers]
    return 'bad', None


def category_list():
    return '\n'.join(f'  {i}  {label}' for i, label in enumerate(LABELS, start=1))


def label(doc_id, annotator, root=ROOT, ask=input, say=print, clock=time.monotonic):
    """Label (or continue labelling) one document. Returns the saved record."""
    if annotator not in ANNOTATORS:
        raise ValueError('The annotator must be A1 (Hemanth) or A2 (Jayakrishna).')
    doc, _, sentences = load_document(doc_id, root)
    path = label_path(annotator, doc_id, root)
    record = json.loads(path.read_text(encoding='utf-8')) if path.exists() else new_record(doc, annotator)
    if record.get('doc_sha256') != doc['sha256'] or record.get('annotator') != annotator:
        raise ValueError(f'{path} belongs to another document version or annotator. Do not edit it; tell the team.')
    say(f'Labelling {doc["title"]} ({doc_id}) as {annotator}. Guide: docs/LABELLING_GUIDE.md')
    say('Categories:\n' + category_list())
    say('Type numbers like 3 or 1,5; Enter = none; ? = unsure; b = back; h = list; q = save and stop.')
    i = len(record['sentences'])
    while i < len(sentences):
        s = sentences[i]
        say('')
        if i > 0:
            say(f'    (before) {sentences[i - 1].text}')
        say(f'Sentence {i + 1} of {len(sentences)}:')
        say(f'    {s.text}')
        started = clock()
        kind, value = parse_answer(ask('Categories: '))
        record['seconds_active'] = round(record['seconds_active'] + min(clock() - started, 300.0), 1)
        if kind == 'quit':
            save(record, path)
            say(f'Saved {i} of {len(sentences)} sentences to {path.relative_to(root)}. Run the same command to continue.')
            return record
        if kind == 'help':
            say('Categories:\n' + category_list())
            continue
        if kind == 'bad':
            say('Not understood. Type numbers 1 to 8 separated by commas, Enter, ?, b, h or q.')
            continue
        if kind == 'back':
            if i > 0:
                record['sentences'].pop()
                i -= 1
                save(record, path)
            continue
        record['sentences'].append({'sentence_id': i, 'start': s.start, 'end': s.end, 'labels': value,
                                    'unsure': kind == 'unsure'})
        i += 1
        save(record, path)
    record['complete'] = True
    record['finished_utc'] = record['finished_utc'] or now()
    save(record, path)
    say(f'Done: {doc_id}, {len(sentences)} sentences saved to {path.relative_to(root)}.')
    return record


def fingerprint(annotator, root=ROOT, folder=PRIVATE):
    """SHA-256 over the annotator's complete label files in manifest order, or None if any is missing or incomplete."""
    h = hashlib.sha256()
    for doc_id in documents(root):
        path = label_path(annotator, doc_id, root, folder)
        if not path.exists() or not json.loads(path.read_text(encoding='utf-8')).get('complete'):
            return None
        h.update(path.read_bytes())
    return h.hexdigest()


def status(annotator, root=ROOT, say=print):
    done = 0
    docs = documents(root)
    for doc_id, doc in docs.items():
        path = label_path(annotator, doc_id, root)
        n = len(json.loads(path.read_text(encoding='utf-8'))['sentences']) if path.exists() else 0
        done += n == doc['sentences']
        say(f'{doc_id:12s} {n:4d} of {doc["sentences"]:4d} sentences' + ('  done' if n == doc['sentences'] else ''))
    fp = fingerprint(annotator, root)
    if fp:
        say(f'All {len(docs)} documents labelled by {annotator}. Fingerprint: {fp}')
    else:
        say(f'{done} of {len(docs)} documents finished by {annotator}. No fingerprint until all are finished.')
    return fp


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument('--annotator', required=True, choices=ANNOTATORS)
    p.add_argument('--doc', help='document ID from examples/fresh/manifest.json')
    p.add_argument('--status', action='store_true', help='show progress and the fingerprint')
    a = p.parse_args(argv)
    try:
        if a.status:
            status(a.annotator)
        elif a.doc:
            label(a.doc, a.annotator)
        else:
            p.error('Give --doc <doc_id> or --status.')
    except (ValueError, OSError) as e:
        p.exit(2, f'Not labelled: {e}\n')
    except (KeyboardInterrupt, EOFError):
        p.exit(1, '\nStopped. Everything up to the last answer is saved; run the same command to continue.\n')
    return 0


if __name__ == '__main__':
    sys.exit(main())
