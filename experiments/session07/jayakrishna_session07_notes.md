# Session 07: what shipping per-category thresholds changed (Jayakrishna, Data&Eval)

Source files: [threshold_ship_eval.md](threshold_ship_eval.md) (made by `python scripts/compare_thresholds.py` from committed files only) and [fragment_trial.md](fragment_trial.md) (made by `python scripts/fragment_trial.py`). Validation split only; the test split was not read.

## 1. Checks

Checks passed: same sentences, identical scores, app runs the evaluated tuned model, thresholds = Session 05 experiment. In plain words: the old and new models were scored on exactly the same 2,275 validation sentences, the model itself did not change (only the cut-offs did), and the model in the app is the one we evaluated.

## 2. The headline, honestly

Macro-F1 went from 0.6333 with the old fixed 0.5 cut-off to 0.6768 on the honest leave-one-company-out estimate. Wrong tags fell from 195 to 79, about 6 in 10 gone, but missed labels rose from 46 to 77, so 31 more annotated clauses now have no flag. The middle column (0.7244) must not be quoted as the result because the cut-offs were chosen on those same sentences, like marking your own exam.

## 3. Per category

Best Category: Limitation of liability had the biggest drop in wrong tags: 53 to 16 under the honest estimate. Its precision rose from 0.509 to 0.733.

Worst Category: Limitation of liability also lost the most clauses: recall fell from 0.821 to 0.657, and missed labels went from 12 to 23 out of 67. A user would notice that about one in three liability clauses now gets no flag. Unilateral termination was close behind (recall 0.898 to 0.746, missed 6 to 15).

Arbitration: Honest estimate: precision 0.286, recall 0.444, support 9. With only 9 examples in validation, one or two sentences moving changes the numbers a lot, so we should not trust this category's threshold or score.

## 4. Heading and short-fragment filter (trial promised in the mid-semester decision memo)

Fragment Result: no candidate passes the rule; do not ship a fragment filter. The closest was "8 words or fewer and no . ! ? ; : at the end": it hid 53 sentences, removed 2 wrong tags, 0 correct tags and 0 annotator labels, but the rule needed at least 5 wrong tags removed. The four word-count filters hid 0 sentences because no validation sentence has fewer than 6 words, and the ALL-CAPS filter also hid 0.

Fragment Limit: The trial only used the 10 validation companies, where no sentence is under 6 words, so it cannot tell us whether headings or short fragments are a problem in other documents or in the app's raw text. The one filter that hid anything (53 sentences) removed only 2 wrong tags.

## 5. What I recommend next

Try lower cut-offs for Limitation of liability and Unilateral termination only (they lost 20 recall labels between them) and re-run leave-one-company-out. It worked if honest recall for each goes back above 0.75 while their combined wrong tags stay under about 60 (now 16 + 25 = 41). Separately, keep the "no flag does not mean safe" message in the app, since 77 labels now get no flag.
