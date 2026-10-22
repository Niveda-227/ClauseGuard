"""Tests for the local web app (webapp/server.py). They start the real server on a free port."""
import hashlib
import http.client
import json
import re
import tempfile
import threading
import unittest
from pathlib import Path

from clauses.model import DEFAULT_MODEL, analyze, load
from clauses.schema import LABELS
from clauses.session_v2 import run_trial_v2
from webapp.server import EXAMPLE, MAX_BODY, STATIC, make_server

ROOT = Path(__file__).resolve().parents[1]


class WebAppTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.bundle = load(DEFAULT_MODEL)
        cls.server = make_server(cls.bundle, port=0, quiet=True)
        cls.port = cls.server.server_address[1]
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()

    def request(self, method, path, body=None, headers=None):
        conn = http.client.HTTPConnection('127.0.0.1', self.port, timeout=30)
        sent = {'Host': f'127.0.0.1:{self.port}'}
        if body is not None and not isinstance(body, bytes):
            body = json.dumps(body).encode('utf-8')
            sent['Content-Type'] = 'application/json'
        sent.update(headers or {})
        conn.request(method, path, body=body, headers=sent)
        response = conn.getresponse()
        data = response.read()
        conn.close()
        return response, data

    # ---- the product: same model, same results as the desktop app ---------------------
    def test_listens_on_this_computer_only(self):
        self.assertEqual(self.server.server_address[0], '127.0.0.1')

    def test_meta_reports_the_running_model(self):
        response, data = self.request('GET', '/api/meta')
        self.assertEqual(response.status, 200)
        meta = json.loads(data)
        on_disk = hashlib.sha256((ROOT / 'artifacts/selected.joblib').read_bytes()).hexdigest()
        self.assertEqual(meta['model_id'], on_disk)
        self.assertEqual(meta['labels'], list(LABELS))
        manifest = json.loads((ROOT / 'artifacts/selected.json').read_text())
        self.assertEqual([meta['thresholds'][l] for l in LABELS], [float(t) for t in manifest['thresholds']])

    def test_analysis_is_identical_to_the_desktop_app(self):
        text = EXAMPLE.read_text(encoding='utf-8')
        response, data = self.request('POST', '/api/analyze', {'text': text})
        self.assertEqual(response.status, 200)
        self.assertEqual(json.loads(data)['result'], json.loads(json.dumps(analyze(text, self.bundle))))

    def test_example_endpoint_returns_the_fictional_example(self):
        response, data = self.request('GET', '/api/example')
        self.assertEqual(json.loads(data)['text'], EXAMPLE.read_text(encoding='utf-8'))

    def test_export_is_escaped_html_of_the_same_analysis(self):
        response, data = self.request('POST', '/api/export', {'text': 'We may <b>change</b> these terms at any time.'})
        self.assertEqual(response.status, 200)
        self.assertIn('attachment', response.getheader('Content-Disposition'))
        html = data.decode('utf-8')
        self.assertIn('&lt;b&gt;change&lt;/b&gt;', html)
        self.assertNotIn('<b>change</b>', html)

    # ---- refusing bad input ---------------------------------------------------------
    def test_empty_text_is_a_clear_400(self):
        response, data = self.request('POST', '/api/analyze', {'text': '   '})
        self.assertEqual(response.status, 400)
        self.assertIn('Paste some text', json.loads(data)['error'])

    def test_non_json_is_refused(self):
        response, _ = self.request('POST', '/api/analyze', b'text=hello',
                                   {'Content-Type': 'application/x-www-form-urlencoded'})
        self.assertEqual(response.status, 415)

    def test_oversized_body_is_refused(self):
        response, _ = self.request('POST', '/api/analyze', b'{"text": ""}',
                                   {'Content-Type': 'application/json', 'Content-Length': str(MAX_BODY + 1)})
        self.assertEqual(response.status, 413)

    def test_other_host_names_are_refused(self):
        response, _ = self.request('GET', '/api/meta', headers={'Host': 'attacker.example:80'})
        self.assertEqual(response.status, 403)

    def test_cross_site_posts_are_refused(self):
        response, _ = self.request('POST', '/api/analyze', {'text': 'We may change these terms.'},
                                   {'Origin': 'https://attacker.example'})
        self.assertEqual(response.status, 403)

    def test_only_the_app_files_are_served(self):
        for path in ('/static/../server.py', '/static/%2e%2e/server.py', '/static/server.py',
                     '/static/.hidden.js', '/etc/passwd', '/static/'):
            response, _ = self.request('GET', path)
            self.assertEqual(response.status, 404, path)

    # ---- the page itself -------------------------------------------------------------
    def test_page_and_assets_load_with_security_headers(self):
        for path in ('/', '/static/app.css', '/static/app.js', '/static/mark.svg'):
            response, _ = self.request('GET', path)
            self.assertEqual(response.status, 200, path)
            self.assertIn("default-src 'self'", response.getheader('Content-Security-Policy'))
            self.assertEqual(response.getheader('X-Content-Type-Options'), 'nosniff')

    def test_page_loads_nothing_from_the_internet(self):
        # Works offline on demo day, and nothing about the user leaks to other sites.
        for file in STATIC.iterdir():
            text = file.read_text(encoding='utf-8')
            urls = [u for u in re.findall(r'https?://[^\s"\')]+', text) if not u.startswith('http://www.w3.org/')]
            self.assertEqual(urls, [], file.name)

    def test_page_shows_the_safety_notice_words(self):
        script = (STATIC / 'app.js').read_text(encoding='utf-8')
        self.assertIn('No category flagged. This is not a finding of safety.', script)


class WebInterfaceRecordingTests(unittest.TestCase):
    """The study recorder accepts the web app as a ClauseGuard interface (protocol unchanged)."""

    def run_trial(self, condition, interface):
        out = Path(tempfile.mkdtemp()) / 'tasks.csv'
        answers = iter(['yes', 'yes', '', '', 'answer', 'yes', 'note'])
        times = iter([10.0, 25.0])
        return out, run_trial_v2(out, 'U900', 'E1', condition, interface, 'OBS01', 'a' * 64,
                                 {'E1': {'document': 'examples/study/document_E.txt', 'prompt': 'p'}},
                                 ask=lambda _='': next(answers), clock=lambda: next(times), say=lambda *a: None)

    def test_web_interface_is_recorded(self):
        out, row = self.run_trial('clauseguard', 'web')
        record = json.loads(next(out.parent.glob('*.json')).read_text())
        self.assertEqual(record['interface'], 'web')
        self.assertEqual(row['seconds'], 15.0)

    def test_manual_trials_cannot_use_the_web_app(self):
        with self.assertRaises(ValueError):
            self.run_trial('manual', 'web')


if __name__ == '__main__':
    unittest.main()
