---
team: ClauseGuard
session: "04"
date: "2026-09-22"
members:
  - name: Ameer
    github: TODO
    hat: Product
  - name: Hemanth
    github: TODO
    hat: Engineering
  - name: Jayakrishna
    github: TODO
    hat: Data&Eval
  - name: Niveda
    github: TODO
    hat: Users&Research
  - name: Ankan
    github: TODO
    hat: Operations
north_star:
  metric: "Correct clause-finding tasks completed within 180 seconds (%)"
  value: null
  previous: null
---

> DRAFT — technical work verified September 22; real GitHub handles, reviewed merges, individual contributions and outside-user evidence await the team. This is AI-assisted preparation, not proof of student work or a submitted report.

## Shipped this week

**Repository status: PENDING team merge and approving review.** No remote repository has been inspected. Before submission, add the real issue, approved PR and merge-commit links here.

The locally verified deliverable is ClauseGuard: an English Terms-of-Service classifier that helps a user locate potentially concerning categories and inspect the original source passage. The following implementation is ready for team review and integration:

- A local [desktop app](../app.py) and [CLI](../clauses/cli.py) with text input, eight-category prediction, preserved source offsets and [HTML export](../clauses/export.py). The trained selected artifact is bundled; analysis needs no API key or data download.
- Three trained traditional NLP pipelines: unigram baseline, class-balanced word n-grams, and selected word/character hybrid. [Model code](../clauses/model.py), [artifacts](../artifacts/), [original September 10 selection record](../experiments/initial/selection.json).
- A September 22 [verification command](../scripts/verify_sep22.py) and actual [test log](../experiments/session04/test_results.txt), validating the pipeline and reproducing the three validation comparisons.
- An observer-operated [task timer](../clauses/task_timer.py), [study protocol](../USER_SESSION_QUICKSTART.md), anonymous record/summary utilities and report-finishing tools. These support actual data collection; they do not create fictional participants.

The model was originally generated September 10 and re-evaluated September 22. This report does not present the candidate comparisons as successive weeks of improvement. The GUI is included but still needs visual smoke testing on a desktop; CLI inference and HTML export were exercised locally.

## User evidence

- **PENDING actual outside-user session.** No outside-team participant record has been provided, so product validation and the north-star value remain unknown.
- **Raw artifact**: the genuine records must be committed in [evidence/session04/](../evidence/session04/) today. The supplied README, fictional documents, tests and model predictions are not user evidence.
- Planned pilot: outside users perform a clause-finding task with the running product, with correctness and elapsed time captured at the time. [Task instructions and observer answer key](../USER_SESSION_QUICKSTART.md).
- No user-driven change is claimed yet. Add the observed friction and the actual change PR or next-action issue after the session.

## Metrics snapshot

**Product north-star:** not measured; current `null`, previous `null`. No outside-user trial has been supplied. Do not substitute model F1 for this product metric.

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

- **Niveda and Ameer:** outside-user evidence and task-success measurement are PENDING; recruit an outside participant and commit contemporaneous anonymous records.
- **Ankan and all members:** real handles, actual contribution descriptions, approved PR links and repository status are PENDING. Verify branch protection and instructor access, finalize this report from facts, and merge before 5:00 p.m. Eastern.
- **Hemanth:** confirm GUI behavior on a real laptop; document any installation/display issue and use the working CLI/HTML route if needed.
- **Jayakrishna:** rare categories and validation-selection bias limit claims. Inspect the listed errors and preserve the reserved test split for later frozen evaluation.

## Next week's goal

Reduce unsupported arbitration/unilateral-change flags while preserving recall, guided by the actual outside-user pilot. Inspect source error cases first, then compare a validation-only threshold experiment with the frozen current hybrid. Report gains or losses, use the selected artifact in the product, and repeat the task protocol with new participants or unseen tasks. Session 05 is due September 29 at 5:00 p.m. Eastern.

## Individual contributions

- Ameer (Product): TODO actual completed engineering and user/product research work, with real issue/PR/commit evidence. Assigned focus: app workflow, observation and lean canvas.
- Hemanth (Engineering): TODO actual completed code/setup and technical investigation, with real issue/PR/commit evidence. Assigned focus: pipeline integration and laptop smoke test.
- Jayakrishna (Data&Eval): TODO actual completed evaluation code and error analysis, with real issue/PR/commit evidence. Assigned focus: reproducibility, rare-category diagnosis and split/license audit.
- Niveda (Users&Research): TODO actual completed recorder/protocol work and outside-user sessions, with real issue/PR/commit evidence. Assigned focus: contemporaneous CSV/JSON records and observations.
- Ankan (Operations): TODO actual completed validation/report tooling and requirement audit, with real issue/PR/commit evidence. Assigned focus: board, reviews, proof links and final merge check.

## Lean canvas changes (if any)

The current [lean canvas](../docs/lean_canvas.md) treats English-reading app users as the initial audience and manual reading/Find as the comparison. Distribution begins with a local app/HTML workflow. Inference has no metered API call, though setup, CPU and support have costs. The initial scope is eight source-defined review categories with original-text evidence; it does not promise detection of every contractual risk. The largest risk is that development F1 will not translate into useful clause-finding on unfamiliar documents. Outside-user validation remains unconfirmed; the canvas is a hypothesis, not proven demand.
