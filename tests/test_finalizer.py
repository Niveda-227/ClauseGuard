"""Report checks use fabricated fixtures ONLY inside temporary test directories."""
import contextlib
import importlib.util
import io
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from clauses.study import record

PROJECT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('finalize_session04', PROJECT/'scripts/finalize_session04.py')
finalizer = importlib.util.module_from_spec(spec)
spec.loader.exec_module(finalizer)


class FinalizerTests(unittest.TestCase):
    def test_missing_facts_does_not_change_report(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);(root/'reports').mkdir()
            report=root/'reports/session04.md';report.write_text('unchanged')
            facts=root/'facts.json';facts.write_text('{}')
            with patch.object(finalizer,'ROOT',root), patch('sys.argv',['finalizer','--facts',str(facts)]), contextlib.redirect_stderr(io.StringIO()):
                with self.assertRaises(SystemExit) as err:finalizer.main()
            self.assertEqual(err.exception.code,2)
            self.assertEqual(report.read_text(),'unchanged')

    def test_actual_records_determine_metric_and_all_members_are_filled(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);(root/'reports').mkdir()
            report=root/'reports/session04.md'
            report.write_text((PROJECT/'reports/session04.md').read_text())
            # These rows are temporary test fixtures, never delivery evidence.
            evidence=root/'evidence/session04/tasks.csv'
            record(evidence,'TEST01','A1','clauseguard',True,30,'a'*64,'sep22_v1')
            record(evidence,'TEST02','A1','clauseguard',True,181,'a'*64,'sep22_v1')
            repo='https://github.com/example/test-fixture'
            facts={'repo_url':repo, 'branch_protection_verified':True,
                   'outside_user_evidence_reviewed':True,'contributions_verified':True,
                   'shipped_evidence_urls':[repo+'/pull/1',repo+'/commit/abcdef0'],
                   'user_observation':'TEST FIXTURE ONLY: two temporary trials.',
                   'change_from_user':'TEST FIXTURE ONLY: queued review.',
                   'user_change_evidence_urls':[repo+'/issues/2'],
                   'current_blockers':'TEST FIXTURE ONLY: limited sample.',
                   'members':{name:{'github':'test-'+name.lower(),
                        'completed_work':'TEST FIXTURE ONLY: reviewed code and evaluated behavior.',
                        'evidence_urls':[repo+'/pull/1']} for name,_ in finalizer.PEOPLE}}
            path=root/'facts.json';path.write_text(json.dumps(facts))
            with patch.object(finalizer,'ROOT',root),patch.object(finalizer,'load',return_value={'model_id':'a'*64}),patch('sys.argv',['finalizer','--facts',str(path)]),contextlib.redirect_stdout(io.StringIO()):
                finalizer.main()
            result=report.read_text()
            self.assertIn('  value: 50.00',result)
            self.assertIn('1/2 tasks correct',result)
            self.assertNotIn('github: TODO',result)
            self.assertNotIn('DRAFT',result)
            for name,_ in finalizer.PEOPLE:self.assertIn('github: test-'+name.lower(),result)
            summary=json.loads((evidence.parent/'summary.json').read_text())
            self.assertEqual(summary['groups'][0]['success_percent'],50)
