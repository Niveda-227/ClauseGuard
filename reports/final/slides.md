# ClauseGuard: final presentation (outline)

Outline written in Session 11 by Ameer (Product); speaker notes drafted in Session 12; numbers added in Session 13. About 12 minutes plus 3 minutes of questions; Ameer presents and runs the live demo. Every number on a slide is copied from the source file named next to it, after the Session 12 freeze. No number is written here before that.

| # | Slide | What it shows | Source of every number on it | Time |
|---:|---|---|---|---:|
| 1 | The problem | People accept Terms of Service they do not read; the clauses that matter (ending the account, changing the terms, courts and arbitration) are hard to find in long text | - | 0:45 |
| 2 | Who it is for | Students and app users who need to find one clause quickly; what they do today (read everything, or Cmd+F) | `docs/lean_canvas.md` | 0:45 |
| 3 | The product, live | Web app on the laptop, offline: paste or open a document, flags with the original sentence, category explanation, score and cut-off | live demo (`docs/DEMO_RUNSHEET_web.md`) | 2:30 |
| 4 | Honest about misses | "Possible" cue just under a cut-off; the "Check it yourself" panel lists unflagged sentences with search words; the reminder that no flag does not mean the clause is not there | live demo; `experiments/session09/hint_eval.md` | 1:30 |
| 5 | The NLP method | UNFAIR-ToS, 8 categories; word and character TF-IDF with one logistic regression per category; per-category cut-offs tuned with leave-one-company-out | `artifacts/selected.json`, `experiments/session11/ablation.md` | 1:15 |
| 6 | What we tried | The 12-configuration ablation and its pre-set rule; why the shipped model was kept or changed | `experiments/session11/ablation.md`, `docs/decisions/2026-11-11_final_model_rule.md` | 1:00 |
| 7 | How good is it | Baseline vs final model on validation (honest) and on the test split, read once after the freeze | `experiments/session07/threshold_ship_eval.json`, `experiments/session12/test_eval.json` | 1:00 |
| 8 | Real documents | Fresh real Terms of Service: the model finds fewer clauses there (domain shift); the labels' limits | `experiments/session10/fresh_eval.md`, `reports/session10.md` | 1:00 |
| 9 | Users | Outside participants across sessions, ClauseGuard vs manual, what we changed because of them | `experiments/session12/study_summary.json`, the weekly reports | 1:15 |
| 10 | Limits, ethics and next steps | Not legal advice; text stays on the computer; over- and under-flagging; what we would build next | `reports/final/report.md` (section 5) | 1:00 |

## Rules for the slides

- The model on the slides is the model in the demo (`artifacts/selected.joblib`, same SHA-256).
- Run `python scripts/demo_check.py` the day before and one hour before; it must end `READY FOR THE DEMO`.
- No participant names, no screenshots with personal details.
- Every teammate can explain slides 5 to 8 when asked.

## Speaker notes (draft, Session 12)

Words only; every number is added in Session 13 from the source named in the table above.

1. **The problem.** Everyone clicks "I agree". The clauses that can hurt you, like the company ending your account or changing the terms, are a few sentences in pages of text. We asked: can a small tool point you to them, without pretending to be a lawyer?
2. **Who it is for.** Students and app users who need one answer quickly, for example "can they delete my account?". Today they read everything or search with Cmd+F and hope they used the right word.
3. **The product, live.** Open a real Terms of Service, click Analyze, pick a flag. The sentence is shown in its place in the document, with the category, what it means, its score and its cut-off. Everything runs on this laptop; nothing is sent anywhere.
4. **Honest about misses.** A model misses things. The "possible" cue shows sentences just under a cut-off, the "Check it yourself" panel lists sentences with the category's search words, and the reminder says plainly that no flag does not mean the clause is not there.
5. **The NLP method.** The data is UNFAIR-ToS, split by company, so the model is always judged on companies it has not seen. Word and character features feed one logistic regression per category, and each category has its own cut-off, chosen on the validation split; our honest estimate scores each company with cut-offs chosen on the other nine.
6. **What we tried.** Before we froze the model we compared twelve configurations under a rule written first. The rule said: keep what we ship unless something is clearly better. Nothing was, so we kept it.
7. **How good is it.** The honest validation estimate, and the test split read once, after the freeze, with the result reported whatever it showed.
8. **Real documents.** On real terms from companies outside the dataset, the model found fewer clauses. That is why the reminder and the panel matter, and why we say "starting point", not "answer".
9. **Users.** Outside participants did timed tasks with and without the app, on fictional and then real documents. Say what they did well, where they went wrong, and what we changed because of them.
10. **Limits, ethics and next steps.** Not legal advice. Text stays on the computer. Wrong tags and missed clauses both happen, and the app shows both. Next: more real documents and labels made independently.
