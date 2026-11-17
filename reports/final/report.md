# ClauseGuard: final report

Skeleton written in Session 11; the text is written in Sessions 12 and 13 (1,000 to 2,500 words in total). Every number is copied from the result file named in the plan of its section, after the Session 12 freeze; no number is written before that.

## 1. Problem and users

Plan: the problem (unread Terms of Service; the clauses that matter are hard to find); who the users are and what they do today; the north-star measure (a correct clause-finding task within 180 seconds). Sources: `docs/lean_canvas.md`, `reports/session04.md`.

## 2. Product

Plan: what the web app shows (flags next to the original sentence, the category explanation, score and cut-off; the "possible" cue; the "Check it yourself" panel; the reminder that no flag does not mean the clause is not there); that it runs offline. Sources: `docs/DEMO_RUNSHEET_web.md`, `docs/decisions/`.

## 3. NLP method and evaluation

Plan: data (UNFAIR-ToS, split by company); the model and its per-category cut-offs; the honest leave-one-company-out estimate; the Session 11 ablation and its rule; the one-time test-split result after the freeze; the fresh real documents (domain shift) and the limits of those labels. Sources: `docs/MODEL_CARD.md`, `experiments/session07/threshold_ship_eval.json`, `experiments/session11/ablation.json`, `experiments/session12/` (after the freeze), `experiments/session10/fresh_eval.json`.

## 4. User evidence

Plan: the protocol; the outside participants in each session; ClauseGuard against manual; what changed in the product because of them; the limits (small samples, mostly fictional documents before Session 10). Sources: `evidence/session*/`, the weekly reports.

## 5. Ethics and limitations

Plan: not legal advice; privacy (text stays on the computer); wrong tags and missed clauses, and how the product shows them; domain shift; the labels' context (EU consumer law, legal experts) and our own labels' limits; what we would do next. Sources: `docs/MODEL_CARD.md`, `reports/session10.md`.
