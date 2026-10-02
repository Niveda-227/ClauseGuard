import json
import shutil
import tempfile
import unittest
from pathlib import Path

from scripts.demo_check import EXPECTED_DEMO_LABELS, check_identity, check_packages, compare_demo, run

ROOT = Path(__file__).resolve().parents[1]


class DemoCheckTests(unittest.TestCase):
    def test_identity_fails_when_the_app_model_differs_from_the_evaluated_model(self):
        tmp = Path(tempfile.mkdtemp())
        (tmp / 'artifacts').mkdir()
        (tmp / 'experiments/session04/hybrid').mkdir(parents=True)
        shutil.copy(ROOT / 'artifacts/selected.json', tmp / 'artifacts/selected.json')
        shutil.copy(ROOT / 'experiments/session04/hybrid/metrics.json', tmp / 'experiments/session04/hybrid/metrics.json')
        shutil.copy(ROOT / 'artifacts/hybrid.joblib', tmp / 'artifacts/hybrid.joblib')
        (tmp / 'artifacts/selected.joblib').write_bytes(b'a different model')
        self.assertEqual(check_identity(tmp)['status'], 'FAIL')

    def test_identity_passes_on_this_repository(self):
        self.assertEqual(check_identity(ROOT)['status'], 'PASS')

    def test_compare_demo_reports_each_changed_sentence(self):
        rows = [{'labels': list(x)} for x in EXPECTED_DEMO_LABELS]
        self.assertEqual(compare_demo({'sentences': rows})['status'], 'PASS')
        rows[2]['labels'] = ['Unilateral change']
        out = compare_demo({'sentences': rows})
        self.assertEqual(out['status'], 'FAIL')
        self.assertEqual(out['differences'][0]['sentence'], 3)

    def test_wrong_scikit_learn_version_is_a_failure(self):
        req = Path(tempfile.mkdtemp()) / 'requirements.txt'
        req.write_text('scikit-learn==0.0.1\nnumpy==0.0.1\n')
        status = {c['check']: c['status'] for c in check_packages(req)}
        self.assertEqual(status['package scikit-learn'], 'FAIL')
        self.assertEqual(status['package numpy'], 'WARN')

    def test_full_run_is_ready_and_records_no_personal_details(self):
        report, html = run(repeats=1, long_copies=5)
        self.assertEqual(report['model_sha256'][:12], '04713fbf6e23')
        names = {c['check']: c['status'] for c in report['checks']}
        self.assertEqual(names['demo model is the reported model'], 'PASS')
        self.assertEqual(names['demo document flags match the rehearsal'], 'PASS')
        self.assertEqual(report['cost_to_serve']['network_calls'], 0)
        text = json.dumps(report)
        import getpass, platform
        self.assertNotIn(platform.node(), text)
        self.assertNotIn(str(Path.home()), text)
        self.assertIn('Arbitration', html)


if __name__ == '__main__':
    unittest.main()
