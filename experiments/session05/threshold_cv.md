# Per-category threshold experiment (Session 05)

Source: `experiments/session04/hybrid/predictions.jsonl` · 2275 validation sentences · 10 companies.
Final test split not read.

| Decision rule | Macro-F1 | Micro-F1 | Flags per 100 sentences |
|---|---:|---:|---:|
| Fixed 0.5 (ships today) | 0.6333 | 0.6275 | 17.49 |
| Tuned and scored on the same data (optimistic) | 0.7244 | 0.7254 | 10.51 |
| **Leave-one-company-out (honest)** | **0.6768** | **0.6880** | 11.03 |

## Per category: fixed 0.5 vs leave-one-company-out

| Category | Support | P (0.5) | R (0.5) | F1 (0.5) | P (LOCO) | R (LOCO) | F1 (LOCO) | Threshold range across folds |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| Limitation of liability | 67 | 0.509 | 0.821 | 0.629 | 0.733 | 0.657 | 0.693 | 0.75–0.85 |
| Unilateral termination | 59 | 0.520 | 0.898 | 0.658 | 0.638 | 0.746 | 0.688 | 0.60–0.70 |
| Unilateral change | 28 | 0.382 | 0.750 | 0.506 | 0.667 | 0.643 | 0.654 | 0.80–0.80 |
| Content removal | 32 | 0.476 | 0.625 | 0.540 | 0.708 | 0.531 | 0.607 | 0.70–0.80 |
| Contract by using | 18 | 0.562 | 1.000 | 0.720 | 0.682 | 0.833 | 0.750 | 0.70–0.85 |
| Choice of law | 18 | 0.929 | 0.722 | 0.812 | 0.923 | 0.667 | 0.774 | 0.65–0.70 |
| Jurisdiction | 18 | 0.783 | 1.000 | 0.878 | 0.818 | 1.000 | 0.900 | 0.55–0.55 |
| Arbitration | 9 | 0.227 | 0.556 | 0.323 | 0.286 | 0.444 | 0.348 | 0.35–0.90 |

A wide threshold range across folds means the tuned value depends on which companies it was tuned on, so it may not transfer to unseen documents.
