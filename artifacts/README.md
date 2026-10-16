# Trained artifacts

| File | What it is |
|---|---|
| `selected.joblib`, `selected.json` | **The product model**: the file the app and the command line load by default. Since Session 07 it is a byte-identical copy of `tuned.joblib` |
| `tuned.joblib`, `tuned.json` | The hybrid model with **per-category thresholds** tuned on the validation split (Session 07, `scripts/ship_thresholds.py`). Only the thresholds differ from `hybrid.joblib` |
| `hybrid.joblib`, `hybrid.json` | Word 1-2-gram + character 3-5-gram TF-IDF (term frequency-inverse document frequency) features, balanced logistic regression, fixed 0.5 thresholds. The product model until Session 06 |
| `balanced.joblib`, `baseline.joblib` (+ `.json`) | Comparison models (Session 04) |

Each `.json` (JavaScript Object Notation) manifest records the training data hash, the thresholds and their source, and `artifact_sha256`, the fingerprint of the `.joblib` file. A model's evaluation lives next to the experiment that produced it:

- `hybrid`: `experiments/session04/hybrid/metrics.json`
- `tuned` (the product since Session 07): `experiments/session07/tuned/metrics.json`. These validation numbers are **optimistic**, because the thresholds were chosen on that same split. The honest estimate is the leave-one-company-out result in `experiments/session05/threshold_cv.md`.

`python scripts/demo_check.py` confirms the app's model is byte-identical to the evaluated one.

Joblib can execute code during loading. Use only these supplied artifacts or models you trained and trust. The app does not accept user-uploaded model files. Source data is fetched separately and cited in `data/README.md`.

A model update must be accompanied by a matching manifest, evaluation output and release notes. Never report one artifact's metrics while showing another model without explaining the difference.
