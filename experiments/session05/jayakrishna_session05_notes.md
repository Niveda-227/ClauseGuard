# Per-category thresholds: leave-one-company-out estimate (Jayakrishna, Sep 27 2026)

## Decision rule, written before running the experiment

Recommend shipping per-category thresholds in Session 07 only if ALL of these hold for the leave-one-company-out row (not the in-sample row):
1. Macro-F1 is at least 0.02 higher than fixed 0.5.
2. No category's F1 drops by more than 0.05 compared with fixed 0.5.
3. Flags per 100 sentences rise by no more than 3 (more flags means more for users to check).
Otherwise keep the fixed 0.5 threshold and report the negative result.

## Results (validation split only; test split untouched)

| Decision rule | Macro-F1 | Micro-F1 | Flags / 100 sentences |
|---|---:|---:|---:|
| Fixed 0.5 (ships today) | 0.6333 | 0.6275 | 17.49 |
| Tuned and scored in-sample (optimistic) | 0.7244 | 0.7254 | 10.51 |
| Leave-one-company-out (honest) | 0.6768 | 0.6880 | 11.03 |

About 48% of the in-sample gain survives once you tune honestly (leave-one-company-out).
So roughly half of what looked like improvement was really just the model fitting to
quirks in the same data it was being scored on.

## Per category
Almost every category did better with tuned thresholds. Unilateral change improved the
most (0.506 to 0.654), Content removal too (0.540 to 0.607). Choice of law was the one
exception as it actually got slightly worse, 0.812 to 0.774. Arbitration barely counts as signal either way since there are only 9 positive examples in the whole validation set, so its F1 change (0.323 to 0.348) is really just a couple of sentences moving around, not a trend I'd trust.

## Threshold stability
Most categories picked roughly the same threshold no matter which companies were left
out — Jurisdiction and Choice of law barely moved at all. Arbitration is the outlier:
its "best" threshold ranged anywhere from 0.35 to 0.90 depending on the fold, which
makes sense given how few examples it has. I wouldn't lean on Arbitration's result being
real.

## One company in detail
I looked at an Airbnb sentence, validation:05797: "airbnb reserves the right to modify
these terms at any time in accordance with this provision." The correct label is just
Unilateral change. At the fixed 0.5 threshold, the model also flags Unilateral
termination (score 0.56) and that's wrong, since the sentence is about Airbnb changing the terms, not ending anyone's account. My guess is the model latched onto phrases like
"right to" and "at any time," which probably show up a lot in real termination clauses
too. The tuned threshold for Unilateral termination (0.60–0.70 across folds) would have
caught this and suppressed the false flag, while the real signal — Unilateral change at
0.99 — stays flagged no matter what threshold you pick.

## Decision against the rule
1. Macro-F1 gain: 0.0435, clears the 0.02 bar.
2. Worst per-category drop: Choice of law at 0.038, under the 0.05 limit.
3. Flags per 100 sentences actually went down (17.49 to 11.03), not up.

All three conditions hold, so by the rule I set before running this: **ship the tuned
thresholds in Session 07.** The Airbnb example is a good sanity check too, it's not
just numbers moving, it's a real sentence where tuning fixes a mistake a person reading
it wouldn't make. The one caveat I'd flag going into Session 07: don't trust Arbitration's
number much, it's built on 9 examples and swings all over the place depending on the
fold.

## Limits
Validation was already used once to pick the hybrid model in the first place, so even
this leave-one-company-out number is still a development estimate, not a final one. Ten
companies isn't a lot of folds either. The test split hasn't been touched and stays that
way until the model is actually frozen.