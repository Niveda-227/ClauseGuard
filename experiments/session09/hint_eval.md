# Do the search words reach the clauses the model misses? (Session 09)

Product model `dafbb5470f2f` on the validation split (2,275 sentences). Search words: `clauses/absence.py` (SHA-256 of the list `23a25b09f82f`), written before any validation run. The test split is not read.

| | Product cut-offs (optimistic) | Leave-one-company-out (honest) |
|---|---:|---:|
| Annotator labels | 249 | 249 |
| Flags | 239 | 251 |
| Missed labels (annotator label, no flag) | 72 | 77 |
| Marks (not flagged, contains a search word) | 727 | 720 |
| Marks per 100 sentences | 31.96 | 31.65 |
| Sentences with any mark, per 100 | 27.74 | 27.52 |
| Missed labels with a mark | 34 | 39 |
| Percent of missed labels with a mark | 47.2 | 50.6 |
| Marks that are annotator labels | 34 | 39 |
| Percent of marks that are annotator labels | 4.7 | 5.4 |

**Per category (honest column):**

| Category | Missed labels | Marks | Missed labels with a mark |
|---|---:|---:|---:|
| Limitation of liability | 23 | 183 | 16 |
| Unilateral termination | 15 | 65 | 5 |
| Unilateral change | 10 | 87 | 3 |
| Content removal | 15 | 50 | 5 |
| Contract by using | 3 | 130 | 3 |
| Choice of law | 6 | 21 | 2 |
| Jurisdiction | 0 | 49 | 0 |
| Arbitration | 5 | 135 | 5 |

Rule set before running: KEEP if, honest column: marks reach at least 40% of missed labels AND add at most 20 per 100 sentences.

**Result:** RECONSIDER the worth-a-look list in Session 10 (coverage passed, volume failed).

Validation split only; the test split is never read. No sentence text is stored. UNFAIR-ToS labels only potentially unfair clauses, so many marks are on-topic but fair sentences.
