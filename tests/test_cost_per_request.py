"""Session 09: cost per request of the web app (scripts/cost_per_request.py)."""
import json
import platform
import unittest
from pathlib import Path

from scripts.cost_per_request import check_price, hosted, p95, run, to_markdown

ROOT = Path(__file__).resolve().parents[1]
PRICE = {'per_hour_usd': 0.01, 'plan': 'Example plan', 'url': 'https://example.com/pricing', 'looked_up_on': '2026-10-27'}


class CostPerRequestTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = run(requests=5, long_copies=3)

    def test_measures_both_documents_on_the_real_request_path(self):
        docs = self.report['documents']
        self.assertEqual(set(docs), {'study', 'long'})
        self.assertEqual(docs['study']['sentences'], 16)
        self.assertEqual(docs['long']['sentences'], 33)  # the 11-sentence example, 3 times
        for d in docs.values():
            self.assertEqual(d['requests'], 5)
            self.assertGreater(d['median_seconds'], 0)
            self.assertGreaterEqual(d['p95_seconds'], d['median_seconds'])
            self.assertGreaterEqual(d['cpu_seconds_per_request'], 0)
        self.assertGreater(self.report['peak_memory_mb'], 0)

    def test_local_cost_is_zero_and_no_price_means_no_hosted_estimate(self):
        self.assertEqual(self.report['network_calls_outside_this_computer'], 0)
        self.assertEqual(self.report['api_cost_per_request_usd'], 0.0)
        self.assertIsNone(self.report['hosted_estimate'])
        self.assertIn('not made', to_markdown(self.report))

    def test_runs_the_model_the_app_ships(self):
        shipped = json.loads((ROOT / 'artifacts/selected.json').read_text())['artifact_sha256']
        self.assertEqual(self.report['model_sha256'], shipped)

    def test_records_no_personal_details(self):
        text = json.dumps(self.report)
        self.assertNotIn(platform.node(), text)
        self.assertNotIn(str(Path.home()), text)


class PriceTests(unittest.TestCase):
    def test_hosted_estimate_is_price_times_seconds(self):
        docs = {'study': {'median_seconds': 0.036}, 'long': {'median_seconds': 0.36}}
        h = hosted(PRICE, docs, peak_mb=200.0, plan_memory_mb=1024)
        # 0.01 dollars per hour x 0.036 s / 3600 s = 1e-7 dollars per request = 0.1 dollars per million
        self.assertEqual(h['study_cost_per_million_requests_usd'], 0.1)
        self.assertEqual(h['long_cost_per_million_requests_usd'], 1.0)
        self.assertEqual(h['study_requests_per_hour_one_at_a_time'], 100000)
        self.assertTrue(h['peak_memory_fits_in_plan'])
        self.assertEqual(h['price_source_url'], PRICE['url'])
        self.assertEqual(h['price_looked_up_on'], PRICE['looked_up_on'])

    def test_a_price_needs_its_source_and_date(self):
        for missing in ('plan', 'url', 'looked_up_on'):
            with self.assertRaises(ValueError):
                check_price({**PRICE, missing: None})
        with self.assertRaises(ValueError):
            check_price({**PRICE, 'url': 'http://example.com'})
        with self.assertRaises(ValueError):
            check_price({**PRICE, 'looked_up_on': 'yesterday'})
        with self.assertRaises(ValueError):
            check_price({**PRICE, 'per_hour_usd': 0})
        self.assertIsNone(check_price(None))

    def test_p95_is_nearest_rank(self):
        self.assertEqual(p95(list(range(1, 21))), 19)
        self.assertEqual(p95([5.0]), 5.0)
        with self.assertRaises(ValueError):
            p95([])


if __name__ == '__main__':
    unittest.main()
