# Session 12 outside-user evidence (protocol sep29_v2): the final user check on release 1.0.0

Real outside-user task tests of the frozen ClauseGuard release 1.0.0 on 2026-11-23. Before the first trial, `python scripts/check_release.py` printed THIS IS RELEASE 1.0.0 on the session laptop. New participants: U018 and U019, none of them on the five-person team and none who took part in Sessions 04 to 11. Who they were, without names: two friends of the observer. How they were recruited: in person, by the observer. Booked: 2; came: 2. Each gave verbal consent before their trials.

Each did one task without the tool (plain text editor) and the other with ClauseGuard in the web app (`python -m webapp`), with task order and tool order swapped between participants; 180-second limit. The clock stopped when the participant stated the answer; typing the answer was not timed. Both participants were in the same room for all trials and could hear each other, so the second participant's results are not independent of the first's (see session_notes.md).

The two tasks (`examples/study/tasks_v7.json`) are on real, openly licensed Terms of Service (`examples/fresh/SOURCES.md`): M1 on the Cloudup terms and N1 on the Basecamp terms. In both, the app flags the answer sentence. See `experiments/session12/study_doc_check.json`.

Files:
- `tasks.csv`: one row per trial (task, condition, correct, seconds, model ID, protocol)
- `U0XX_<task>_<condition>_sep29_v2.json`: timestamped trial records with the exact prompt read aloud, number of readings, the answer, interface and observer notes
- `session_notes.md`: notes written up after the sessions from the saved records and the observer's answers, with measurement notes
- No screenshots were taken.

The answer keys are not in the repository. No names, emails, faces or contact details are included.
