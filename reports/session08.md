---
team: ClauseGuard
session: "08"
date: "2026-10-27"
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

**Merged this week:** [PR #57](https://github.com/Niveda-227/ClauseGuard/pull/57), [PR #58](https://github.com/Niveda-227/ClauseGuard/pull/58), [PR #59](https://github.com/Niveda-227/ClauseGuard/pull/59), [PR #60](https://github.com/Niveda-227/ClauseGuard/pull/60), [PR #61](https://github.com/Niveda-227/ClauseGuard/pull/61). Every PR was approved by a teammate before merge; `main` requires one approving review.

* A web app. `python -m webapp` opens ClauseGuard in the browser on the user's own computer. It loads the same model file and calls the same analysis as the desktop app, listens only on 127.0.0.1, and loads nothing from the internet ([webapp/server.py](../webapp/server.py), [webapp/static/](../webapp/static/)). The desktop app still works.
* Review cues near a cut-off, planned in the mid-semester decision memo for this session. A flag whose score is less than 0.05 above its category's cut-off is marked "uncertain", and a category whose score is less than 0.05 below its cut-off is shown as "possible" instead of being hidden. Flags, scores and cut-offs did not change ([clauses/cues.py](../clauses/cues.py), [model card](../docs/MODEL_CARD.md)).
* What the cues show on the validation split, with a pass rule written before the first run: [cue_eval.md](../experiments/session08/cue_eval.md). Result: RECONSIDER the cue display in Session 09 (coverage failed, volume passed).
* The demo check now also starts the web app and confirms it returns exactly what the desktop app returns ([scripts/demo_check.py](../scripts/demo_check.py), [demo_check.json](../experiments/session08/demo_check.json)).
* An explanation check for the user sessions: after their timed tasks, participants match four category explanations, word for word as the app shows them, to example sentences ([clauses/explain_check.py](../clauses/explain_check.py), [cards](../examples/study/explain_check_v1.json)).
* A re-check of the mid-semester decision rule now that at least six participants have taken part ([decision_recheck_final.md](../experiments/session08/decision_recheck_final.md)).
* A demo run-sheet for presenting with the web app ([docs/DEMO_RUNSHEET_web.md](../docs/DEMO_RUNSHEET_web.md)).

The model running in the product did not change this week. It is still `dafbb5470f2fb2678cae273eac7c23046bbad0487c7be247174a99a08ad493bd`, the Session 04 hybrid model with per-category cut-offs shipped in Session 07. Only what users see changed: the web app and the review cues.

## User evidence

- **Raw artifact**: [task records](../evidence/session08/tasks.csv), [trial files and notes](../evidence/session08/), [summary](../evidence/session08/summary.json). Protocol `sep29_v2`.
- ClauseGuard: 3/3 ClauseGuard tasks correct within 180 seconds (100.00%), 3 outside participant(s), median 47.5 s.
- Manual comparison: 3/3 manual tasks correct within the limit (100.00%), median 66.9 s.
- On October 25, 2026, 3 new outside participants (U008, U009, U010), who were classmates of the observer and were recruited in person, completed user study trials. None were members of the core team or participants in prior sessions. Each participant completed one task using a plain text editor and one using ClauseGuard running in the web app (python -m webapp).
- 1 participant (U009) did task F1 with the web app and answered correctly in 66.302 seconds. The observer reported that U009 noticed the "Possible: Jurisdiction" tag or the dashed underline, but no specific action or quote was recorded to confirm how they used the cue.
- 2 participants (U008 and U010) completed task E1 using the web app, and both answered correctly. U008 read the list text before clicking and used the Unilateral change filter chip, while U010 scanned the findings, read category labels, and verified the source sentence in the document before answering.
- Result: RECONSIDER the cue display in Session 09. Cues appeared at a rate of 1.05 per 100 sentences and pointed to 7.8% (6 of 77) of missed labels on the validation split, falling short of the pre-set 10% coverage target. However, uncertain flags proved to be a strong signal, being wrong 53.6% of the time compared to 28.7% for standard flags.
- Resulting change or next action: RECONSIDER the cue display in Session 09 (evidence: [issue #52](https://github.com/Niveda-227/ClauseGuard/issues/52), [PR #60](https://github.com/Niveda-227/ClauseGuard/pull/60), [PR #61](https://github.com/Niveda-227/ClauseGuard/pull/61))
- This is a small pilot on short fictional documents, not a population estimate or a check of legal correctness.

## Metrics snapshot

**Product north-star:** 100.00% this week; previous 100.00%.

The previous value is Session 07 (two ClauseGuard trials, tasks E1 and F1, desktop app). This week uses the same tasks with new participants, the same model, and the web app with review cues. 100.00% of participants successfully identified the target clause within the 180-second limit using the web app (3 of 3 correct).

**Re-check of the mid-semester rule** ([decision_recheck_final.md](../experiments/session08/decision_recheck_final.md)): KEEP THE PRODUCT DIRECTION. Re-checking the mid-semester decision rule across Sessions 05–08 shows that all four conditions were met: the model gate passed (+0.4217 gain over baseline), 6 outside participants were included, ClauseGuard outperformed manual success by 16.67 percentage points (100.0% vs 83.33%), and 0 participants were misled by wrong tags.

**Model development results** (validation split, 2,275 sentences, 10 companies; final test split not evaluated). The model did not change this week, so these are the Session 07 numbers. Source: [threshold_ship_eval.md](../experiments/session07/threshold_ship_eval.md).

| | Fixed 0.5 (before Session 07) | Product cut-offs, tuned on this split (optimistic) | Product cut-offs, leave-one-company-out (honest estimate) |
|---|---:|---:|---:|
| Macro-F1 (8 categories) | 0.6333 | 0.7244 | 0.6768 |
| Micro-F1 (8 categories) | 0.6275 | 0.7254 | 0.6880 |
| Flags per 100 sentences (annotators: 10.95) | 17.49 | 10.51 | 11.03 |
| Wrong tags (flag the annotators did not give) | 195 | 62 | 79 |
| Missed labels (annotator label with no flag) | 46 | 72 | 77 |

**Review cues on the validation split** (honest column, margin 0.05). Source: [cue_eval.md](../experiments/session08/cue_eval.md).

| | Value |
|---|---:|
| Possible cues per 100 sentences | 1.05 |
| Missed labels with a possible cue | 6 of 77 (7.8%) |
| Wrong share of uncertain flags | 53.6% |
| Wrong share of the other flags | 28.7% |

**Same model as the product?** Yes. `artifacts/selected.joblib`, SHA-256 `dafbb5470f2fb2678cae273eac7c23046bbad0487c7be247174a99a08ad493bd`, is the model evaluated in `experiments/session07/tuned/metrics.json`; every ClauseGuard trial this week ran it, and the demo check confirms the web app returns exactly what the desktop app returns.

## What did not work

- The "possible" cue rarely points to a missed clause. Under the honest estimate it marks only 6 of the 77 annotator labels that get no flag, below the 10% the pre-set rule required, so by that rule the cue display must be reconsidered in Session 09. The "uncertain" marking did carry information: those flags were wrong 53.6% of the time against 28.7% for the other flags.
- One participant (U009) attempted task F1 with the web app and answered correctly in 66.302 seconds, but the observer's notes could not confirm whether the "Possible: Jurisdiction" cue directly aided their search or if they checked the Delaware governing-law sentence first.
- Four new outside participants were planned for Session 08, but only three came (U008, U009, U010).

## Challenges / blockers

Recruitment fell short of the four planned participants, yielding three outside participants for Session 08. Additionally, observational recording in the session notes contained minor inconsistencies that required marking certain participant actions as unconfirmed, and report drafting remained tightly sequenced behind the sequential PR reviews and merges.

## Next week's goal

For Session09, re-evaluate and refine the review cue display mechanism based on validation coverage results.

## Individual contributions

- Ameer (Product): Built and shipped the ClauseGuard web app interface running locally in the browser. (evidence: [issue #53](https://github.com/Niveda-227/ClauseGuard/issues/53), [PR #57](https://github.com/Niveda-227/ClauseGuard/pull/57))
- Hemanth (Engineering): Implemented review cues near decision cut-offs across the engine, desktop app, and web app. (evidence: [issue #52](https://github.com/Niveda-227/ClauseGuard/issues/52), [PR #58](https://github.com/Niveda-227/ClauseGuard/pull/58))
- Jayakrishna (Data&Eval): Evaluated review cues on the validation split and conducted the mid-semester decision rule re-check. (evidence: [issue #54](https://github.com/Niveda-227/ClauseGuard/issues/54), [PR #59](https://github.com/Niveda-227/ClauseGuard/pull/59))
- Niveda (Users&Research): Conducted explanation checks and managed user study trials with three outside participants on the web app. (evidence: [issue #55](https://github.com/Niveda-227/ClauseGuard/issues/55), [PR #61](https://github.com/Niveda-227/ClauseGuard/pull/61))
- Ankan (Operations): Finalized the Session 08 report, ran the final mid-semester decision re-check, and prepared the web demo run-sheet. (evidence: [issue #56](https://github.com/Niveda-227/ClauseGuard/issues/56), [PR #62](https://github.com/Niveda-227/ClauseGuard/pull/62))

## Lean canvas changes (if any)

No changes were made to the Lean Canvas [docs/lean_canvas.md](../docs/lean_canvas.md) this week. The current evidence section remains as updated on 2026-10-06 with the Session 06 user study results and the mid-semester decision to persevere, as no structural changes to the target user, value proposition, or risk model were required following the Session 08 web app deployment and review cue evaluation.
