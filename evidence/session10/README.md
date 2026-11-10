# Session 10 outside-user evidence (protocol sep29_v2)

Real outside-user task tests of the running ClauseGuard product on 2026-11-09. New participants: U014 and U015, none of them on the five-person team and none who took part in Sessions 04 to 09. Who they were, without names: two classmates of the observer. How they were recruited: in person, by the observer. Booked: 2; came: 2. Each gave verbal consent before their trials.

Each did one task without the tool (plain text editor) and the other with ClauseGuard in the web app (`python -m webapp`), with task order and tool order swapped between participants; 180-second limit. The clock stopped when the participant stated the answer; typing the answer was not timed. Both participants were run together in one sitting, with one introduction and back-to-back trials, and did not watch each other's trials (observer's report).

The two tasks (`examples/study/tasks_v5.json`) are the first on real documents: openly licensed Terms of Service from companies that are not in UNFAIR-ToS (`examples/fresh/SOURCES.md`). I1 on the Basecamp terms (the model does not flag the answer sentence) and J1 on the Crowdsignal terms (the model flags the answer sentence). See `experiments/session10/study_doc_check.json`.

Files:
- `tasks.csv`: one row per trial (task, condition, correct, seconds, model ID, protocol)
- `U0XX_<task>_<condition>_sep29_v2.json`: timestamped trial records with the exact prompt read aloud, number of readings, the answer, interface and observer notes
- `session_notes.md`: notes written up after the sessions from the saved records and the observer's answers, with measurement notes
- No screenshots were taken.

The answer keys are not in the repository. No names, emails, faces or contact details are included.
