"""Session 09: 'Not flagged, but worth a look' (clauses/absence.py), in the web app and the HTML export."""
import http.client
import json
import threading
import unittest

from clauses.absence import NOTE, SEARCH_WORDS, ZERO_FLAGS, search_hits, worth_a_look
from clauses.export import render_html
from clauses.model import DEFAULT_MODEL, analyze, load
from clauses.schema import LABELS
from webapp.server import EXAMPLE, STATIC, make_server

# The list written on Oct 27, 2026 from the category definitions, before any validation run.
# This test pins it: the words must not be edited to improve a validation result.
PRE_REGISTERED = {
    'Limitation of liability': ['liable', 'liability', 'damages', 'responsible', 'losses'],
    'Unilateral termination': ['terminat*', 'suspend*', 'suspension', 'deactivat*', 'close your account',
                               'end your access'],
    'Unilateral change': ['modif*', 'amend*', 'revis*', 'change these', 'changes to', 'update these',
                          'update the terms'],
    'Content removal': ['remov*', 'delet*', 'take down', 'taken down'],
    'Contract by using': ['by using', 'by accessing', 'by signing up', 'by creating', 'you agree',
                          'you accept', 'continued use'],
    'Choice of law': ['governed by', 'laws of', 'law of', 'governing law'],
    'Jurisdiction': ['court', 'courts', 'jurisdiction', 'venue'],
    'Arbitration': ['arbitrat*', 'dispute resolution'],
}


def sentence(i, text, labels=(), possible=()):
    return {'sentence_id': i, 'text': text, 'labels': list(labels), 'possible': list(possible)}


class SearchWordTests(unittest.TestCase):
    def test_the_list_is_exactly_the_pre_registered_one(self):
        self.assertEqual(SEARCH_WORDS, PRE_REGISTERED)
        self.assertEqual(list(SEARCH_WORDS), list(LABELS))

    def test_a_star_matches_any_word_with_that_stem(self):
        cases = {'We may terminate it.': 'terminate', 'Termination is final.': 'termination',
                 'Your account was terminated.': 'terminated', 'We may suspend access.': 'suspend'}
        for text, word in cases.items():
            self.assertEqual(search_hits(text).get('Unilateral termination'), [word], text)

    def test_whole_words_only(self):
        self.assertNotIn('Jurisdiction', search_hits('Thank you for your courtesy.'))
        self.assertNotIn('Unilateral termination', search_hits('This is determinate.'))
        self.assertEqual(search_hits('The courts of Denver.')['Jurisdiction'], ['courts'])
        self.assertEqual(search_hits('A court in Denver.')['Jurisdiction'], ['court'])
        self.assertNotIn('Limitation of liability', search_hits('Your responsibility.'))

    def test_case_insensitive_and_phrases_match_across_spaces(self):
        self.assertEqual(search_hits('We may TAKE   DOWN photos.')['Content removal'], ['take down'])
        self.assertEqual(search_hits('Deleted photos stay for a while.')['Content removal'], ['deleted'])
        self.assertNotIn('Content removal', search_hits('Take the stairs down.'))

    def test_words_found_are_listed_once_in_order(self):
        hits = search_hits('By creating an account, you agree. You agree again, by creating more.')
        self.assertEqual(hits, {'Contract by using': ['by creating', 'you agree']})

    def test_categories_come_in_label_order_and_empty_text_has_none(self):
        hits = search_hits('Disputes go to arbitration; these terms are governed by the laws of Vermont; we are not liable.')
        self.assertEqual(list(hits), ['Limitation of liability', 'Choice of law', 'Arbitration'])
        self.assertEqual(hits['Choice of law'], ['governed by', 'laws of'])
        self.assertEqual(search_hits('Nothing here.'), {})
        with self.assertRaises(TypeError):
            search_hits(None)


class WorthALookTests(unittest.TestCase):
    def analysis(self):
        return {'sentences': [
            sentence(0, 'We may remove your posts.', labels=['Content removal']),
            sentence(1, 'Deleted files stay in the trash.'),
            sentence(2, 'We are not responsible for losses.', possible=['Limitation of liability']),
            sentence(3, 'You keep your rights.'),
        ]}

    def test_flagged_sentences_are_counted_not_listed(self):
        by = {c['category']: c for c in worth_a_look(self.analysis())['categories']}
        removal = by['Content removal']
        self.assertEqual(removal['flagged'], 1)
        self.assertEqual(removal['flagged_sentence_ids'], [0])
        self.assertEqual(removal['worth_a_look'], [{'sentence_id': 1, 'words': ['deleted']}])

    def test_possible_sentences_are_reported_and_can_also_be_worth_a_look(self):
        by = {c['category']: c for c in worth_a_look(self.analysis())['categories']}
        liability = by['Limitation of liability']
        self.assertEqual(liability['flagged'], 0)
        self.assertEqual(liability['possible_sentence_ids'], [2])
        self.assertEqual(liability['worth_a_look'], [{'sentence_id': 2, 'words': ['responsible', 'losses']}])

    def test_every_category_is_present_with_its_search_words(self):
        panel = worth_a_look(self.analysis())
        self.assertEqual([c['category'] for c in panel['categories']], list(LABELS))
        for c in panel['categories']:
            self.assertEqual(c['search_words'], SEARCH_WORDS[c['category']])
        self.assertEqual(panel['note'], NOTE)
        self.assertIn('not model predictions', panel['note'])
        self.assertEqual(panel['zero_flags_note'], ZERO_FLAGS)

    def test_the_panel_changes_nothing_in_the_analysis(self):
        bundle = load(DEFAULT_MODEL)
        text = EXAMPLE.read_text(encoding='utf-8')
        before = analyze(text, bundle)
        snapshot = json.dumps(before, sort_keys=True)
        worth_a_look(before)
        self.assertEqual(json.dumps(before, sort_keys=True), snapshot)
        self.assertEqual(json.dumps(analyze(text, bundle), sort_keys=True), snapshot)


class ExportPanelTests(unittest.TestCase):
    def test_export_contains_the_panel_and_escapes_text(self):
        bundle = load(DEFAULT_MODEL)
        result = analyze('Deleted <b>photos</b> stay in the trash folder for thirty days.\nThe weather is nice.', bundle)
        removal = [c for c in worth_a_look(result)['categories'] if c['category'] == 'Content removal'][0]
        self.assertEqual(removal['flagged'], 0)  # the model does not flag this sentence (score 0.04)
        page = render_html(result)
        self.assertIn('Check it yourself', page)
        self.assertIn('Word matches, not model predictions.', page)
        self.assertIn(ZERO_FLAGS, page)
        self.assertIn('Not flagged, but worth a look: sentence 1 (&#x27;deleted&#x27;)', page)
        self.assertIn('&lt;b&gt;photos&lt;/b&gt;', page)
        self.assertNotIn('<b>photos</b>', page)


class WebPanelTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.bundle = load(DEFAULT_MODEL)
        cls.server = make_server(cls.bundle, port=0, quiet=True)
        cls.port = cls.server.server_address[1]
        threading.Thread(target=cls.server.serve_forever, daemon=True).start()

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()

    def test_analyze_returns_the_panel_next_to_the_unchanged_result(self):
        text = EXAMPLE.read_text(encoding='utf-8')
        conn = http.client.HTTPConnection('127.0.0.1', self.port, timeout=30)
        conn.request('POST', '/api/analyze', body=json.dumps({'text': text}),
                     headers={'Host': f'127.0.0.1:{self.port}', 'Content-Type': 'application/json'})
        data = json.loads(conn.getresponse().read())
        conn.close()
        direct = json.loads(json.dumps(analyze(text, self.bundle)))
        self.assertEqual(data['result'], direct)
        self.assertEqual(data['worth_a_look'], json.loads(json.dumps(worth_a_look(direct))))

    def test_page_has_the_panel_and_its_wording(self):
        page = (STATIC / 'index.html').read_text(encoding='utf-8')
        script = (STATIC / 'app.js').read_text(encoding='utf-8')
        self.assertIn('Check it yourself', page)
        self.assertIn('Word matches, not model predictions', page)
        self.assertIn('Not flagged, but worth a look:', script)
        self.assertIn('state.worth.zero_flags_note', script)


if __name__ == '__main__':
    unittest.main()
