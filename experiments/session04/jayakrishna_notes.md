# Validation error analysis — 2026-09-22 (Jayakrishna)

Source: jayakrishna_error_dashboard.md, built from hybrid/predictions.jsonl. Model 04713fbf, validation split, n=2275, recomputed macro-F1 0.6333. Sentences below were recovered by ID from the pinned dataset. These are disagreements with the dataset annotation, not legal judgments. The final test split was not touched.

## Where the model is weakest

Arbitration (F1 0.3226), Unilateral change (0.5060) and Content removal (0.5405) are the three worst. Precision is the problem everywhere, not recall: six of the eight categories have precision below 0.60 while recall runs 0.56 to 1.00. Class balancing bought recall at the cost of many false positives, which matches what the app shows on the demo documents, where single sentences carry three labels.

## Why arbitration looks so bad

Only 9 positive examples in the whole validation split. With support that small, 4 misses drop recall to 0.56 and 17 false positives push precision to 0.23, so one or two decisions move the score a lot. The number is fragile, not a stable estimate of ability.

## Cases I inspected

**False negative, validation:07413 (Oculus), gold Arbitration, predicted nothing.** "you and oculus empower the arbitrator with the exclusive authority to resolve any dispute..." Arbitration scores 0.410, below the fixed 0.5 threshold. The clause is real and unambiguous; the threshold, not the ranking, caused the miss.

**False negative, validation:06087 (Airbnb), gold Arbitration, predicted nothing.** A CIETAC/Beijing clause that names arbitration four times, yet Choice of law (0.371) outranks Arbitration (0.361). The sentence is dominated by governing-law and court-relief wording, so features shared with choice-of-law and jurisdiction pull the decision away from the correct label. Both arbitration misses sit in a narrow 0.36 to 0.41 band.

**False positive, validation:06857 (Headspace), gold none, predicted Arbitration (0.745).** The "sentence" is the section heading "( b ) arbitration rules ." There is no obligation in it at all. The model is matching the topic word, not a clause. High confidence on a heading shows the scores are not calibrated confidence.

**False positive, validation:06513 (Supercell), gold Jurisdiction, also predicted Arbitration.** "...must be resolved exclusively by a court located in helsinki , finland ." Jurisdiction 0.554 and Arbitration 0.527 are nearly tied, even though a named court is the opposite of arbitration. Dispute-resolution vocabulary is shared across the two categories and the model has not learned what separates them.

**Paired errors in one document, validation:06178 and 06125 (Crowdtangle).** The genuine change clause ("crowdtangle may change these terms of service...") scores only 0.258 for Unilateral change and is missed. The neighbouring termination clause ("may terminate the license ... at any time at its discretion") is correctly flagged Unilateral termination (0.930) but also wrongly flagged Unilateral change (0.673). Surface cues such as "terms of service", "at any time" and "at its discretion" drive the prediction more than the power actually granted.

## What I would try next, and why

1. Per-category thresholds tuned on validation only. Every arbitration false negative I read sits at 0.36 to 0.41, so a lower arbitration threshold would recover them. It will also admit more false positives; the trade-off has to be measured, not assumed, and reported as a coverage/precision curve.
2. Exclude heading-like fragments. 06857 is a numbered heading of four words. A minimum-length or no-verb filter would remove a class of false positives without touching the model.
3. Treat jurisdiction, arbitration and choice-of-law confusion as one problem. 06513 and 06087 are both cases of those three categories competing. Worth a confusion analysis restricted to them.

## Limits of this analysis

Six sentences is an illustration, not a measurement. Validation was used to select among the three candidate models, so these numbers are development estimates and are optimistic. Counts show where errors are, not why; my explanations above are hypotheses from reading the text, not established causes. Some disagreements may reflect the dataset's annotation criteria rather than model error.
