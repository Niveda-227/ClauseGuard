# Five-person work plan for Session 04

These are **assignments, not claims of completed contributions**. Each person should understand their code, make or verify a substantive change, investigate a research/evaluation question and link actual work. All five code; hats are accountability.

| Member / hat | Engineering work today | Research / evaluation work today | Required evidence / coordination | Reviewer |
|---|---|---|---|---|
| Ameer — Product | Review and run `app.py`; test input → analysis → category filter → source → HTML export. Implement a small usability change only if the session exposes a concrete need; add its meaningful regression check where relevant. | Observe an outside user's friction; compare the workflow with manual reading; revise the lean canvas from observed evidence. | Product/usability issue, actual code/document diff, test notes, linked PR; confirm the pitch and report claims. | Hemanth |
| Hemanth — Engineering | Integrate the source and bundled models; reproduce setup on a laptop; verify model loading and CLI/GUI error behavior; fix any reproducible setup/segmentation defect. | Investigate sentence-boundary examples and local inference limits; explain why source offsets and model version identity matter. | Engineering issue and reviewed implementation PR; laptop smoke-test notes with OS/Python and observed result. | Jayakrishna |
| Jayakrishna — Data&Eval | Run `scripts/verify_sep22.py`; review the F1/error-count code; add or adapt an evaluation check based on a real discovered failure. | Inspect arbitration FP/FN examples using their dataset IDs; explain macro versus micro F1 and document split/licensing limitations. | Evaluation issue/PR, today's logs, actual error-analysis notes; confirm that test scores remain unexposed. | Niveda |
| Niveda — Users&Research | Review/run `clauses/task_timer.py`; verify task timing and anonymous output; improve the recorder/protocol only where a rehearsal identifies a real issue. | Recruit outside users, run the counterbalanced pilot, compare answers to the key, capture observations at the time. | Research/timer issue and PR; real CSV + companion JSON; observation and next-action issue. Team rehearsals stay separate. | Ankan |
| Ankan — Operations | Review/run the report finalizer and submission validator; check failure behavior for missing evidence; maintain a reproducible packaging/submission check. | Audit the official template, deadline, evidence standard and consistency between report and results. | Operations issue/PR, board/milestone upkeep, actual five-member proof links, branch-protection verification and final merge check. | Ameer |

## Explain your part in 30 seconds

- **Ameer:** “Our user needs to find a specific contractual passage. I verify whether the interface helps a real user complete that task, and I connect observed friction to the roadmap.”
- **Hemanth:** “Text is split without losing source offsets, then the same saved classifier powers CLI and GUI. I check that a stranger can reproduce the product.”
- **Jayakrishna:** “We fit on 5,532 training sentences and compare on 2,275 validation sentences from different companies. Eight-label macro F1 prevents ordinary sentences from hiding weak clause categories.”
- **Niveda:** “I record real users doing a task in the running product, with timing and correctness. The north-star is successful tasks within 180 seconds.”
- **Ankan:** “I keep the issue → branch → approved PR → main chain and make sure every report claim has evidence at the correct path before the deadline.”

These explain responsibilities, not personal accomplishments. In the submitted report, replace role descriptions with concrete completed work and real proof.
