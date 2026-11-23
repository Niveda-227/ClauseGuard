# Session 12 evaluation notes (Jayakrishna)

This week I read the UNFAIR-ToS test split once, with the frozen release and its shipped cut-offs, under the rule Ameer merged before (`docs/decisions/final_test_rule.json`). Every number below is filled from `experiments/session12/test_eval.json` by `scripts/fill_notes.py`; the words are mine.

## Result

- Test split: 1607 sentences from 10 companies, read once with release 1.0.0.
- test macro-F1 0.7626; honest validation 0.6768; difference +0.0858 (margin 0.05).
- **Result: HIGHER than the honest validation estimate**
- How the run went: I ran scripts/final_test.py exactly once, after the release was merged and tagged and the release check passed. Nothing went wrong, and the record check confirmed one reading.

## What the result shows, in words

- Against validation: The test macro-F1 is higher than the honest validation number, by more than the margin of `0.05`, and it is also a little higher than the optimistic validation number. So the leave-one-company-out estimate was on the cautious side and did not flatter the model. This is one reading of one split of ten companies, so I would not claim more than that.
- By category: Most of the gain comes from arbitration, which was very low on validation and is high on the test split, and from choice of law and content removal, which are also better. Jurisdiction is clearly worse on the test split. The other four categories are about the same as on validation. Arbitration, choice of law and jurisdiction have few test sentences, so those swings are noisy.
- Errors: On the test split the model makes about as many wrong tags as it misses labels (fifty-one wrong tags against fifty missed labels). The flag rate per hundred sentences is close to the validation one. This differs from the fresh documents of Session 10, where misses were far more common than wrong tags, so the shift to new kinds of documents still looks like the bigger risk than the UNFAIR-ToS test split.

## Limits

- One reading of one split: the test result has its own noise, especially for the categories with few test sentences.
- Nothing in the product was changed because of this result; the rule says so.

<!-- Numbers filled by scripts/fill_notes.py from the result files in experiments/. -->
