---
team: ClauseGuard
session: "07"
date: "2026-10-20"
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

**Merged this week:** [PR #46](https://github.com/Niveda-227/ClauseGuard/pull/46), [PR #47](https://github.com/Niveda-227/ClauseGuard/pull/47), [PR #48](https://github.com/Niveda-227/ClauseGuard/pull/48), [PR #49](https://github.com/Niveda-227/ClauseGuard/pull/49), [PR #50](https://github.com/Niveda-227/ClauseGuard/pull/50). Every PR was approved by a teammate before merge; `main` requires one approving review.

* Per-category thresholds are now in the product. The app runs the same trained hybrid model as before, but each of the eight categories has its own cut-off, chosen on the validation split, instead of a fixed 0.5 ([artifacts/README.md](../artifacts/README.md), [ship record](../experiments/session07/tuned/ship_record.json)).
* The results list in the desktop app now shows the start of each sentence next to its tags, so a user can see which sentence a flag belongs to without clicking it ([clauses/display.py](../clauses/display.py)). This change was inspired after session06, where all three ClauseGuard trials, participants clicked a result to read the source sentence before answering. Across all three ClauseGuard trials, participants looked at the category tags but based their answers directly on the source sentence rather than the tags. Specifically, every app user clicked a result just to read its sentence.
* Before/after comparison of the old and new product model on the same validation sentences: [threshold_ship_eval.md](../experiments/session07/threshold_ship_eval.md).
* Trial of a heading and short-fragment filter, promised in the mid-semester decision memo; measured on validation, not added to the app ([fragment_trial.md](../experiments/session07/fragment_trial.md)). Result: no candidate passes the rule; do not ship a fragment filter (closest candidate: "8 words or fewer and no . ! ? ; : at the end" removed 2 wrong tags with 0 annotator labels on hidden sentences).
* New study task bank v3 with fictional documents E and F, replacing the retired tasks C1 and D1, which were shown publicly in the mid-semester deck ([tasks_v3.json](../examples/study/tasks_v3.json), [study_doc_check.json](../experiments/session07/study_doc_check.json)).
* The mid-semester decision record (Persevere) and the updated lean canvas were merged ([decision](../docs/decisions/2026-10-06_midpoint_decision.md)).

The model running in the product changed this week. It is the Session 04 hybrid model (`04713fbf6e23784a5d32e5cdd5fef459182408565bfe8a4fb6a9f10d53dbff76`) with per-category thresholds; the new product file is `dafbb5470f2fb2678cae273eac7c23046bbad0487c7be247174a99a08ad493bd`.

## User evidence

- **Raw artifact**: [task records](../evidence/session07/tasks.csv), [trial files and notes](../evidence/session07/), [summary](../evidence/session07/summary.json). Protocol `sep29_v2`.
- ClauseGuard: 2/2 ClauseGuard tasks correct within 180 seconds (100.00%), 2 outside participant(s), median 81.4 s.
- Manual comparison: 1/2 manual tasks correct within the limit (50.00%), median 139.6 s.
- Sessions took place on 2026-10-19 with 2 new outside participants (U006 and U007), who were classmates recruited outside the five-person team, using the desktop interface.
- U006 did task E1 with ClauseGuard, quickly finding the answer and completing the task correctly in 89.72 seconds.
- 1 participant (U007) did F1 with ClauseGuard and answered correctly in 73.107 seconds, providing the Denver court sentence. Whether they read sentences with no flag was not observed.
- In 0 out of 2 ClauseGuard trials (U006 E1, U007 F1) was it observed whether the participant read the answer from the list text before clicking.
- Resulting change or next action: Investigate improving near-threshold visibility and unflagged sentence guidance for Session 08, because Task F1 showed that participants may encounter key sentences that fall just below the decision threshold (evidence: [issue #42](https://github.com/Niveda-227/ClauseGuard/issues/42))
- This is a small pilot on short fictional documents, not a population estimate or a check of legal correctness.

## Metrics snapshot

**Product north-star:** 100.00% this week; previous 100.00%.

The previous value is Session 05 (one ClauseGuard trial, task D1, fixed-0.5 model). This week uses new tasks (E1, F1) and the new product model, so the two numbers are not a like-for-like comparison. Session 06 had no weekly report; its user sessions (3 new participants, tasks C1 and D1) recorded 3/3 ClauseGuard tasks and 3/3 manual tasks correct. This week's north-star result shows that participants succeeded on both ClauseGuard tasks (E1 and F1) under a small two-participant pilot. However, because the app flags E1's answer but intentionally does not flag F1's, this small sample does not establish a population estimate or prove general legal correctness across unflagged clauses.

**Model development results** (validation split, 2,275 sentences, 10 companies; final test split not evaluated). Source: [threshold_ship_eval.md](../experiments/session07/threshold_ship_eval.md).

| | Old product (fixed 0.5) | New product, tuned on this split (optimistic) | New product, leave-one-company-out (honest estimate) |
|---|---:|---:|---:|
| Macro-F1 (8 categories) | 0.6333 | 0.7244 | 0.6768 |
| Micro-F1 (8 categories) | 0.6275 | 0.7254 | 0.6880 |
| Flags per 100 sentences (annotators: 10.95) | 17.49 | 10.51 | 11.03 |
| Wrong tags (flag the annotators did not give) | 195 | 62 | 79 |
| Missed labels (annotator label with no flag) | 46 | 72 | 77 |

The thresholds were chosen on the same validation split they are scored on, so the middle column overstates performance. The honest estimate is the leave-one-company-out column (thresholds chosen on 9 companies, applied to the 10th): macro-F1 0.6333 → 0.6768. Wrong tags fall by more than half (195 → 79), but missed labels rise (46 → 77).

**Same model as the product?** Yes. `artifacts/selected.joblib`, SHA-256 `dafbb5470f2fb2678cae273eac7c23046bbad0487c7be247174a99a08ad493bd`, is the model evaluated in `experiments/session07/tuned/metrics.json`, and every ClauseGuard trial this week ran it.

## What did not work

- Fewer wrong tags came with more missed clauses: under the honest estimate the new thresholds miss 77 annotator labels on the validation split, against 46 before. A sentence with no flag is not a safe sentence, and the app now shows fewer flags.
- This week's own change caused a miss in our study material: the F1 answer sentence (where you must go to court) scores 0.531 for Jurisdiction, which the old fixed 0.5 flagged and the new 0.55 threshold does not ([study_doc_check.json](../experiments/session07/study_doc_check.json)). 1 participant (U007) did F1 with ClauseGuard and answered correctly in 73.107 seconds using the Denver court sentence, even though the app did not flag it.
- Arbitration is still weak: under the honest estimate its precision is 0.286 and recall 0.444 on only 9 validation examples. Choice of law recall fell from 0.722 to 0.667.
- The mid-semester decision record (section 5 of the decision memo) and the lean canvas update were not merged before the October 6 deadline; they were merged on 2026-10-15 (#46). The decision itself (Persevere) was presented on October 6 and did not change.

## Challenges / blockers

Recruitment planned for 4 new outside participants, but only 2 came (U006 and U007). Coordinating the PR chain and waiting for dependent reviews (such as review queues for Niveda's study materials and evidence PRs) required careful timing before report finalization.

## Next week's goal

The one thing the team will do in Session 08 is investigate improving near-threshold visibility and unflagged sentence guidance.

## Individual contributions

- Ameer (Product): Finished the mid-semester decision PR and created the Session 07 milestone and issues. (evidence: [issue #30](https://github.com/Niveda-227/ClauseGuard/issues/30), [PR #46](https://github.com/Niveda-227/ClauseGuard/pull/46))
- Hemanth (Engineering): Shipped per-category thresholds into the product model. (evidence: [issue #41](https://github.com/Niveda-227/ClauseGuard/issues/41), [PR #47](https://github.com/Niveda-227/ClauseGuard/pull/47))
- Jayakrishna (Data&Eval): Evaluated threshold changes and ran the heading and short-fragment filter trial. (evidence: [issue #43](https://github.com/Niveda-227/ClauseGuard/issues/43), [PR #48](https://github.com/Niveda-227/ClauseGuard/pull/48))
- Niveda (Users&Research): Prepared new study documents E/F, task bank v3, and conducted outside user sessions with 2 new participants. (evidence: [issue #44](https://github.com/Niveda-227/ClauseGuard/issues/44), [PR #49](https://github.com/Niveda-227/ClauseGuard/pull/49), [PR #50](https://github.com/Niveda-227/ClauseGuard/pull/50))
- Ankan (Operations): Reviewed Niveda's PRs, finalized the Session 07 report, and cleaned up repository leftovers. (evidence: [issue #45](https://github.com/Niveda-227/ClauseGuard/issues/45), [PR #51](https://github.com/Niveda-227/ClauseGuard/pull/51))

## Lean canvas changes (if any)

No changes this week, because the mid-semester decision memo and lean canvas updates were already finalized and merged under PR #46.
