---
team: ClauseGuard
session: "12"
date: "2026-11-24"
members:
  - name: Ameer
    github: sohail-umd
    hat: Product
  - name: Hemanth
    github: hreddy14
    hat: Engineering
  - name: Jayakrishna
    github: Jayakrishna-Reddy
    hat: Data&Eval
  - name: Niveda
    github: Niveda-227
    hat: Users&Research
  - name: Ankan
    github: aroycoder
    hat: Operations
north_star:
  metric: "Correct clause-finding tasks completed within 180 seconds (%)"
  value: 100.00
  previous: 100.00
---

## Shipped this week

**Merged this week:** [PR #101](https://github.com/Niveda-227/ClauseGuard/pull/101), [PR #102](https://github.com/Niveda-227/ClauseGuard/pull/102), [PR #103](https://github.com/Niveda-227/ClauseGuard/pull/103), [PR #104](https://github.com/Niveda-227/ClauseGuard/pull/104), [PR #105](https://github.com/Niveda-227/ClauseGuard/pull/105). `main` is a protected branch. Every PR was approved by a teammate before merge.

This week's question: how good is the product model on data no choice of ours has touched? We froze the product as a release and read the UNFAIR-ToS test split once, under a rule written before.

* The rule for reporting the test result, written as a decision record before the test split was read ([docs/decisions/2026-11-18_final_test_rule.md](../docs/decisions/2026-11-18_final_test_rule.md), [final_test_rule.json](../docs/decisions/final_test_rule.json)). The kit was checked with validation rows in place of test rows, so no test result existed before the one run below.
* The product frozen as **release 1.0.0**: 28 product files (the apps, the model and its cut-offs, the pinned packages) fingerprinted in `RELEASE.json`, checked by `scripts/check_release.py`, and the merge commit of the release PR tagged `v1.0.0` ([docs/RELEASE.md](../docs/RELEASE.md)).
* The test split read once with that release ([scripts/final_test.py](../scripts/final_test.py), [test_eval.md](../experiments/session12/test_eval.md)); `scripts/check_final_test.py` confirms the reading is recorded exactly once in `experiments/test_exposure.jsonl`. Result: HIGHER than the honest validation estimate.
* The final user check on the frozen release: study tasks M1 and N1 on two of the fresh real documents, where the app flags the answer ([tasks_v7.json](../examples/study/tasks_v7.json), [study_doc_check.json](../experiments/session12/study_doc_check.json)).
* Every outside-user session so far in one table ([scripts/study_summary.py](../scripts/study_summary.py), [study_summary.md](../experiments/session12/study_summary.md)).
* Speaker notes for the final presentation ([reports/final/slides.md](final/slides.md)) and the model card updated with the release and the test result ([docs/MODEL_CARD.md](../docs/MODEL_CARD.md)).

The model running in the product did not change this week. It is still `dafbb5470f2fb2678cae273eac7c23046bbad0487c7be247174a99a08ad493bd`, the hybrid model with per-category cut-offs shipped in Session 07, now release 1.0.0.

## User evidence

- **Raw artifact**: [task records](../evidence/session12/tasks.csv), [trial files and notes](../evidence/session12/), [summary](../evidence/session12/summary.json). Protocol `sep29_v2`.
- ClauseGuard: 2/2 ClauseGuard tasks correct within 180 seconds (100.00%), 2 outside participant(s), median 35.3 s.
- Manual comparison: 2/2 manual tasks correct within the limit (100.00%), median 53.5 s.
- Participants: U018, U019. The sessions took place on November 23, 2026, with two new outside participants who were neither on the team nor in Sessions 04 to 11. Both participants were friends of the observer recruited in person, and the release check printed THIS IS RELEASE 1.0.0 on the session laptop before the first trial.
- The two tasks. In both, the app flags the answer sentence. **M1** asks how a dispute with the company must be settled (Cloudup terms): the answer is flagged Arbitration (score 0.983, cut-off 0.80), and the governing-law sentence is flagged too. **N1** asks whether the company can remove your content and whether it checks content first (Basecamp terms): the answer is flagged Content removal (score 0.996, cut-off 0.80).

| Participant | Task | Condition | Interface | Correct within the limit | Seconds |
|---|---|---|---|---|---:|
| U018 | M1 | ClauseGuard | web | yes | 46.107 |
| U018 | N1 | manual | text_editor | yes | 60.731 |
| U019 | N1 | ClauseGuard | web | yes | 24.461 |
| U019 | M1 | manual | text_editor | yes | 46.18 |

- M1 with the web app: The participant opened the Cloudup document and reviewed the findings, navigated to the Arbitration Agreement section, read the passage, and stated that disputes must be resolved through final and binding arbitration rather than a judge or jury, identifying JAMS rules, three arbitrators, and possible locations. Which flag or category they opened first is not observed, and they did not answer from the governing-law sentence instead.
- N1 with the web app: The participant opened the Basecamp document in ClauseGuard, reviewed the available findings, located the Your Content section, and checked the relevant sentences, stating that the company can remove content that users submit. Which flag or category they opened first is not observed, and whether they answered from the termination sentence instead is not observed.
- Manual trials: For the manual N1 trial, how the participant searched is not observed, and they stated that the company can remove submitted content and does not actively review content before upload. For the manual M1 trial, the participant opened the Cloudup terms in Notepad and searched for dispute-resolution information, navigating to the Arbitration Agreement section and stating that disputes must be resolved through final and binding arbitration rather than a judge or jury.
- Resulting change or next action: In the final report and slides, the Session 12 trials are reported as weak evidence: the participants could hear each other, the second participant's typed answer for M1 is word for word the same as the first participant's, and one ClauseGuard answer was incomplete. The frozen product does not change. (evidence: [issue #99](https://github.com/Niveda-227/ClauseGuard/issues/99), [PR #105](https://github.com/Niveda-227/ClauseGuard/pull/105))
- **All sessions so far:** 17 outside participants in 8 sessions (Sessions 05 to 12): ClauseGuard 17/17 tasks correct within the limit, manual 16/17 ([study_summary.md](../experiments/session12/study_summary.md)). These are small, non-random samples; each participant did one task with the app and one without, and the tasks changed from session to session.

## Metrics snapshot

**Product north-star:** 100.00% this week; previous 100.00%.

The previous value is Session 11 (tasks K1 and L1, where the app missed the answer). This week's tasks are different (the app flags the answer), so the two values are not directly comparable.

**The one-time test-split result.** Release 1.0.0, shipped cut-offs, nothing tuned on the test split. Test split: 1607 sentences from 10 companies. Source: [test_eval.md](../experiments/session12/test_eval.md).

| Measure | Test split | Honest validation | Optimistic validation |
|---|---:|---:|---:|
| Macro-F1 (8 categories) | 0.7626 | 0.6768 | 0.7244 |
| Micro-F1 | 0.7292 | 0.6880 | 0.7254 |
| Flags per 100 sentences | 11.64 | 11.03 | 10.51 |
| Correct tags | 136 | 172 | 177 |
| Wrong tags | 51 | 79 | 62 |
| Missed labels | 50 | 77 | 72 |

The validation columns cover 2275 sentences, so the counts are not directly comparable with the test split's; the F1 scores and flags per 100 sentences are.

**The pre-set rule** (the test macro-F1 is CONSISTENT with the honest validation estimate if it is within `0.05` of it): test macro-F1 0.7626; honest validation 0.6768; difference +0.0858 (margin 0.05). **Result: HIGHER than the honest validation estimate.**

| Category | Test support | Test precision | Test recall | Test F1 | Honest validation F1 |
|---|---:|---:|---:|---:|---:|
| Limitation of liability | 38 | 0.6750 | 0.7105 | 0.6923 | 0.6929 |
| Unilateral termination | 38 | 0.6522 | 0.7895 | 0.7143 | 0.6875 |
| Unilateral change | 38 | 0.7188 | 0.6053 | 0.6571 | 0.6545 |
| Content removal | 13 | 0.5789 | 0.8462 | 0.6875 | 0.6071 |
| Contract by using | 23 | 0.9375 | 0.6522 | 0.7692 | 0.7500 |
| Choice of law | 13 | 0.9231 | 0.9231 | 0.9231 | 0.7742 |
| Jurisdiction | 16 | 0.8571 | 0.7500 | 0.8000 | 0.9000 |
| Arbitration | 7 | 0.8571 | 0.8571 | 0.8571 | 0.3478 |

**Same model as the product?** Yes. `artifacts/selected.joblib`, SHA-256 `dafbb5470f2fb2678cae273eac7c23046bbad0487c7be247174a99a08ad493bd`, is release 1.0.0: the model every ClauseGuard trial used this week and the model the test split was scored with.

## What did not work

- **The test result, in words:** The test macro-F1 is higher than the honest validation estimate by more than the margin, and is also slightly higher than the optimistic validation number. Arbitration, choice of law, and content removal were clearly better on the test split, while jurisdiction was clearly worse, and limitation of liability, unilateral termination, unilateral change, and contract by using were about the same as on validation.
- **Wrong answers in the study:** One answer was incomplete. The participant who did N1 with the web app said only that the company can remove content that users submit, and nothing about whether it checks content first, so by the both-parts rule it is not correct; the observer saved it as correct and the record was not edited, so the counts and the north-star value above include it as correct. Every other answer was correct.
- **Limits:** the test split comes from the same dataset (other companies, but the same kind of documents and the same annotation), so it says nothing new about the real documents we labelled ourselves, where Session 10 found the model misses more. The study samples are small and not random.

## Challenges / blockers

Both participants were in the same room for all trials and could hear each other, and the second participant did each task after the first participant had done the same task, so the second participant's answers and times are not independent of the first's; the second participant's typed answer for M1 is word for word the same as the first participant's. In the ClauseGuard N1 trial the participant gave only the first half of the required answer, but it was recorded as correct. Which flag was opened first was not observed, and how the participant searched in the manual N1 trial was not observed.

## Next week's goal

Session 13 (the final submission, due Tuesday December 1, 5:00 pm): fill the final README, report and slides from the result files, rehearse the demo on release 1.0.0 with `scripts/demo_check.py` and `scripts/check_release.py`, and present.

## Individual contributions

- Ameer (Product): Wrote the rule for reporting the one-time test-split result before the test split was read, and drafted the speaker notes for the final presentation. (evidence: [issue #96](https://github.com/Niveda-227/ClauseGuard/issues/96), [PR #101](https://github.com/Niveda-227/ClauseGuard/pull/101))
- Hemanth (Engineering): Froze the product as release 1.0.0 before the test split was read, with a fingerprint of every product file, a check that a folder is still the release, and the release tag. (evidence: [issue #97](https://github.com/Niveda-227/ClauseGuard/issues/97), [PR #102](https://github.com/Niveda-227/ClauseGuard/pull/102))
- Jayakrishna (Data&Eval): Read the test split once with the frozen release under the pre-set rule, reported it next to the validation numbers by category, and added a check of that record that never reads the test split again. (evidence: [issue #98](https://github.com/Niveda-227/ClauseGuard/issues/98), [PR #103](https://github.com/Niveda-227/ClauseGuard/pull/103))
- Niveda (Users&Research): Prepared study tasks M1 and N1 on two fresh real documents, ran the final user check on the frozen release with new outside participants, and summarised every outside-user session in one table. (evidence: [issue #99](https://github.com/Niveda-227/ClauseGuard/issues/99), [PR #104](https://github.com/Niveda-227/ClauseGuard/pull/104), [PR #105](https://github.com/Niveda-227/ClauseGuard/pull/105))
- Ankan (Operations): Checked the release, the test-split record and the study summary before writing the Session 12 report, wrote the report with every number filled from its source file, and updated the lean canvas. (evidence: [issue #100](https://github.com/Niveda-227/ClauseGuard/issues/100), [PR #106](https://github.com/Niveda-227/ClauseGuard/pull/106))

## Lean canvas changes (if any)

Updated [docs/lean_canvas.md](../docs/lean_canvas.md): "Current evidence" now says the test split was read once after the release freeze, and points to the release, the test result and the summary of all outside-user sessions. The target user, value proposition, cost and biggest risk did not change.
