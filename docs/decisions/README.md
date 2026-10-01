# Decision records

Each file records one product decision: the evidence available when it was made, the rule used, and the outcome.

The rule is written and merged **before** the evidence it uses is collected, so the decision cannot be fitted to the results afterwards. The machine-readable part of a rule lives next to the memo as JSON and is evaluated by a script, not by hand.

| Date | Decision | Memo | Rule | Evaluated by |
|---|---|---|---|---|
| 2026-10-06 | Mid-semester: pivot or persevere | [2026-10-06_midpoint_decision.md](2026-10-06_midpoint_decision.md) | [midpoint_rule.json](midpoint_rule.json) | `scripts/midpoint_facts.py` |
