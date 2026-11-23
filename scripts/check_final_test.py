"""Check the record of the one-time test-split run WITHOUT reading the test split (Session 12).

    python scripts/check_final_test.py

For reviewers and the report. It reads only committed files: experiments/test_exposure.jsonl must
hold exactly one reading, by scripts/final_test.py, of the released model; experiments/session12/
test_eval.json must name the same release and model; the rule's result must follow from the
numbers in it; and test_eval.md must be exactly what those numbers produce. It never opens the
dataset. The last line is "FINAL TEST RECORD OK" or "FINAL TEST RECORD NOT OK".
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from scripts.final_test import OUT_JSON, OUT_MD, RULE, decide, to_markdown  # noqa: E402
from scripts.release_files import LEDGER  # noqa: E402


def check(root):
    root = Path(root)
    lines, ok = [], True

    def add(passed, text):
        nonlocal ok
        ok = ok and passed
        lines.append(('PASS  ' if passed else 'FAIL  ') + text)

    release = json.loads((root / 'RELEASE.json').read_text(encoding='utf-8')) if (root / 'RELEASE.json').exists() else {}
    ledger = root / LEDGER
    entries = [json.loads(l) for l in ledger.read_text(encoding='utf-8').splitlines() if l.strip()] if ledger.exists() else []
    add(len(entries) == 1, f'the test split was read exactly once ({len(entries)} reading(s) in {LEDGER})')
    if entries:
        e = entries[0]
        add(e.get('model_id') == release.get('model_sha256') and e.get('by') == 'scripts/final_test.py',
            'the reading used the released model, through scripts/final_test.py')
    if not (root / OUT_JSON).exists():
        add(False, f'{OUT_JSON} exists')
        lines.append('FINAL TEST RECORD NOT OK')
        return False, lines
    r = json.loads((root / OUT_JSON).read_text(encoding='utf-8'))
    add(r['model_sha256'] == release.get('model_sha256') and r['release'] == release.get('version'),
        f"the result names release {r['release']} and model {r['model_sha256'][:12]}")
    rule = json.loads((root / RULE).read_text(encoding='utf-8'))
    diff, result = decide(r['test_macro_f1'], r['honest_validation_macro_f1'], rule)
    add(diff == r['difference_from_honest_validation'] and result == r['result'], f"the rule's result follows from the numbers: {r['result']}")
    add((root / OUT_MD).exists() and (root / OUT_MD).read_text(encoding='utf-8') == to_markdown(r), f'{OUT_MD} matches {OUT_JSON}')
    lines.append('FINAL TEST RECORD OK' if ok else 'FINAL TEST RECORD NOT OK')
    return ok, lines


def main():
    ok, lines = check(ROOT)
    print('\n'.join(lines))
    return 0 if ok else 1


if __name__ == '__main__':
    sys.exit(main())
