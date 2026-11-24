---
team: ClauseGuard
session: "12"
date: "2026-11-24"
members:
  - name: Ameer
    github: {{AUTO_GITHUB_Ameer}}
    hat: Product
  - name: Hemanth
    github: {{AUTO_GITHUB_Hemanth}}
    hat: Engineering
  - name: Jayakrishna
    github: {{AUTO_GITHUB_Jayakrishna}}
    hat: Data&Eval
  - name: Niveda
    github: {{AUTO_GITHUB_Niveda}}
    hat: Users&Research
  - name: Ankan
    github: {{AUTO_GITHUB_Ankan}}
    hat: Operations
north_star:
  metric: "Correct clause-finding tasks completed within 180 seconds (%)"
  value: {{AUTO_VALUE}}
  previous: {{AUTO_PREVIOUS}}
---

## Shipped this week

**Merged this week:** {{AUTO_SHIPPED_LINKS}}. `main` is a protected branch. Every PR was approved by a teammate before merge.

This week's question: how good is the product model on data no choice of ours has touched? We froze the product as a release and read the UNFAIR-ToS test split once, under a rule written before.

* The rule for reporting the test result, written as a decision record before the test split was read ([docs/decisions/2026-11-18_final_test_rule.md](../docs/decisions/2026-11-18_final_test_rule.md), [final_test_rule.json](../docs/decisions/final_test_rule.json)). The kit was checked with validation rows in place of test rows, so no test result existed before the one run below.
* The product frozen as **release {{FROM:experiments/session12/release_summary.json#version}}**: {{FROM:experiments/session12/release_summary.json#product_files}} product files (the apps, the model and its cut-offs, the pinned packages) fingerprinted in `RELEASE.json`, checked by `scripts/check_release.py`, and the merge commit of the release PR tagged `{{FROM:experiments/session12/release_summary.json#tag}}` ([docs/RELEASE.md](../docs/RELEASE.md)).
* The test split read once with that release ([scripts/final_test.py](../scripts/final_test.py), [test_eval.md](../experiments/session12/test_eval.md)); `scripts/check_final_test.py` confirms the reading is recorded exactly once in `experiments/test_exposure.jsonl`. Result: {{FROM:experiments/session12/test_eval.json#result}}.
* The final user check on the frozen release: study tasks M1 and N1 on two of the fresh real documents, where the app flags the answer ([tasks_v7.json](../examples/study/tasks_v7.json), [study_doc_check.json](../experiments/session12/study_doc_check.json)).
* Every outside-user session so far in one table ([scripts/study_summary.py](../scripts/study_summary.py), [study_summary.md](../experiments/session12/study_summary.md)).
* Speaker notes for the final presentation ([reports/final/slides.md](final/slides.md)) and the model card updated with the release and the test result ([docs/MODEL_CARD.md](../docs/MODEL_CARD.md)).

The model running in the product did not change this week. It is still `{{AUTO_MODEL_ID}}`, the hybrid model with per-category cut-offs shipped in Session 07, now release {{FROM:experiments/session12/release_summary.json#version}}.

## User evidence

- **Raw artifact**: {{AUTO_EVIDENCE_LINKS}}. Protocol `{{AUTO_PROTOCOL}}`.
- ClauseGuard: {{AUTO_TOOL_RESULT}}.
- Manual comparison: {{AUTO_MANUAL_RESULT}}.
- Participants: {{AUTO_PARTICIPANT_IDS}}. The sessions took place on November 23, 2026, with two new outside participants who were neither on the team nor in Sessions 04 to 11. Both participants were friends of the observer recruited in person, and the release check printed THIS IS RELEASE 1.0.0 on the session laptop before the first trial.
- The two tasks. In both, the app flags the answer sentence. **M1** asks how a dispute with the company must be settled (Cloudup terms): the answer is flagged {{FROM:experiments/session12/study_doc_check.json#tasks.0.target_category}} (score {{FROM:experiments/session12/study_doc_check.json#tasks.0.target_score}}, cut-off {{FROM:experiments/session12/study_doc_check.json#tasks.0.target_cut_off|2}}), and the governing-law sentence is flagged too. **N1** asks whether the company can remove your content and whether it checks content first (Basecamp terms): the answer is flagged {{FROM:experiments/session12/study_doc_check.json#tasks.1.target_category}} (score {{FROM:experiments/session12/study_doc_check.json#tasks.1.target_score}}, cut-off {{FROM:experiments/session12/study_doc_check.json#tasks.1.target_cut_off|2}}).

{{AUTO_TRIALS_TABLE}}

- M1 with the web app: The participant opened the Cloudup document and reviewed the findings, navigated to the Arbitration Agreement section, read the passage, and stated that disputes must be resolved through final and binding arbitration rather than a judge or jury, identifying JAMS rules, three arbitrators, and possible locations. Which flag or category they opened first is not observed, and they did not answer from the governing-law sentence instead.
- N1 with the web app: The participant opened the Basecamp document in ClauseGuard, reviewed the available findings, located the Your Content section, and checked the relevant sentences, stating that the company can remove content that users submit. Which flag or category they opened first is not observed, and whether they answered from the termination sentence instead is not observed.
- Manual trials: For the manual N1 trial, how the participant searched is not observed, and they stated that the company can remove submitted content and does not actively review content before upload. For the manual M1 trial, the participant opened the Cloudup terms in Notepad and searched for dispute-resolution information, navigating to the Arbitration Agreement section and stating that disputes must be resolved through final and binding arbitration rather than a judge or jury.
- Resulting change or next action: For the final submission, the team will use these trials in the report, slides, or demo while noting the session observations and measurement caveats without changing the frozen product. (evidence: {{AUTO_CHANGE_LINKS}})
- **All sessions so far:** {{FROM:experiments/session12/study_summary.json#totals.summary}} ([study_summary.md](../experiments/session12/study_summary.md)). These are small, non-random samples; each participant did one task with the app and one without, and the tasks changed from session to session.

## Metrics snapshot

**Product north-star:** {{AUTO_VALUE}}% this week; previous {{AUTO_PREVIOUS}}%.

The previous value is Session 11 (tasks K1 and L1, where the app missed the answer). This week's tasks are different (the app flags the answer), so the two values are not directly comparable.

**The one-time test-split result.** Release {{FROM:experiments/session12/test_eval.json#release}}, shipped cut-offs, nothing tuned on the test split. Test split: {{FROM:experiments/session12/test_eval.json#sentences}} sentences from {{FROM:experiments/session12/test_eval.json#companies}} companies. Source: [test_eval.md](../experiments/session12/test_eval.md).

| Measure | Test split | Honest validation | Optimistic validation |
|---|---:|---:|---:|
| Macro-F1 (8 categories) | {{FROM:experiments/session12/test_eval.json#test_macro_f1|4}} | {{FROM:experiments/session12/test_eval.json#honest_validation_macro_f1|4}} | {{FROM:experiments/session12/test_eval.json#optimistic_validation_macro_f1|4}} |
| Micro-F1 | {{FROM:experiments/session12/test_eval.json#test_micro_f1|4}} | {{FROM:experiments/session07/threshold_ship_eval.json#new_product_leave_one_company_out_HONEST.micro_f1|4}} | {{FROM:experiments/session07/threshold_ship_eval.json#new_product_tuned_OPTIMISTIC.micro_f1|4}} |
| Flags per 100 sentences | {{FROM:experiments/session12/test_eval.json#flags_per_100_sentences|2}} | {{FROM:experiments/session07/threshold_ship_eval.json#new_product_leave_one_company_out_HONEST.flags_per_100_sentences|2}} | {{FROM:experiments/session07/threshold_ship_eval.json#new_product_tuned_OPTIMISTIC.flags_per_100_sentences|2}} |
| Correct tags | {{FROM:experiments/session12/test_eval.json#correct_tags}} | {{FROM:experiments/session07/threshold_ship_eval.json#new_product_leave_one_company_out_HONEST.correct_tags}} | {{FROM:experiments/session07/threshold_ship_eval.json#new_product_tuned_OPTIMISTIC.correct_tags}} |
| Wrong tags | {{FROM:experiments/session12/test_eval.json#wrong_tags}} | {{FROM:experiments/session07/threshold_ship_eval.json#new_product_leave_one_company_out_HONEST.wrong_tags}} | {{FROM:experiments/session07/threshold_ship_eval.json#new_product_tuned_OPTIMISTIC.wrong_tags}} |
| Missed labels | {{FROM:experiments/session12/test_eval.json#missed_labels}} | {{FROM:experiments/session07/threshold_ship_eval.json#new_product_leave_one_company_out_HONEST.missed_labels}} | {{FROM:experiments/session07/threshold_ship_eval.json#new_product_tuned_OPTIMISTIC.missed_labels}} |

The validation columns cover {{FROM:experiments/session07/threshold_ship_eval.json#sentences}} sentences, so the counts are not directly comparable with the test split's; the F1 scores and flags per 100 sentences are.

**The pre-set rule** (the test macro-F1 is CONSISTENT with the honest validation estimate if it is within `0.05` of it): {{FROM:experiments/session12/test_eval.json#summary}}. **Result: {{FROM:experiments/session12/test_eval.json#result}}.**

| Category | Test support | Test precision | Test recall | Test F1 | Honest validation F1 |
|---|---:|---:|---:|---:|---:|
| Limitation of liability | {{FROM:experiments/session12/test_eval.json#per_category.Limitation of liability.support}} | {{FROM:experiments/session12/test_eval.json#per_category.Limitation of liability.precision|4}} | {{FROM:experiments/session12/test_eval.json#per_category.Limitation of liability.recall|4}} | {{FROM:experiments/session12/test_eval.json#per_category.Limitation of liability.f1|4}} | {{FROM:experiments/session12/test_eval.json#per_category.Limitation of liability.honest_validation_f1|4}} |
| Unilateral termination | {{FROM:experiments/session12/test_eval.json#per_category.Unilateral termination.support}} | {{FROM:experiments/session12/test_eval.json#per_category.Unilateral termination.precision|4}} | {{FROM:experiments/session12/test_eval.json#per_category.Unilateral termination.recall|4}} | {{FROM:experiments/session12/test_eval.json#per_category.Unilateral termination.f1|4}} | {{FROM:experiments/session12/test_eval.json#per_category.Unilateral termination.honest_validation_f1|4}} |
| Unilateral change | {{FROM:experiments/session12/test_eval.json#per_category.Unilateral change.support}} | {{FROM:experiments/session12/test_eval.json#per_category.Unilateral change.precision|4}} | {{FROM:experiments/session12/test_eval.json#per_category.Unilateral change.recall|4}} | {{FROM:experiments/session12/test_eval.json#per_category.Unilateral change.f1|4}} | {{FROM:experiments/session12/test_eval.json#per_category.Unilateral change.honest_validation_f1|4}} |
| Content removal | {{FROM:experiments/session12/test_eval.json#per_category.Content removal.support}} | {{FROM:experiments/session12/test_eval.json#per_category.Content removal.precision|4}} | {{FROM:experiments/session12/test_eval.json#per_category.Content removal.recall|4}} | {{FROM:experiments/session12/test_eval.json#per_category.Content removal.f1|4}} | {{FROM:experiments/session12/test_eval.json#per_category.Content removal.honest_validation_f1|4}} |
| Contract by using | {{FROM:experiments/session12/test_eval.json#per_category.Contract by using.support}} | {{FROM:experiments/session12/test_eval.json#per_category.Contract by using.precision|4}} | {{FROM:experiments/session12/test_eval.json#per_category.Contract by using.recall|4}} | {{FROM:experiments/session12/test_eval.json#per_category.Contract by using.f1|4}} | {{FROM:experiments/session12/test_eval.json#per_category.Contract by using.honest_validation_f1|4}} |
| Choice of law | {{FROM:experiments/session12/test_eval.json#per_category.Choice of law.support}} | {{FROM:experiments/session12/test_eval.json#per_category.Choice of law.precision|4}} | {{FROM:experiments/session12/test_eval.json#per_category.Choice of law.recall|4}} | {{FROM:experiments/session12/test_eval.json#per_category.Choice of law.f1|4}} | {{FROM:experiments/session12/test_eval.json#per_category.Choice of law.honest_validation_f1|4}} |
| Jurisdiction | {{FROM:experiments/session12/test_eval.json#per_category.Jurisdiction.support}} | {{FROM:experiments/session12/test_eval.json#per_category.Jurisdiction.precision|4}} | {{FROM:experiments/session12/test_eval.json#per_category.Jurisdiction.recall|4}} | {{FROM:experiments/session12/test_eval.json#per_category.Jurisdiction.f1|4}} | {{FROM:experiments/session12/test_eval.json#per_category.Jurisdiction.honest_validation_f1|4}} |
| Arbitration | {{FROM:experiments/session12/test_eval.json#per_category.Arbitration.support}} | {{FROM:experiments/session12/test_eval.json#per_category.Arbitration.precision|4}} | {{FROM:experiments/session12/test_eval.json#per_category.Arbitration.recall|4}} | {{FROM:experiments/session12/test_eval.json#per_category.Arbitration.f1|4}} | {{FROM:experiments/session12/test_eval.json#per_category.Arbitration.honest_validation_f1|4}} |

**Same model as the product?** Yes. `artifacts/selected.joblib`, SHA-256 `{{AUTO_MODEL_ID}}`, is release {{FROM:experiments/session12/release_summary.json#version}}: the model every ClauseGuard trial used this week and the model the test split was scored with.

## What did not work

- **The test result, in words:** The test macro-F1 is higher than the honest validation estimate by more than the margin, and is also slightly higher than the optimistic validation number. Arbitration, choice of law, and content removal were clearly better on the test split, while jurisdiction was clearly worse, and limitation of liability, unilateral termination, unilateral change, and contract by using were about the same as on validation.
- **Wrong answers in the study:** No wrong answers were recorded this week.
- **Limits:** the test split comes from the same dataset (other companies, but the same kind of documents and the same annotation), so it says nothing new about the real documents we labelled ourselves, where Session 10 found the model misses more. The study samples are small and not random.

## Challenges / blockers

Both participants were in the same room for all trials and could hear each other with each of the second participant's tasks occurring after the first participant did the same task, and in the ClauseGuard N1 trial the participant gave only the first half of the required answer despite being recorded as correct. In addition, which flag was opened first was not observed, and how the participant searched in the manual N1 trial was not observed.

## Next week's goal

Session 13 (the final submission, due Tuesday December 1, 5:00 pm): fill the final README, report and slides from the result files, rehearse the demo on release {{FROM:experiments/session12/release_summary.json#version}} with `scripts/demo_check.py` and `scripts/check_release.py`, and present.

## Individual contributions

{{AUTO_CONTRIBUTIONS}}

## Lean canvas changes (if any)

Updated [docs/lean_canvas.md](../docs/lean_canvas.md): "Current evidence" now says the test split was read once after the release freeze, and points to the release, the test result and the summary of all outside-user sessions. The target user, value proposition, cost and biggest risk did not change.
