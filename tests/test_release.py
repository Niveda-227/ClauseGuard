"""Session 12: the release freeze (scripts/make_release.py, scripts/check_release.py)."""
import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from scripts import check_release, make_release
from scripts.release_files import fingerprint, product_files

ROOT = Path(__file__).resolve().parents[1]


def fake_product(root):
    root = Path(root)
    model = b'model bytes\r\n'
    (root / 'clauses').mkdir()
    (root / 'webapp/static').mkdir(parents=True)
    (root / 'artifacts').mkdir()
    (root / 'app.py').write_text('print(1)\n')
    (root / 'requirements.txt').write_text('numpy==2.3.5\n')
    (root / 'clauses/model.py').write_text('x = 1\n')
    (root / 'webapp/static/app.js').write_text('let a;\n')
    (root / 'artifacts/selected.joblib').write_bytes(model)
    (root / 'artifacts/selected.json').write_text(json.dumps({
        'artifact_sha256': hashlib.sha256(model).hexdigest(), 'variant': 'hybrid', 'labels': ['A', 'B'],
        'thresholds': [0.75, 0.7000000000000002], 'dataset_sha256': 'd' * 64}))
    return root


def freeze(root):
    release, summary = make_release.build(root)
    (Path(root) / 'RELEASE.json').write_text(json.dumps(release))
    return release, summary


class ReleaseTests(unittest.TestCase):
    def test_a_fresh_release_checks_out(self):
        with tempfile.TemporaryDirectory() as d:
            root = fake_product(d)
            release, summary = freeze(root)
            self.assertEqual(release['version'], '1.0.0')
            self.assertEqual(release['cut_offs'], {'A': 0.75, 'B': 0.7})
            self.assertEqual(summary['product_files'], 6)
            (root / 'webapp/static/.DS_Store').write_bytes(b'finder')  # hidden files are not product files
            ok, lines = check_release.check(root)
            self.assertTrue(ok)
            self.assertEqual(lines[-1], 'THIS IS RELEASE 1.0.0')

    def test_a_changed_or_new_product_file_is_not_the_release(self):
        with tempfile.TemporaryDirectory() as d:
            root = fake_product(d)
            freeze(root)
            (root / 'clauses/model.py').write_text('x = 2\n')
            (root / 'clauses/new.py').write_text('y = 1\n')
            ok, lines = check_release.check(root)
            self.assertFalse(ok)
            self.assertIn('clauses/model.py', lines[1])
            self.assertIn('clauses/new.py', lines[2])
            self.assertTrue(lines[-1].startswith('NOT RELEASE 1.0.0'))

    def test_the_freeze_refuses_after_the_test_split_was_read(self):
        with tempfile.TemporaryDirectory() as d:
            root = fake_product(d)
            (root / 'experiments').mkdir()
            (root / 'experiments/test_exposure.jsonl').write_text('{}\n')
            with self.assertRaises(ValueError):
                make_release.build(root)

    def test_windows_line_endings_do_not_change_a_text_fingerprint(self):
        with tempfile.TemporaryDirectory() as d:
            a, b = Path(d) / 'a.py', Path(d) / 'b.py'
            a.write_bytes(b'x = 1\n')
            b.write_bytes(b'x = 1\r\n')
            self.assertEqual(fingerprint(a), fingerprint(b))

    def test_this_folder_is_the_release_once_it_is_frozen(self):
        self.assertIn('artifacts/selected.joblib', product_files(ROOT))
        if (ROOT / 'RELEASE.json').exists():
            ok, lines = check_release.check(ROOT)
            self.assertTrue(ok, '\n'.join(lines))


if __name__ == '__main__':
    unittest.main()
