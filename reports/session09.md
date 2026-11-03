---
team: ClauseGuard
session: "09"
date: "2026-11-03"
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

**Merged this week:** [PR #68](https://github.com/Niveda-227/ClauseGuard/pull/68), [PR #69](https://github.com/Niveda-227/ClauseGuard/pull/69), [PR #70](https://github.com/Niveda-227/ClauseGuard/pull/70), [PR #71](https://github.com/Niveda-227/ClauseGuard/pull/71), [PR #72](https://github.com/Niveda-227/ClauseGuard/pull/72). Every PR was approved by a teammate before merge; `main` requires one approving review.

This week's question, from the mid-semester decision memo: does "no flags" read as "safe"? When the model misses a clause, the user sees nothing at all.

* A "Check it yourself" panel in the web app and in the downloaded HTML report. For each of the eight categories it shows how many sentences were flagged and, under "Not flagged, but worth a look", the unflagged sentences that contain one of that category's search words, each one click away from its place in the document. When a category has no flag, it says so plainly: "No sentence was flagged for this category. That does not mean the document has none." The panel is labelled as word matches, not model predictions, and it changes no flag, score or cut-off ([clauses/absence.py](../clauses/absence.py), [webapp/static/](../webapp/static/), [clauses/export.py](../clauses/export.py)). The search words were written from the category definitions before any validation run.
* A decision on the Session 08 review cues: keep "uncertain"; keep "possible" but stop presenting it as the way to find missed clauses; test a wider cue margin only on fresh hand-labelled documents ([docs/decisions/2026-10-28_cue_decision.md](../docs/decisions/2026-10-28_cue_decision.md)). The same memo set the rule for the search words before they were measured.
* What the search words reach on the validation split, with that pre-set rule: [hint_eval.md](../experiments/session09/hint_eval.md). Result: RECONSIDER the worth-a-look list in Session 10.
* The cost of one request to the web app, measured on the real request path: [cost_per_request.md](../experiments/session09/cost_per_request.md) ([scripts/cost_per_request.py](../scripts/cost_per_request.py)).
* A check that every number in this report comes from a source file ([scripts/check_report_numbers.py](../scripts/check_report_numbers.py)). The report finalizer now fills numbers straight from the result files ([scripts/finalize_report.py](../scripts/finalize_report.py)), and the interim Session 08 re-check is marked superseded ([decision_recheck.md](../experiments/session08/decision_recheck.md)).
* Study materials for two absence tasks: documents G and H, the task bank, and a study check that handles an answer that is absent from the document ([tasks_v4.json](../examples/study/tasks_v4.json), [scripts/check_study_docs.py](../scripts/check_study_docs.py), [study_doc_check.json](../experiments/session09/study_doc_check.json)).

The model running in the product did not change this week. It is still `dafbb5470f2fb2678cae273eac7c23046bbad0487c7be247174a99a08ad493bd`, the hybrid model with per-category cut-offs shipped in Session 07.

## User evidence

- **Raw artifact**: [task records](../evidence/session09/tasks.csv), [trial files and notes](../evidence/session09/), [summary](../evidence/session09/summary.json). Protocol `sep29_v2`.
- ClauseGuard: 2/2 ClauseGuard tasks correct within 180 seconds (100.00%), 2 outside participant(s), median 59.5 s.
- Manual comparison: 2/2 manual tasks correct within the limit (100.00%), median 61.1 s.
- Participants: U012, U013. Sessions were held in person on 2026-11-02. The participants were new outside participants who were classmates of the observer, recruited in person by the observer, and were neither on the team nor took part in Sessions 04 to 08.
- The two tasks. **G1** asks whether the company can remove your photos without telling you first. The answer sentence is in document G, but the model does not flag it (Content removal score 0.29, cut-off 0.80) and shows no "possible" cue; the "Check it yourself" panel lists it as worth a look. **H1** asks which courts you would have to use in a dispute. Document H has no such sentence: the correct answer is "there is none". The app flags no sentence for Jurisdiction and lists none as worth a look; the sentence that names Minnesota law is flagged as Choice of law, and giving it as the answer counts as wrong.

| Participant | Task | Condition | Interface | Correct within the limit | Seconds |
|---|---|---|---|---|---:|
| U012 | G1 | ClauseGuard | web | yes | 63.822 |
| U012 | H1 | manual | text_editor | yes | 83.948 |
| U013 | H1 | ClauseGuard | web | yes | 55.189 |
| U013 | G1 | manual | text_editor | yes | 38.342 |

- G1 with the web app: Reviewed the app's findings, inspected the relevant sentence, and answered that the company can take down photos without telling first.
- H1 with the web app: Reviewed the app's results, looked at the Minnesota sentence first, and stated that the document does not specify which courts handle legal disputes.
- Manual trials: For task H1, the participant searched the document using Ctrl+F for courts and Minnesota and concluded that no court-location sentence was present. For task G1, the participant searched using Ctrl+F for photos, located the photo-removal sentence, and answered that the company can take down photos and albums without notifying first.
- Resulting change or next action: test the "Check it yourself" panel and the hint rule on fresh hand-labelled documents in Session 10 (evidence: [issue #63](https://github.com/Niveda-227/ClauseGuard/issues/63), [PR #68](https://github.com/Niveda-227/ClauseGuard/pull/68), [PR #72](https://github.com/Niveda-227/ClauseGuard/pull/72)).
- This is a small pilot on short fictional documents, not a population estimate or a check of legal correctness.

## Metrics snapshot

**Product north-star:** 100.00% this week; previous 100.00%.

The previous value is Session 08 (tasks E1 and F1, web app). This week's tasks are the absence tasks G1 and H1 on the new documents G and H, so the two values are not directly comparable. For H1 the correct answer is that the document has no such sentence.

**Do the search words reach the clauses the model misses?** (validation split, 2275 sentences; test split not read). Source: [hint_eval.md](../experiments/session09/hint_eval.md). A "mark" is a sentence that is not flagged for a category but contains one of its search words; a "missed label" is an annotator label with no flag.

| | Product cut-offs (optimistic) | Leave-one-company-out (honest) |
|---|---:|---:|
| Missed labels | 72 | 77 |
| Marks | 727 | 720 |
| Marks per 100 sentences | 31.96 | 31.65 |
| Missed labels with a mark | 34 (47.2%) | 39 (50.6%) |
| Marks that are annotator labels | 4.7% | 5.4% |

Rule set before the first run: keep the list if, in the honest column, the marks reach at least 40% of the missed labels and add at most 20 marks per 100 sentences. **Result: RECONSIDER the worth-a-look list in Session 10** (coverage passed, volume failed). For comparison, in Session 08 the "possible" cue reached 6 of the 77 missed labels ([cue_eval.md](../experiments/session08/cue_eval.md)). UNFAIR-ToS labels only potentially unfair clauses, so many marks fall on sentences that are on topic but fair.

**Cost per request** of the web app, measured on macOS with real HTTP requests to `/api/analyze`, one at a time. Source: [cost_per_request.md](../experiments/session09/cost_per_request.md).

| Document | Sentences | Median | 95th percentile | CPU per request |
|---|---:|---:|---:|---:|
| Study document F | 16 | 4.4 ms | 4.9 ms | 3.7 ms |
| Long document (the example, repeated) | 1100 | 140.6 ms | 154.3 ms | 139.2 ms |

Peak memory 143.0 MB. The app makes no network calls outside the computer and calls no API, so each request costs us $0.00; the real costs are the user's own computer and their setup time. If it were hosted on one small server (DigitalOcean Basic Droplet, Regular: 1 GiB memory, 1 vCPU, $0.00893 per hour, from the provider's pricing page, looked up 2026-10-31), answering one request at a time, a million requests on the study document would cost $0.0109. An always-on server is billed by the hour whatever the traffic, so at low traffic the hourly price is what matters.

**Model development results** (validation split, 2275 sentences, 10 companies; final test split not evaluated). The model did not change this week, so these are the Session 07 numbers. Source: [threshold_ship_eval.md](../experiments/session07/threshold_ship_eval.md).

| | Fixed 0.5 (before Session 07) | Product cut-offs, tuned on this split (optimistic) | Product cut-offs, leave-one-company-out (honest estimate) |
|---|---:|---:|---:|
| Macro-F1 (8 categories) | 0.6333 | 0.7244 | 0.6768 |
| Micro-F1 (8 categories) | 0.6275 | 0.7254 | 0.6880 |
| Flags per 100 sentences (annotators: 10.95) | 17.49 | 10.51 | 11.03 |
| Wrong tags (flag the annotators did not give) | 195 | 62 | 79 |
| Missed labels (annotator label with no flag) | 46 | 72 | 77 |

**Same model as the product?** Yes. `artifacts/selected.joblib`, SHA-256 `dafbb5470f2fb2678cae273eac7c23046bbad0487c7be247174a99a08ad493bd`, is the model evaluated in `experiments/session07/tuned/metrics.json`; every ClauseGuard trial this week ran it, and the cost measurement ran it through the web app.

## What did not work

- **The search words mark too many sentences.** By the rule set before the first run, the result is RECONSIDER the worth-a-look list in Session 10: coverage passed, volume failed. In the honest column the marks add 31.65 per 100 sentences against a limit of 20, and 5.4% of the marks are annotator labels. The panel stays collapsed per category so the extra sentences do not crowd the results list, and the words are not edited to change this result.
- **Wrong absence answers:** No wrong answers were recorded this week.
- **Recruitment:** Booked 3; came 3.
- **Correction to the Session 08 report.** Its "Metrics snapshot" re-check paragraph said 6 outside participants and a gap of 16.67 percentage points (100.0% vs 83.33%). Those were the interim numbers for Sessions 05 to 07 ([decision_recheck.md](../experiments/session08/decision_recheck.md), now marked superseded). The final re-check over Sessions 05 to 08, which that paragraph linked to, found 9 participants (U002 to U010), ClauseGuard 9/9 and manual 8/9 (100.0% vs 88.89%), a gap of 11.11 points, and 0 participants misled by wrong tags ([decision_recheck_final.md](../experiments/session08/decision_recheck_final.md)). The outcome, KEEP THE PRODUCT DIRECTION, is the same. The same report also left PR [#60](https://github.com/Niveda-227/ClauseGuard/pull/60) (Niveda's explanation check) out of her contribution line, and its "Next week's goal" was vague ("Session09"). The lean canvas was not updated either; it is updated this week (last section).

## Challenges / blockers

Scheduling and participant management required careful coordination, including excluding the first participant because a saved trial record did not match its task. The Session 08 report was merged with interim numbers because no script checked numbers written in sentences. From this week, every number in the report is filled from its source file by the finalizer and checked by `scripts/check_report_numbers.py` before the PR is opened, and every teammate's commits use an email address linked to their GitHub account.

## Next week's goal

Session 10: hand-label a small set of fresh Terms of Service documents that the model has never seen, and use them to check the model and the "Check it yourself" list outside the validation split. On those documents, and not on validation, test the two ideas that came out of this week: a wider cue margin of 0.10, and showing worth-a-look marks only for categories with no flag in the document.

## Individual contributions

- Ameer (Product): Added the "Check it yourself" panel (not flagged, but worth a look) to the web app and the HTML export, and recorded the review-cue decision with the pre-set rule for the search words. (evidence: [issue #63](https://github.com/Niveda-227/ClauseGuard/issues/63), [PR #68](https://github.com/Niveda-227/ClauseGuard/pull/68))
- Hemanth (Engineering): Measured the cost per request of the web app on the real request path, and added the report number check and source-file number tokens to the report finalizer. (evidence: [issue #64](https://github.com/Niveda-227/ClauseGuard/issues/64), [PR #69](https://github.com/Niveda-227/ClauseGuard/pull/69))
- Jayakrishna (Data&Eval): Measured on the validation split whether the search words reach the clauses the model misses, under the pre-set rule, and marked the interim Session 08 re-check as superseded. (evidence: [issue #65](https://github.com/Niveda-227/ClauseGuard/issues/65), [PR #70](https://github.com/Niveda-227/ClauseGuard/pull/70))
- Niveda (Users&Research): Prepared the absence tasks G1 and H1 (documents G and H, study check for an absent answer) and ran the Session 09 study with new outside participants on the web app. (evidence: [issue #66](https://github.com/Niveda-227/ClauseGuard/issues/66), [PR #71](https://github.com/Niveda-227/ClauseGuard/pull/71), [PR #72](https://github.com/Niveda-227/ClauseGuard/pull/72))
- Ankan (Operations): Wrote the Session 09 report with every number filled from its source file, corrected the Session 08 report, and updated the lean canvas and the web demo run-sheet. (evidence: [issue #67](https://github.com/Niveda-227/ClauseGuard/issues/67), [PR #73](https://github.com/Niveda-227/ClauseGuard/pull/73))

## Lean canvas changes (if any)

Updated [docs/lean_canvas.md](../docs/lean_canvas.md), which the Session 08 report left unchanged. "Current evidence" still described Session 06 (4 participants, macro-F1 0.6333 for the model shipped before Session 07). It now gives the shipped model's honest macro-F1 (0.6768) and the final mid-semester re-check (9 participants, Sessions 05 to 08). "Cost" now points to the measured cost per request. The target user, value proposition and biggest risk did not change.
