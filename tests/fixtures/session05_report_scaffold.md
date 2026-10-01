---
team: ClauseGuard
session: "05"
date: "2026-09-29"
members:
  - name: Ameer
    github: {{AUTO_GITHUB_Ameer}}
    hat: Product
  - name: Hemanth
    github: {{AUTO_GITHUB_Hemanth}}
    hat: Engineering
  - name: Jayakrishna
    github: {{AUTO_GITHUB_Jayakrishna}}
    hat: Data&Eval
  - name: Niveda
    github: {{AUTO_GITHUB_Niveda}}
    hat: Users&Research
  - name: Ankan
    github: {{AUTO_GITHUB_Ankan}}
    hat: Operations
north_star:
  metric: "Correct clause-finding tasks completed within 180 seconds (%)"
  value: {{AUTO_VALUE}}
  previous: {{AUTO_PREVIOUS}}
---

## Shipped this week

**Merged this week:** {{AUTO_SHIPPED_LINKS}}. Every PR was approved by a teammate before merge; `main` requires one approving review.

<<HUMAN: 3-5 bullets, one per merged change, each saying what it does for a user or for the evaluation. Cover: session protocol v2 (clock stops before answer entry, prompt restated before timing), the stale detail-panel fix in the desktop app, the leave-one-company-out threshold experiment, the new study documents C and D with a private answer key, the repository cleanup, and the reusable report finalizer. Link the file for each, e.g. [session protocol v2](../clauses/session_v2.py).>>

The model running in the product is unchanged this week: `{{AUTO_MODEL_ID}}`.

## User evidence

- <<HUMAN: One or two sentences from evidence/session05/session_notes.md: date(s), number of outside participants by code (U002...), which tasks each did in which order, and which interface. Copy what the notes say; do not add observations that are not in the notes.>>
- **Raw artifact**: {{AUTO_EVIDENCE_LINKS}}. Protocol `{{AUTO_PROTOCOL}}`.
- ClauseGuard: {{AUTO_TOOL_RESULT}}.
- Manual comparison: {{AUTO_MANUAL_RESULT}}.
- <<HUMAN: The most important thing participants did, in plain words, taken from session_notes.md. Example of the kind of sentence (replace with what really happened): "On task C1, where the answer sentence carries two extra category tags, U003 read all three tags aloud as facts before opening the source text.">>
- Resulting change or next action: <<HUMAN: what the team changed because of this, or the issue opened for next week, in one sentence.>> (evidence: {{AUTO_CHANGE_LINKS}})
- This is a small pilot on short fictional documents, not a population estimate or a check of legal correctness.

## Metrics snapshot

**Product north-star:** {{AUTO_VALUE}}% this week; previous {{AUTO_PREVIOUS}}%.

<<HUMAN: One paragraph on comparability. Session 04 used protocol sep22_v1, whose clock included the observer typing the answer and whose task prompt was not confirmed; this week uses sep29_v2, which fixes both. State plainly that the two numbers are therefore not a like-for-like comparison, and what the change means for interpreting the difference.>>

**Model development results** (validation split, 2,275 sentences, 10 companies; final test split not evaluated):

| Decision rule | Macro-F1 (8) | Micro-F1 (8) | Source |
|---|---:|---:|---|
| Fixed 0.5, current product | <<HUMAN: from experiments/session05/threshold_cv.md>> | <<HUMAN>> | [threshold_cv.md](../experiments/session05/threshold_cv.md) |
| Per-category thresholds, tuned and scored on the same data (optimistic) | <<HUMAN>> | <<HUMAN>> | same |
| Per-category thresholds, leave-one-company-out (honest estimate) | <<HUMAN>> | <<HUMAN>> | same |

<<HUMAN: One or two sentences interpreting the table in Jayakrishna's words (from experiments/session05/jayakrishna_session05_notes.md): how much of the in-sample gain survives leave-one-company-out, which categories gain or lose, and whether the team will ship tuned thresholds in Session 07.>>

**Same model as the product?** Yes. `artifacts/selected.joblib`, SHA-256 `{{AUTO_MODEL_ID}}`. The threshold experiment did not change the shipped model.

## What did not work

- <<HUMAN: the biggest failure or negative result this week, with evidence. Candidates: a task participants failed and why; a category that gets worse under tuned thresholds; any trial the protocol could not rescue.>>
- <<HUMAN: a second honest item: a limitation of the study (participant count, different documents per condition), or a flaw found in our own evaluation.>>
- Session 04's product metric (0.00%) was not interpretable as product performance because of the timing and prompt-confirmation problems fixed this week ([issue #14](https://github.com/Niveda-227/ClauseGuard/issues/14)).

## Challenges / blockers

<<HUMAN: 2-4 sentences. The real remaining problem, who owns it, and what help is needed. Include recruitment if fewer than 3 participants took part.>>

## Next week's goal

Mid-semester presentation on October 6: demonstrate the running product, show this week's user evidence and the threshold experiment against the fixed-threshold baseline, and state a pivot-or-persevere decision backed by that evidence.

## Individual contributions

{{AUTO_CONTRIBUTIONS}}

## Lean canvas changes (if any)

<<HUMAN: What changed in docs/lean_canvas.md this week and why (Ameer's update), or "Unchanged because ..." with a real reason.>>
