# What shipping per-category thresholds changed (Session 07)

2,275 validation sentences from 10 companies; 249 labels marked by the annotators (10.95 per 100 sentences). Test split not read. Scores identical between the two models (max difference 7.8e-16); only the thresholds changed.

| | Old product (fixed 0.5) | New product, tuned on this split (optimistic) | New product, leave-one-company-out (honest) |
|---|---:|---:|---:|
| Macro-F1 | 0.6333 | 0.7244 | **0.6768** |
| Micro-F1 | 0.6275 | 0.7254 | **0.6880** |
| Flags per 100 sentences | 17.49 | 10.51 | **11.03** |
| Correct tags | 203 | 177 | **172** |
| Wrong tags | 195 | 62 | **79** |
| Missed labels | 46 | 72 | **77** |

## Per category (old vs honest estimate)

| Category | Threshold | Support | Precision | Recall | Wrong tags | Missed labels |
|---|---:|---:|---|---|---|---|
| Limitation of liability | 0.75 | 67 | 0.509 → 0.733 | 0.821 → 0.657 | 53 → 16 | 12 → 23 |
| Unilateral termination | 0.70 | 59 | 0.520 → 0.638 | 0.898 → 0.746 | 49 → 25 | 6 → 15 |
| Unilateral change | 0.80 | 28 | 0.382 → 0.667 | 0.750 → 0.643 | 34 → 9 | 7 → 10 |
| Content removal | 0.80 | 32 | 0.476 → 0.708 | 0.625 → 0.531 | 22 → 7 | 12 → 15 |
| Contract by using | 0.80 | 18 | 0.562 → 0.682 | 1.000 → 0.833 | 14 → 7 | 0 → 3 |
| Choice of law | 0.65 | 18 | 0.929 → 0.923 | 0.722 → 0.667 | 1 → 1 | 5 → 6 |
| Jurisdiction | 0.55 | 18 | 0.783 → 0.818 | 1.000 → 1.000 | 5 → 4 | 0 → 0 |
| Arbitration | 0.80 | 9 | 0.227 → 0.286 | 0.556 → 0.444 | 17 → 10 | 4 → 5 |

New product model: `dafbb5470f2fb2678cae273eac7c23046bbad0487c7be247174a99a08ad493bd`. Old product model: `04713fbf6e23784a5d32e5cdd5fef459182408565bfe8a4fb6a9f10d53dbff76`.

Read the honest column. Fewer wrong tags came with more missed labels: a sentence the old model flagged correctly may now have no flag, which is why "no flag" must never be read as "safe".
