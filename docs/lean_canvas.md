# ClauseGuard lean canvas

Initial hypotheses September 10, 2026; revised September 24, 2026 after the Session 04 pilot; evidence and cost updated for the Session 09 report. Revisit every report.

| Area | Hypothesis / measurement plan |
|---|---|
| User | English-reading students/app users who need to locate clauses in a long ToS |
| Problem | Finding relevant passages by reading everything or keyword search takes effort |
| Alternatives | Manual reading, browser find, published ToS summaries and generic assistants; research actual alternatives before claiming an advantage |
| Value proposition | Help users find important contractual categories with original-text evidence and reviewed category explanations |
| Distribution | Working local app/HTML workflow shared with classmates and student groups; optional later hosting |
| Cost | Local CPU inference on the user's own computer: no API calls, so no cost to us per request; the real costs are the user's computer and setup time. Measured cost per request of the web app, with a hosted estimate from a looked-up price: experiments/session09/cost_per_request.md (Session 09) |
| North-star | Correct completion of assigned clause-finding tasks within 180 seconds |
| Ethics/privacy | Data rights, European annotation context, false positives/negatives, no-input-storage default, user-consented exports |
| Biggest risk | Validation performance does not translate into useful decisions on unfamiliar documents; and because six of eight categories have precision below 0.60, users may trust confident wrong tags instead of reading the source sentence. |
| Cheapest early test | Outside user attempts a defined task in the working app on a permitted unfamiliar document |
| Current evidence | Shipped model (per-category cut-offs, Session 07): honest leave-one-company-out validation macro-F1 0.6768 vs 0.2551 unigram baseline; test split untouched. Outside users (protocol sep29_v2, Sessions 05-08): 9 participants (U002-U010); ClauseGuard 9/9 correct within 180 s vs manual 8/9 (experiments/session08/decision_recheck_final.md). Mid-semester decision: Persevere (docs/decisions/2026-10-06_midpoint_decision.md), re-checked in Session 08: keep the product direction. Session 09 absence tasks (does "no flags" read as "safe"?): reports/session09.md. |

The company is a course simulation; no incorporation, revenue, payment collection or equity arrangement is required.

## Change log

- 2026-09-24: Current evidence and biggest risk updated from the Session 04 pilot and error analysis. The over-tagging risk was added because the model assigns several categories to single sentences.
- 2026-10-06: Current evidence updated with the Session 06 outside-user results (4 participants) and the mid-semester decision to persevere.
- Session 09 report (due 2026-11-03): Current evidence updated to the shipped model's honest macro-F1 and the final Sessions 05-08 re-check (9 participants); this update was missed in the Session 08 report. Cost now points to the Session 09 cost-per-request measurement.
