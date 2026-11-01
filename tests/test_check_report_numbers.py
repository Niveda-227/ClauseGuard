"""Session 09: every number in a report must come from a source file (scripts/check_report_numbers.py)."""
import json
import shutil
import tempfile
import unittest
from pathlib import Path

from scripts.check_report_numbers import NumberCheckError, check, report_numbers

ROOT = Path(__file__).resolve().parents[1]
FINAL = ['experiments/session08/decision_recheck_final.json', 'experiments/session08/decision_recheck_final.md']


def facts_file(**facts):
    path = Path(tempfile.mkdtemp()) / 'facts.json'
    path.write_text(json.dumps(facts))
    return path


class Session08ReportTests(unittest.TestCase):
    """The Session 08 report quoted the interim re-check (16.67 points, 83.33%). The check must catch that."""

    def test_flags_the_interim_numbers_when_only_the_final_recheck_is_a_source(self):
        results = check(ROOT / 'reports/session08.md', facts_file(number_sources=FINAL), ROOT)
        failed = {shown for status, _, shown, _ in results if status == 'FAIL'}
        self.assertIn('16.67', failed)
        self.assertIn('83.33%', failed)
        passed = {shown for status, _, shown, _ in results if status == 'OK'}
        self.assertIn('0.4217', passed)
        self.assertIn('100.0%', passed)


class NumberCheckTests(unittest.TestCase):
    def setUp(self):
        self.root = Path(tempfile.mkdtemp())
        (self.root / 'src').mkdir()
        (self.root / 'src/result.json').write_text(json.dumps({
            'honest': {'marks_per_100': 31.648, 'share': 0.5065, 'missed': 77}, 'rule': 'at least 40% of missed labels'}))
        (self.root / 'src/old.json').write_text(json.dumps({'superseded_by': 'src/result.json', 'gap': 16.67}))
        (self.root / 'src/old.md').write_text('SUPERSEDED by src/result.json\n\n16.67 points\n')
        (self.root / 'src/report08.md').write_text('It said 16.67 points.\n')
        self.report = self.root / 'report.md'

    def run_check(self, text, **facts):
        self.report.write_text(text)
        facts.setdefault('number_sources', ['src/result.json'])
        return check(self.report, facts_file(**facts), self.root)

    def statuses(self, results):
        return {shown: status for status, _, shown, _ in results}

    def test_numbers_match_at_the_reports_rounding_and_shares_as_percentages(self):
        got = self.statuses(self.run_check('Marks per 100 sentences: 31.65. Share: 50.6%. Rule: 40%.\n'))
        self.assertEqual(got, {'31.65': 'OK', '50.6%': 'OK', '40%': 'OK'})

    def test_a_number_from_nowhere_fails(self):
        got = self.statuses(self.run_check('Marks per 100 sentences: 31.75.\n'))
        self.assertEqual(got, {'31.75': 'FAIL'})

    def test_whole_numbers_code_links_and_addresses_are_not_checked(self):
        text = ('77 missed labels in 2,275 sentences, PR #62, Session 09, U011, 2026-11-03.\n'
                'Run `python 3.12` and see [file](../x/v1.5/a.md) or https://example.com/1.5 and 127.0.0.1\n'
                '```\nvalue 9.99\n```\n<!-- 8.88 -->\n')
        self.assertEqual(report_numbers(text), [])

    def test_superseded_sources_are_refused(self):
        for rel in ('src/old.json', 'src/old.md'):
            with self.assertRaisesRegex(NumberCheckError, '(?i)superseded'):
                self.run_check('Gap 16.67 points.\n', number_sources=[rel])

    def test_missing_sources_and_missing_list_are_refused(self):
        with self.assertRaisesRegex(NumberCheckError, 'does not exist'):
            self.run_check('x 1.5\n', number_sources=['src/nothing.json'])
        with self.assertRaisesRegex(NumberCheckError, 'number_sources'):
            self.run_check('x 1.5\n', number_sources=[])

    def test_a_quoted_wrong_number_must_really_be_in_the_file_it_is_quoted_from(self):
        quote = [{'number': '16.67', 'source': 'src/report08.md', 'why': 'the wrong number being corrected'}]
        got = self.statuses(self.run_check('The old report said 16.67 points.\n', quoted_numbers=quote))
        self.assertEqual(got, {'16.67': 'QUOTE'})
        bad = [{'number': '12.34', 'source': 'src/report08.md', 'why': 'x'}]
        with self.assertRaisesRegex(NumberCheckError, 'does not appear'):
            self.run_check('12.34\n', quoted_numbers=bad)
        with self.assertRaisesRegex(NumberCheckError, 'needs'):
            self.run_check('16.67\n', quoted_numbers=[{'number': '16.67', 'source': 'src/report08.md'}])


if __name__ == '__main__':
    unittest.main()
