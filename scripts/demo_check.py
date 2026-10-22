"""Pre-flight check for a live ClauseGuard demo, plus a cost-to-serve measurement.

Run it on the laptop that will present, the day before and one hour before:

    python scripts/demo_check.py

It answers five questions and exits with code 1 if any hard check fails:
  1. Is this the model we report numbers for? (the running artifact is byte-identical
     to the evaluated model named below and to its validation metrics)
  2. Will the demo look like the rehearsal? (the fictional demo document gets the
     same flags as when the demo was scripted)
  3. How much does one request cost? (load time, time per document, time per
     sentence on a ~1,100-sentence document; no network calls are made)
  4. Can this laptop open the desktop app? (Tk available; display available)
  5. Does the web app (python -m webapp, Session 08) show exactly what the desktop app shows?
     (it starts the web server on a free local port for a moment and compares the results)

Writes experiments/session08/demo_check.json (no hostname, username or file paths)
and an HTML fallback of the demo document to analysis.html (git-ignored), which can
be opened in a browser if the desktop app fails during the presentation.
"""
import argparse
import hashlib
import importlib
import json
import platform
import statistics
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

DEMO_DOC = 'examples/fictional_terms.txt'
# The model the app should be running, and the evaluation of exactly that file.
# Session 07: per-category thresholds were shipped (scripts/ship_thresholds.py --promote).
EVALUATED_ARTIFACT = 'artifacts/tuned.joblib'
EVALUATED_METRICS = 'experiments/session07/tuned/metrics.json'
# Flags the shipped model gives the demo document, one entry per sentence, recorded
# when the demo was scripted (Session 06) and re-checked when per-category thresholds
# shipped (Session 07): unchanged, including the wrong 'Unilateral termination' tag on
# sentence 3 (score 0.841 > its 0.70 threshold). A change means the demo will not match
# the rehearsal, so the presenter must know before going live.
EXPECTED_DEMO_LABELS = [
    [],
    ['Contract by using'],
    ['Unilateral termination', 'Unilateral change'],
    ['Unilateral termination', 'Content removal'],
    ['Content removal'],
    ['Limitation of liability'],
    ['Choice of law'],
    ['Jurisdiction'],
    ['Arbitration'],
    [],
    [],
]
PACKAGES = {'numpy': 'numpy', 'scipy': 'scipy', 'scikit-learn': 'sklearn', 'joblib': 'joblib'}


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def pinned_versions(requirements):
    pins = {}
    for line in Path(requirements).read_text(encoding='utf-8').splitlines():
        line = line.split('#')[0].strip()
        if '==' in line:
            name, version = line.split('==', 1)
            pins[name.strip().lower()] = version.strip()
    return pins


def check_packages(requirements):
    """scikit-learn must match exactly (the model file depends on it); others warn."""
    out = []
    pins = pinned_versions(requirements)
    for dist, module in PACKAGES.items():
        want = pins.get(dist)
        try:
            have = importlib.import_module(module).__version__
        except ImportError:
            have = None
        if have == want:
            status = 'PASS'
        elif dist == 'scikit-learn' or have is None:
            status = 'FAIL'
        else:
            status = 'WARN'
        out.append({'check': f'package {dist}', 'status': status, 'expected': want, 'found': have})
    return out


def check_identity(root):
    """The artifact the app loads must be the one whose validation numbers we present."""
    root = Path(root)
    selected = sha256(root / 'artifacts/selected.joblib')
    evidence = {
        'artifacts/selected.joblib (file on disk)': selected,
        'artifacts/selected.json artifact_sha256': json.loads((root / 'artifacts/selected.json').read_text())['artifact_sha256'],
        f'{EVALUATED_ARTIFACT} (evaluated model file)': sha256(root / EVALUATED_ARTIFACT),
        f'{EVALUATED_METRICS} model_id': json.loads((root / EVALUATED_METRICS).read_text())['model_id'],
    }
    same = len(set(evidence.values())) == 1
    return {'check': 'demo model is the reported model', 'status': 'PASS' if same else 'FAIL',
            'model_sha256': selected, 'compared': evidence}


def compare_demo(result, expected=EXPECTED_DEMO_LABELS):
    got = [row['labels'] for row in result['sentences']]
    diffs = []
    for i in range(max(len(got), len(expected))):
        g = got[i] if i < len(got) else None
        e = expected[i] if i < len(expected) else None
        if g != e:
            diffs.append({'sentence': i + 1, 'expected': e, 'found': g})
    return {'check': 'demo document flags match the rehearsal', 'status': 'PASS' if not diffs else 'FAIL',
            'sentences': len(got), 'flagged': sum(bool(x) for x in got), 'differences': diffs}


def timed(fn, repeats):
    times = []
    for _ in range(repeats):
        t = time.perf_counter()
        fn()
        times.append(time.perf_counter() - t)
    return statistics.median(times)


def check_tk():
    try:
        import tkinter
    except ImportError as exc:
        return {'check': 'desktop app (Tk) available', 'status': 'FAIL', 'detail': f'tkinter missing: {exc}'}
    try:
        root = tkinter.Tk()
        root.withdraw()
        root.destroy()
        return {'check': 'desktop app (Tk) available', 'status': 'PASS', 'tk_version': tkinter.TkVersion}
    except tkinter.TclError as exc:
        return {'check': 'desktop app (Tk) available', 'status': 'WARN', 'tk_version': tkinter.TkVersion,
                'detail': f'Tk is installed but no display was found here ({exc}). Fine on a laptop screen.'}


def check_web(bundle, text):
    """Start the web app's server on a free port on 127.0.0.1, analyse the demo document through it,
    and compare with analyze() called directly (what the desktop app does)."""
    import http.client
    import threading
    from clauses.model import analyze
    from webapp.server import make_server
    name = 'web app shows the same result as the desktop app'
    try:
        server = make_server(bundle, port=0, quiet=True)
    except OSError as exc:
        return {'check': name, 'status': 'FAIL', 'detail': f'could not start the web server: {exc}'}
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        port = server.server_address[1]
        headers = {'Host': f'127.0.0.1:{port}', 'Content-Type': 'application/json'}
        conn = http.client.HTTPConnection('127.0.0.1', port, timeout=60)
        conn.request('GET', '/api/meta', headers={'Host': headers['Host']})
        meta = json.loads(conn.getresponse().read())
        conn.request('POST', '/api/analyze', body=json.dumps({'text': text}), headers=headers)
        response = conn.getresponse()
        web = json.loads(response.read())
        conn.close()
    finally:
        server.shutdown()
        server.server_close()
    direct = json.loads(json.dumps(analyze(text, bundle)))
    same = response.status == 200 and web.get('result') == direct and meta.get('model_id') == bundle['model_id']
    return {'check': name, 'status': 'PASS' if same else 'FAIL', 'web_model_sha256': meta.get('model_id'),
            'detail': '' if same else 'the web app returned a different result or model'}


def run(root=ROOT, repeats=5, long_copies=100):
    from clauses.model import load, analyze
    from clauses.export import render_html
    root = Path(root)
    checks = []
    py = platform.python_version()
    checks.append({'check': 'Python 3.12', 'status': 'PASS' if py.startswith('3.12.') else 'WARN', 'found': py})
    checks += check_packages(root / 'requirements.txt')
    checks.append(check_identity(root))

    t = time.perf_counter()
    bundle = load(root / 'artifacts/selected.joblib')
    load_seconds = time.perf_counter() - t
    demo_text = (root / DEMO_DOC).read_text(encoding='utf-8')
    result = analyze(demo_text, bundle)
    checks.append(compare_demo(result))
    tk, web = check_tk(), check_web(bundle, demo_text)
    if tk['status'] == 'FAIL' and web['status'] == 'PASS':
        # From Session 08 the demo can run in the browser, so a laptop without Tk can still present.
        tk = {**tk, 'status': 'WARN', 'detail': f"{tk.get('detail', '')} Present with the web app instead: python -m webapp".strip()}
    checks += [tk, web]

    long_text = '\n'.join([demo_text.strip()] * long_copies)
    long_sentences = len(analyze(long_text, bundle)['sentences'])
    demo_s = timed(lambda: analyze(demo_text, bundle), repeats)
    long_s = timed(lambda: analyze(long_text, bundle), max(1, repeats // 2))
    cost = {
        'model_load_seconds': round(load_seconds, 3),
        'demo_document_sentences': len(result['sentences']),
        'demo_document_median_seconds': round(demo_s, 4),
        'long_document_sentences': long_sentences,
        'long_document_characters': len(long_text),
        'long_document_median_seconds': round(long_s, 3),
        'ms_per_sentence_long_document': round(1000 * long_s / long_sentences, 3),
        'network_calls': 0,
        'api_cost_per_request_usd': 0.0,
        'note': 'Measured on this laptop only. The product runs locally on the user\'s CPU and makes no '
                'API or network calls, so there is no per-request service cost; the costs are the user\'s '
                'setup time and their own computer.',
    }
    return {
        'checked_utc': datetime.now(timezone.utc).isoformat(timespec='seconds'),
        'purpose': 'Pre-flight check of the running app (model identity, demo flags, environment) and cost-to-serve measurement',
        'machine': {'os': platform.system(), 'os_release': platform.release(), 'cpu_arch': platform.machine(),
                    'python': py},
        'model_sha256': bundle['model_id'],
        'threshold_source': bundle['manifest']['threshold_source'],
        'demo_document': DEMO_DOC,
        'checks': checks,
        'cost_to_serve': cost,
        'passed': all(c['status'] != 'FAIL' for c in checks),
    }, render_html(result)


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument('--output', default='experiments/session08/demo_check.json')
    p.add_argument('--html-out', default='analysis.html', help='HTML fallback of the demo document (git-ignored)')
    p.add_argument('--repeats', type=int, default=5)
    a = p.parse_args(argv)
    report, html = run(repeats=a.repeats)
    out = ROOT / a.output
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    (ROOT / a.html_out).write_text(html, encoding='utf-8')
    for c in report['checks']:
        extra = c.get('found') or c.get('detail') or ''
        print(f"{c['status']:4s}  {c['check']}" + (f'  ({extra})' if extra and c['status'] != 'PASS' else ''))
        for d in c.get('differences', []):
            print(f"        sentence {d['sentence']}: expected {d['expected']}, found {d['found']}")
    cost = report['cost_to_serve']
    print(f"\nModel {report['model_sha256'][:12]} · load {cost['model_load_seconds']} s · demo document "
          f"{cost['demo_document_median_seconds']} s · {cost['ms_per_sentence_long_document']} ms per sentence "
          f"on a {cost['long_document_sentences']}-sentence document · no network calls")
    print(f'Wrote {a.output} and {a.html_out} (HTML fallback for the demo).')
    print('READY FOR THE DEMO' if report['passed'] else 'NOT READY: fix every FAIL line above before presenting.')
    return 0 if report['passed'] else 1


if __name__ == '__main__':
    sys.exit(main())
