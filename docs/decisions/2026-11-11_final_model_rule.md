# Decision rule: the final model (Session 11)

- **Date written:** 2026-11-10, when the Session 11 kit was prepared, **before the ablation was first run.** The ablation was then dry-run once on 2026-11-10 to check the kit (its output is in the Session 11 runbooks), after this rule was frozen. Merged on `main` before `scripts/ablation.py` was added, and never changed after. Machine-readable copy: [final_model_rule.json](final_model_rule.json). Evaluated by `scripts/ablation.py`.
- **Owner:** Ameer (Product)
- **Why:** the model has not changed since Session 07. Before the release is frozen in Session 12 (when the test split is read once), we check whether a simpler or different configuration would do better, using the validation split only.

## What is compared (12 configurations)

| Part | Options |
|---|---|
| Features | word 1-2-grams; character 3-5-grams; both together (hybrid, shipped) |
| Class weighting | balanced (shipped); none |
| Cut-offs | one per category, tuned on validation (shipped); fixed 0.5 |

Every configuration is trained on the train split only with the same classifier (one logistic regression per category, seed 641). Its score is the **honest** validation macro-F1: for tuned cut-offs, leave-one-company-out (each company's cut-offs are tuned on the other nine); for fixed 0.5, nothing is tuned.

## The rule (fixed now; never changed after a result exists)

- **Keep** the shipped configuration (hybrid, balanced, per-category cut-offs) unless another configuration's honest macro-F1 is **at least 0.02 higher**.
- If one or more are, choose the highest. Among configurations **within 0.005** of the highest, choose the simplest (word or character before hybrid; fixed 0.5 before tuned; no weighting before balanced).
- Result texts: "KEEP the shipped model for the final release" or "SWITCH to ... at the Session 12 freeze". A switch is not shipped during Session 11, so this week's study runs on the same build.

## Reported, but deciding nothing

- Micro-F1 and flags per 100 sentences.
- Macro-F1 on the three Session 10 fresh documents (strict answers). Those labels were not made independently (see [reports/session10.md](../../reports/session10.md)), so they cannot decide anything.
- Training time (printed only, not saved: it differs on every laptop).

## Checks and limits

- The ablation first retrains the shipped configuration and checks that it reproduces the committed validation predictions of the product model; if not, it stops.
- Comparing 12 configurations on the same split makes the best one look a little better than it is; the 0.02 margin guards against switching on noise, and the Session 12 test-split run is the unbiased number.
- A contextual model (for example sentence embeddings) is not a candidate: it cannot be installed offline on every laptop.

## Interface decision for the final release (from Sessions 09 and 10)

- **Check it yourself panel:** keep, with all worth-a-look marks shown (Session 10 rule: KEEP showing all marks; the "Only for categories with no flag" switch stays off by default).
- **Possible cue:** keep the 0.05 margin (Session 10 rule: KEEP the 0.05 margin).
- **Domain shift** is the main risk (Session 10: strict macro-F1 on fresh documents well below validation). The web app now says so in plain words above the findings, so users read the document and do not rely on "no flag" alone.
