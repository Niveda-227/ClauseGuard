# Session 08 outside-user evidence (protocol sep29_v2)

Real outside-user task tests of the running ClauseGuard product on 2026-10-25. 3 new participants (U008, U009, U010), none of them on the five-person team and none who took part in Sessions 04 to 07. Who they were, without names: three classmates of the observer, each seen in person. Each gave verbal consent before their trials.

Each did one task without the tool (plain text editor) and one with ClauseGuard in the web app (`python -m webapp`), with task order and tool order swapped between participants; 180-second limit. The clock stopped when the participant stated the answer; typing the answer was not timed. After both tasks, each did the explanation check (`clauses/explain_check.py`): four cards, each with a category, the app's explanation for it, and three invented sentences to choose from. Not timed.

The app in these trials is the Session 08 product: the same model as Session 07 (per-category cut-offs), shown in the web app, with review cues near the cut-offs. Task E1's answer sentence is flagged; task F1's answer sentence is not flagged but is shown as "Possible: Jurisdiction" (see `experiments/session08/study_doc_check.json`).

Files:
- `tasks.csv`: one row per trial (task, condition, correct, seconds, model ID, protocol)
- `U0XX_<task>_<condition>_sep29_v2.json`: timestamped trial records with the exact prompt read aloud, number of readings, the answer, interface and observer notes
- `U0XX_explain_v1.json`: the explanation check (letters chosen, right or wrong, optional note)
- `session_notes.md`: notes written up after the sessions from the saved records and the observer's session document, with measurement notes
No screenshots were taken.

The answer keys are not in the repository. No names, emails, faces or contact details are included.
