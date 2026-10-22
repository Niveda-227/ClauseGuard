"""ClauseGuard web app (Session 08).

    python -m webapp                      # opens http://127.0.0.1:8641 in your browser
    python -m webapp --port 8642          # if 8641 is busy
    python -m webapp --no-browser         # start the server only

The web app is a second front end for the same product as the desktop app: it loads the same
model file (artifacts/selected.joblib) and calls the same clauses.model.analyze(), so a document
gets exactly the same flags in both. It only listens on 127.0.0.1 (this computer). Pasted text is
kept in memory for one request and is never written to disk or sent anywhere; the page loads no
outside fonts, scripts or images.

Uses only the Python standard library on top of the packages in requirements.txt.
"""
import argparse
import json
import re
import sys
import threading
import webbrowser
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:  # allows `python webapp/server.py` as well as `python -m webapp`
    sys.path.insert(0, str(ROOT))

from clauses.export import render_html  # noqa: E402
from clauses.model import DEFAULT_MODEL, analyze, load  # noqa: E402
from clauses.schema import EXPLANATIONS, LABELS, NOTICE  # noqa: E402
from clauses.text import MAX_CHARS  # noqa: E402

STATIC = Path(__file__).resolve().parent / 'static'
EXAMPLE = ROOT / 'examples/fictional_terms.txt'
DEFAULT_PORT = 8641
HOST = '127.0.0.1'
MAX_BODY = 1_000_000  # bytes per request; the analyzer itself refuses more than MAX_CHARS characters
STATIC_NAME = re.compile(r'^[a-z0-9][a-z0-9_-]*\.(css|js|svg)$')
CONTENT_TYPES = {
    '.html': 'text/html; charset=utf-8',
    '.css': 'text/css; charset=utf-8',
    '.js': 'text/javascript; charset=utf-8',
    '.svg': 'image/svg+xml',
}
# Everything the page needs comes from this server; nothing is loaded from the internet.
CSP = ("default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self' data:; "
       "connect-src 'self'; font-src 'self'; object-src 'none'; base-uri 'none'; "
       "form-action 'none'; frame-ancestors 'none'")


class ClauseGuardWeb:
    """The product behind the web page: one loaded model, the same analyze() as the desktop app."""

    def __init__(self, bundle):
        self.bundle = bundle
        self._lock = threading.Lock()

    def meta(self):
        manifest = self.bundle['manifest']
        return {
            'model_id': self.bundle['model_id'],
            'variant': manifest['variant'],
            'threshold_source': manifest['threshold_source'],
            'labels': list(LABELS),
            'explanations': dict(EXPLANATIONS),
            'thresholds': {label: float(t) for label, t in zip(LABELS, manifest['thresholds'])},
            'notice': NOTICE,
            'max_chars': MAX_CHARS,
        }

    def analyze(self, text):
        with self._lock:
            return analyze(text, self.bundle)

    def export_html(self, text):
        # Re-analyse on the server so the exported file always matches the running model.
        return render_html(self.analyze(text))


class Handler(BaseHTTPRequestHandler):
    server_version = 'ClauseGuard'
    sys_version = ''

    # ---- small helpers -------------------------------------------------------------------
    def _allowed_hosts(self):
        port = self.server.server_address[1]
        return {f'127.0.0.1:{port}', f'localhost:{port}'}

    def _headers(self, status, content_type, length, extra=None):
        self.send_response(status)
        self.send_header('Content-Type', content_type)
        self.send_header('Content-Length', str(length))
        self.send_header('Content-Security-Policy', CSP)
        self.send_header('X-Content-Type-Options', 'nosniff')
        self.send_header('Referrer-Policy', 'no-referrer')
        self.send_header('Cache-Control', 'no-store')
        for key, value in (extra or {}).items():
            self.send_header(key, value)
        self.end_headers()

    def _send(self, status, body, content_type, extra=None):
        data = body if isinstance(body, bytes) else body.encode('utf-8')
        self._headers(status, content_type, len(data), extra)
        if self.command != 'HEAD':
            self.wfile.write(data)

    def _json(self, status, payload):
        self._send(status, json.dumps(payload), 'application/json; charset=utf-8')

    def _error(self, status, message):
        self._json(status, {'error': message})

    def _host_ok(self):
        # Refuse requests that reach this port under another name (DNS rebinding protection).
        if self.headers.get('Host', '') not in self._allowed_hosts():
            self._error(HTTPStatus.FORBIDDEN, 'Open the app at http://127.0.0.1 on this computer.')
            return False
        return True

    def _read_json(self):
        """The JSON body of a POST, or None after an error response has been sent."""
        origin = self.headers.get('Origin')
        if origin is not None and origin not in {f'http://{h}' for h in self._allowed_hosts()}:
            self._error(HTTPStatus.FORBIDDEN, 'Requests from other websites are refused.')
            return None
        if self.headers.get('Content-Type', '').split(';')[0].strip().lower() != 'application/json':
            self._error(HTTPStatus.UNSUPPORTED_MEDIA_TYPE, 'Send the text as JSON.')
            return None
        try:
            length = int(self.headers.get('Content-Length', ''))
        except ValueError:
            self._error(HTTPStatus.LENGTH_REQUIRED, 'Content-Length is required.')
            return None
        if length < 0 or length > MAX_BODY:
            self._error(HTTPStatus.REQUEST_ENTITY_TOO_LARGE,
                        f'The text is too long. Limit it to {MAX_CHARS:,} characters.')
            return None
        try:
            payload = json.loads(self.rfile.read(length).decode('utf-8'))
        except (UnicodeDecodeError, json.JSONDecodeError):
            self._error(HTTPStatus.BAD_REQUEST, 'The request was not valid JSON.')
            return None
        if not isinstance(payload, dict) or not isinstance(payload.get('text'), str):
            self._error(HTTPStatus.BAD_REQUEST, 'Send {"text": "..."} with the terms to analyze.')
            return None
        return payload

    # ---- routes --------------------------------------------------------------------------
    def do_HEAD(self):
        self.do_GET()

    def do_GET(self):
        if not self._host_ok():
            return
        path = self.path.split('?', 1)[0]
        app = self.server.app
        if path in ('/', '/index.html'):
            self._static('index.html')
        elif path.startswith('/static/'):
            self._static(path[len('/static/'):])
        elif path == '/api/meta':
            self._json(HTTPStatus.OK, app.meta())
        elif path == '/api/example':
            self._json(HTTPStatus.OK, {'text': EXAMPLE.read_text(encoding='utf-8')})
        else:
            self._error(HTTPStatus.NOT_FOUND, 'Not found.')

    def do_POST(self):
        if not self._host_ok():
            return
        path = self.path.split('?', 1)[0]
        if path not in ('/api/analyze', '/api/export'):
            self._error(HTTPStatus.NOT_FOUND, 'Not found.')
            return
        payload = self._read_json()
        if payload is None:
            return
        app = self.server.app
        try:
            if path == '/api/analyze':
                self._json(HTTPStatus.OK, {'result': app.analyze(payload['text'])})
            else:
                self._send(HTTPStatus.OK, app.export_html(payload['text']), 'text/html; charset=utf-8',
                           {'Content-Disposition': 'attachment; filename="clauseguard-analysis.html"'})
        except ValueError as exc:  # empty text, too long, too many sentences
            self._error(HTTPStatus.BAD_REQUEST, str(exc))
        except Exception:  # never echo the pasted text into logs or responses
            self.log_error('analysis failed (%s)', path)
            self._error(HTTPStatus.INTERNAL_SERVER_ERROR, 'The analysis could not complete. Restart the app and try again.')

    def _static(self, name):
        if name != 'index.html' and not STATIC_NAME.fullmatch(name):
            self._error(HTTPStatus.NOT_FOUND, 'Not found.')
            return
        file = STATIC / name
        if not file.is_file():
            self._error(HTTPStatus.NOT_FOUND, 'Not found.')
            return
        self._send(HTTPStatus.OK, file.read_bytes(), CONTENT_TYPES[file.suffix])

    def log_message(self, fmt, *args):
        # The request line and status only; request bodies (the pasted terms) are never logged.
        if not getattr(self.server, 'quiet', False):
            sys.stderr.write('  ' + (fmt % args) + '\n')


def make_server(bundle=None, port=DEFAULT_PORT, quiet=False):
    """Create (but do not start) the server. port=0 picks a free port (used by the tests)."""
    server = ThreadingHTTPServer((HOST, port), Handler)
    server.daemon_threads = True
    server.app = ClauseGuardWeb(bundle if bundle is not None else load(DEFAULT_MODEL))
    server.quiet = quiet
    return server


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument('--port', type=int, default=DEFAULT_PORT, help=f'port on 127.0.0.1 (default {DEFAULT_PORT})')
    p.add_argument('--no-browser', action='store_true', help='do not open a browser window')
    p.add_argument('--quiet', action='store_true', help='do not print each request')
    a = p.parse_args(argv)
    print('Loading the ClauseGuard model...')
    try:
        bundle = load(DEFAULT_MODEL)
    except (FileNotFoundError, ValueError) as exc:
        return p.exit(2, f'Could not load the model: {exc}\n')
    try:
        server = make_server(bundle, a.port, a.quiet)
    except OSError:
        return p.exit(2, f'Port {a.port} is busy. Try: python -m webapp --port {a.port + 1}\n')
    url = f'http://{HOST}:{server.server_address[1]}/'
    print(f'ClauseGuard is running at {url}  (model {bundle["model_id"][:12]})')
    print('Everything stays on this computer. Press Ctrl+C here to stop.')
    if not a.no_browser:
        threading.Timer(0.6, webbrowser.open, args=(url,)).start()
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print('\nStopped.')
    finally:
        server.server_close()
    return 0


if __name__ == '__main__':
    sys.exit(main())
