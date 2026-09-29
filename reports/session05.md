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
- On task C1, where the answer sentence carries two extra category tags, U003 read all three tags aloud as facts before opening the source text.
- Resulting change or next action: Logged user-driven issue [#21](https://github.com/Niveda-227/ClauseGuard/issues/21) to address sentence over-tagging during task C1. (evidence: [issue #21](https://github.com/Niveda-227/ClauseGuard/issues/21))
- This is a small pilot on short fictional documents, not a population estimate or a check of legal correctness.

## Metrics snapshot

**Product north-star:** 100.00% this week; previous 0.00%.

Session 04 used protocol sep22_v1, whose clock included the observer typing the answer and whose task prompt was not confirmed. This week uses sep29_v2, which fixes both timing stops and prompt restatements. Consequently, the two numbers are not a direct like-for-like comparison, but the updated protocol provides a substantially more accurate measure of true user completion speed.

**Model development results** (validation split, 2,275 sentences, 10 companies; final test split not evaluated):

| Decision rule | Macro-F1 (8) | Micro-F1 (8) | Source |
|---|---:|---:|---|
| Fixed 0.5, current product | 0.712 | 0.784 | [threshold_cv.md](../experiments/session05/threshold_cv.md) |
| Per-category thresholds, tuned and scored on the same data (optimistic) | 0.758 | 0.812 | [threshold_cv.md](../experiments/session05/threshold_cv.md) |
| Per-category thresholds, leave-one-company-out (honest estimate) | 0.729 | 0.793 | [threshold_cv.md](../experiments/session05/threshold_cv.md) |

While optimistic in-sample tuning showed a strong F1 boost, leave-one-company-out validation demonstrates that only modest gains survive when generalizing to unseen document structures. Minor improvements were observed across most categories, but low-frequency classes remain volatile, leading the team to hold off on shipping tuned thresholds until further validation in Session 07.

**Same model as the product?** Yes. `artifacts/selected.joblib`, SHA-256 `04713fbf6e23784a5d32e5cdd5fef459182408565bfe8a4fb6a9f10d53dbff76`. The threshold experiment did not change the shipped model.

## What did not work

- Participants experienced confusion during task C1 due to over-tagging, where sentences assigned multiple redundant categories slowed down verification.
- Small sample size constraints (2 participants) limit statistical confidence across document conditions.
- Session 04's product metric (0.00%) was not interpretable as product performance because of the timing and prompt-confirmation problems fixed this week ([issue #14](https://github.com/Niveda-227/ClauseGuard/issues/14)).

## Challenges / blockers

Participant recruitment remains tight with only 2 outside participants joining this week's pilot. Niveda is coordinating outreach to expand the testing pool for upcoming sessions. Additional pipeline refinements are required to handle multi-label confidence calibration without confusing end users.

## Next week's goal

Mid-semester presentation on October 6: demonstrate the running product, show this week's user evidence and the threshold experiment against the fixed-threshold baseline, and state a pivot-or-persevere decision backed by that evidence.

## Individual contributions

- Ameer (Product): Restored the dataset provenance/license file and two other READMEs lost in Session 04, retired the public A1/B1 answer key and removed six one-off files while keeping every Session 04 report link valid. (evidence: [issue #18](https://github.com/Niveda-227/ClauseGuard/issues/18), [PR #23](https://github.com/Niveda-227/ClauseGuard/pull/23))
- Hemanth (Engineering): Implemented protocol v2 timing changes and fixed the stale detail-panel bug in the application. (evidence: [issue #14](https://github.com/Niveda-227/ClauseGuard/issues/14), [PR #24](https://github.com/Niveda-227/ClauseGuard/pull/24))
- Jayakrishna (Data&Eval): Executed leave-one-company-out threshold cross-validation and documented classification metric gains. (evidence: [issue #19](https://github.com/Niveda-227/ClauseGuard/issues/19), [PR #25](https://github.com/Niveda-227/ClauseGuard/pull/25))
- Niveda (Users&Research): Created study documents C/D and conducted Session 05 user pilot testing sessions. (evidence: [issue #20](https://github.com/Niveda-227/ClauseGuard/issues/20), [issue #21](https://github.com/Niveda-227/ClauseGuard/issues/21), [PR #26](https://github.com/Niveda-227/ClauseGuard/pull/26), [PR #27](https://github.com/Niveda-227/ClauseGuard/pull/27))
- Ankan (Operations): Built report finalizer tooling and compiled Session 05 final submission materials. (evidence: [issue #22](https://github.com/Niveda-227/ClauseGuard/issues/22), [PR #28](https://github.com/Niveda-227/ClauseGuard/pull/28))

## Lean canvas changes (if any)

Updated `docs/lean_canvas.md` to incorporate current evidence from the Session 04/05 pilots, explicitly listing the risk of model over-tagging and noting that no formal usable product measurement exists yet.
