# ClauseGuard implementation and experiment guide

## What is implemented

The product supports a local desktop workflow and a command line. The desktop UI is deliberately optional: every essential model operation can be reproduced from the CLI, and the HTML export can be opened by a user without a web server. No accounts, paid model API or hosted integration are required. The course requires a usable product; it does not mandate a particular framework or public hosting. A later hosted interface is a team decision, not a prerequisite for the supplied local product.

| Component | File | Behavior |
|---|---|---|
| Label schema and reviewed descriptions | `clauses/schema.py` | Exact eight-label order and category explanations |
| Data access | `clauses/data.py` | Downloads pinned archive, checks SHA-256, validates counts and labels, preserves official splits |
| Segmentation | `clauses/text.py` | Sentence records with offsets into original input, simple abbreviation handling, input limits |
| Training/inference | `clauses/model.py` | Train-only checks, one-vs-rest classifiers, optional dev threshold tuning, saved manifests, shared product/batch predictions |
| Evaluation | `clauses/evaluate.py` | Eight-label metrics, LexGLUE-derived ninth label, predictions by ID, batch timing |
| Export | `clauses/export.py` | Self-contained escaped HTML with original sentences and model identity |
| Study tools | `clauses/study.py` | Anonymous task CSVs, timestamping, duplicate prevention, grouped summaries |
| CLI | `clauses/cli.py` | Data, train, evaluate, analyze, record-task, summarize-tasks commands |
| Desktop | `app.py` | Input, categories, matching source highlight, local export |
| Course validator | `scripts/validate_submission.py` | Correct report names, dates, five-member fields, exact headings, draft blockers |

## Data and labels

The original Zenodo UNFAIR-ToS release has company provenance, text, labels and a source split. `val` maps to `validation`. Counts: train 5,532, validation 2,275, test 1,607. Training companies and validation companies are disjoint in the checked source. Preserve the official split for comparisons and use company-level splits for any added data. Never treat shuffled neighboring sentences as context. Development evaluation is repeatedly consulted; reserve the official test for freeze.

Labels, in the exact order used by this code: Limitation of liability; Unilateral termination; Unilateral change; Content removal; Contract by using; Choice of law; Jurisdiction; Arbitration. Empty labels mean no annotated category, not legal safety. A sentence may have several labels.

## Baselines and implementation details

`baseline`: word unigram TF-IDF, minimum document frequency 2, sublinear term frequency, maximum 30,000 features. Eight independent logistic regressions use C=1, liblinear, 1,000 maximum iterations, seed 641. No class weighting. No stop-word removal discards negation.

`balanced`: word unigrams and bigrams, otherwise the same base feature settings; each binary classifier uses balanced class weights. This changes both representation and weighting. It is a useful initial comparison but does not isolate each factor. The weekly plan therefore includes ablations to separate those effects.

`hybrid`: combines the balanced word model's features with character word-boundary n-grams of length 3–5, min_df=3, maximum 25,000 character features. Uses the same weighted one-vs-rest classifier. This comparison with `balanced` isolates adding the character representation, with remaining settings held fixed.

All initial models use the strict decision rule score > 0.5. The application displays an additional “near threshold” cue when any score is within 0.05 of its category threshold. That heuristic is an inspection cue, not a calibrated uncertainty guarantee and not automatic abstention. Evaluate it separately before claiming it improves user decisions.

The optional tuning command selects thresholds from a fixed grid on validation per-label F1 and prefers higher thresholds on ties. It has not been run in the initial results. Small validation supports make per-label tuning unstable, so retain the fixed-threshold comparison and examine precision/recall trade-offs.

## Evaluation details

Eight-label macro-F1 is the primary modeling measure for category coverage. Micro-F1 pools all positive category decisions. Per-label precision, recall, F1 and support identify which categories fail. The LexGLUE reference evaluator appends a ninth column indicating that none of the eight labels is present, for both ground truth and predictions. This package reports that convention separately as `lexglue_macro_f1_9` and `lexglue_micro_f1_9`. Do not compare eight-label macro-F1 to a published nine-column macro-F1.

Scores use 0–1 in JSON. Multiply by 100 for percentage-style slide tables. Differences on that scale are percentage points, not relative percentages. All metrics use zero_division=0. High exact-match accuracy and nine-column micro-F1 can obscure poor performance on rare categories. Include the eight-label and per-label diagnostics.

Model selection in the initial package uses validation eight-label macro-F1. It has seen no test performance. The selected artifact is exactly the copied winner, and its SHA-256 connects desktop/CLI outputs and evaluation records. Initial selection is not a final semester freeze; students should reproduce and improve the system before final evaluation.

## Experiments over the term

Follow the five-member timeline, adapting to actual evidence. Useful controlled experiments include word-only weighting versus no weighting, char-only versus word+char, a separate linear SVM baseline, threshold trade-offs, valid context windows, and a contextual-embedding classifier. The embedding/transformer experiment is not implemented in this package and is optional; the traditional pipeline already provides substantive NLP. No model is guaranteed to win.

For each experiment save its hypothesis, exact command/configuration, seed, dataset SHA, code commit, metrics, prediction IDs, error examples or permitted references, runtime and resulting decision. Keep an unchanged baseline. Do not relabel September 10 runs as new experiments in later reports.

## Meaningful verification

The supplied tests cover original-text offsets, punctuation/Unicode/decimal cases, input limits, exact label scoring, no-category derivation, metric behavior under imbalance, HTML escaping, task-log validation and duplicate prevention, training-split guards, train/development document separation, and saved-model/product prediction consistency. CLI analysis has been executed on the fictional example.

The GUI is standard Tk source and compiles, but it could not be visually exercised without a display. Hemanth and a reviewer should run it on a desktop early. Fixes must have real PRs and should preserve the inference contract. No software can honestly be guaranteed error-free from these checks alone.

## Startup value and user study

The hypothesis is that ClauseGuard helps users find specified clauses correctly within 180 seconds. Run original-text and ClauseGuard conditions on matched documents, counterbalance order, and use a pre-reviewed answer key including absence cases. Track task IDs, anonymous participant IDs, timing, correct/incorrect outcome, model identity and protocol version. The timed task is more informative than asking whether someone was surprised by a flag.

A small convenience sample supports descriptive findings. Do not infer legal expertise or broad consumer benefit from classmates' agreement. Interviews about the idea are discovery work; real outside-user interaction with the running application is the graded validation evidence.

## Scope and fallback

The safe completion path is the local trained classifier, evidence view, correct evaluation, and real user tasks. Add models or interfaces only when they resolve an observed problem. If a contextual model loses, retain the better baseline and explain the loss. If hosting proves difficult, document reliable local setup and show the same evaluated pipeline in a live or recorded demo.
