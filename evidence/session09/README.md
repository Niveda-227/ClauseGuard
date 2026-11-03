# Session 09 outside-user evidence (protocol sep29_v2)

Real outside-user task tests of the running ClauseGuard product on 2026-11-02. New participants: U012 and U013, none of them on the five-person team and none who took part in Sessions 04 to 08. Who they were, without names: two classmates of the observer. How they were recruited: in person, by the observer. Booked: 3; came: 3. The first of the three (U011) was run and then excluded because the saved record of one trial did not match its task; U011's files are not in this folder (see the measurement notes in `session_notes.md`). Each participant gave verbal consent before their trials.

Each did one absence task without the tool (plain text editor) and the other with ClauseGuard in the web app (`python -m webapp`), with task order and tool order swapped between participants; 180-second limit. The clock stopped when the participant stated the answer; typing the answer was not timed. The explanation check from Session 08 was not repeated in Session 09, by design.

The two tasks (`examples/study/tasks_v4.json`): G1 on document G (the answer sentence is in the document but the model does not flag it; the app's "Check it yourself" panel lists it as worth a look) and H1 on document H (the document has no such sentence; the correct answer is that there is none). See `experiments/session09/study_doc_check.json`.

Files:
- `tasks.csv`: one row per trial (task, condition, correct, seconds, model ID, protocol)
- `U0XX_<task>_<condition>_sep29_v2.json`: timestamped trial records with the exact prompt read aloud, number of readings, the answer, interface and observer notes
- `session_notes.md`: notes written up after the sessions from the saved records and the observer's answers, with measurement notes
- No screenshots were taken.

The answer keys are not in the repository. No names, emails, faces or contact details are included.
