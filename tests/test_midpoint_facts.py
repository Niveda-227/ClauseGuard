import json
import unittest
from pathlib import Path

from scripts.midpoint_facts import build, evaluate_rule, user_facts

ROOT = Path(__file__).resolve().parents[1]
RULE = json.loads((ROOT / 'docs/decisions/midpoint_rule.json').read_text())
SHIPPED = RULE['shipped_model_sha256']


def trial(p, task, cond, correct, seconds=60.0, session='session06', protocol='sep29_v2', model=None):
    return {'participant_id': p, 'task_id': task, 'condition': cond, 'correct': '1' if correct else '0',
            'seconds': str(seconds), 'limit_seconds': '180', 'protocol_version': protocol, 'session': session,
            'model_id': 'manual' if cond == 'manual' else (model or SHIPPED)}


MODEL_OK = {'identical': True, 'gain_over_baseline': 0.378}


class RuleTests(unittest.TestCase):
    def outcome(self, trials, model=MODEL_OK):
        return evaluate_rule(RULE, model, user_facts(trials, RULE))['outcome']

    def test_fewer_than_three_participants_is_provisional(self):
        self.assertEqual(self.outcome([trial('U002', 'C1', 'manual', True), trial('U002', 'D1', 'clauseguard', True)]),
                         'PROVISIONAL_PERSEVERE')

    def test_model_gate_failure_is_pivot_regardless_of_users(self):
        self.assertEqual(self.outcome([], {'identical': True, 'gain_over_baseline': 0.05}), 'PIVOT')

    def test_all_correct_is_persevere(self):
        t = []
        for p, c1 in (('U003', 'clauseguard'), ('U004', 'manual'), ('U005', 'clauseguard')):
            other = 'manual' if c1 == 'clauseguard' else 'clauseguard'
            t += [trial(p, 'C1', c1, True), trial(p, 'D1', other, True)]
        self.assertEqual(self.outcome(t), 'PERSEVERE')

    def test_failing_the_over_tagged_task_with_the_app_is_persevere_with_change(self):
        t = [trial('U003', 'C1', 'clauseguard', False), trial('U003', 'D1', 'manual', False),
             trial('U004', 'C1', 'manual', True), trial('U004', 'D1', 'clauseguard', True),
             trial('U005', 'C1', 'clauseguard', True), trial('U005', 'D1', 'manual', True)]
        self.assertEqual(self.outcome(t), 'PERSEVERE_WITH_CHANGE')

    def test_clearly_worse_with_the_app_is_pivot(self):
        t = [trial('U003', 'C1', 'clauseguard', False), trial('U003', 'D1', 'manual', True),
             trial('U004', 'C1', 'manual', True), trial('U004', 'D1', 'clauseguard', False),
             trial('U005', 'C1', 'clauseguard', True), trial('U005', 'D1', 'manual', True)]
        self.assertEqual(self.outcome(t), 'PIVOT')

    def test_answer_after_the_limit_is_not_a_success(self):
        u = user_facts([trial('U003', 'D1', 'clauseguard', True, seconds=181)], RULE)
        self.assertEqual(u['by_condition']['clauseguard']['successes'], 0)

    def test_other_protocols_and_other_models_are_excluded(self):
        u = user_facts([trial('U001', 'B1', 'clauseguard', True, protocol='sep22_v1'),
                        trial('U003', 'D1', 'clauseguard', True, model='0' * 64)], RULE)
        self.assertEqual(u['trials'], 0)
        self.assertEqual(len(u['excluded']), 2)

    def test_a_participant_repeating_a_task_across_sessions_is_refused(self):
        with self.assertRaises(ValueError):
            user_facts([trial('U002', 'C1', 'manual', True, session='session05'),
                        trial('U002', 'C1', 'manual', True, session='session06')], RULE)


class RepositoryTests(unittest.TestCase):
    def test_numbers_match_the_committed_results(self):
        facts = build(ROOT)
        t = facts['tokens']
        self.assertEqual(t['HYBRID_MACRO_F1'], '0.6333')
        self.assertEqual(t['BASELINE_MACRO_F1'], '0.2551')
        self.assertEqual(t['MODEL_SHA12'], SHIPPED[:12])
        self.assertTrue(facts['model']['identical'])
        self.assertFalse(facts['model']['threshold_experiment']['shipped'])
        self.assertNotIn('test:', json.dumps(facts))


if __name__ == '__main__':
    unittest.main()
