# ClauseGuard: final presentation (outline)

Outline written in Session 11 by Ameer (Product); filled in Sessions 12 and 13. About 12 minutes plus 3 minutes of questions; Ameer presents and runs the live demo. Every number on a slide is copied from the source file named next to it, after the Session 12 freeze. No number is written here before that.

| # | Slide | What it shows | Source of every number on it | Time |
|---:|---|---|---|---:|
| 1 | The problem | People accept Terms of Service they do not read; the clauses that matter (ending the account, changing the terms, courts and arbitration) are hard to find in long text | - | 0:45 |
| 2 | Who it is for | Students and app users who need to find one clause quickly; what they do today (read everything, or Cmd+F) | `docs/lean_canvas.md` | 0:45 |
| 3 | The product, live | Web app on the laptop, offline: paste or open a document, flags with the original sentence, category explanation, score and cut-off | live demo (`docs/DEMO_RUNSHEET_web.md`) | 2:30 |
| 4 | Honest about misses | "Possible" cue just under a cut-off; the "Check it yourself" panel lists unflagged sentences with search words; the reminder that no flag does not mean the clause is not there | live demo; `experiments/session09/hint_eval.md` | 1:30 |
| 5 | The NLP method | UNFAIR-ToS, 8 categories; word and character TF-IDF with one logistic regression per category; per-category cut-offs tuned with leave-one-company-out | `artifacts/selected.json`, `experiments/session11/ablation.md` | 1:15 |
| 6 | What we tried | The 12-configuration ablation and its pre-set rule; why the shipped model was kept or changed | `experiments/session11/ablation.md`, `docs/decisions/2026-11-11_final_model_rule.md` | 1:00 |
| 7 | How good is it | Baseline vs final model on validation (honest) and on the test split, read once after the freeze | `experiments/session07/threshold_ship_eval.json`, `experiments/session12/` (Session 12) | 1:00 |
| 8 | Real documents | Fresh real Terms of Service: the model finds fewer clauses there (domain shift); the labels' limits | `experiments/session10/fresh_eval.md`, `reports/session10.md` | 1:00 |
| 9 | Users | Outside participants across sessions, ClauseGuard vs manual, what we changed because of them | `evidence/session*/summary.json`, the weekly reports | 1:15 |
| 10 | Limits, ethics and next steps | Not legal advice; text stays on the computer; over- and under-flagging; what we would build next | `reports/final/report.md` (section 5) | 1:00 |

## Rules for the slides

- The model on the slides is the model in the demo (`artifacts/selected.joblib`, same SHA-256).
- Run `python scripts/demo_check.py` the day before and one hour before; it must end `READY FOR THE DEMO`.
- No participant names, no screenshots with personal details.
- Every teammate can explain slides 5 to 8 when asked.
