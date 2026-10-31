"""Check that every decimal number and percentage in a weekly report comes from a source file (Session 09).

    python scripts/check_report_numbers.py --report reports/session09.md

Why: the Session 08 report quoted interim numbers (16.67 points, 83.33%) instead of the final
re-check it linked to. No script checked numbers in prose. This one does.

How it works:
  1. It reads the report and ignores code (`...` and fenced blocks), HTML comments, link
     addresses and web addresses.
  2. It finds every number with a decimal point (31.65, 0.6768, 100.00) and every percentage
     (40%, 50.6%). Whole numbers without % (counts, issue numbers, years) are not checked.
  3. It reads the source files listed under "number_sources" in reports/facts/sessionNN.json:
     JSON files (every number in them, including numbers inside text values) and text files such
     as .md or .csv (every number written in them). A source whose JSON has a "superseded_by" key,
     or whose text starts with "SUPERSEDED", is refused: an interim result must not be quoted.
  4. A report number passes when some source number rounds to it at the report's precision
     (31.65 matches 31.648), or, for shares, when 100 x the source number does (50.6 matches 0.5065).
  5. A number the report deliberately quotes from an older file (for example a wrong number it
     corrects) is listed under "quoted_numbers" in the facts file, with the file it is quoted
     from; the script checks that the number really appears in that file.

Every OK line names the source file that matched. A number can match by coincidence (for example
83.33% matches a precision of 0.8333 in another file), so the reviewer still reads each OK line and
checks that its source makes sense for that sentence.

Exit code 1 if any number fails or a source is missing or superseded. It changes nothing.
"""
import argparse
import json
import re
import sys
from decimal import Decimal, InvalidOperation
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
NUMBER = re.compile(r'(?<![\w.])(\d{1,3}(?:,\d{3})+|\d+)(\.\d+)?(\s?%)?(?![\w%]|\.\d)')


class NumberCheckError(ValueError):
    pass


def prose(text):
    """The report text without code, comments, link addresses and web addresses (same length per line)."""
    def blank(m):
        return re.sub(r'[^\n]', ' ', m.group())
    text = re.sub(r'^\s*```.*?^\s*```[^\n]*$', blank, text, flags=re.M | re.S)
    text = re.sub(r'<!--.*?-->', blank, text, flags=re.S)
    text = re.sub(r'`[^`\n]*`', blank, text)
    text = re.sub(r'\]\([^)\n]*\)', blank, text)
    text = re.sub(r'https?://\S+', blank, text)
    return text


def report_numbers(text):
    """[(line, number text, Decimal value, decimals, is_percent)] for decimals and percentages."""
    found = []
    for line_no, line in enumerate(prose(text).splitlines(), start=1):
        for m in NUMBER.finditer(line):
            whole, frac, pct = m.group(1), m.group(2) or '', bool(m.group(3))
            if not frac and not pct:
                continue
            value = Decimal(whole.replace(',', '') + frac)
            found.append((line_no, (whole + frac + ('%' if pct else '')), value, len(frac) - 1 if frac else 0, pct))
    return found


def numbers_in_text(text):
    out = set()
    for m in NUMBER.finditer(text):
        try:
            out.add(Decimal(m.group(1).replace(',', '') + (m.group(2) or '')))
        except InvalidOperation:
            pass
    return out


def numbers_in_json(value, out):
    if isinstance(value, bool) or value is None:
        return out
    if isinstance(value, (int, float)):
        out.add(Decimal(str(value)))
    elif isinstance(value, str):
        out |= numbers_in_text(value)
    elif isinstance(value, list):
        for v in value:
            numbers_in_json(v, out)
    elif isinstance(value, dict):
        for v in value.values():
            numbers_in_json(v, out)
    return out


def load_source(root, rel):
    path = (root / rel).resolve()
    if not path.is_relative_to(root.resolve()):
        raise NumberCheckError(f'{rel} is outside the repository.')
    if not path.is_file():
        raise NumberCheckError(f'number source {rel} does not exist.')
    text = path.read_text(encoding='utf-8')
    if path.suffix == '.json':
        data = json.loads(text)
        if isinstance(data, dict) and 'superseded_by' in data:
            raise NumberCheckError(f'{rel} is superseded by {data["superseded_by"]}. List that file instead.')
        return numbers_in_json(data, set())
    if text.lstrip().upper().startswith('SUPERSEDED'):
        raise NumberCheckError(f'{rel} is marked SUPERSEDED. List the file that replaces it instead.')
    return numbers_in_text(text)


def match_quality(value, decimals, candidates):
    """0 = a source number equals it, 1 = rounds to it, 2 = 100 x a source number equals it,
    3 = 100 x a source number rounds to it; None = no match."""
    half = Decimal(5) * Decimal(10) ** -(decimals + 1)
    best = None
    for c in candidates:
        for quality, scaled in ((0, c), (2, c * 100)):
            if scaled == value:
                q = quality
            elif abs(scaled - value) <= half:
                q = quality + 1
            else:
                continue
            best = q if best is None else min(best, q)
    return best


def check(report, facts, root=ROOT):
    root = Path(root)
    text = Path(report).read_text(encoding='utf-8')
    facts = json.loads(Path(facts).read_text(encoding='utf-8'))
    sources = facts.get('number_sources')
    if not isinstance(sources, list) or not sources:
        raise NumberCheckError('The facts file has no "number_sources" list. List every file the report takes numbers from.')
    by_source = {rel: load_source(root, rel) for rel in sources}
    quoted = {}
    for q in facts.get('quoted_numbers', []):
        number, rel = str(q.get('number', '')), q.get('source', '')
        if not number or not rel or not q.get('why'):
            raise NumberCheckError('Each quoted_numbers entry needs "number", "source" and "why".')
        if Decimal(number.rstrip('%')) not in load_source(root, rel):
            raise NumberCheckError(f'quoted number {number} does not appear in {rel}.')
        quoted[number.rstrip('%')] = rel
    results = []
    for line, shown, value, decimals, pct in report_numbers(text):
        bare = shown.rstrip('%').replace(',', '')
        if bare in quoted:
            results.append(('QUOTE', line, shown, f'quoted from {quoted[bare]} (listed in quoted_numbers)'))
            continue
        found = []
        for order, (rel, nums) in enumerate(by_source.items()):
            q = match_quality(value, decimals, nums)
            if q is not None:
                found.append((q, order, rel))
        if found:
            found.sort()
            extra = f' (also matches {len(found) - 1} other source(s))' if len(found) > 1 else ''
            results.append(('OK', line, shown, found[0][2] + extra))
        else:
            results.append(('FAIL', line, shown, 'not found in any number source'))
    return results


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument('--report', required=True, help='e.g. reports/session09.md')
    p.add_argument('--facts', help='default: reports/facts/sessionNN.json for reports/sessionNN.md')
    a = p.parse_args(argv)
    report = ROOT / a.report
    m = re.fullmatch(r'session(\d{2})\.md', report.name)
    if a.facts:
        facts = ROOT / a.facts
    elif m:
        facts = ROOT / f'reports/facts/session{m.group(1)}.json'
    else:
        p.error('Give --facts for a report not named sessionNN.md.')
    try:
        results = check(report, facts)
    except (NumberCheckError, OSError, json.JSONDecodeError) as e:
        print(f'NUMBER CHECK FAILED: {e}')
        return 1
    for status, line, shown, detail in results:
        print(f'{status:5s} line {line:3d}  {shown:>10s}  {detail}')
    failed = [r for r in results if r[0] == 'FAIL']
    print(f'\n{len(results)} numbers checked, {len(failed)} not found in a source.')
    print('NUMBER CHECK FAILED: fix every FAIL line before pushing.' if failed else 'NUMBER CHECK PASSED')
    return 1 if failed else 0


if __name__ == '__main__':
    sys.exit(main())
