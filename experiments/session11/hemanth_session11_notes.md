# Session 11 engineering notes (Hemanth)

This week I made the product model rebuildable from a clean clone and checked it (`scripts/reproduce_model.py`), and I added a section to the model card whose numbers are checked by a test (`tests/test_model_card.py`). Every number below is filled from `experiments/session11/reproduce.json` by `scripts/fill_notes.py`; the words are mine.

## The rebuild

- Result: **REPRODUCED** (6 of 6 checks passed).
- Trained on 5532 sentences from 30 companies, checked on 2275 validation sentences.
- Fingerprint of the validation flags: `0e635d75ca4662bd4e5b0511f101117e78c3b0d14da76b16a22c03a9565cea3b`
- In a fresh clone of the repository (not my working folder): I cloned the repo into a fresh folder, ~/clauseguard_clean_check, and copied in only the dataset file. I ran the rebuild script there and it printed the same validation flags fingerprint as on my working copy, so the model rebuilds from the repository alone.

## What I learned

- Different versions of scikit-learn or numpy could change how the model trains, so the fingerprint might differ even with the same seed. Anyone rebuilding should install the versions pinned in requirements.
- The numbers in MODEL_CARD.md used to be typed by hand and could drift from the real results. Now a test compares each number on the card with experiments/session11/reproduce.json, so a stale number fails the test suite.

## Limits

- The rebuild is checked by its outputs (scores and flags), not by the file's bytes: a saved model file contains its creation time.
- It was checked on the train and validation splits only. The test split stays unread until the Session 12 freeze.

<!-- Numbers filled by scripts/fill_notes.py from the result files in experiments/. -->
