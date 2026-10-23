# Review cues near a cut-off: what they show (Session 08)

Product model `dafbb5470f2f` on the validation split (2,275 sentences). Margin 0.05 (`clauses/cues.py`, fixed in advance). The test split is not read.

| | Product cut-offs (optimistic) | Leave-one-company-out (honest) |
|---|---:|---:|
| Annotator labels | 249 | 249 |
| Flags | 239 | 251 |
| Missed labels (annotator label, no flag) | 72 | 77 |
| Possible cues | 31 | 24 |
| Possible cues per 100 sentences | 1.36 | 1.05 |
| Possible cues that are annotator labels | 4 | 6 |
| Missed labels with a possible cue | 4 | 6 |
| Share of missed labels with a possible cue | 0.0556 | 0.0779 |
| Sentences with any cue, per 100 | 2.51 | 2.29 |
| Uncertain flags | 26 | 28 |
| Wrong share of uncertain flags | 0.3077 | 0.5357 |
| Wrong share of the other flags | 0.2535 | 0.287 |

**Per category (honest column):**

| Category | Missed labels | Possible cues | Missed labels with a possible cue | Uncertain flags |
|---|---:|---:|---:|---:|
| Limitation of liability | 23 | 9 | 1 | 6 |
| Unilateral termination | 15 | 6 | 2 | 8 |
| Unilateral change | 10 | 3 | 0 | 5 |
| Content removal | 15 | 1 | 1 | 3 |
| Contract by using | 3 | 1 | 1 | 2 |
| Choice of law | 6 | 1 | 1 | 0 |
| Jurisdiction | 0 | 1 | 0 | 2 |
| Arbitration | 5 | 2 | 0 | 2 |

**Sensitivity only (honest column; never used to choose the margin):**

| Margin | Possible cues per 100 sentences | Share of missed labels with a possible cue |
|---:|---:|---:|
| 0.05 | 1.05 | 0.0779 |
| 0.03 | 0.53 | 0.026 |
| 0.10 | 2.33 | 0.2468 |

Rule set before running: KEEP if, honest column at margin 0.05: possible cues point to at least 10% of missed labels AND add at most 5 per 100 sentences.

**Result:** RECONSIDER the cue display in Session 09 (coverage failed, volume passed).

Validation split only; the test split is never read. Margins other than the product margin are sensitivity checks, not candidates. No sentence text is stored.
