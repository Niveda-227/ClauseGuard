# Session 11 outside-user evidence (protocol sep29_v2)

Real outside-user task tests of the running ClauseGuard product on 2026-11-16. New participants: U016 and U017, none of them on the five-person team and none who took part in Sessions 04 to 10. Who they were, without names: two classmates of the observer. How they were recruited: in person, in one of the observer's classes. Booked: 3; came: 2. Each gave verbal consent before their trials.

Each did one task without the tool (plain text editor) and the other with ClauseGuard in the web app (`python -m webapp`), with task order and tool order swapped between participants; 180-second limit. The clock stopped when the participant stated the answer; typing the answer was not timed. Each participant had their own introduction and did not watch the other's trials (observer's report).

The two tasks (`examples/study/tasks_v6.json`) are on real, openly licensed Terms of Service (`examples/fresh/SOURCES.md`): K1 on the Cloudup terms and L1 on the Crowdsignal terms. In both, the model does not flag the answer sentence, but the app's "Check it yourself" panel lists it as worth a look. See `experiments/session11/study_doc_check.json`.

Files:
- `tasks.csv`: one row per trial (task, condition, correct, seconds, model ID, protocol)
- `U0XX_<task>_<condition>_sep29_v2.json`: timestamped trial records with the exact prompt read aloud, number of readings, the answer, interface and observer notes
- `session_notes.md`: notes written up after the sessions from the saved records and the observer's answers, with measurement notes
- No screenshots were taken.

The answer keys are not in the repository. No names, emails, faces or contact details are included.
