# ClauseGuard model card

**Selected artifact:** `artifacts/selected.joblib` (a copy of `artifacts/tuned.joblib`)  
**Variant:** hybrid, with one threshold per category  
**SHA-256:** `dafbb5470f2fb2678cae273eac7c23046bbad0487c7be247174a99a08ad493bd`  
**Base model:** `artifacts/hybrid.joblib`, SHA-256 `04713fbf6e23784a5d32e5cdd5fef459182408565bfe8a4fb6a9f10d53dbff76` (same trained weights, fixed 0.5 thresholds; the product model until Session 06)  
**Status:** Session 07 model, unchanged through Session 11 (Sessions 08 to 10 changed only what users see). A rebuild check was added in Session 11 (see below and `experiments/session11/reproduce.md`). Not a final semester freeze: the freeze and the one-time test-split result come in Session 12.

Purpose: classify eight contractual categories in English ToS sentences for source-linked review. Not a legal-enforceability system, safety rating, or replacement for reading an agreement. The annotations reflect the source's consumer-law context.

Training data: official UNFAIR-ToS train, 5,532 sentences. Development: official validation, 2,275. Final test not evaluated. The selected representation combines word TF-IDF and character n-grams with balanced one-vs-rest logistic regressions. Manifest lists exact thresholds, seed, packages and data hash.

## Thresholds (Session 07)

A sentence gets a category when its score is **above** that category's threshold. Thresholds were chosen per category on the validation split (grid 0.10 to 0.90; ties go to the higher threshold) by `scripts/ship_thresholds.py`, and equal the in-sample thresholds of the Session 05 experiment (`experiments/session05/threshold_cv.json`).

| Category | Threshold |
|---|---:|
| Limitation of liability | 0.75 |
| Unilateral termination | 0.70 |
| Unilateral change | 0.80 |
| Content removal | 0.80 |
| Contract by using | 0.80 |
| Choice of law | 0.65 |
| Jurisdiction | 0.55 |
| Arbitration | 0.80 |

## Review cues near a cut-off (Session 08)

The model, its scores and its thresholds did not change in Session 08. What users see did: scores within **0.05** of a category's threshold are now named instead of hidden (`clauses/cues.py`).

- **Uncertain flag:** the category is flagged, but its score is less than 0.05 above the threshold.
- **Possible category:** the category is not flagged, but its score is less than 0.05 below the threshold (or exactly on it). The desktop list shows `(possible: Jurisdiction)`; the web app shows a dashed "Possible" tag and a dashed underline.

The 0.05 margin is the distance the app has used since Session 04 for its note "One score is near its decision threshold". It was fixed before any Session 08 result and is not tuned on any split. How often the cues appear on the validation split, and how many missed labels they point to, is measured in `experiments/session08/cue_eval.md`.

## Results (validation split)

| Model | 8-category macro-F1 | 8-category micro-F1 | LexGLUE macro-F1 (9 columns) | LexGLUE micro-F1 (9 columns) |
|---|---:|---:|---:|---:|
| baseline | 0.2551 | 0.3300 | 0.3331 | 0.9153 |
| balanced | 0.6156 | 0.6084 | 0.6540 | 0.9107 |
| hybrid, fixed 0.5 (product until Session 06) | 0.6333 | 0.6275 | 0.6695 | 0.9126 |
| hybrid, per-category thresholds, scored on the split they were tuned on (**optimistic**) | 0.7244 | 0.7254 | 0.7522 | 0.9479 |
| hybrid, per-category thresholds, leave-one-company-out (**honest estimate**) | 0.6768 | 0.6880 | not computed | not computed |

Sources: `experiments/session04/*/metrics.json`, `experiments/session07/tuned/metrics.json`, `experiments/session05/threshold_cv.json`. Quote the honest estimate, not the optimistic row.

The per-category thresholds trade wrong tags for missed labels: flags per 100 validation sentences fall from 17.49 to 11.03 under the honest estimate, so fewer wrong tags are shown, but more annotated clauses get no flag. A sentence with no flag is not a safe sentence. Arbitration rests on 9 validation examples, so its threshold is unreliable.

Current scores are not calibrated probabilities. The near-threshold cue is a heuristic. Source sentences are available for inspection, but category explanations are general descriptions, not faithful model-feature attributions.

No runtime API calls or default input logging. A requested export includes the supplied text; users should store it appropriately. English input and a 100,000-character limit apply. An application of this model to new services, new document versions or other languages needs separate testing. The synthetic demo cannot establish domain generalization.

Outside-user results are in `evidence/` and the weekly reports in `reports/`. Version the card as actual studies and model changes occur. After final evaluation, update test status with evidence rather than silently changing previous claims.

## Rebuild from a clean clone (Session 11)

`python scripts/reproduce_model.py` retrains this model with the product code (`clauses.model.train`, variant hybrid, seed 641) on the train split only, gives it the product cut-offs, and checks that it reproduces the product model: the same validation scores (within one millionth), the same flags on every validation sentence, and the same flags on the demo document. It records the fingerprints of the release (dataset archive, product file, training data, cut-offs, and a SHA-256 over the validation flags) in [experiments/session11/reproduce.md](../experiments/session11/reproduce.md). The rebuilt model is compared by its outputs, not by its file bytes: a saved file contains its creation time.

## Real documents (Session 10)

On three real Terms of Service from companies outside UNFAIR-ToS ([experiments/session10/fresh_eval.md](../experiments/session10/fresh_eval.md)) the model found clearly fewer clauses than on validation. Those labels were made by two team members but not independently ([reports/session10.md](../reports/session10.md)), so the number is a warning, not a precise estimate. Since Session 11 the web app says above the findings that no flag does not mean the clause is not there.

## Numbers checked against their sources (Session 11)

Each row below is checked by `tests/test_model_card.py` against its source file, so these numbers cannot drift from the results.

| Number | Value | Source file | Key |
|---|---:|---|---|
| Training sentences | 5532 | artifacts/selected.json | train_count |
| Validation macro-F1, honest (leave-one-company-out) | 0.6768 | experiments/session07/threshold_ship_eval.json | new_product_leave_one_company_out_HONEST.macro_f1 |
| Validation macro-F1, cut-offs tuned and scored on the same split (optimistic) | 0.7244 | experiments/session07/threshold_ship_eval.json | new_product_tuned_OPTIMISTIC.macro_f1 |
| Validation micro-F1, honest | 0.688 | experiments/session07/threshold_ship_eval.json | new_product_leave_one_company_out_HONEST.micro_f1 |
| Flags per 100 validation sentences, honest | 11.03 | experiments/session07/threshold_ship_eval.json | new_product_leave_one_company_out_HONEST.flags_per_100_sentences |
| Annotator labels per 100 validation sentences | 10.95 | experiments/session07/threshold_ship_eval.json | gold_labels_per_100_sentences |
| Weakest category: Arbitration F1, honest | 0.3478 | experiments/session07/threshold_ship_eval.json | new_product_leave_one_company_out_HONEST.per_category.Arbitration.f1 |
| Fresh real documents, strict macro-F1 (labels not made independently) | 0.4139 | experiments/session10/fresh_eval.json | strict.macro_f1 |
