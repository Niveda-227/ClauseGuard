# Trained artifacts

The ZIP includes trusted model artifacts produced from the verified source data. `selected.joblib` is the current product model and `selected.json` is its manifest. Baseline, balanced and hybrid artifacts enable direct comparisons. Use the pinned environment to load them; train fresh artifacts when changing package versions.

Joblib can execute code during loading. Use only these supplied artifacts or models you trained and trust. The UI does not accept user-uploaded model files. Source data is fetched separately and cited in data/README.md.

A model update must be accompanied by matching manifest, evaluation output and release notes. Never report one artifact's metrics while showing another model without explaining the difference.
