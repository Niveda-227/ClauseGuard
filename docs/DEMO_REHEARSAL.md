# Demo rehearsal checklist (from Session 11)

For the demo-day presentation (date, slot and length as set by the course). Ameer presents and runs the live demo with [DEMO_RUNSHEET_web.md](DEMO_RUNSHEET_web.md); the slides follow [reports/final/slides.md](../reports/final/slides.md). Tick each line at every rehearsal.

## One week before

- [ ] The release is frozen (Session 12): `artifacts/selected.json` names the model, and `python scripts/reproduce_model.py` says `REPRODUCED`.
- [ ] Every number on the slides is copied from the source file named in `reports/final/slides.md`; nobody types a number from memory.
- [ ] Full rehearsal with a timer, in the time the course gives (check it on the course page), with questions from a teammate at the end.
- [ ] Each teammate can explain the method slides (5 to 8): the data split by company, the honest leave-one-company-out estimate, the ablation rule, the test-split result, domain shift.

## The day before

- [ ] On the presenting laptop: `git switch main`, `git pull --ff-only origin main`, `python scripts/demo_check.py --output /tmp/demo_check_rehearsal.json` ends `READY FOR THE DEMO`.
- [ ] Run the whole run-sheet once: the example, a wrong extra tag, the "Possible" cue, the "Check it yourself" panel, the reminder above the findings, the category cards, the HTML download.
- [ ] Back-up plan works: `analysis.html` (written by the demo check) opens in the browser without the server.
- [ ] The slides open offline (PDF copy on the laptop and on a USB stick).

## One hour before

- [ ] Charger plugged in; Do Not Disturb on; chat apps and email closed; one browser window.
- [ ] `python scripts/demo_check.py --output /tmp/demo_check_rehearsal.json` again: `READY FOR THE DEMO`.
- [ ] `python -m webapp` running; the app is open at `http://127.0.0.1:8641` and cleared.

## Questions to prepare (one teammate asks them at the rehearsal)

- Why per-category cut-offs, and why is the honest number lower than the tuned one?
- What does the model miss, and how does the product tell the user?
- How do you know the model in the demo is the model in the report?
- What happened on real Terms of Service outside the dataset, and how far can those labels be trusted?
- What did users actually do with the app, and what did you change because of them?
