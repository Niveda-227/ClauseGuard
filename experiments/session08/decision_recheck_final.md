# Re-check of the mid-semester decision rule (Session 08)

Rule: docs/decisions/2026-10-06_midpoint_decision.md, section 5 ("What would change our mind"). Protocol `sep29_v2` trials only.

| Condition | Value | Needed | Met |
|---|---|---|---|
| Model gate: honest macro-F1 gain over baseline, app runs the evaluated model | 0.6768 vs 0.2551 (+0.4217); same model: True | +0.10 and same model | yes |
| Outside participants | 9 (U002, U003, U004, U005, U006, U007, U008, U009, U010) | at least 6 | yes |
| ClauseGuard success minus manual success | 100.0% - 88.89% = 11.11 points | not more than 25 points below | yes |
| Participants misled by wrong tags (from: evidence/session05 to session08 session_notes.md) | 0 | 0 | yes |

**Outcome: KEEP THE PRODUCT DIRECTION**

| Session | Participants | ClauseGuard | Manual | ClauseGuard model |
|---|---|---:|---:|---|
| 05 | U002 | 1/1 | 1/1 | 04713fbf6e23 |
| 06 | U003, U004, U005 | 3/3 | 3/3 | 04713fbf6e23 |
| 07 | U006, U007 | 2/2 | 1/2 | dafbb5470f2f |
| 08 | U008, U009, U010 | 3/3 | 3/3 | dafbb5470f2f |

Median seconds (reported, not deciding): ClauseGuard 51.79, manual 72.84.

A pre-committed decision heuristic, not a statistical test. Speed is reported but does not decide. Tasks differ in difficulty between sessions; pooled rates mix tasks and product versions.
