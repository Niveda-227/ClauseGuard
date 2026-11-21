# Session 12 engineering notes (Hemanth)

This week I froze the product as a release before the test split was read (`scripts/make_release.py`, `RELEASE.json`) and added a check that a folder is still that release (`scripts/check_release.py`). Every number below is filled from `experiments/session12/release_summary.json` by `scripts/fill_notes.py`; the words are mine.

## The release

- release 1.0.0: 28 product files, model dafbb5470f2f (tag `v1.0.0`).
- Model: `dafbb5470f2fb2678cae273eac7c23046bbad0487c7be247174a99a08ad493bd`.
- What is frozen, in my words: The product files are the desktop app (app.py), the web app (webapp), the code in clauses, the model artifacts/selected.joblib with its manifest artifacts/selected.json, and requirements.txt. Scripts, tests, documents and result files are not product files, because changing them cannot change what the product flags.
- The demo check on my laptop: The last line was READY FOR THE DEMO on my MacBook Air (macOS), and the web app showed the same result as the desktop app.

## What I learned

- Someone could edit a product file by accident, or run a demo from a different branch or with other package versions. check_release.py compares every product file with its fingerprint and says NOT RELEASE 1.0.0 with the files that differ; demo_check.py covers the package versions.

## Limits

- The release check compares files with their fingerprints. It cannot tell whether the installed package versions match `requirements.txt`; `scripts/demo_check.py` checks those.
- The tag `v1.0.0` is put on the merge commit of the release PR, after it is merged.

<!-- Numbers filled by scripts/fill_notes.py from the result files in experiments/. -->
