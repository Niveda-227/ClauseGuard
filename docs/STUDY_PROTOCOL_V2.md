# Study protocol v2 (`sep29_v2`), from Session 05

Replaces the Session 04 procedure (`USER_SESSION_QUICKSTART.md`, protocol `sep22_v1`, retired).

## Why v2 exists

The Session 04 pilot produced 0/1, but both trials failed for measurement reasons ([issue #14](https://github.com/Niveda-227/ClauseGuard/issues/14)):

1. The clock kept running while the observer typed the answer (486 s recorded for a task solved quickly).
2. The participant answered a different task from the one assigned, and nothing checked that the task was understood.

v2 fixes both. The clock stops the moment the participant states the answer; typing is not timed. The observer reads the prompt word for word from the task bank, and the participant restates it before the clock starts.

## Materials

| Item | Where | Public? |
|---|---|---|
| Documents | `examples/study/document_C.txt`, `document_D.txt` | yes |
| Task prompts | `examples/study/tasks_v2.json` | yes |
| Answer key | `private/session05_answer_key.json` on the observer's laptop | **no, git-ignored** |
| Recorder | `python -m clauses.session_v2` | yes |
| Fairness check | `python scripts/check_study_docs.py` (writes a sanitized summary) | yes |

Documents A and B are retired because their answers were published.

## Design

- Each participant does **two** trials: one without the tool (plain text editor) and one with ClauseGuard.
- Each participant sees each document **once**.
- Order is **counterbalanced** across participants:

| Participant | Trial 1 | Trial 2 |
|---|---|---|
| U002 | Manual, C1 | ClauseGuard, D1 |
| U003 | ClauseGuard, C1 | Manual, D1 |
| U004 | Manual, C1 | ClauseGuard, D1 |
| U005 | ClauseGuard, C1 | Manual, D1 |

- Participants must be outside the five-person team. U001 is already used; start at U002.
- Time limit: 180 seconds. A correct answer after the limit is unsuccessful.
- Correct means the right sentence **and** the right meaning.

## Scoring

North-star = 100 × ClauseGuard trials correct within 180 s ÷ all ClauseGuard trials, under protocol `sep29_v2` and the current model. Summaries never pool different protocols or models.

## Privacy

No names, emails, faces or contact details in any file. Participant codes only. Screenshots only with consent, screen only. The code-to-person mapping stays on paper.

## Known limits

Short fictional documents and small samples. C1 and D1 differ in difficulty, so even with counterbalancing the manual and ClauseGuard conditions are not perfectly matched.
