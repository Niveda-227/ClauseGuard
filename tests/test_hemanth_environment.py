import importlib.util
import json
import tempfile
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location("member_module", ROOT/"scripts/check_environment.py")
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)

class EnvironmentTests(unittest.TestCase):
    def test_missing_artifacts_fail(self):
        with tempfile.TemporaryDirectory() as d:self.assertFalse(m.check_model(d)['ok'])
    def test_valid_hash_and_tampering(self):
        import hashlib
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'artifacts';p.mkdir();model=p/'selected.joblib';model.write_bytes(b'test fixture, not executable')
            (p/'selected.json').write_text(json.dumps({'artifact_sha256':hashlib.sha256(model.read_bytes()).hexdigest()}))
            self.assertTrue(m.check_model(d)['ok'])
            model.write_bytes(b'changed')
            self.assertFalse(m.check_model(d)['ok'])
    def test_invalid_manifest_is_diagnostic(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'artifacts';p.mkdir();(p/'selected.joblib').write_bytes(b'test');(p/'selected.json').write_text('{}')
            self.assertFalse(m.check_model(d)['ok'])
