# Capture real evidence today (Session 04, protocol sep22_v1, retired)

> **Superseded.** This is the Session 04 procedure, kept so the Session 04 report remains reproducible. For Session 05 onwards use `docs/STUDY_PROTOCOL_V2.md`.

**Owner: Niveda; observer/product partner: Ameer.** The course requires an outside-team user to use the running product. It does not prescribe a sample size. Aim for two outside participants for an initial pilot; report the actual number even if it is smaller.

## Prepare

1. Run the product on a laptop and verify the example. Use `python app.py`; alternatively the participant can operate the documented CLI and open the exported HTML. Record which interface they actually used.
2. Use the fictional study documents in `examples/study/`. They are fixtures for usability tasks, not benchmark training/evaluation data.
3. Ask whether the participant agrees to anonymous task timing/answer notes. Do not record names, email, private ToS text or faces. Request separate explicit consent if recording a screen/video; it is optional.
4. Assign `U001`, `U002`, etc. Keep any identity mapping outside the repo. No teammate can count as an outside participant.
5. Explain: “This is a prototype that suggests categories to inspect. It can miss or mislabel clauses. Locate the passage yourself and explain what it says. You can stop at any time.”

## Small counterbalanced pilot

Each person sees each document only once. Use the same task wording and time limit in both conditions; do not coach or show the observer answer key.

| Participant | First trial | Second trial |
|---|---|---|
| U001 | Manual reading, A1, document A | ClauseGuard, B1, document B |
| U002 | ClauseGuard, A1, document A | Manual reading, B1, document B |

- **A1:** “Find the sentence explaining how disputes must be resolved. Show the passage and state whether binding arbitration is required.”
- **B1:** “Find the sentence describing the provider's right to end your account. Show the passage and state whether advance notice is promised.”
- Manual condition: open the unannotated `.txt` in a normal text editor. Allow ordinary Find. No ClauseGuard output.
- ClauseGuard condition: the participant loads the assigned `.txt`, runs analysis and uses the interface/source to answer. A lack of a flag does not permit observer assistance.
- Give 180 seconds per trial. Time begins when the participant starts the task; stop at completion or the limit. The observer enters the answer promptly. The timer includes entry time, a limitation to disclose. A separate phone timer may signal the limit; the recorder does not enforce an automatic timeout.
- Score success only when the participant locates the correct passage **and** gives the right meaning within 180 seconds. Record wrong/late attempts, not only successes.

## Record while it happens

Run each command immediately before that real trial; the script asks for consent confirmation and a start signal. Keep the terminal on the observer's screen and the product on the participant's screen. Do not feed scripted answers into the real evidence folder.

```bash
python -m clauses.task_timer --participant U001 --task A1 --condition manual
python -m clauses.task_timer --participant U001 --task B1 --condition clauseguard
python -m clauses.task_timer --participant U002 --task A1 --condition clauseguard
python -m clauses.task_timer --participant U002 --task B1 --condition manual
```

Only run trials that actually occur. If someone declines, stop. For an abandoned trial, record contemporaneous anonymous notes; explain exclusions and do not silently delete failures. Use a new participant/task ID for a legitimate new trial rather than overwriting old observations.

The recorder appends `evidence/session04/tasks.csv` and writes one JSON per trial, with timestamps, answer and observation. It does not take screenshots or verify who the person is; the team remains responsible for authenticity and anonymization. Rehearsal/test outputs belong in a temporary folder, never this evidence folder.

After the sessions:

```bash
python -m clauses.cli summarize-tasks --input evidence/session04/tasks.csv
```

The report finalizer saves the same summary as `evidence/session04/summary.json`.

## Observer-only answer key (removed)

The Session 04 answer key was removed from this public repository on 2026-09-24 because anyone could read it before taking part. Tasks A1 and B1 (documents A and B) are **retired**: do not use them in any future session.

From Session 05 the team uses protocol `sep29_v2`: the public task bank is `examples/study/tasks_v2.json`, the recorder is `python -m clauses.session_v2`, and the procedure is in `docs/STUDY_PROTOCOL_V2.md`. Answer keys are kept only in the git-ignored `private/` folder on the observer's laptop.

## Report the result honestly

North-star = `100 × correct ClauseGuard tasks completed within 180 seconds / all recorded ClauseGuard tasks`. Include numerator, denominator, participant count and interface used. `previous: null` is appropriate for the first recorded week; the manual control is a same-session comparison, not last week's result. Do not pool different model hashes or protocols.

Write one concrete observation and its consequence: implemented change with its PR, or planned change with its issue. If no change was made yet, say so. A two-person pilot on short fictional text can expose usability friction; it cannot establish general population benefit or performance on real legal documents.

Commit raw records and notes through a reviewed PR today. If no outside user is available, leave the metric unknown and say user validation was not completed; a synthetic replacement does not satisfy the requirement.
