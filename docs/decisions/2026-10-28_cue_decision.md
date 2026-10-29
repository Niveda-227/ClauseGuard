# Decision: what to do with the review cues after Session 08

- **Date:** 2026-10-28 (Session 09)
- **Decided by:** Ameer (Product)
- **Evidence:** [experiments/session08/cue_eval.md](../../experiments/session08/cue_eval.md) and `cue_eval.json`, validation split, honest (leave-one-company-out) column. The model and the cut-offs did not change.

## The evidence

The Session 08 pre-set rule was: keep the cue display if, in the honest column at margin 0.05, "possible" cues point to at least 10% of the missed labels **and** add at most 5 cues per 100 sentences.

| | Honest column, margin 0.05 | Rule |
|---|---:|---|
| Missed labels with a "possible" cue | 6 of 77 (7.8%) | at least 10%: **failed** |
| "Possible" cues per 100 sentences | 1.05 | at most 5: passed |
| Wrong share of "uncertain" flags | 53.6% | (information) |
| Wrong share of the other flags | 28.7% | (information) |

The rule's result was **RECONSIDER the cue display in Session 09**.

## The decision

1. **Keep "uncertain" as it is.** Flags marked "uncertain" were wrong 53.6% of the time, against 28.7% for the other flags. The marking tells the user something true: read these flags more carefully.
2. **Keep "possible" as it is, but stop presenting it as the way to find missed clauses.** It reaches only 6 of the 77 missed labels. It stays because it is cheap (1.05 cues per 100 sentences) and, in Session 08, it marked the answer sentence of task F1 as "Possible: Jurisdiction" ([study_doc_check.json](../../experiments/session08/study_doc_check.json)).
3. **This week's answer to missed clauses is the "Check it yourself" panel** in the web app and the HTML export ([clauses/absence.py](../../clauses/absence.py)): for each category, how many sentences were flagged and, under "Not flagged, but worth a look", the unflagged sentences that contain one of the category's search words. It is labelled as word matches, not model predictions, and it changes no flag, score or cut-off.
4. **A wider cue margin is not chosen.** At margin 0.10 the "possible" cue would reach 19 of 77 missed labels (24.7%) on validation. That number came from the same split, so it cannot pick the margin. Margin 0.10 is only a **Session 10 candidate**, to be tested on fresh hand-labelled documents. It must never be chosen on the validation split.

## The rule for the search words, set before they are measured

The search words in `clauses/absence.py` were written on 2026-10-27 from the category definitions only, before any validation run, and must not be edited to improve a validation result. `scripts/hint_eval.py` (Session 09) measures them on the validation split with this rule:

> The "Not flagged, but worth a look" list is **KEPT** if, in the honest column, (a) the marks reach **at least 40%** of the missed labels **and** (b) the marks add **at most 20 per 100 sentences**. Otherwise it is **RECONSIDERED in Session 10**.

A "mark" is a sentence that is not flagged for a category but contains one of that category's search words. A "missed label" is an annotator label that gets no flag.

## What would change this decision

- If participants in the Session 09 absence tasks ignore the panel or are confused by it, the panel's wording or placement is reconsidered in Session 10, whatever `hint_eval.py` shows.
- If the Session 10 fresh documents show that the panel's marks are mostly noise there, the panel is changed. Any change is tested on those new documents, not chosen on validation.
