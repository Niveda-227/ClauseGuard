# Mid-semester presentation (Session 06, Tuesday October 6, 2026)

Presented in class on October 6: five minutes plus two minutes of questions. 

Member contributions:
* Ankan - Introduction (Slides 1, 2)
* Hemanth - Shipped product and NLP method (Slides 3, 4)
* Jayakrishna - Validation results and error analysis (Slides 5, 6)
* Niveda - Outside user evidence and what we learned (Slides 7, 8)
* Ameer - The next model change and plan to demo day (Slides 9, 10)

The app was shown as a creenshot during the mid-semester presentation, with plans for a detailed live demo on demo day.


| File | What it is |
|---|---|
| `ClauseGuard_Midsemester_10_Slides.pptx` | The deck as presented (PowerPoint) |
| `ClauseGuard_Midsemester_10_Slides.pdf` | The same deck as a PDF, for reading on GitHub or in a browser |

## Where the numbers in the deck come from

Every number on the slides comes from a file already in this repository.

- Model vs baseline: `experiments/session04/*/metrics.json` (validation split; the test split is not used before Session 12).
- Threshold experiment: `experiments/session05/threshold_cv.md` (not in the product at the time of the presentation; shipped in Session 07).
- Users: `evidence/session05/` and `evidence/session06/` (protocol sep29_v2).
- Decision rule: `docs/decisions/midpoint_rule.json`, committed before the Session 06 user sessions; the decision (Persevere) and the reasons are in `docs/decisions/2026-10-06_midpoint_decision.md`.
- Facts used to apply the rule: recompute them from committed files with `python scripts/midpoint_facts.py --out-dir private/midpoint_check` (the `private/` folder is never committed).
- Cost to serve and demo checks: `experiments/session06/demo_check.json`.

## Note on study tasks C1 and D1

The deck showed the study tasks C1 and D1 and their answers in public. Those tasks are retired: from Session 07 the team uses tasks E1 and F1 (`examples/study/tasks_v3.json`).

## Product since the presentation

The app shown in the deck used fixed 0.5 thresholds (model `04713fbf6e23…`). From Session 07 the app uses per-category thresholds on the same trained model; see `artifacts/README.md` and `experiments/session07/threshold_ship_eval.md`.
