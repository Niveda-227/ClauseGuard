"""Fresh real Terms of Service for the Session 10 domain-shift check.

    python scripts/fresh_docs.py --check          # verify the committed documents (no network)

The three documents in examples/fresh/ are real, current Terms of Service from companies that are
NOT in the UNFAIR-ToS dataset (not in its train, validation or test split). They were chosen
because their owners publish them under open licences, so the full text may be stored here with
attribution (see examples/fresh/SOURCES.md):

  basecamp     37signals Terms of Service            CC BY 4.0      github.com/basecamp/policies
  cloudup      Cloudup Terms of Service (Automattic) CC BY-SA 4.0   github.com/Automattic/legalmattic
  crowdsignal  Crowdsignal Terms and Conditions      CC BY-SA 4.0   github.com/Automattic/legalmattic

Each was converted from the Markdown source at a pinned commit to plain text with md_to_text()
below (front matter, links, emphasis and list markers removed; one paragraph or list item per
line; nothing reworded). --check confirms every committed file still has the SHA-256 and the
sentence count (with the product's own sentence splitter, clauses/text.py) recorded in
examples/fresh/manifest.json, so labels made against these files stay valid.
"""
import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from clauses.text import segment  # noqa: E402

MANIFEST = 'examples/fresh/manifest.json'


def md_to_text(md):
    """Plain text from a Markdown policy page, one paragraph or list item per line."""
    md = re.sub(r'^---\n.*?\n---\n', '', md, flags=re.S)
    md = re.sub(r'<!--.*?-->', '', md, flags=re.S)
    md = re.sub(r'\{\{[^}]*\}\}', '', md)
    md = re.sub(r'!\[[^\]]*\]\([^)]*\)', '', md)
    md = re.sub(r'\[([^\]]+)\]\([^)]*\)', r'\1', md)
    md = re.sub(r'\[([^\]]+)\]\[[^\]]*\]', r'\1', md)
    md = re.sub(r'<[^>]+>', '', md)
    out = []
    for line in md.splitlines():
        s = line.strip()
        if not s:
            continue
        s = re.sub(r'^#{1,6}\s*', '', s)
        s = re.sub(r'^([-*+]|\d+\.)\s+', '', s)
        s = s.replace('**', '').replace('__', '').replace('`', '')
        s = re.sub(r'(?<!\w)\*(?!\s)([^*]+)\*(?!\w)', r'\1', s)
        s = re.sub(r'(?<!\w)_(?!\s)([^_]+)_(?!\w)', r'\1', s)
        s = re.sub(r'\\([\\`*_{}\[\]()#+\-.!@])', r'\1', s)
        s = re.sub(r'\s+', ' ', s).strip()
        if s and not re.fullmatch(r'[-=*_|: ]+', s):
            out.append(s)
    return '\n'.join(out) + '\n'


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def load_manifest(root=ROOT):
    return json.loads((Path(root) / MANIFEST).read_text(encoding='utf-8'))


def check(root=ROOT):
    """[(doc_id, problem or '')] for every document in the manifest."""
    root = Path(root)
    results = []
    for doc in load_manifest(root)['documents']:
        path = root / doc['file']
        if not path.is_file():
            results.append((doc['doc_id'], f'{doc["file"]} is missing'))
            continue
        problems = []
        if sha256(path) != doc['sha256']:
            problems.append('SHA-256 differs from the manifest (the file was changed)')
        n = len(segment(path.read_text(encoding='utf-8')))
        if n != doc['sentences']:
            problems.append(f'{n} sentences, manifest says {doc["sentences"]}')
        for field in ('title', 'company', 'license', 'license_url', 'source_url', 'source_commit'):
            if not doc.get(field):
                problems.append(f'manifest field {field} is empty')
        results.append((doc['doc_id'], '; '.join(problems)))
    return results


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument('--check', action='store_true', help='verify the committed documents')
    p.add_argument('--convert', nargs=2, metavar=('MARKDOWN', 'OUT_TXT'), help='convert one Markdown file')
    a = p.parse_args(argv)
    if a.convert:
        Path(a.convert[1]).write_text(md_to_text(Path(a.convert[0]).read_text(encoding='utf-8')), encoding='utf-8')
        print(f'Wrote {a.convert[1]}')
        return 0
    results = check()
    total = 0
    for doc in load_manifest()['documents']:
        total += doc['sentences']
    for doc_id, problem in results:
        print(f"{'FAIL' if problem else 'PASS'}  {doc_id}" + (f'  -> {problem}' if problem else ''))
    bad = [r for r in results if r[1]]
    print(f'{len(results)} documents, {total} sentences. ' + ('FRESH DOCUMENTS CHANGED: stop and tell the team.' if bad else 'Fresh documents OK.'))
    return 1 if bad else 0


if __name__ == '__main__':
    sys.exit(main())
