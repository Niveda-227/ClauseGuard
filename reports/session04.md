---
team: ClauseGuard
session: "04"
date: "2026-09-22"
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
  value: 0.00
  previous: null
---

## Shipped this week

**Repository evidence:** [evidence 1](https://github.com/Niveda-227/ClauseGuard/pull/8), [evidence 2](https://github.com/Niveda-227/ClauseGuard/pull/9), [evidence 3](https://github.com/Niveda-227/ClauseGuard/pull/10), [evidence 4](https://github.com/Niveda-227/ClauseGuard/pull/11), [evidence 5](https://github.com/Niveda-227/ClauseGuard/pull/12), [evidence 6](https://github.com/Niveda-227/ClauseGuard/pull/13). The team confirms the linked work was merged through teammate-approved PRs and main requires one approving review.

The locally verified deliverable is ClauseGuard: an English Terms-of-Service (ToS) classifier that helps a user locate potentially concerning categories and inspect the original source passage. The following implementation is ready for team review and integration:

- A local [desktop app](../app.py) and [CLI](../clauses/cli.py) with text input, eight-category prediction, preserved source offsets and [HTML export](../clauses/export.py). The trained selected artifact is bundled; analysis needs no API key or data download.
- Three trained traditional NLP pipelines: unigram baseline, class-balanced word n-grams, and selected word/character hybrid. [Model code](../clauses/model.py), [artifacts](../artifacts/), [original September 10 selection record](../experiments/initial/selection.json).
- A September 22 [verification command](../scripts/verify_sep22.py) and actual [test log](../experiments/session04/test_results.txt), validating the pipeline and reproducing the three validation comparisons.
- An observer-operated [task timer](../clauses/task_timer.py), [study protocol](../USER_SESSION_QUICKSTART.md), anonymous record/summary utilities and report-finishing tools. These support actual data collection; they do not create fictional participants.

The model was originally generated September 10 and re-evaluated September 22. This report does not present the candidate comparisons as successive weeks of improvement. The GUI is included but still needs visual smoke testing on a desktop; CLI inference and HTML export were exercised locally.

## User evidence

- On 2026-09-22 one outside participant (U001, not a team member) used the running product in the desktop app after giving verbal consent. They completed task A1 on document A without the tool in a plain text editor, then task B1 on document B with ClauseGuard, each under a 180-second limit. The participant read the category list top to bottom before opening any source sentence, and hesitated at the sentence carrying three category tags.
- **Raw artifact**: [timestamped task records](../evidence/session04/tasks.csv), companion trial JSON files in [evidence/session04/](../evidence/session04/), and [summary](../evidence/session04/summary.json). The team must include these in this week's approved merge.
- ClauseGuard: 0/1 tasks correct within 180 seconds (0.00%), across 1 outside participant(s).
- Resulting change or documented next action: Opened an issue to make the source sentence the primary result and de-emphasise secondary category tags, because the participant treated all three tags on one sentence as established findings. (evidence: [evidence 1](https://github.com/Niveda-227/ClauseGuard/issues/14)).
- This is a small pilot on fictional documents, not a population estimate or validation of legal correctness.

## Metrics snapshot

**Product north-star:** 0.00% (0/1 ClauseGuard tasks correct within 180 seconds); previous `null` because this is the first recorded week. Same-session manual comparison, if collected, is in the raw summary; it is not last week's metric.

**Model development results:** fixed validation split, 2,275 sentences from 10 companies, disjoint from the 30 training companies / 5,532 training sentences. The 1,607-sentence final test split was not evaluated. All F1 scores below use a 0–1 scale.

| Model | Macro F1 (8) | Micro F1 (8) | Macro F1 (9) | Micro F1 (9) | Evidence |
|---|---:|---:|---:|---:|---|
| Baseline | 0.2551 | 0.3300 | 0.3331 | 0.9153 | [raw metrics](../experiments/session04/baseline/metrics.json) |
| Balanced | 0.6156 | 0.6084 | 0.6540 | 0.9107 | [raw metrics](../experiments/session04/balanced/metrics.json) |
| Hybrid (selected) | 0.6333 | 0.6275 | 0.6695 | 0.9126 | [raw metrics](../experiments/session04/hybrid/metrics.json) |

The 9-label convention adds a derived no-category label. Eight-category macro F1 is the model-selection metric: hybrid 0.6333 versus baseline 0.2551, a +0.3782 difference. These are same-split method comparisons, not a previous-week comparison. The first weekly prior metric remains unavailable rather than invented.

**Same model as the product?** Yes for the bundled app/CLI: `artifacts/selected.joblib` is byte-identical to the evaluated hybrid artifact. SHA-256: `04713fbf6e23784a5d32e5cdd5fef459182408565bfe8a4fb6a9f10d53dbff76`. Fixed threshold 0.5 per category, seed 641. [Verification record](../experiments/session04/verification.json) and [model manifest](../artifacts/selected.json).

The validation set was used to select among candidates, so these are development estimates, not unbiased final-test performance. The source archive is pinned by SHA-256 in [data.py](../clauses/data.py). This run used Python 3.12.14 and scikit-learn 1.8.0. Batch inference timing is recorded but is not end-to-end GUI latency.

## What did not work

- Hybrid **lost to the baseline on 9-label micro F1**: 0.9126 versus 0.9153, and exact match: 0.9081 versus 0.9178. Class balancing improves category recall while adding false positives. We selected by eight-category macro F1 and disclose this tradeoff.
- Arbitration remains weak: precision 0.2273, recall 0.5556, F1 0.3226 on only 9 positive validation examples. There are 17 false positives and 4 false negatives. Unilateral-change detection has 34 false positives and 7 false negatives. [Per-label metrics](../experiments/session04/hybrid/metrics.json) and [error counts/source IDs](../experiments/session04/error_analysis.json).
- A [four-case source audit](../experiments/session04/ERROR_NOTES.md) found an arbitration clause mislabeled as contract-by-using and a two-category sentence receiving no flag. One arbitration-topic sentence has no source label, so topic detection and the dataset annotation criterion may differ; this needs contextual review, not a claim that the annotation is wrong.
- 2,045 of 2,275 validation sentences have no target category. A high aggregate score can conceal failures on the categories users need; we therefore report per-category performance and macro F1.
- The environment has no desktop display, so automated pipeline tests do not establish visual GUI usability. Short fictional task documents also cannot establish usefulness on long real-world agreements.

## Challenges / blockers

Arbitration F1 is 0.3226 on only 9 validation positives, and six of the eight categories have precision below 0.60, so single sentences receive several labels and users see confident wrong tags. Per-category thresholds tuned on validation are the next experiment (owner: Jayakrishna, Session 05). Outside-user evidence is one participant on short fictional documents, so the product metric is directional only and needs more participants next week.

- A teammate must verify the final report and evidence are merged into main before 5:00 p.m. Eastern. This local script does not inspect GitHub or submit anything.

## Next week's goal

Reduce unsupported arbitration/unilateral-change flags while preserving recall, guided by the actual outside-user pilot. Inspect source error cases first, then compare a validation-only threshold experiment with the frozen current hybrid. Report gains or losses, use the selected artifact in the product, and repeat the task protocol with new participants or unseen tasks. Session 05 is due September 29 at 5:00 p.m. Eastern.

## Individual contributions

- Ameer (Product): Integrated and verified the initial ClauseGuard implementation (desktop app, CLI with HTML export, three trained classifiers, validation evaluation and tests), rewrote the README with real setup commands and measured results, and observed the user session; found confident false positives where a terms-change sentence is also flagged Unilateral termination at score 0.841. (evidence: [evidence 1](https://github.com/Niveda-227/ClauseGuard/issues/1), [evidence 2](https://github.com/Niveda-227/ClauseGuard/pull/8))
- Hemanth (Engineering): Added scripts/check_environment.py with tests, reporting Python and dependency versions, verifying the model file by SHA-256 against its manifest and probing Tk display availability; verified the desktop app on a real laptop with both study documents before the user session and documented a macOS SSL certificate failure that blocks the dataset download. (evidence: [evidence 1](https://github.com/Niveda-227/ClauseGuard/issues/2), [evidence 2](https://github.com/Niveda-227/ClauseGuard/pull/9))
- Jayakrishna (Data&Eval): Added scripts/build_error_report.py with tests and produced the per-category validation error dashboard, recomputing macro-F1 0.6333; inspected six error cases by source ID and found arbitration misses cluster at 0.36 to 0.41 just below the fixed threshold while a four-word section heading scores 0.745. (evidence: [evidence 1](https://github.com/Niveda-227/ClauseGuard/issues/3), [evidence 2](https://github.com/Niveda-227/ClauseGuard/pull/10))
- Niveda (Users&Research): Added clauses/session_capture.py with tests, recording which interface each real trial used plus an anonymous observer ID without changing the CSV schema; recruited an outside participant, ran the counterbalanced pilot under a 180-second limit and committed the contemporaneous anonymous records. (evidence: [evidence 1](https://github.com/Niveda-227/ClauseGuard/issues/4), [evidence 2](https://github.com/Niveda-227/ClauseGuard/pull/11), [evidence 3](https://github.com/Niveda-227/ClauseGuard/issues/6), [evidence 4](https://github.com/Niveda-227/ClauseGuard/pull/13))
- Ankan (Operations): Added scripts/check_report_links.py with tests, resolving every local Markdown link in the weekly report, rejecting paths outside the repository and flagging unresolved report fields; audited the report against the course template and verified branch protection, then assembled and finalized the Session 04 report from merged evidence. (evidence: [evidence 1](https://github.com/Niveda-227/ClauseGuard/issues/5), [evidence 2](https://github.com/Niveda-227/ClauseGuard/pull/12))

## Lean canvas changes (if any)

The current [lean canvas](../docs/lean_canvas.md) treats English-reading app users as the initial audience and manual reading/Find as the comparison. Distribution begins with a local app/HTML workflow. Inference has no metered API call, though setup, CPU and support have costs. The initial scope is eight source-defined review categories with original-text evidence; it does not promise detection of every contractual risk. The largest risk is that development F1 will not translate into useful clause-finding on unfamiliar documents. Outside-user validation remains unconfirmed; the canvas is a hypothesis, not proven demand.
