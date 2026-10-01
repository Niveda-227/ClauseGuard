# Mid-semester decision: pivot or persevere

**Decision date:** Tuesday, October 6, 2026 (Session 06 presentation) · **Owner:** Product (`sohail-umd`)
**Rule written:** October 1, 2026, before any Session 06 participant session. Machine-readable rule: [midpoint_rule.json](midpoint_rule.json).

## 1. What we are deciding

Whether to keep building ClauseGuard for the same user and problem (**persevere**), keep them but change how the product produces or shows flags (**persevere with change**), or stop and change the product, the user or the method (**pivot**).

Current product: a local desktop app (`app.py`) and command-line/HTML route that splits English Terms of Service into sentences, flags eight clause categories with a trained classifier, and shows the original sentence beside each flag.

## 2. Evidence available when the rule was written (October 1)

Every number below comes from a file already on `main`.

**Model** (source: `experiments/session04/*/metrics.json`, `artifacts/selected.json`)
- The product runs the hybrid model (word 1-2-gram and character 3-5-gram TF-IDF, one logistic regression per category, fixed 0.5 thresholds). Artifact SHA-256 `04713fbf6e23…`.
- Validation (2,275 sentences from 10 companies not used in training): macro-F1 **0.6333**, against **0.2551** for the unigram baseline. The test split has not been used.
- Weakest category: Arbitration, F1 0.323 on 9 validation sentences.
- Over-flagging: at fixed 0.5 the model makes 17.5 flags per 100 validation sentences; the annotators marked 10.9. 195 of the 398 flags (49%) are a category the annotators did not assign to that sentence (source: `experiments/session04/hybrid/predictions.jsonl`).

**Threshold experiment** (source: `experiments/session05/threshold_cv.md`)
- Per-category thresholds, estimated honestly with leave-one-company-out, raise macro-F1 from 0.6333 to 0.6768 and cut flags from 17.5 to 11.0 per 100 sentences. The pre-written Session 05 decision rule was met, so per-category thresholds ship in Session 07. **They are not in the product yet.**

**Users** (source: `evidence/session05/`, `reports/session05.md`, issue #29)
- Session 04 pilot: not interpretable (the clock included answer typing and the participant answered a different task).
- Session 05, protocol `sep29_v2`: one outside participant (U002). Manual C1 correct in 87.0 s; ClauseGuard D1 correct in 51.8 s.
- The over-tagged task (C1 with the app) has not been tested with anyone yet (issue #29).

**Plain reading:** the model clearly beats its baseline; there is almost no user evidence; the product's most visible flaw (too many and partly wrong tags) is known and has a tested fix waiting.

## 3. The rule (pre-registered)

Inputs are computed by `scripts/midpoint_facts.py` from the files listed in `midpoint_rule.json`. Only protocol `sep29_v2` trials count, and ClauseGuard trials count only if they ran the shipped model (`04713fbf…`).

- **Model gate:** the shipped model's validation macro-F1 is at least **0.10** above the unigram baseline, and the shipped artifact is byte-identical to the evaluated hybrid model.
- **Enough participants:** at least **3** distinct outside participants across Sessions 05 and 06.
- **Success rate:** a trial is a success if the answer was correct (right sentence **and** right meaning) within 180 seconds. Compare the ClauseGuard success rate with the manual success rate.
- **Over-tagging check:** did any participant fail task C1 (whose answer sentence carries two wrong tags) while using ClauseGuard?

| Outcome | When |
|---|---|
| **PIVOT** | Model gate fails, **or** (enough participants **and** ClauseGuard success rate is more than 25 percentage points below manual) |
| **PERSEVERE WITH CHANGE** | Model gate passes, enough participants, **and** (ClauseGuard is below manual by at most 25 points **or** someone failed C1 with ClauseGuard) |
| **PERSEVERE** | Model gate passes, enough participants, ClauseGuard success rate ≥ manual, nobody failed C1 with ClauseGuard |
| **PROVISIONAL PERSEVERE** | Model gate passes but fewer than 3 participants. User value is unproven; re-run this rule at Session 08 with at least 6 participants |

Not part of the rule: speed (C1 and D1 differ in difficulty, so time is reported but does not decide) and statistical significance (with this few participants the rule is a pre-committed heuristic, not a test).

## 4. What each outcome would mean in practice

**If we persevere** (with or without change), the plan to Session 12 stays:
- Session 07: ship per-category thresholds (Session 05 result); act on issue #29; heading-fragment filter experiment.
- Session 08: show near-threshold flags as uncertain; test whether users understand the category explanations.
- Session 09: absence tasks (does "no flags" read as "safe"?); cost per request.
- Sessions 10-12: hand-labelled fresh documents for a domain-shift check; ablations; freeze the model and run the test split once.

**If we pivot**, the candidates we would compare (none is chosen in advance):
- **Change the job:** from "flag every category" to "answer one question about these terms" (the user asks, the product returns the one sentence that answers it). Same data and model family; fewer tags on screen.
- **Change the interface:** show flags only when the user asks for a category, instead of tagging every sentence.
- **Change the method:** a sentence-pair or retrieval model instead of eight independent classifiers.

## 5. Decision

Not yet decided. This section is completed on October 5, after the Session 06 participant sessions, from the output of `scripts/midpoint_facts.py`.
