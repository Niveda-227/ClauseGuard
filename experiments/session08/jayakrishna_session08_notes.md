# Session 08 evaluation notes (Jayakrishna)

Two questions this week, both on files already committed (no dataset download needed for either):
1. What do the new review cues show on the validation split? (`scripts/cue_eval.py`)
2. Does the mid-semester rule still say "keep the product direction"? (`scripts/decision_recheck.py`)

## 1. Review cues near a cut-off (`experiments/session08/cue_eval.md`)

The cues: an **uncertain** flag is less than 0.05 above its cut-off; a **possible** category is less than 0.05 below it and is not flagged. The margin was fixed before any result (`clauses/cues.py`).

- How often possible cues appear (honest column): 1.05 per 100 sentences. For a 16-sentence study document that is about one possible cue in every six documents, so the cue is rare.

- How many missed clauses they point to (honest column): 6 of the 77 missed labels have a possible cue, which is 7.8%. The other 71 missed clauses still show only "No category flagged".

- Are uncertain flags less reliable? 53.6% of uncertain flags are wrong, against 28.7% of the other flags. So an "uncertain" flag is a good warning: it is wrong about twice as often as a normal flag, and a user should check that sentence first.

- Which categories the possible cues help most and least: Unilateral termination has the most missed labels with a possible cue (2 of 15). Limitation of liability has the most possible cues (9) but points to only 1 of its 23 missed labels, and Unilateral change has 3 possible cues that point to none of its 10. Every count is tiny (Arbitration rests on 9 validation examples), so no category result is reliable.

- Pre-set rule and result: Result: RECONSIDER the cue display in Session 09 (coverage failed, volume passed). The rule needed possible cues to point to at least 10% of missed labels, and they reached 7.8%. They add only 1.05 per 100 sentences, well under the limit of 5. The rule and the margin were not changed.

## 2. Re-check of the mid-semester rule (`experiments/session08/decision_recheck.md`)

- Inputs: 6 participants (U002, U003, U004, U005, U006, U007). ClauseGuard 6 of 6 correct, manual 5 of 6, a gap of 16.67 points in ClauseGuard's favour. The model gate passed: honest macro-F1 0.6768 against 0.2551 for the baseline, a gain of 0.4217.

- Misled by wrong tags: 0. I read evidence/session05, session06 and session07 session_notes.md. In Session 06, U003 and U005 were asked directly whether they treated the wrong tags as true on the answer sentence, and both said no. U004 looked at the tags but answered from the sentence. In Session 07, how U006 and U007 used the tags was not observed, so 0 means none were seen misled, not that it was confirmed for every trial.

- Outcome: KEEP THE PRODUCT DIRECTION. This run covers Sessions 05 to 07 only. Ankan re-runs it after Niveda's Session 08 evidence is merged, and the report quotes his run.

## Limits

- Validation split only; the test split is not read. The product cut-offs were tuned on this same split, so the honest column is the one to quote.
- Pooled user results mix different tasks and two product versions; they are a pre-committed heuristic, not a statistical test.
- The cue_eval sensitivity table is reported only and was not used to choose the margin: a margin of 0.10 would cover 24.7% of missed labels but add 2.33 cues per 100 sentences. Picking it now, on this same split, would be tuning on validation, so it can only be a Session 09 candidate that needs new documents.
