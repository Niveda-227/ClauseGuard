---
team: ClauseGuard
session: "10"
date: "2026-11-10"
members:
  - name: Ameer
    github: sohail-umd
    hat: Product
  - name: Hemanth
    github: hreddy14
    hat: Engineering
  - name: Jayakrishna
    github: Jayakrishna-Reddy
    hat: Data&Eval
  - name: Niveda
    github: Niveda-227
    hat: Users&Research
  - name: Ankan
    github: royak747
    hat: Operations
north_star:
  metric: "Correct clause-finding tasks completed within 180 seconds (%)"
  value: 100.00
  previous: 100.00
---

## Shipped this week

**Merged this week:** [PR #79](https://github.com/Niveda-227/ClauseGuard/pull/79), [PR #80](https://github.com/Niveda-227/ClauseGuard/pull/80), [PR #81](https://github.com/Niveda-227/ClauseGuard/pull/81), [PR #82](https://github.com/Niveda-227/ClauseGuard/pull/82), [PR #83](https://github.com/Niveda-227/ClauseGuard/pull/83). Every PR was approved by a teammate before merge; `main` requires one approving review.

This week's question, from the mid-semester decision memo: does the model hold up on real Terms of Service it has never seen? Until now every model number came from the UNFAIR-ToS validation split.

* Three fresh, real, openly licensed Terms of Service from companies that are not in UNFAIR-ToS (37signals Basecamp, Cloudup and Crowdsignal; 376 sentences), each pinned to a source commit with its licence and SHA-256 fingerprint ([examples/fresh/SOURCES.md](../examples/fresh/SOURCES.md), [manifest.json](../examples/fresh/manifest.json), [scripts/fresh_docs.py](../scripts/fresh_docs.py)).
* A labelling guide for the eight categories and a labelling tool that shows one sentence at a time, exactly as the app splits the document ([docs/LABELLING_GUIDE.md](../docs/LABELLING_GUIDE.md), [clauses/labelling.py](../clauses/labelling.py)). Hemanth and Jayakrishna labelled every sentence on their own, and each posted the fingerprint of their finished labels in the team chat before the other's labels were on `main` ([data/fresh_labels/](../data/fresh_labels/)).
* The rules for judging the model on these labels, written before any label existed ([docs/decisions/2026-11-04_fresh_documents_rule.md](../docs/decisions/2026-11-04_fresh_documents_rule.md), [fresh_rule.json](../docs/decisions/fresh_rule.json)).
* A label checker and an agreement measure between the two annotators ([scripts/check_labels.py](../scripts/check_labels.py), [scripts/label_agreement.py](../scripts/label_agreement.py), [label_agreement.md](../experiments/session10/label_agreement.md)).
* The shipped model on the fresh documents, with the three pre-set rules: [fresh_eval.md](../experiments/session10/fresh_eval.md) ([scripts/fresh_eval.py](../scripts/fresh_eval.py)).
* In the web app's "Check it yourself" panel, a switch "Only for categories with no flag", off by default. Whether it becomes the default was decided by the pre-set rule on the fresh documents, not on validation.
* Study tasks I1 and J1 on two of the fresh documents ([tasks_v5.json](../examples/study/tasks_v5.json), [study_doc_check.json](../experiments/session10/study_doc_check.json)).

The model running in the product did not change this week. It is still `dafbb5470f2fb2678cae273eac7c23046bbad0487c7be247174a99a08ad493bd`, the hybrid model with per-category cut-offs shipped in Session 07.

## User evidence

- **Raw artifact**: [task records](../evidence/session10/tasks.csv), [trial files and notes](../evidence/session10/), [summary](../evidence/session10/summary.json). Protocol `sep29_v2`.
- ClauseGuard: 2/2 ClauseGuard tasks correct within 180 seconds (100.00%), 2 outside participant(s), median 46.0 s.
- Manual comparison: 2/2 manual tasks correct within the limit (100.00%), median 78.5 s.
- Participants: U014, U015. The sessions took place on November ninth, two thousand twenty-six. The participants were new outside participants who were not on the team and had not taken part in Sessions zero four to zero nine. They were two classmates of the observer, recruited in person by the observer.
- The two tasks, both on real documents for the first time. **I1** asks whether the company can raise the price for customers who already pay, and how much notice it must give (Basecamp terms, 156 sentences). The model does not flag the answer sentence (Unilateral change score 0.62, cut-off 0.80), and the panel does not list it as worth a look; the one sentence it flags for Unilateral change is about changing the services, not prices. **J1** asks whether the company can end your access without warning (Crowdsignal terms, 143 sentences). The model flags the answer sentence (Unilateral termination score 0.80, cut-off 0.70).

| Participant | Task | Condition | Interface | Correct within the limit | Seconds |
|---|---|---|---|---|---:|
| U014 | I1 | ClauseGuard | web | yes | 51.718 |
| U014 | J1 | manual | text_editor | yes | 73.729 |
| U015 | J1 | ClauseGuard | web | yes | 40.33 |
| U015 | I1 | manual | text_editor | yes | 83.177 |

- I1 with the web app: The participant first reviewed the flagged sentence seventy-two, kept reading, searched for pricing-related information, and answered that the company can change prices for existing customers and must give at least thirty days notice by email. Whether they read unflagged sentences or opened the Check it yourself panel was not observed.
- J1 with the web app: The participant reviewed the flagged termination section and answered that the company can suspend or terminate access at its discretion, with or without notice, and does not have to warn first.
- Manual trials: For the manual trial on task J1, the participant searched the document for termination-related terms using browser search and answered that the company can suspend or terminate access without notice and does not have to warn first. For the manual trial on task I1, the participant searched the document for pricing-related information using browser search and answered that the company can raise prices for existing customers with at least thirty days notice by email.
- Resulting change or next action: Because this is a small pilot on two documents, no immediate product change was triggered, and the team will treat domain shift as the main risk in Session 11. (evidence: [issue #77](https://github.com/Niveda-227/ClauseGuard/issues/77), [PR #83](https://github.com/Niveda-227/ClauseGuard/pull/83), [PR #81](https://github.com/Niveda-227/ClauseGuard/pull/81))
- This is a small pilot on two real documents, not a population estimate or a check of legal correctness.

## Metrics snapshot

**Product north-star:** 100.00% this week; previous 100.00%.

The previous value is Session 09 (absence tasks on short fictional documents). This week's tasks are on long real documents, so the two values are not directly comparable.

**Do the two annotators agree?** (376 sentences, three documents.) Source: [label_agreement.md](../experiments/session10/label_agreement.md). Cohen's kappa corrects agreement for the agreement two people would reach by chance: 1 is perfect, 0 is no better than chance; it is not defined for a category neither annotator gave.

| Category | Hemanth (A1) | Jayakrishna (A2) | Both (strict) | Either (lenient) | Cohen's kappa |
|---|---:|---:|---:|---:|---:|
| Limitation of liability | 21 | 21 | 21 | 21 | 1.00 |
| Unilateral termination | 18 | 23 | 18 | 23 | 0.87 |
| Unilateral change | 9 | 15 | 9 | 15 | 0.74 |
| Content removal | 5 | 6 | 4 | 7 | 0.72 |
| Contract by using | 9 | 14 | 9 | 14 | 0.78 |
| Choice of law | 1 | 1 | 1 | 1 | 1.00 |
| Jurisdiction | 1 | 2 | 1 | 2 | 0.67 |
| Arbitration | 7 | 7 | 7 | 7 | 1.00 |

Pooled kappa over all categories and sentences: 0.87. The two annotators gave different categories to 20 of the 376 sentences. Strict answers (both gave the category): 70; lenient answers (either gave it): 90. The rules below use the strict answers only.

**The shipped model on the fresh documents.** Source: [fresh_eval.md](../experiments/session10/fresh_eval.md). Same model and cut-offs as the product. Macro-F1 is averaged over the categories that have at least one answer (fixed in the rule before any label existed).

| | Strict answers (both annotators) | Lenient answers (either) |
|---|---:|---:|
| Macro-F1 | 0.4139 | 0.3606 |
| Answer labels | 70 | 90 |
| Flags | 33 | 33 |
| Correct tags | 22 | 22 |
| Wrong tags (a flag the answers do not have) | 11 | 11 |
| Missed labels (an answer with no flag) | 48 | 68 |
| Flags per 100 sentences | 8.78 | 8.78 |

For comparison, the honest validation macro-F1 of the same model is 0.6768 ([threshold_ship_eval.md](../experiments/session07/threshold_ship_eval.md)). Per category, with the strict answers:

| Category | Answers | Flags | Correct | Wrong | Missed | F1 |
|---|---:|---:|---:|---:|---:|---:|
| Limitation of liability | 21 | 11 | 7 | 4 | 14 | 0.44 |
| Unilateral termination | 18 | 11 | 7 | 4 | 11 | 0.48 |
| Unilateral change | 9 | 4 | 2 | 2 | 7 | 0.31 |
| Content removal | 4 | 2 | 1 | 1 | 3 | 0.33 |
| Contract by using | 9 | 3 | 3 | 0 | 6 | 0.50 |
| Choice of law | 1 | 1 | 1 | 0 | 0 | 1.00 |
| Jurisdiction | 1 | 0 | 0 | 0 | 1 | 0.00 |
| Arbitration | 7 | 1 | 1 | 0 | 6 | 0.25 |

**Help for missed clauses on the fresh documents** (strict answers):

| What the user sees | How many | Per 100 sentences | Missed labels reached |
|---|---:|---:|---:|
| "Possible" cue, margin `0.05` (the product today) | 6 | 1.60 | 2 of 48 (4.2%) |
| "Possible" cue, margin `0.10` (tested) | 11 | 2.93 | 4 of 48 (8.3%) |
| Worth-a-look marks, all categories (the product today) | 64 | 17.02 | 18 of 48 (37.5%) |
| Worth-a-look marks, only categories with no flag (tested) | 11 | 2.93 | 1 of 48 (2.1%) |

**The three rules, fixed on 2026-11-04 before any label existed** (strict answers):
- Domain shift: fresh macro-F1 0.4139 against 0.6768 on validation, a drop of 0.2629 (the limit is 0.15). **Result: DOMAIN SHIFT: treat it as the main risk in Session 11.**
- Cue margin `0.10`: the cues reach 8.3% of the missed labels (4 of 48), 2.93 per 100 sentences (needs at least 20% and at most 5 per 100). **Result: KEEP the 0.05 margin.**
- Marks only for categories with no flag: the marks reach 2.1% of the missed labels (1 of 48), 2.93 per 100 sentences (needs at least 40% and at most 20 per 100). **Result: KEEP showing all marks, off-by-default toggle stays.**

**Model development results** (validation split, 2275 sentences, 10 companies; final test split not evaluated). The model did not change this week. Honest leave-one-company-out macro-F1 0.6768, against 0.6333 with the fixed `0.5` cut-off used before Session 07 ([threshold_ship_eval.md](../experiments/session07/threshold_ship_eval.md)).

**Same model as the product?** Yes. `artifacts/selected.joblib`, SHA-256 `dafbb5470f2fb2678cae273eac7c23046bbad0487c7be247174a99a08ad493bd`, is the model the fresh-document check ran and every ClauseGuard trial this week used.

## What did not work

- **Errors on the fresh documents:** The model mostly misses clauses and rarely flags the wrong thing, struggling with plain conversational wording, arbitration rules, class actions, and reason-giving change sentences, while its wrong tags mostly come from section headings or confusing service modifications with termination.
- **Where the annotators disagreed:** Nearly all disagreements followed a pattern where one annotator added a second category, mostly between Contract by using and Unilateral change or concerning frozen accounts and deleted content—because one annotator read each sentence together with the surrounding clause while the other read each sentence by itself.
- **Wrong answers in the study:** No wrong answers were recorded this week.
- **Limits of this check:** three documents, two of them from the same company, and two annotators from the team who are not lawyers (the UNFAIR-ToS annotators were legal experts). With so few answers, one sentence can move a percentage a lot; the counts are always given next to the percentages.

## Challenges / blockers

The main challenges this week were scheduling the two annotators and completing the independent labelling within a tight window while maintaining strict separation of their work. To keep the two sets of labels independent, each annotator posted the fingerprint of their finished labels before the other's labels were on `main`; the fingerprints in [labels_A1.json](../experiments/session10/labels_A1.json) and [labels_A2.json](../experiments/session10/labels_A2.json) match the ones posted.

## Next week's goal

Session 11: choose the final model on the validation split only, with an ablation table (word-only, character-only and the hybrid; class weighting on and off; fixed and per-category cut-offs) and a selection rule written before the first run. Apply this week's pre-set results in the product: KEEP the 0.05 margin; KEEP showing all marks, off-by-default toggle stays. The domain-shift result (DOMAIN SHIFT: treat it as the main risk in Session 11) is carried into the final report.

## Individual contributions

- Ameer (Product): Chose three fresh, real, openly licensed Terms of Service from companies outside UNFAIR-ToS, wrote the labelling guide, the labelling tool and the rules for judging the model before any label existed, and added the "Only for categories with no flag" switch to the web app. (evidence: [issue #74](https://github.com/Niveda-227/ClauseGuard/issues/74), [PR #79](https://github.com/Niveda-227/ClauseGuard/pull/79))
- Hemanth (Engineering): Labelled every sentence of the fresh documents as the first annotator, and added the label checker, the agreement measure between the two annotators and the notes filler. (evidence: [issue #75](https://github.com/Niveda-227/ClauseGuard/issues/75), [PR #80](https://github.com/Niveda-227/ClauseGuard/pull/80))
- Jayakrishna (Data&Eval): Labelled every sentence of the fresh documents as the second annotator, and measured the shipped model on them with the three pre-set rules (domain shift, cue margin, marks only for categories with no flag). (evidence: [issue #76](https://github.com/Niveda-227/ClauseGuard/issues/76), [PR #81](https://github.com/Niveda-227/ClauseGuard/pull/81))
- Niveda (Users&Research): Prepared study tasks I1 and J1 on two of the fresh real documents and ran the Session 10 study with new outside participants on the web app. (evidence: [issue #77](https://github.com/Niveda-227/ClauseGuard/issues/77), [PR #82](https://github.com/Niveda-227/ClauseGuard/pull/82), [PR #83](https://github.com/Niveda-227/ClauseGuard/pull/83))
- Ankan (Operations): Wrote the Session 10 report with every number filled from its source file, and updated the lean canvas. (evidence: [issue #78](https://github.com/Niveda-227/ClauseGuard/issues/78), [PR #84](https://github.com/Niveda-227/ClauseGuard/pull/84))

## Lean canvas changes (if any)

Updated [docs/lean_canvas.md](../docs/lean_canvas.md): "Current evidence" now points to the Session 10 check of the shipped model on fresh real Terms of Service from companies outside UNFAIR-ToS ([fresh_eval.md](../experiments/session10/fresh_eval.md)). This week's result: DOMAIN SHIFT: treat it as the main risk in Session 11 (strict macro-F1 0.4139 against 0.6768 on validation). The biggest risk stays the same: validation performance may not carry over to unfamiliar documents, and this week is the first direct measurement of it. The target user, value proposition and cost did not change.
