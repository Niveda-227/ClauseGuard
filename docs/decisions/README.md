# Decision records

Each file records one product decision: the evidence available when it was made, the rule used, and the outcome.

The rule is written and merged **before** the evidence it uses is collected, so the decision cannot be fitted to the results afterwards. The machine-readable part of a rule lives next to the memo as JSON and is evaluated by a script, not by hand.

| Date | Decision | Memo | Rule | Evaluated by |
|---|---|---|---|---|
| 2026-10-06 | Mid-semester: pivot or persevere | [2026-10-06_midpoint_decision.md](2026-10-06_midpoint_decision.md) | [midpoint_rule.json](midpoint_rule.json) | `scripts/midpoint_facts.py` |
| 2026-10-28 | Review cues after Session 08; rule for the "Not flagged, but worth a look" search words | [2026-10-28_cue_decision.md](2026-10-28_cue_decision.md) | in the memo (section "The rule for the search words") | `scripts/hint_eval.py` (Session 09) |
| 2026-11-04 | Fresh real Terms of Service: domain shift, cue margin 0.10, zero-flag-only marks | [2026-11-04_fresh_documents_rule.md](2026-11-04_fresh_documents_rule.md) | [fresh_rule.json](fresh_rule.json) | `scripts/fresh_eval.py` (Session 10) |
| 2026-11-10 | The final model (Session 11 ablation) and the final interface | [2026-11-11_final_model_rule.md](2026-11-11_final_model_rule.md) | [final_model_rule.json](final_model_rule.json) | `scripts/ablation.py` (Session 11) |
