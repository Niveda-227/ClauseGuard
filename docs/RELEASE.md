# Release 1.0.0 (Session 12 freeze)

The product is frozen as **release 1.0.0** (git tag `v1.0.0`) before the UNFAIR-ToS test split is read. From the freeze to the final submission, the product files do not change: the demo, the last user study and the one-time test-split result all use exactly this release.

## What is frozen

`RELEASE.json` lists the fingerprint (SHA-256) of every product file:

- the desktop app (`app.py`) and the core package (`clauses/*.py`),
- the web app (`webapp/*.py` and `webapp/static/*`),
- the model `artifacts/selected.joblib` and its manifest `artifacts/selected.json` (the model ID, the per-category cut-offs, the training data),
- the pinned packages (`requirements.txt`).

Scripts, tests, documents, results and evidence are not product files: they can still change after the freeze.

## Check that a folder is the release

```bash
python scripts/check_release.py
```

The last line must be `THIS IS RELEASE 1.0.0`. Run it before every demo, before every user session and before the test-split run. If it says `NOT RELEASE 1.0.0`, it lists the files that differ: do not demo, run a study or read the test split on that folder.

## How it was made

`python scripts/make_release.py` wrote `RELEASE.json` and `experiments/session12/release_summary.json`. It refuses to run once the test split has been read (`experiments/test_exposure.jsonl`), so the freeze always comes first. After the release PR is merged, its merge commit on `main` is tagged `v1.0.0`.
