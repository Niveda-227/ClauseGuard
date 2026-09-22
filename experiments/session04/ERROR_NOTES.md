# Qualitative error audit — September 22

These are observed disagreements with dataset annotations from the **validation** predictions, not assessments of current legal enforceability. They were inspected during AI-assisted preparation; no named team member's authorship is implied. Full source sentences can be recovered by ID from the pinned dataset after `python -m clauses.cli data`.

| Source ID / company | Gold label(s) | Selected-model output | Observed issue and next investigation |
|---|---|---|---|
| `validation:05731` / Airbnb | Arbitration | Contract by using | The clause combines acceptance wording with an arbitration/class-action waiver. Arbitration score is 0.4316, below 0.5, while contract-by-using is 0.6534. Investigate overlapping wording and threshold tradeoffs; do not assume lowering a threshold will improve overall F1. |
| `validation:05578` / Nintendo | Unilateral change; Content removal | No category | One sentence combines service changes and deletion of user content. Change is 0.4510, content removal 0.2678, and termination nearly crosses the threshold at 0.4978. This is a concrete multilabel miss with category confusion to inspect. |
| `validation:05798` / Airbnb | No category | Unilateral change | The sentence explains publishing revised terms and updating their date. The change score is 0.8404. High confidence does not guarantee agreement with the task's annotation criteria. Inspect whether procedural notices differ from annotated unilateral-power clauses. |
| `validation:06040` / Airbnb | No category | Arbitration | The source describes negotiation followed by binding arbitration, but has no target annotation; arbitration score is 0.6418. A topic mention and a source-labeled concerning clause are not necessarily identical tasks. Review annotation definitions/context before declaring the annotation wrong. |

**Implication:** the product must communicate that its flags approximate the source dataset's categories. Do not interpret every flagged mention as an unfair, illegal or unenforceable term. Some disagreements may reflect missing document context or annotation/task distinctions; those are hypotheses for review, not established causal explanations.

**Next experiment:** manually audit a fixed sample of false positives and false negatives, categorize error causes with two team reviewers, then compare a validation-only threshold experiment against the frozen current hybrid. Retain all losses and keep the final test split reserved.

Reproduce the source inspection from a Python prompt in the project root:

```python
from clauses.data import load_split
wanted = {"validation:05731", "validation:05578", "validation:05798", "validation:06040"}
for row in load_split("validation"):
    if row["id"] in wanted:
        print(row)
```

Data/source attribution: see [docs/CITATIONS.md](../../docs/CITATIONS.md). Scores and labels: [hybrid/predictions.jsonl](hybrid/predictions.jsonl). Counts: [error_analysis.json](error_analysis.json).
