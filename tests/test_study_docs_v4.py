"""Session 09 study materials: task bank v4, documents G and H (absence tasks)."""
import csv
import json
import tempfile
import unittest
from pathlib import Path

from clauses.absence import worth_a_look
from clauses.model import analyze, load
from clauses.session_v2 import load_tasks
from scripts.check_evidence import FIELDS
from scripts.check_evidence import check as check_evidence
from scripts.check_study_docs import check

ROOT = Path(__file__).resolve().parents[1]
BANK = ROOT / 'examples/study/tasks_v4.json'
# Only sentence openings are here (needed to find the sentences); the answers stay in private/.
KEY = {
    'G1': {'target_category': 'Content removal', 'answer_sentence_starts_with': 'We may take down photos or albums'},
    'H1': {'target_category': 'Jurisdiction', 'answer_absent': True,
           'distractor_starts_with': 'These terms are governed by the laws of the State of Minnesota'},
}


def flags(text, bundle):
    """{sentence number counted from 1: labels} for the flagged sentences."""
    return {s['sentence_id'] + 1: s['labels'] for s in analyze(text, bundle)['sentences'] if s['labels']}


class StudyDocsV4Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.bundle = load()
        tmp = Path(tempfile.mkdtemp())
        key = tmp / 'key.json'
        key.write_text(json.dumps(KEY))
        cls.summary = check(BANK, key, cls.bundle)
        cls.by_task = {t['task_id']: t for t in cls.summary['tasks']}
        cls.g = (ROOT / 'examples/study/document_G.txt').read_text(encoding='utf-8')
        cls.h = (ROOT / 'examples/study/document_H.txt').read_text(encoding='utf-8')

    def test_bank_has_g1_and_h1_only(self):
        self.assertEqual(sorted(load_tasks(BANK)), ['G1', 'H1'])

    def test_documents_are_fictional_and_have_sixteen_sentences(self):
        for text in (self.g, self.h):
            self.assertIn('fictional', text)
            self.assertEqual(len(text.splitlines()), 16)
            self.assertEqual(len(analyze(text, self.bundle)['sentences']), 16)

    def test_the_model_flags_what_the_study_design_expects(self):
        self.assertEqual(flags(self.g, self.bundle), {11: ['Limitation of liability'], 12: ['Choice of law'], 13: ['Arbitration']})
        self.assertEqual(flags(self.h, self.bundle), {9: ['Unilateral change'], 10: ['Unilateral termination'], 12: ['Choice of law']})
        for text in (self.g, self.h):
            for s in analyze(text, self.bundle)['sentences']:
                self.assertEqual((s['uncertain'], s['possible']), ([], []))

    def test_g1_answer_is_missed_by_the_model_but_listed_as_worth_a_look(self):
        g1 = self.by_task['G1']
        self.assertEqual(g1['answer'], 'sentence')
        self.assertFalse(g1['answer_sentence_flagged_with_target'])
        self.assertEqual(g1['answer_sentence_cue'], 'none')
        self.assertTrue(g1['answer_sentence_in_worth_a_look'])
        self.assertEqual(g1['worth_a_look_sentences_for_target'], 2)
        removal = {c['category']: c for c in worth_a_look(analyze(self.g, self.bundle))['categories']}['Content removal']
        self.assertEqual(removal['worth_a_look'], [{'sentence_id': 7, 'words': ['take down']},
                                                   {'sentence_id': 14, 'words': ['deleted']}])

    def test_h1_has_no_answer_sentence_and_nothing_points_to_one(self):
        h1 = self.by_task['H1']
        self.assertEqual(h1['answer'], 'absent')
        self.assertEqual(h1['sentences_flagged_with_target'], 0)
        self.assertEqual(h1['worth_a_look_sentences_for_target'], 0)
        self.assertEqual(h1['sentences_with_target_search_words'], 0)
        self.assertEqual(h1['distractor_flagged_categories'], ['Choice of law'])
        panel = {c['category']: c for c in worth_a_look(analyze(self.h, self.bundle))['categories']}
        self.assertEqual(panel['Contract by using']['worth_a_look'], [{'sentence_id': 3, 'words': ['by creating', 'you agree']}])
        self.assertEqual(panel['Limitation of liability']['worth_a_look'], [{'sentence_id': 10, 'words': ['responsible']}])

    def test_summary_contains_no_answer_text_or_positions(self):
        text = json.dumps(self.summary)
        for word in ('take down', 'notify', 'Minnesota', 'governed', 'sentence_id'):
            self.assertNotIn(word, text)

    def test_an_absent_answer_cannot_also_name_a_sentence(self):
        tmp = Path(tempfile.mkdtemp()) / 'key.json'
        tmp.write_text(json.dumps({**KEY, 'H1': {**KEY['H1'], 'answer_sentence_starts_with': 'These terms'}}))
        with self.assertRaisesRegex(ValueError, 'absent'):
            check(BANK, tmp, self.bundle)


class Session09EvidenceTests(unittest.TestCase):
    def test_explanation_check_is_not_asked_for_after_session_08(self):
        root = Path(tempfile.mkdtemp())
        (root / 'artifacts').mkdir()
        (root / 'artifacts/selected.joblib').write_bytes(b'model')
        import hashlib
        model = hashlib.sha256(b'model').hexdigest()
        folder = root / 'evidence/session09'
        folder.mkdir(parents=True)
        rows = [dict(zip(FIELDS, ['2026-10-31T15:00:00+00:00', 'U011', 'G1', 'clauseguard', '1', '50.0', '180', model, 'sep29_v2'])),
                dict(zip(FIELDS, ['2026-10-31T15:05:00+00:00', 'U011', 'H1', 'manual', '1', '70.0', '180', 'manual', 'sep29_v2']))]
        with (folder / 'tasks.csv').open('w', newline='') as f:
            w = csv.DictWriter(f, fieldnames=FIELDS)
            w.writeheader()
            w.writerows(rows)
        for r, interface in zip(rows, ('web', 'text_editor')):
            (folder / f"{r['participant_id']}_{r['task_id']}_{r['condition']}_sep29_v2.json").write_text(json.dumps(
                {'record': {k: r[k] for k in ('participant_id', 'task_id', 'condition')},
                 'outside_team_and_consented': True, 'interface': interface}))
        (folder / 'session_notes.md').write_text('U011 notes\n')
        (folder / 'README.md').write_text('readme\n')
        results = check_evidence(root, '09')
        names = [name for _, name, _ in results]
        self.assertFalse(any('explanation' in n for n in names))
        self.assertIn('ClauseGuard trials used the web app', names)
        self.assertFalse([r for r in results if r[0] == 'FAIL'])


if __name__ == '__main__':
    unittest.main()
