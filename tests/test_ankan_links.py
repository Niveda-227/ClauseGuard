import importlib.util
import json
import tempfile
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location("member_module", ROOT/"scripts/check_report_links.py")
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)

class ReportLinkTests(unittest.TestCase):
    def test_existing_missing_and_external_links(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d);(p/'reports').mkdir();(p/'evidence').mkdir();(p/'evidence/raw.csv').write_text('header')
            r=p/'reports/session04.md';r.write_text('[ok](../evidence/raw.csv) [missing](../evidence/no.csv) [remote](https://github.com/example/repo/pull/1)')
            result=m.check_report(r,p)
            self.assertEqual(len(result['issues']),1);self.assertFalse(result['external_links'][0]['checked_online'])
    def test_escape_and_unresolved_fields(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d);r=p/'report.md';r.write_text('  value: null\n[escape](../outside.txt)')
            result=m.check_report(r,p)
            self.assertTrue(result['unresolved_submission_fields']);self.assertIn('escapes',result['issues'][0])
    def test_code_fences_do_not_create_links(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d);r=p/'report.md';r.write_text('```markdown\n[example](missing.txt)\n```\n')
            self.assertTrue(m.check_report(r,p)['path_checks_passed'])
