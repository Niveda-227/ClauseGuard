"""Cost per request of the ClauseGuard web app, measured on the real request path (Session 09).

    python scripts/cost_per_request.py
    python scripts/cost_per_request.py --price-per-hour 0.00893 --price-plan "..." --price-url https://... \
        --price-date 2026-10-27 --plan-memory-mb 1024

It starts the web app's own server (webapp.server.make_server) on a free port on 127.0.0.1, then
sends real HTTP requests to /api/analyze, one at a time, for two documents:
  study  examples/study/document_F.txt, a 16-sentence study document
  long   examples/fictional_terms.txt repeated 100 times (1,100 sentences)
For each document it records, per request:
  - wall-clock latency: median and 95th percentile (nearest rank)
  - CPU seconds per request (time.process_time of this process, which runs both the server and
    the client, so it slightly overstates the server's share)
and, for the whole process, the peak memory (resource.getrusage; on Windows, tracemalloc, which
counts Python allocations only).

Money: the product runs on the user's own computer and calls no API, so the cost to us per request
is $0; the honest costs are the user's computer and their setup time. A hosted estimate is written
ONLY when a price looked up on a provider's pricing page is given, with its URL and the date it was
looked up. It is never invented. The estimate assumes one small server answering requests one at a
time: cost per request = price per hour x median seconds per request / 3600.

Writes experiments/session09/cost_per_request.json and .md (no hostname, username or file paths).
"""
import argparse
import http.client
import json
import math
import platform
import re
import statistics
import sys
import threading
import time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

STUDY_DOC = 'examples/study/document_F.txt'
LONG_DOC = 'examples/fictional_terms.txt'
LONG_COPIES = 100
REQUESTS = 30
WARMUP = 2
OUT = 'experiments/session09/cost_per_request'


def p95(values):
    """95th percentile by the nearest-rank method (always one of the measured values)."""
    ordered = sorted(values)
    if not ordered:
        raise ValueError('No measurements.')
    return ordered[max(0, math.ceil(0.95 * len(ordered)) - 1)]


def peak_memory_mb():
    try:
        import resource
    except ImportError:  # Windows
        import tracemalloc
        return round(tracemalloc.get_traced_memory()[1] / 1024 / 1024, 1), 'tracemalloc (Python allocations only)'
    peak = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    # macOS reports bytes, Linux reports kilobytes.
    mb = peak / 1024 / 1024 if sys.platform == 'darwin' else peak / 1024
    return round(mb, 1), 'resource.getrusage, peak resident memory of the whole process'


def check_price(price):
    """None, or a validated dict with a looked-up price; refuse partial or invented-looking input."""
    if price is None:
        return None
    needed = ('per_hour_usd', 'plan', 'url', 'looked_up_on')
    missing = [k for k in needed if price.get(k) in (None, '')]
    if missing:
        raise ValueError('A hosted price needs all of --price-per-hour, --price-plan, --price-url and --price-date '
                         f'(missing: {", ".join(missing)}).')
    if not (isinstance(price['per_hour_usd'], (int, float)) and 0 < price['per_hour_usd'] < 100):
        raise ValueError('--price-per-hour must be a positive number of US dollars per hour.')
    if not re.fullmatch(r'https://[^\s]+', price['url']):
        raise ValueError('--price-url must be the https:// address of the pricing page.')
    if not re.fullmatch(r'\d{4}-\d{2}-\d{2}', price['looked_up_on']):
        raise ValueError('--price-date must be the date the price was looked up, as YYYY-MM-DD.')
    return price


class Client:
    def __init__(self, port):
        self.port = port

    def analyze(self, text):
        body = json.dumps({'text': text}).encode('utf-8')
        conn = http.client.HTTPConnection('127.0.0.1', self.port, timeout=120)
        conn.request('POST', '/api/analyze', body=body,
                     headers={'Host': f'127.0.0.1:{self.port}', 'Content-Type': 'application/json'})
        response = conn.getresponse()
        data = response.read()
        conn.close()
        if response.status != 200:
            raise RuntimeError(f'The web app answered {response.status}.')
        return json.loads(data)


def measure(client, text, requests):
    for _ in range(WARMUP):
        client.analyze(text)
    wall, cpu = [], []
    for _ in range(requests):
        t, c = time.perf_counter(), time.process_time()
        client.analyze(text)
        wall.append(time.perf_counter() - t)
        cpu.append(time.process_time() - c)
    med, high, cpu_med = statistics.median(wall), p95(wall), statistics.median(cpu)
    return {
        'requests': requests,
        'median_seconds': round(med, 4),
        'p95_seconds': round(high, 4),
        'cpu_seconds_per_request': round(cpu_med, 4),
        'median_ms': round(1000 * med, 1),
        'p95_ms': round(1000 * high, 1),
        'cpu_ms_per_request': round(1000 * cpu_med, 1),
    }


def hosted(price, documents, peak_mb, plan_memory_mb):
    if price is None:
        return None
    out = {
        'plan': price['plan'],
        'price_per_hour_usd': price['per_hour_usd'],
        'price_source_url': price['url'],
        'price_looked_up_on': price['looked_up_on'],
        'assumption': 'One server of this plan answers requests one at a time; the cost of a request is the '
                      'price of the seconds it takes (price per hour x median seconds / 3600).',
    }
    for name, d in documents.items():
        per_request = price['per_hour_usd'] * d['median_seconds'] / 3600
        out[f'{name}_cost_per_million_requests_usd'] = round(per_request * 1_000_000, 4)
        out[f'{name}_requests_per_hour_one_at_a_time'] = round(3600 / d['median_seconds']) if d['median_seconds'] else None
    if plan_memory_mb:
        out['plan_memory_mb'] = plan_memory_mb
        out['peak_memory_fits_in_plan'] = peak_mb < plan_memory_mb
    out['note'] = ('An always-on server is billed by the hour whatever the traffic, so at low traffic the '
                   'hourly price, not the cost per request, is what matters.')
    return out


def run(root=ROOT, requests=REQUESTS, long_copies=LONG_COPIES, price=None, plan_memory_mb=None):
    root = Path(root)
    price = check_price(price)
    if requests < 5:
        raise ValueError('Use at least 5 requests per document.')
    if 'resource' not in sys.modules:
        try:
            import resource  # noqa: F401
        except ImportError:
            import tracemalloc
            tracemalloc.start()
    from clauses.model import DEFAULT_MODEL, load
    from webapp.server import make_server

    t = time.perf_counter()
    bundle = load(DEFAULT_MODEL)
    load_seconds = time.perf_counter() - t
    server = make_server(bundle, port=0, quiet=True)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        client = Client(server.server_address[1])
        study_text = (root / STUDY_DOC).read_text(encoding='utf-8')
        long_text = '\n'.join([(root / LONG_DOC).read_text(encoding='utf-8').strip()] * long_copies)
        documents = {}
        for name, path, text in (('study', STUDY_DOC, study_text),
                                 ('long', f'{LONG_DOC} x {long_copies}', long_text)):
            sentences = len(client.analyze(text)['result']['sentences'])
            documents[name] = {'document': path, 'sentences': sentences, 'characters': len(text),
                               **measure(client, text, requests)}
    finally:
        server.shutdown()
        server.server_close()
    peak_mb, method = peak_memory_mb()
    return {
        'measured_utc': datetime.now(timezone.utc).isoformat(timespec='seconds'),
        'purpose': 'Cost per request of the web app on the real request path (HTTP to /api/analyze on 127.0.0.1)',
        'machine': {'os': {'Darwin': 'macOS'}.get(platform.system(), platform.system()),
                    'os_release': platform.release(), 'cpu_arch': platform.machine(),
                    'python': platform.python_version()},
        'model_sha256': bundle['model_id'],
        'model_load_seconds': round(load_seconds, 3),
        'warmup_requests_per_document': WARMUP,
        'documents': documents,
        'peak_memory_mb': peak_mb,
        'peak_memory_method': method,
        'network_calls_outside_this_computer': 0,
        'api_cost_per_request_usd': 0.0,
        'local_cost_note': 'The product runs on the user\'s own computer and calls no API, so each request costs '
                           'us nothing. The honest costs are the user\'s computer, its electricity and their setup time.',
        'hosted_estimate': hosted(price, documents, peak_mb, plan_memory_mb),
    }


def to_markdown(r):
    d = r['documents']
    lines = ['# Cost per request of the web app (Session 09)', '',
             f"Measured {r['measured_utc']} on {r['machine']['os']} {r['machine']['cpu_arch']}, Python {r['machine']['python']}, "
             f"model `{r['model_sha256'][:12]}`. Real HTTP requests to `/api/analyze` on 127.0.0.1, one at a time, "
             f"after {r['warmup_requests_per_document']} warm-up requests.", '',
             '| Document | Sentences | Requests | Median (ms) | 95th percentile (ms) | CPU per request (ms) |',
             '|---|---:|---:|---:|---:|---:|']
    for name in ('study', 'long'):
        x = d[name]
        lines.append(f"| {x['document']} | {x['sentences']} | {x['requests']} | {x['median_ms']} | {x['p95_ms']} | {x['cpu_ms_per_request']} |")
    lines += ['', f"Model load: {r['model_load_seconds']} s. Peak memory: {r['peak_memory_mb']} MB ({r['peak_memory_method']}).",
              f"Network calls outside this computer: {r['network_calls_outside_this_computer']}. "
              f"API cost per request: ${r['api_cost_per_request_usd']:.2f}.", '', r['local_cost_note'], '']
    h = r['hosted_estimate']
    if h is None:
        lines.append('Hosted estimate: not made, because no looked-up price was given.')
    else:
        lines += [f"**Hosted estimate** ({h['plan']}, ${h['price_per_hour_usd']} per hour, from {h['price_source_url']}, "
                  f"looked up {h['price_looked_up_on']}): ${h['study_cost_per_million_requests_usd']} per million requests "
                  f"for the study document and ${h['long_cost_per_million_requests_usd']} per million for the long document. "
                  + h['assumption']]
        if 'peak_memory_fits_in_plan' in h:
            lines.append(f"Peak memory fits in the plan's {h['plan_memory_mb']} MB: {'yes' if h['peak_memory_fits_in_plan'] else 'NO'}.")
        lines += ['', h['note']]
    return '\n'.join(lines) + '\n'


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument('--requests', type=int, default=REQUESTS, help=f'requests per document (default {REQUESTS})')
    p.add_argument('--price-per-hour', type=float, help='US dollars per hour, copied from the pricing page')
    p.add_argument('--price-plan', help='the plan name as the pricing page shows it')
    p.add_argument('--price-url', help='https:// address of the pricing page')
    p.add_argument('--price-date', help='date the price was looked up, YYYY-MM-DD')
    p.add_argument('--plan-memory-mb', type=int, help="the plan's memory in MB, to check the peak memory fits")
    p.add_argument('--output', default=OUT, help=f'output path without extension (default {OUT})')
    a = p.parse_args(argv)
    given = [a.price_per_hour, a.price_plan, a.price_url, a.price_date]
    price = None if all(v is None for v in given) else {
        'per_hour_usd': a.price_per_hour, 'plan': a.price_plan, 'url': a.price_url, 'looked_up_on': a.price_date}
    try:
        r = run(requests=a.requests, price=price, plan_memory_mb=a.plan_memory_mb)
    except (ValueError, RuntimeError, OSError) as e:
        print(f'STOPPED: {e}', file=sys.stderr)
        return 1
    out = ROOT / a.output
    out.parent.mkdir(parents=True, exist_ok=True)
    out.with_suffix('.json').write_text(json.dumps(r, indent=2) + '\n', encoding='utf-8')
    out.with_suffix('.md').write_text(to_markdown(r), encoding='utf-8')
    for name in ('study', 'long'):
        x = r['documents'][name]
        print(f"{name:5s} {x['sentences']:5d} sentences: median {x['median_ms']} ms, 95th percentile {x['p95_ms']} ms, "
              f"CPU {x['cpu_ms_per_request']} ms per request")
    print(f"Peak memory {r['peak_memory_mb']} MB. Network calls outside this computer: 0. API cost per request: $0.00.")
    h = r['hosted_estimate']
    if h:
        print(f"Hosted estimate: ${h['study_cost_per_million_requests_usd']} per million requests (study document), "
              f"${h['long_cost_per_million_requests_usd']} (long document)"
              + (f"; peak memory fits in {h['plan_memory_mb']} MB: {'yes' if h['peak_memory_fits_in_plan'] else 'NO'}"
                 if 'peak_memory_fits_in_plan' in h else ''))
    else:
        print('Hosted estimate: not made (no looked-up price given).')
    print(f'Wrote {a.output}.json and {a.output}.md')
    return 0


if __name__ == '__main__':
    sys.exit(main())
