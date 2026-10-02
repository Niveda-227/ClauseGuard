# Mid-semester numbers: audit notes (Session 06)

Author: Jayakrishna (`Jayakrishna-Reddy`) · Date: 2026-10-02
Script: `scripts/midpoint_facts.py` · Checked on commit: 9eae17e

## 1. Comparability checks I ran by hand

| Check | Command result | Passed? |
|---|---|---|
| Same 2,275 validation sentences for all three models, no test sentences | `2275 True False` | yes |
| Validation companies absent from training | `10 []` | yes |
| App model = evaluated model | `04713fbf6e23 04713fbf6e23` | yes |
| Arbitration row matches metrics.json | precision 0.2273, recall 0.5556, f1 0.3226, support 9 | yes |

## 2. What the numbers support

The shipped hybrid model scores 0.6333 macro-F1 on validation, against 0.2551 for the
unigram baseline, a gain of +0.3782. That comparison is apples to apples: all three
models were scored on the exact same 2,275 validation sentences, none of the 10
validation companies appear in training, and I confirmed by hand that the model file
the app actually loads is byte for byte the same one the metrics were computed from
(same SHA-256 fingerprint, 04713fbf6e23). So the headline number isn't just claimed,
it's independently checkable, and I checked it myself rather than trusting the script.

## 3. What the numbers do not support

This is a validation split result, not a test split result. The final test split has
never been read, so this isn't an unbiased final estimate of real world performance.
The Session 05 threshold experiment is explicitly labelled not shipped in the script's
output; the product still runs on the fixed 0.5 threshold, so none of that tuning
benefit applies here. The outside user numbers are from a single participant so far
(this week's sessions haven't run yet), which is nowhere near enough to generalize
from. The rule evaluation correctly reports "Provisional persevere" rather than a real
decision for exactly this reason. C1 (the over tagged task) and D1 are not the same
difficulty, so a straight manual vs ClauseGuard comparison across them isn't a fair,
matched test. The script's own metrics.md says so too.

## 4. Rule logic

I read evaluate_rule() against section 3 of
docs/decisions/2026-10-06_midpoint_decision.md and the four conditions it checks (model
gain gate, participant count gate, success rate comparison, and the C1 failure check)
match the table row for row. tests/test_midpoint_facts.py covers each possible outcome
with its own test (test_fewer_than_three_participants_is_provisional,
test_model_gate_failure_is_pivot_regardless_of_users, test_all_correct_is_persevere,
test_failing_the_over_tagged_task_with_the_app_is_persevere_with_change,
test_clearly_worse_with_the_app_is_pivot), so each branch of the if/elif chain has at
least one test that would fail if the logic were wrong.