# ClauseGuard model card

**Selected artifact:** `artifacts/selected.joblib`  
**Variant:** hybrid  
**SHA-256:** `04713fbf6e23784a5d32e5cdd5fef459182408565bfe8a4fb6a9f10d53dbff76`  
**Status:** Initial locally trained release, September 10, 2026. Not a final semester freeze.

Purpose: classify eight contractual categories in English ToS sentences for source-linked review. Not a legal-enforceability system, safety rating, or replacement for reading an agreement. The annotations reflect the source's consumer-law context.

Training data: official UNFAIR-ToS train, 5,532 sentences. Development: official validation, 2,275. Final test not evaluated. The selected representation combines word TF-IDF and character n-grams with balanced one-vs-rest logistic regressions. Manifest lists exact thresholds, seed, packages and data hash.

| Model | 8-category macro-F1 | LexGLUE macro-F1 (9 columns) | LexGLUE micro-F1 (9 columns) |
|---|---:|---:|---:|
| baseline | 0.2551 | 0.3331 | 0.9153 |
| balanced | 0.6156 | 0.6540 | 0.9107 |
| hybrid | 0.6333 | 0.6695 | 0.9126 |


The false-negative and false-positive trade-off remains substantial, especially for rare categories. Current scores are not calibrated probabilities. The near-threshold cue is a heuristic. Source sentences are available for inspection, but category explanations are general descriptions, not faithful model-feature attributions.

No runtime API calls or default input logging. A requested export includes the supplied text; users should store it appropriately. English input and a 100,000-character limit apply. An application of this model to new services, new document versions or other languages needs separate testing. The synthetic demo cannot establish domain generalization.

No outside-user results are available as of this package. Version the card as actual studies and model changes occur. After final evaluation, update test status with evidence rather than silently changing previous claims.
