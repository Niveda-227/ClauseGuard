# Session 11 evaluation notes (Jayakrishna)

This week I compared 12 model configurations on the validation split with the rule Ameer froze before the ablation was first run and merged before the script existed (`docs/decisions/final_model_rule.json`). Every number below is filled from `experiments/session11/ablation.json` by `scripts/fill_notes.py`; the words are mine.

## Result

- Sanity check (the retrained shipped model reproduces the product model): passed before anything was measured.
- best hybrid / balanced / per_category 0.6768; shipped 0.6768; gain 0.0000 (a switch needs at least 0.02).
- Best configuration other than the shipped one: word / balanced / per_category, honest macro-F1 0.6563, against 0.6768 for the shipped model.
- **Result: KEEP the shipped model for the final release**

## What the table shows, in words

- Features: Using both words and characters is best. Words only comes second and characters only third, both clearly lower. Words only is better on two categories (contract by using and arbitration), but it loses on unilateral change and several others, so the combined version wins overall. Characters only catches wording variations but flags more sentences for a lower score.
- Class weighting: Without balanced weights every configuration gets worse, and the drop is huge when the cut-off is also fixed. The model flags far fewer sentences. I think this is because rare categories have few examples, so without extra weight the model leans towards “no clause” and its scores rarely pass the cut-off. Per-category cut-offs rescue part of this, which is why the drop is smaller there.
- Cut-offs: On validation, one cut-off per category beats a fixed `0.5` for every feature set, because categories have very different score ranges, and a fixed cut-off flags too many sentences. On the fresh documents the order is reversed: the fixed `0.5` versions score higher there.
- The fresh-documents column (reported only): The configurations that flag more sentences do better on the fresh documents, which fits the Session 10 finding that the shipped model mostly misses clauses on new documents. But the labels were not made independently and there are only three documents, so I treat this as a hint for Session 12, not a reason to switch, and the rule uses validation only.

## Limits

- Validation split only; the test split stays unread until the Session 12 freeze. Choosing among 12 configurations on one split flatters the best one; the margin of 0.02 guards against switching on noise.
- The rule, the grid and the margins were not changed after the results existed.

<!-- Numbers filled by scripts/fill_notes.py from the result files in experiments/. -->
