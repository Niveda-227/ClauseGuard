# Decision rule: the one-time test-split result (Session 12)

- **Date written:** 2026-11-18, when the Session 12 kit was prepared. **No test-split result exists when this is merged:** the kit was checked with validation rows in place of test rows, and the test split was never opened. Machine-readable copy: [final_test_rule.json](final_test_rule.json). Used by `scripts/final_test.py`.
- **Owner:** Ameer (Product)
- **Why:** every model number so far comes from the validation split. The UNFAIR-ToS test split has been kept unread since the start of the project, so that one number at the end is not flattered by any choice we made. Session 11 kept the shipped model (`experiments/session11/ablation.md`); Session 12 freezes it as release 1.0.0 and reads the test split once.

## What is measured

- **Model:** release 1.0.0, `artifacts/selected.joblib`, SHA-256 `dafbb5470f2fb2678cae273eac7c23046bbad0487c7be247174a99a08ad493bd`, with its shipped per-category cut-offs. Nothing is tuned on the test split.
- **Who and when:** Jayakrishna runs `scripts/final_test.py` once, after release 1.0.0 is merged on `main` and tagged `v1.0.0`. The script refuses to run if the release check fails or if the test split was already read (`experiments/test_exposure.jsonl`).
- **Measure:** macro-F1 over the 8 categories on the test split (1,607 sentences).
- **Compared with:** the honest leave-one-company-out validation macro-F1 and the optimistic validation macro-F1 of the same model (`experiments/session07/threshold_ship_eval.json`).

## The rule (fixed now; never changed after a result exists)

- The difference is the test macro-F1 minus the honest validation macro-F1.
- Within 0.05 either way: "CONSISTENT with the honest validation estimate".
- More than 0.05 below: "LOWER than the honest validation estimate".
- More than 0.05 above: "HIGHER than the honest validation estimate".

## Reported, but deciding nothing

- Micro-F1, flags per 100 sentences, correct tags, wrong tags and missed labels on the test split.
- Precision, recall and F1 for each category, next to the honest validation F1 of that category.

## After the result

- The test split is read once and never again.
- Nothing in the product changes because of the test result before the final submission. The result goes into the Session 12 report, the model card and the final report, whatever it shows, next to the validation numbers.
