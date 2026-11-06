# Session 10 labelling notes (Hemanth, annotator A1)

I labelled every sentence of the three fresh Terms of Service in `examples/fresh/` with `docs/LABELLING_GUIDE.md`, on my own, without seeing Jayakrishna's labels or what the model says about these documents. The numbers below are filled from `experiments/session10/labels_A1.json` by `scripts/fill_notes.py`.

## What I labelled

- Sentences labelled: 376 (basecamp 156, cloudup 77, crowdsignal 143).
- Sentences with at least one category: 68. Marked unsure (saved with no category): 0.
- Time spent answering: about 7 minutes.
- Per category: Limitation of liability 21, Unilateral termination 18, Unilateral change 9, Content removal 5, Contract by using 9, Choice of law 1, Jurisdiction 1, Arbitration 7.
- Fingerprint, posted in the team chat on Wed Nov 4, 6:43 pm, before Jayakrishna's labels were on `main`: `5ee325d69f3abbd51a141ffff5264ba2d6b61aef94722a2abb915c91668f9c3e`

## Sentences that were hard to decide (words only)

- HARD 1: A sentence in Basecamp said the company could temporarily disable an account if its usage was significantly higher than other customers. I found it difficult to decide whether temporary suspension counted as Unilateral termination. I treated it as Unilateral termination because the company decides whether to restrict account access.
- HARD 2: A sentence in Crowdsignal said that continuing to use the software after changes to the agreement means accepting those changes. I labelled it both Unilateral change and Contract by using because it involves changes to the terms and acceptance through continued use.

## The labelling guide

- GUIDE: The guide could be clearer about temporary account suspensions and sentences that fit multiple categories. More examples distinguishing Unilateral termination from temporary access restrictions, and Unilateral change from Contract by using, would help make labelling more consistent.

## Limits

- I am a team member, not a lawyer, and the UNFAIR-ToS labels were made by legal experts. My labels alone are not the answer set: the evaluation uses only the categories both annotators gave (strict).
- Three documents from two companies is a small check.

<!-- Numbers filled by scripts/fill_notes.py from the result files in experiments/session10/. -->
