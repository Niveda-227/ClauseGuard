# Decision rule: fresh real Terms of Service (Session 10)

- **Date written:** 2026-11-04, **before any label of the fresh documents existed.** Machine-readable copy: [fresh_rule.json](fresh_rule.json). Evaluated by `scripts/fresh_eval.py`.
- **Owner:** Ameer (Product)
- **Why:** every model number so far comes from the UNFAIR-ToS validation split (10 companies). The mid-semester memo planned a domain-shift check on hand-labelled fresh documents for Sessions 10-12, and the Session 09 cue decision ([2026-10-28_cue_decision.md](2026-10-28_cue_decision.md)) said two ideas may only be tested on new documents, never chosen on validation: a 0.10 cue margin, and showing worth-a-look marks only for categories with no flag.

## The documents and the labels

- Three real, openly licensed Terms of Service from companies not in UNFAIR-ToS: 37signals (Basecamp), Cloudup and Crowdsignal (both Automattic), 376 sentences in total ([examples/fresh/SOURCES.md](../../examples/fresh/SOURCES.md)).
- Two annotators (Hemanth = A1, Jayakrishna = A2) label every sentence independently with [docs/LABELLING_GUIDE.md](../LABELLING_GUIDE.md). Each posts the fingerprint (SHA-256) of their finished labels in the team chat before the other's labels are on `main`.
- **Strict** answers: a category counts only when both annotators gave it. **Lenient:** when either did. **The rules below use strict.** Lenient is reported and decides nothing.

## The three rules (fixed now; never changed after the labels exist)

| Rule | Passes when | If it passes | If it fails |
|---|---|---|---|
| Domain shift | fresh macro-F1 (strict, over categories with at least one label) is no more than **0.15** below the validation honest macro-F1 in `experiments/session07/threshold_ship_eval.json` | HOLDS UP on fresh documents | DOMAIN SHIFT: treat it as the main risk in Session 11 |
| Cue margin 0.10 | possible cues at margin 0.10 reach at least **20%** of the missed labels **and** add at most **5 per 100 sentences** | ADOPT the 0.10 margin in Session 11 | KEEP the 0.05 margin |
| Zero-flag-only marks | worth-a-look marks kept only for categories with no flag in that document reach at least **40%** of the missed labels **and** add at most **20 per 100 sentences** (the Session 09 rule) | MAKE zero-flag-only the default in Session 11 | KEEP showing all marks, off-by-default toggle stays |

## What this rule cannot show

- Three documents and two annotators from the team: a small check. Two documents come from the same company.
- The annotators are not lawyers and the UNFAIR-ToS annotators were. Agreement (Cohen's kappa) is reported so readers can judge the labels.
- Few missed labels are expected, so coverage percentages can move a lot with one sentence. The counts are always reported next to the percentages.
