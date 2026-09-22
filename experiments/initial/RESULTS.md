# Actual initial validation results

**Run date:** September 10, 2026. **Split:** official validation, n=2,275. **Training:** 5,532 official training sentences. **Scale:** 0–1. All three models use fixed 0.5 thresholds and seed 641. These runs are AI-assisted implementation results, not completed semester team work or final-test scores.

| Model | 8-category macro-F1 | LexGLUE macro-F1 (9 columns) | LexGLUE micro-F1 (9 columns) |
|---|---:|---:|---:|
| baseline | 0.2551 | 0.3331 | 0.9153 |
| balanced | 0.6156 | 0.6540 | 0.9107 |
| hybrid | 0.6333 | 0.6695 | 0.9126 |


Selected for the included application: **hybrid**, by validation eight-category macro-F1.

Model SHA-256: `04713fbf6e23784a5d32e5cdd5fef459182408565bfe8a4fb6a9f10d53dbff76`.

The balanced model changes both n-gram range and class weighting compared with baseline. A future factorial ablation must separate those effects. Hybrid adds character features to balanced. Selection and repeated inspection make these development results. Final-test metrics remain uncomputed.

## Observed failure

The unweighted baseline has strong exact-match accuracy (0.9178) but poor eight-category macro-F1 (0.2551). It misses many rare positive labels. The selected hybrid improves category macro-F1 but has slightly lower nine-column micro-F1 than baseline, so improvement is not uniform across metrics.

Arbitration remains weak for hybrid (F1 0.3226; validation support 9). Inspect the prediction IDs and original context to distinguish genuine errors from annotation ambiguity. Do not invent case explanations without examining those examples.

## Verification

The checked core tests passed: see `test_results.txt`. They validate behavior and data contracts, not real-world legal accuracy or actual user satisfaction. The desktop GUI still needs visual verification on a desktop. `predictions.jsonl` files hold source IDs, labels and scores without copying full source clauses.

## Reproduction

Commands and settings are documented in the root README and `docs/IMPLEMENTATION.md`. Environment: Python 3.12.14, scikit-learn 1.8.0, NumPy 2.3.5, SciPy 1.17.0, joblib 1.5.3. Timing is single-batch inference in this environment and should not be treated as general hosting performance. SHA-256 manifests identify the saved artifacts.
