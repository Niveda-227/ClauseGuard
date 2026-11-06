"""Fill the numbers in a teammate's session notes from the result files, and check the notes (Session 10).

    python scripts/fill_notes.py experiments/session10/hemanth_session10_notes.md

A notes file has two kinds of places:
  <<...>>   written BY HAND first: your own words (what you saw, how you decided). Words only:
            do not type any number with a decimal point; numbers come from the tokens.
  {{FROM:experiments/session10/<file>.json#<key>|2}}   filled by THIS script with one value
            from a result file (same token format as scripts/finalize_report.py).

The script refuses to change anything while a <<...>> place is left, while a hand-written part
has a decimal number, or when a token points to a file that is not a JSON result in
experiments/session10/. It then writes the filled notes back to the same file, with a last line
saying it was filled, and prints PASS. Running it again on a filled file only checks that no
<<...>> or {{...}} place is left, and changes nothing.
"""
import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from scripts.finalize_report import FROM, from_value  # noqa: E402

RESULTS = 'experiments/session10/'
DECIMAL = re.compile(r'(?<![\w.])\d+\.\d+(?![\w.])')
MARK = '<!-- Numbers filled by scripts/fill_notes.py from the result files in experiments/session10/. -->'


def fill(path, root=ROOT):
    """Return the filled text, or raise ValueError saying what to fix."""
    root = Path(root)
    text = Path(path).read_text(encoding='utf-8')
    if MARK in text:
        if re.search(r'<<|{{', text):
            raise ValueError('The notes were filled before but now contain <<...>> or {{...}} again.')
        return text
    left = re.findall(r'<<[^>]*>>', text)
    if left:
        raise ValueError(f'{len(left)} <<...>> place(s) still to write by hand. First: {left[0][:70]}')
    hand = FROM.sub('', text)
    hand = re.sub(r'`[^`]*`', '', hand)  # file names and commands in backticks may contain version numbers
    typed = DECIMAL.findall(hand)
    if typed:
        raise ValueError(f'Numbers typed by hand: {", ".join(typed[:5])}. Use a {{{{FROM:...}}}} token instead.')
    sources = sorted({m.group(1).strip() for m in FROM.finditer(text)})
    for rel in sources:
        if not rel.startswith(RESULTS) or not rel.endswith('.json'):
            raise ValueError(f'{rel}: tokens may only read JSON results in {RESULTS}')
    text = FROM.sub(lambda m: from_value(root, m.group(1).strip(), m.group(2).strip(), m.group(3) == '%',
                                         m.group(4), sources), text)
    leftover = re.findall(r'{{[^{}]*}}', text)
    if leftover:
        raise ValueError(f'Unknown token(s): {leftover[:3]}')
    return text.rstrip('\n') + '\n\n' + MARK + '\n'


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument('notes')
    a = p.parse_args(argv)
    path = Path(a.notes)
    try:
        text = fill(path, ROOT)
    except (ValueError, OSError) as e:
        print(f'NOTES NOT READY: {e}')
        return 1
    if text != path.read_text(encoding='utf-8'):
        path.write_text(text, encoding='utf-8')
        print(f'PASS: filled the numbers in {a.notes}; no hand-typed decimal numbers.')
    else:
        print(f'PASS: {a.notes} was already filled; nothing changed.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
