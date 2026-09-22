# Validation error dashboard

Raw JSON predictions are hard to inspect in a review. This script turns the saved validation predictions into per-category TP/FP/FN counts, precision, recall and F1, and checks consistency with the existing metrics.

## Run

```bash
python scripts/build_error_report.py
python -m unittest discover -s tests -p 'test_jayakrishna_error_report.py' -v
```

## How it works

A false positive is a predicted category absent from the source labels; a false negative is a source label missed by the model. The dashboard sorts by lowest F1 so rare-category weaknesses stay visible.

The saved predictions are already in the base repository; this dashboard does not need the dataset or a new training run. To inspect full source clauses, use the existing pinned data downloader and `load_split('validation')` as shown in `experiments/session04/ERROR_NOTES.md`. Do not evaluate the final test set for this task.

## Research question

Inspect at least one false positive and one false negative by source ID. Record your interpretation and distinguish topic mentions from the dataset annotation criterion. The included model has arbitration F1 about 0.3226; explain its small support and error counts.

This is AI-assisted implementation material. Team members should record their actual review, adaptation and verification in the PR rather than claim unperformed work.
