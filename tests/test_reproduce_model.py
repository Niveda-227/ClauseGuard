"""Session 11: rebuilding the product model from a clean clone (scripts/reproduce_model.py)."""
import json
import unittest
from pathlib import Path

import numpy as np

from clauses.data import DEFAULT_PATH
from scripts.reproduce_model import OUT, flags_fingerprint, main, run, to_markdown

ROOT = Path(__file__).resolve().parents[1]


class FingerprintTests(unittest.TestCase):
    def test_the_flags_fingerprint_changes_only_when_a_flag_changes(self):
        cuts = [0.5] * 8
        a = np.full((3, 8), 0.1)
        a[0, 2] = 0.9
        b = a.copy()
        b[1, 3] = 0.4   # still below the cut-off: same flags
        c = a.copy()
        c[1, 3] = 0.6   # now flagged
        self.assertEqual(flags_fingerprint(a, cuts), flags_fingerprint(b, cuts))
        self.assertNotEqual(flags_fingerprint(a, cuts), flags_fingerprint(c, cuts))
        self.assertRegex(flags_fingerprint(a, cuts), r'^[0-9a-f]{64}$')

    def test_save_is_refused_outside_private(self):
        with self.assertRaises(SystemExit):
            main(['--save', 'artifacts/reproduced.joblib'])

    def test_markdown_says_no_when_a_check_fails(self):
        r = {'reproduced': False, 'checks': {'same_validation_flags': False},
             'configuration': {'features': 'f', 'classifier': 'c', 'seed': 641},
             'fingerprints': {'dataset_sha256': 'd', 'product_artifact_sha256': 'p', 'training_sentences': 1,
                              'training_companies': 1, 'validation_sentences': 1, 'cut_offs': {'A': 0.5},
                              'validation_flags_sha256': 'x'}, 'note': 'n'}
        md = to_markdown(r)
        self.assertIn('**Reproduced: NO.**', md)
        self.assertIn('| Same flags on every validation sentence | NO |', md)


@unittest.skipUnless(DEFAULT_PATH.exists(), 'dataset not downloaded (python -m clauses.cli data)')
class ReproduceTests(unittest.TestCase):
    def test_the_product_model_is_reproduced_and_matches_the_committed_record(self):
        r, bundle = run(ROOT)
        self.assertTrue(r['reproduced'], r['checks'])
        self.assertEqual(r['fingerprints']['training_companies'], 30)
        self.assertEqual(bundle['manifest']['variant'], 'hybrid')
        committed = ROOT / f'{OUT}.json'
        if committed.exists():
            self.assertEqual(json.loads(committed.read_text(encoding='utf-8')), json.loads(json.dumps(r)))


if __name__ == '__main__':
    unittest.main()
