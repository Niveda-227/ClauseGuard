# Validation error dashboard

Model SHA-256: `04713fbf6e23784a5d32e5cdd5fef459182408565bfe8a4fb6a9f10d53dbff76`.
Sentences: 2275. Recomputed eight-category macro F1: **0.6333**.

Development-set diagnostics, sorted by lowest F1. This is not a final-test estimate or a legal judgment.

| Category | Gold positives | TP | FP | FN | Precision | Recall | F1 |
|---|---:|---:|---:|---:|---:|---:|---:|
| Arbitration | 9 | 5 | 17 | 4 | 0.2273 | 0.5556 | 0.3226 |
| Unilateral change | 28 | 21 | 34 | 7 | 0.3818 | 0.7500 | 0.5060 |
| Content removal | 32 | 20 | 22 | 12 | 0.4762 | 0.6250 | 0.5405 |
| Limitation of liability | 67 | 55 | 53 | 12 | 0.5093 | 0.8209 | 0.6286 |
| Unilateral termination | 59 | 53 | 49 | 6 | 0.5196 | 0.8983 | 0.6584 |
| Contract by using | 18 | 18 | 14 | 0 | 0.5625 | 1.0000 | 0.7200 |
| Choice of law | 18 | 13 | 1 | 5 | 0.9286 | 0.7222 | 0.8125 |
| Jurisdiction | 18 | 18 | 5 | 0 | 0.7826 | 1.0000 | 0.8780 |

## Cases to inspect

- **Arbitration** — FP IDs: validation:06040, validation:06513, validation:06857; FN IDs: validation:05731, validation:06087, validation:07413.
- **Unilateral change** — FP IDs: validation:05798, validation:06115, validation:06125; FN IDs: validation:05578, validation:06178, validation:06357.
- **Content removal** — FP IDs: validation:06114, validation:06155, validation:06202; FN IDs: validation:05578, validation:06003, validation:06004.
- **Limitation of liability** — FP IDs: validation:05570, validation:05613, validation:05614; FN IDs: validation:06264, validation:06614, validation:06846.
- **Unilateral termination** — FP IDs: validation:05573, validation:05628, validation:05757; FN IDs: validation:06003, validation:06004, validation:06006.
- **Contract by using** — FP IDs: validation:05731, validation:06193, validation:06259; FN IDs: none.
- **Choice of law** — FP IDs: validation:07450; FN IDs: validation:06090, validation:07419, validation:07420.
- **Jurisdiction** — FP IDs: validation:06094, validation:06095, validation:06096; FN IDs: none.

## Interpretation

FP means a predicted label absent from the source annotation. FN means a source label was missed. Counts do not establish why the model failed.
Inspect original clauses by ID using the pinned dataset. Topic mentions and source-annotated concerning clauses may differ; review context before questioning the annotation.
Add your own inspected examples and hypotheses in the PR. Do not change the final test split or count this report as outside-user evidence.
