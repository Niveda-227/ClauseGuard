"""Session 10: the fresh real Terms of Service, their sources, the labelling guide and the pre-set rule."""
import json
import tarfile
import unittest
from pathlib import Path

from clauses.data import DEFAULT_PATH
from scripts.fresh_docs import check, load_manifest, md_to_text

ROOT = Path(__file__).resolve().parents[1]
OPEN_LICENCES = {'CC0 1.0', 'CC BY 4.0', 'CC BY-SA 4.0'}


class FreshDocumentTests(unittest.TestCase):
    def test_every_document_matches_its_manifest_entry(self):
        self.assertEqual(check(ROOT), [('basecamp', ''), ('cloudup', ''), ('crowdsignal', '')])

    def test_sources_are_openly_licensed_and_pinned(self):
        for doc in load_manifest(ROOT)['documents']:
            self.assertIn(doc['license'], OPEN_LICENCES, doc['doc_id'])
            self.assertRegex(doc['source_commit'], r'^[0-9a-f]{40}$')
            self.assertIn(doc['source_commit'], doc['source_url'])
            self.assertIn(doc['file'].split('/')[-1], (ROOT / 'examples/fresh/SOURCES.md').read_text(encoding='utf-8'))

    def test_sentence_counts(self):
        counts = {d['doc_id']: d['sentences'] for d in load_manifest(ROOT)['documents']}
        self.assertEqual(counts, {'basecamp': 156, 'cloudup': 77, 'crowdsignal': 143})

    @unittest.skipUnless(DEFAULT_PATH.exists(), 'dataset not downloaded: run python -m clauses.cli data')
    def test_no_fresh_company_is_in_unfair_tos(self):
        with tarfile.open(DEFAULT_PATH, 'r:gz') as archive:
            rows = [json.loads(l) for l in archive.extractfile('unfair_tos.jsonl') if l.strip()]
        companies = {r['company'].lower() for r in rows}
        for name in ('37signals', 'basecamp', 'automattic', 'cloudup', 'crowdsignal', 'wordpress'):
            self.assertNotIn(name, companies)

    def test_markdown_conversion_keeps_words_and_drops_markup(self):
        md = '---\ntitle: x\n---\n# Terms\n\n1. We **may** close [your account](https://x.y) at any time.\n- Use \\[@\\] mail.\n'
        self.assertEqual(md_to_text(md), 'Terms\nWe may close your account at any time.\nUse [@] mail.\n')


class RuleTests(unittest.TestCase):
    def test_the_pre_set_rule_is_pinned(self):
        rule = json.loads((ROOT / 'docs/decisions/fresh_rule.json').read_text(encoding='utf-8'))
        r = rule['rules']
        self.assertEqual(rule['written'], '2026-11-04')
        self.assertEqual(r['domain_shift']['max_drop'], 0.15)
        self.assertEqual((r['cue_margin']['min_coverage'], r['cue_margin']['max_per_100']), (0.20, 5.0))
        self.assertEqual((r['zero_flag_marks']['min_coverage'], r['zero_flag_marks']['max_per_100']), (0.40, 20.0))
        self.assertIn('strict', rule['gold_for_rules'])

    def test_guide_lists_the_eight_categories_in_order(self):
        from clauses.schema import LABELS
        guide = (ROOT / 'docs/LABELLING_GUIDE.md').read_text(encoding='utf-8')
        positions = [guide.index(f'| {i} | {label} |') for i, label in enumerate(LABELS, start=1)]
        self.assertEqual(positions, sorted(positions))


class ZeroOnlyToggleTests(unittest.TestCase):
    def test_the_toggle_is_on_the_page_and_off_by_default(self):
        page = (ROOT / 'webapp/static/index.html').read_text(encoding='utf-8')
        script = (ROOT / 'webapp/static/app.js').read_text(encoding='utf-8')
        self.assertIn('<input type="checkbox" id="check-zero-only">', page)
        self.assertNotIn('id="check-zero-only" checked', page)
        self.assertIn('Only for categories with no flag', page)
        self.assertIn('hiddenByToggle', script)


if __name__ == '__main__':
    unittest.main()
