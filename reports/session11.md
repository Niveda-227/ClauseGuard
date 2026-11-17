---
team: ClauseGuard
session: "11"
date: "2026-11-17"
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
    github: royak747
    hat: Operations
north_star:
  metric: "Correct clause-finding tasks completed within 180 seconds (%)"
  value: 100.00
  previous: 100.00
---

## Shipped this week

**Merged this week:** [PR #90](https://github.com/Niveda-227/ClauseGuard/pull/90), [PR #91](https://github.com/Niveda-227/ClauseGuard/pull/91), [PR #92](https://github.com/Niveda-227/ClauseGuard/pull/92), [PR #93](https://github.com/Niveda-227/ClauseGuard/pull/93), [PR #94](https://github.com/Niveda-227/ClauseGuard/pull/94). `main` is a protected branch. Every PR was approved by a teammate before merge.

This week's question: before the release is frozen in Session 12, would a simpler or different model configuration do better than the one we ship, judged on the validation split only?

* The rule for choosing the final model, written as a decision record ([docs/decisions/2026-11-11_final_model_rule.md](../docs/decisions/2026-11-11_final_model_rule.md), [final_model_rule.json](../docs/decisions/final_model_rule.json)). It was written when the Session 11 kit was prepared, before the ablation was first run (the ablation was dry-run once on 2026-11-10 to check the kit, after the rule was frozen); it was merged on `main` before the ablation script was added, was never changed after, and the ablation script reads it without changing it.
* An ablation of 12 configurations (word, character or both; balanced class weights or none; one cut-off per category or a fixed 0.5), each trained on the train split only and scored honestly on validation ([scripts/ablation.py](../scripts/ablation.py), [ablation.md](../experiments/session11/ablation.md)). Result: KEEP the shipped model for the final release.
* The product model can now be rebuilt from a clean clone and checked against the model we report ([scripts/reproduce_model.py](../scripts/reproduce_model.py), [reproduce.md](../experiments/session11/reproduce.md)). Result: REPRODUCED. The model card has a new section whose numbers are checked against their source files by a test ([docs/MODEL_CARD.md](../docs/MODEL_CARD.md)).
* In the web app, a reminder above the findings, from the Session 10 domain-shift result: no flag does not mean the clause is not there.
* Study tasks K1 and L1 on two of the fresh real documents, where the answer is not flagged but the "Check it yourself" panel lists it ([tasks_v6.json](../examples/study/tasks_v6.json), [study_doc_check.json](../experiments/session11/study_doc_check.json)).
* The outline of the final presentation ([reports/final/slides.md](final/slides.md)), the skeletons of the final README and report ([reports/final/README.md](final/README.md), [reports/final/report.md](final/report.md)) and a demo rehearsal checklist ([docs/DEMO_REHEARSAL.md](../docs/DEMO_REHEARSAL.md)).

The model running in the product did not change this week. It is still `dafbb5470f2fb2678cae273eac7c23046bbad0487c7be247174a99a08ad493bd`, the hybrid model with per-category cut-offs shipped in Session 07.

## User evidence

- **Raw artifact**: [task records](../evidence/session11/tasks.csv), [trial files and notes](../evidence/session11/), [summary](../evidence/session11/summary.json). Protocol `sep29_v2`.
- ClauseGuard: 2/2 ClauseGuard tasks correct within 180 seconds (100.00%), 2 outside participant(s), median 52.2 s.
- Manual comparison: 2/2 manual tasks correct within the limit (100.00%), median 58.4 s.
- Participants: U016, U017. The sessions took place on November 16th, 2026, with two new outside participants who were not on the team and had not participated in Sessions 04 through 10. They were classmates of the observer and were recruited in person in one of the observer's classes.
- The two tasks. In both, the answer sentence is in the document but the model does not flag it, and the "Check it yourself" panel lists it as worth a look. **K1** asks whether there is a limit on what the company would have to pay you (Cloudup terms): the model flags other liability sentences, but not the one with the limit (Limitation of liability score 0.426, cut-off 0.75). **L1** asks whether the company can delete your free account if you stop using it (Crowdsignal terms): no sentence is flagged for Content removal, and the answer is listed under it (score 0.37, cut-off 0.80).

| Participant | Task | Condition | Interface | Correct within the limit | Seconds |
|---|---|---|---|---|---:|
| U016 | K1 | ClauseGuard | web | yes | 44.382 |
| U016 | L1 | manual | text_editor | yes | 47.531 |
| U017 | L1 | ClauseGuard | web | yes | 59.959 |
| U017 | K1 | manual | text_editor | yes | 69.192 |

- K1 with the web app: Participant U016 opened the Cloudup document, reviewed the flagged limitation-of-liability sentences, explored the related findings, checked additional sentences, and located the liability cap of five dollars and twenty-three cents. Whether they read the reminder above the findings or opened the "Check it yourself" panel and clicked a worth-a-look sentence was not observed.
- L1 with the web app: Participant U017 opened the Crowdsignal document, reviewed the available findings, explored the account-related information, and located the inactive free account clause specifying six months. Whether they read the reminder above the findings or opened the "Check it yourself" panel and clicked a worth-a-look sentence was not observed.
- Manual trials: Participant U016 searched the Crowdsignal document for account-related terms, went to the user terms section, and read the account deletion clause, answering that free accounts can be deleted after six months or longer without logging in. Participant U017 searched the Cloudup document for liability-related terms, went to the Limitation of Liability section, and read the liability cap clause, answering that liability is limited to five dollars and twenty-three cents.
- Resulting change or next action: The team keeps the current interface and panel setup unchanged since all trials succeeded, while noting that future trials will explicitly track panel usage. (evidence: [issue #88](https://github.com/Niveda-227/ClauseGuard/issues/88), [PR #94](https://github.com/Niveda-227/ClauseGuard/pull/94))
- This is a small pilot on two real documents, not a population estimate or a check of legal correctness.

## Metrics snapshot

**Product north-star:** 100.00% this week; previous 100.00%.

The previous value is Session 10 (tasks I1 and J1). This week's tasks are different (the answer is never flagged), so the two values are not directly comparable.

**Ablation: which configuration should the final release use?** Validation split only (2275 sentences, 10 companies); test split not read. Honest macro-F1 is leave-one-company-out for per-category cut-offs (each company's cut-offs are tuned on the other nine) and plain for fixed `0.5`. The last column is reported only: those labels were not made independently (Session 10). Source: [ablation.md](../experiments/session11/ablation.md).

| Features | Class weighting | Cut-offs | Honest macro-F1 | Micro-F1 | Flags per 100 sentences | Fresh documents macro-F1 (reported only) |
|---|---|---|---:|---:|---:|---:|
| word | balanced | per_category | 0.6563 | 0.6571 | 10.59 | 0.4359 |
| word | balanced | fixed_0.5 | 0.6156 | 0.6084 | 18.24 | 0.4730 |
| word | none | per_category | 0.4927 | 0.5826 | 9.27 | 0.4158 |
| word | none | fixed_0.5 | 0.1405 | 0.2151 | 1.32 | 0.0891 |
| char | balanced | per_category | 0.6455 | 0.6545 | 13.10 | 0.4055 |
| char | balanced | fixed_0.5 | 0.5684 | 0.5615 | 21.93 | 0.4257 |
| char | none | per_category | 0.5598 | 0.6051 | 11.43 | 0.4055 |
| char | none | fixed_0.5 | 0.2540 | 0.3366 | 2.37 | 0.1640 |
| hybrid (shipped) | balanced | per_category | 0.6768 | 0.6880 | 11.03 | 0.4139 |
| hybrid | balanced | fixed_0.5 | 0.6333 | 0.6275 | 17.49 | 0.4653 |
| hybrid | none | per_category | 0.6277 | 0.6498 | 9.89 | 0.4041 |
| hybrid | none | fixed_0.5 | 0.3598 | 0.4343 | 3.43 | 0.1961 |

**The pre-set rule** (keep the shipped configuration unless another one's honest macro-F1 is at least `0.02` higher): best hybrid / balanced / per_category 0.6768; shipped 0.6768; gain 0.0000 (a switch needs at least 0.02). **Result: KEEP the shipped model for the final release.**

**Rebuild from a clean clone.** Retraining the shipped configuration with the product code gives the same validation scores (within one millionth) and the same flags as the product model, and the same flags on the demo document: 6 of 6 checks passed, **REPRODUCED**. Fingerprint of the validation flags: `0e635d75ca4662bd4e5b0511f101117e78c3b0d14da76b16a22c03a9565cea3b`. Source: [reproduce.md](../experiments/session11/reproduce.md).

**Model development results** (validation split; final test split not evaluated). Honest leave-one-company-out macro-F1 of the product model 0.6768, the same as in Session 07 ([threshold_ship_eval.md](../experiments/session07/threshold_ship_eval.md)).

**Same model as the product?** Yes. `artifacts/selected.joblib`, SHA-256 `dafbb5470f2fb2678cae273eac7c23046bbad0487c7be247174a99a08ad493bd`, is the model every ClauseGuard trial used this week, and the model the ablation and the rebuild check against.

## What did not work

- **The ablation, in words:** Without balanced class weighting every configuration did worse on validation and flagged fewer sentences, far fewer with a fixed cut-off. With balanced weighting, a fixed cut-off also did worse on validation than per-category cut-offs, but it flagged more sentences and scored higher on the fresh documents. Those labels were not made independently and cover only three documents, so this is a hint for Session 12, not a reason to switch; the decision uses validation only.
- **Wrong answers in the study:** No wrong answers were recorded this week.
- **Limits:** the ablation chooses among 12 configurations on one split, which flatters the best one; the Session 12 test-split run is the unbiased number. A contextual model (for example sentence embeddings) was not tried, because it cannot be installed offline on every laptop.

## Challenges / blockers

No major scheduling, recruitment, or technical setup blockers were reported for this session.

## Next week's goal

Session 12 (the last weekly report): freeze the release with the result above (KEEP the shipped model for the final release), read the test split once with the frozen model and report it next to the validation numbers whatever it shows, run the final user check on the frozen build, and fill the final README, report and slides from the result files.

## Individual contributions

- Ameer (Product): Wrote the rule for choosing the final model before the ablation was first run, recorded the final interface decision from the Session 09 and 10 results, added the domain-shift reminder to the web app, and outlined the final presentation. (evidence: [issue #85](https://github.com/Niveda-227/ClauseGuard/issues/85), [PR #90](https://github.com/Niveda-227/ClauseGuard/pull/90))
- Hemanth (Engineering): Made the product model rebuildable from a clean clone with a check that it is the model we report, and added a model card section whose numbers are checked against their sources by a test. (evidence: [issue #86](https://github.com/Niveda-227/ClauseGuard/issues/86), [PR #91](https://github.com/Niveda-227/ClauseGuard/pull/91))
- Jayakrishna (Data&Eval): Compared 12 model configurations on the validation split under the pre-set rule (features, class weighting, cut-offs) and reported the fresh-document scores alongside. (evidence: [issue #87](https://github.com/Niveda-227/ClauseGuard/issues/87), [PR #92](https://github.com/Niveda-227/ClauseGuard/pull/92))
- Niveda (Users&Research): Prepared study tasks K1 and L1 on two fresh real documents, where the answer is not flagged but the Check it yourself panel lists it, and ran the Session 11 study with new outside participants using ClauseGuard. (evidence: [issue #88](https://github.com/Niveda-227/ClauseGuard/issues/88), [PR #93](https://github.com/Niveda-227/ClauseGuard/pull/93), [PR #94](https://github.com/Niveda-227/ClauseGuard/pull/94))
- Ankan (Operations): Wrote the Session 11 report with every number filled from its source file, updated the lean canvas, and set up the final README, the final report skeleton and the demo rehearsal checklist. (evidence: [issue #89](https://github.com/Niveda-227/ClauseGuard/issues/89), [PR #95](https://github.com/Niveda-227/ClauseGuard/pull/95))

## Lean canvas changes (if any)

Updated [docs/lean_canvas.md](../docs/lean_canvas.md): "Current evidence" now points to the Session 11 ablation and the rebuild check. The target user, value proposition, cost and biggest risk did not change.
