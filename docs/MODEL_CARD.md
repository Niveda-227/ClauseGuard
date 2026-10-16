# ClauseGuard model card

**Selected artifact:** `artifacts/selected.joblib` (a copy of `artifacts/tuned.joblib`)  
**Variant:** hybrid, with one threshold per category  
**SHA-256:** `<<NEW SHA: the full artifact_sha256 value in artifacts/selected.json>>`  
**Base model:** `artifacts/hybrid.joblib`, SHA-256 `04713fbf6e23784a5d32e5cdd5fef459182408565bfe8a4fb6a9f10d53dbff76` (same trained weights, fixed 0.5 thresholds; the product model until Session 06)  
**Status:** Session 07 release, October 2026. Not a final semester freeze.

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
