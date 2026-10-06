# ClauseGuard lean canvas

Initial hypotheses September 10, 2026; revised September 24, 2026 after the Session 04 pilot. Revisit every report.

| Area | Hypothesis / measurement plan |
|---|---|
| User | English-reading students/app users who need to locate clauses in a long ToS |
| Problem | Finding relevant passages by reading everything or keyword search takes effort |
| Alternatives | Manual reading, browser find, published ToS summaries and generic assistants; research actual alternatives before claiming an advantage |
| Value proposition | Help users find important contractual categories with original-text evidence and reviewed category explanations |
| Distribution | Working local app/HTML workflow shared with classmates and student groups; optional later hosting |
| Cost | Local CPU inference, user setup time and potential hosting; record actual request latency and actual money spent |
| North-star | Correct completion of assigned clause-finding tasks within 180 seconds |
| Ethics/privacy | Data rights, European annotation context, false positives/negatives, no-input-storage default, user-consented exports |
| Biggest risk | Validation performance does not translate into useful decisions on unfamiliar documents; and because six of eight categories have precision below 0.60, users may trust confident wrong tags instead of reading the source sentence. |
| Cheapest early test | Outside user attempts a defined task in the working app on a permitted unfamiliar document |
| Current evidence | Validation macro-F1 0.6333 (shipped hybrid) vs 0.2551 unigram baseline, test split untouched. Outside users (protocol sep29_v2, Sessions 05-06): 4 participants; ClauseGuard 4/4 correct within 180 s vs manual 4/4; over-tagged task C1 with the app 2/2. Mid-semester decision: Persevere (docs/decisions/2026-10-06_midpoint_decision.md). |

The company is a course simulation; no incorporation, revenue, payment collection or equity arrangement is required.

## Change log

- 2026-09-24: Current evidence and biggest risk updated from the Session 04 pilot and error analysis. The over-tagging risk was added because the model assigns several categories to single sentences.
- 2026-10-06: Current evidence updated with the Session 06 outside-user results (4 participants) and the mid-semester decision to persevere.
