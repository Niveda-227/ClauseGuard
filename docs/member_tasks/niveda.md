# Interface-aware user-session capture

The original user-task log does not explicitly identify whether the participant used the desktop app or CLI/HTML. This wrapper adds interface and anonymous observer IDs to the companion JSON while keeping the existing CSV and report finalizer compatible.

## Run

```bash
python -m clauses.session_capture --help
python -m unittest discover -s tests -p 'test_niveda_capture.py' -v
```

## How it works

The existing timer still handles consent confirmation, measured duration and duplicate checks. The wrapper records interface context after the real trial and leaves the CSV schema unchanged. It never automatically creates participant results.

For an actual outside-user ClauseGuard trial:

```bash
python -m clauses.session_capture --participant U001 --task B1 --condition clauseguard --interface desktop --observer OBS01
```

If the participant operates CLI/HTML, use `--interface cli_html`. For an actual manual trial:

```bash
python -m clauses.session_capture --participant U001 --task A1 --condition manual --interface text_editor --observer OBS01
```

Use these only when those trials actually occur. Follow the counterbalanced order in `USER_SESSION_QUICKSTART.md`. Use the wrapper **instead of** the old timer command for a trial; do not record it twice. Preserve failures. The timing includes answer-entry time and does not enforce an automatic timeout. Test fixtures use temporary directories and must never be copied into real evidence.

Stage `tasks.csv` and the exact anonymous trial JSON files you reviewed; do not stage private screenshots or unreviewed recordings. Ankan generates the shared summary at report-finalization time. If a real session finishes but a later write fails, inspect the raw records before retrying.

## Research question

Run actual outside-user tasks using the original USER_SESSION_QUICKSTART.md. Record the interface, outcome and observed friction. Compare manual and ClauseGuard conditions only with the stated limits; do not treat the tiny pilot as proof of general benefit.

This is AI-assisted implementation material. Team members should record their actual review, adaptation and verification in the PR rather than claim unperformed work.

Keep one ClauseGuard interface for the pilot where possible. Interface is recorded in each trial JSON, but the existing CSV summary does not stratify by interface; disclose any mixed-interface pilot rather than implying a controlled comparison.
