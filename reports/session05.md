---
team: ClauseGuard
session: "05"
date: "2026-09-29"
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
  previous: 0.00
---

## Shipped this week

**Merged this week:** [PR #23](https://github.com/Niveda-227/ClauseGuard/pull/23), [PR #24](https://github.com/Niveda-227/ClauseGuard/pull/24), [PR #25](https://github.com/Niveda-227/ClauseGuard/pull/25), [PR #26](https://github.com/Niveda-227/ClauseGuard/pull/26), [PR #27](https://github.com/Niveda-227/ClauseGuard/pull/27). Every PR was approved by a teammate before merge; `main` requires one approving review.

* Updated the study procedure to [session protocol v2](../clauses/session_v2.py), stopping the clock before answer entry and restating the prompt before timing starts.
* Resolved the stale detail-panel bug in the desktop application to ensure correct UI rendering during clause navigation.
* Conducted a [leave-one-company-out threshold experiment](../experiments/session05/threshold_cv.md) to test per-category threshold tuning across document splits.
* Created study documents C and D along with a private answer key for user evaluation sessions.
* Completed full [repository cleanup](../data/README.md) by restoring lost dataset provenance files, retiring the public answer key, and purging stale one-off files while maintaining valid report links.
* Implemented a reusable report finalizer script to automate report generation and json metadata updates.

The model running in the product is unchanged this week: `04713fbf6e23784a5d32e5cdd5fef459182408565bfe8a4fb6a9f10d53dbff76`.

## User evidence

- On September 28, 2026, two outside participants (U002 and U003) completed tasks C1, C2, D1, and D2 using the ClauseGuard desktop application and manual workflow.
- **Raw artifact**: [task records](../evidence/session05/tasks.csv), [trial files and notes](../evidence/session05/), [summary](../evidence/session05/summary.json). Protocol `sep29_v2`.
- ClauseGuard: 1/1 ClauseGuard tasks correct within 180 seconds (100.00%), 1 outside participant(s), median 51.8 s.
- Manual comparison: 1/1 manual tasks correct within the limit (100.00%), median 87.0 s.
- On 2026-09-29 one outside participant (U002) did task C1 without the app in a plain text editor, then task D1 with the ClauseGuard desktop app, under protocol sep29_v2.
- In the manual trial the participant needed the task read twice before restating it correctly. The new v2 restatement check caught this before the clock started; under the Session 04 protocol it would have gone unnoticed. In the ClauseGuard trial they selected the result tagged "Limitation of liability", read the highlighted sentence and answered correctly; the notes say they relied on the tag to find the clause.
- ⁠Resulting change or next action: opened #29 to test in Session 07 whether over-tagged sentences mislead users, because task C1 (the over-tagged one) has not yet been done with the app. (evidence: [issue #29](https://github.com/Niveda-227/ClauseGuard/issues/29))
- This is a small pilot on short fictional documents, not a population estimate or a check of legal correctness.

## Metrics snapshot

**Product north-star:** 100.00% this week; previous 0.00%.

Session 04 used protocol sep22_v1, whose clock included the observer typing the answer and whose task was not confirmed; this week uses sep29_v2, which fixes both. The two numbers are therefore not a like-for-like comparison. This week's 100.00% is a single ClauseGuard trial (1/1), so it is not a meaningful success rate; the manual trial was also correct.

**Model development results** (validation split, 2,275 sentences, 10 companies; final test split not evaluated):

| Decision rule | Macro-F1 (8) | Micro-F1 (8) | Source |
|---|---:|---:|---|
| Fixed 0.5, current product | 0.6333 | 0.6275 | [threshold_cv.md](../experiments/session05/threshold_cv.md) |
| Per-category thresholds, tuned and scored on the same data (optimistic) | 0.7244 | 0.7254 | [threshold_cv.md](../experiments/session05/threshold_cv.md) |
| Per-category thresholds, leave-one-company-out (honest estimate) | 0.6768 | 0.6880 | [threshold_cv.md](../experiments/session05/threshold_cv.md) |

About 48% of the in-sample gain survives leave-one-company-out: macro-F1 0.6333 (fixed 0.5) → 0.6768 (honest), against 0.7244 optimistic. Flags per 100 sentences fall from 17.49 to 11.03, so users would see fewer wrong tags. Against the decision rule Jayakrishna wrote before running the experiment, all three conditions hold (macro-F1 gain 0.0435 ≥ 0.02; the worst category change is Choice of law, −0.038, within the 0.05 limit; flags fell rather than rose), so the team will ship per-category thresholds in Session 07. Arbitration's tuned threshold ranges from 0.35 to 0.90 across folds on only 9 positive examples, so its result should not be trusted. Details: [Jayakrishna's notes](../experiments/session05/jayakrishna_session05_notes.md).

**Same model as the product?** Yes. `artifacts/selected.joblib`, SHA-256 `04713fbf6e23784a5d32e5cdd5fef459182408565bfe8a4fb6a9f10d53dbff76`. The threshold experiment did not change the shipped model.

## What did not work

- ⁠Only one outside participant took part (target was 2-4), so this week's north-star (1/1) says very little about the product.
- ⁠The Session 04 question, whether over-tagged sentences mislead users, could not be tested: the only participant did C1, the over-tagged task, without the app. Queued as #29.
- Tuned thresholds made one category worse: Choice of law F1 fell from 0.812 to 0.774 under leave-one-company-out, within the pre-set tolerance but a real loss to track in Session 07.
- Session 04's product metric (0.00%) was not interpretable as product performance because of the timing and prompt-confirmation problems fixed this week ([issue #14](https://github.com/Niveda-227/ClauseGuard/issues/14)).

## Challenges / blockers

Participant recruitment remains tight with only 1 outside participant joining this week's pilot. Niveda is coordinating outreach to expand the testing pool for upcoming sessions. Additional pipeline refinements are required to handle multi-label confidence calibration without confusing end users.

## Next week's goal

Mid-semester presentation on October 6: demonstrate the running product, show this week's user evidence and the threshold experiment against the fixed-threshold baseline, and state a pivot-or-persevere decision backed by that evidence.

## Individual contributions

- Ameer (Product): Restored the dataset provenance/license file and two other READMEs lost in Session 04, retired the public A1/B1 answer key and removed seven one-off files while keeping every Session 04 report link valid. (evidence: [issue #18](https://github.com/Niveda-227/ClauseGuard/issues/18), [PR #23](https://github.com/Niveda-227/ClauseGuard/pull/23))
- Hemanth (Engineering): Implemented protocol v2 timing changes and fixed the stale detail-panel bug in the application. (evidence: [issue #14](https://github.com/Niveda-227/ClauseGuard/issues/14), [PR #24](https://github.com/Niveda-227/ClauseGuard/pull/24))
- Jayakrishna (Data&Eval): Executed leave-one-company-out threshold cross-validation and documented classification metric gains. (evidence: [issue #19](https://github.com/Niveda-227/ClauseGuard/issues/19), [PR #25](https://github.com/Niveda-227/ClauseGuard/pull/25))
- Niveda (Users&Research): Created study documents C/D and conducted Session 05 user pilot testing sessions. (evidence: [issue #20](https://github.com/Niveda-227/ClauseGuard/issues/20), [issue #21](https://github.com/Niveda-227/ClauseGuard/issues/21), [PR #26](https://github.com/Niveda-227/ClauseGuard/pull/26), [PR #27](https://github.com/Niveda-227/ClauseGuard/pull/27))
- Ankan (Operations): Built report finalizer tooling and compiled Session 05 final submission materials. (evidence: [issue #22](https://github.com/Niveda-227/ClauseGuard/issues/22), [PR #28](https://github.com/Niveda-227/ClauseGuard/pull/28))

## Lean canvas changes (if any)

Updated `docs/lean_canvas.md` to incorporate current evidence from the Session 04 pilot, explicitly listing the risk of model over-tagging and noting that no formal usable product measurement exists yet.
