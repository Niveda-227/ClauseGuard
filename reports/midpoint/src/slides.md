<!-- time: 10 -->
# ClauseGuard

Find the Terms of Service clauses that matter, with the original sentence beside every flag.

- Ameer (Product) · Hemanth (Engineering) · Jayakrishna (Data and Evaluation) · Niveda (Users and Research, presenting) · Ankan (Operations)
- DATA/MSML 641 · Mid-semester presentation · October 6, 2026
- Repository: [github.com/Niveda-227/ClauseGuard](https://github.com/Niveda-227/ClauseGuard)

---

<!-- time: 20 -->
## The problem and the user

- **User:** <<USER: copy the "User" row of docs/lean_canvas.md on main, shortened to one line>>
- **Today:** <<ALTERNATIVES: copy the "Alternatives" row of docs/lean_canvas.md on main, shortened to one line>>
- **Our bet:** <<VALUE PROPOSITION: copy the "Value proposition" row of docs/lean_canvas.md on main, as one sentence>>
- A flag is a pointer to read, not a legal judgment. Everything runs on the user's own computer; nothing is uploaded.

---

<!-- time: 80 -->
## Live demo: the product running

1. **Load fictional example → Analyze terms.** The status bar shows model `{{AUTO_MODEL_SHA12}}`, the same model behind every number in this talk.
2. **Category → Arbitration → click the result.** The source sentence is highlighted, with the category explanation and model score.
3. **Category → All sentences → sentence 3.** Two tags on one sentence, and one of them is wrong: the over-tagging problem.

If the app fails: the same analysis as a web page (`analysis.html`), then the recorded backup.

---

<!-- time: 35 -->
## Metric vs baseline: the shipped model

![Macro-F1 of the shipped model vs the baseline](figures/metric_vs_baseline.svg)

- Shipped model: macro-F1 **{{AUTO_HYBRID_MACRO_F1}}** vs **{{AUTO_BASELINE_MACRO_F1}}** for the unigram baseline, on {{AUTO_VAL_SENTENCES}} validation sentences from {{AUTO_VAL_COMPANIES}} companies not seen in training. Test split untouched.
- Per-category thresholds scored {{AUTO_LOCO_MACRO_F1}} in a leave-one-company-out test. **Not shipped yet** (Session 07).

---

<!-- time: 25 -->
## Where it fails

![F1 by category](figures/per_category_f1.svg)

- Over-flagging: {{AUTO_MODEL_FLAGS_PER_100}} flags per 100 sentences vs {{AUTO_GOLD_FLAGS_PER_100}} from human annotators; {{AUTO_WRONG_FLAG_PCT}} of flags name a category the annotators did not assign.
- Weakest: {{AUTO_WEAKEST_CATEGORY}}, F1 {{AUTO_WEAKEST_F1}} on only {{AUTO_WEAKEST_SUPPORT}} validation sentences.

---

<!-- time: 55 -->
<!-- layout: split -->
## What real users did with it

{{AUTO_USER_TABLE}}

- {{AUTO_PARTICIPANTS}} outside participants, protocol sep29_v2: task read aloud and restated; the clock stops when they state the answer. Over-tagged task C1 with the app: {{AUTO_C1_CG_SUCCESSES}}/{{AUTO_C1_CG_TRIALS}} correct.
- Observed: <<OBSERVATION 1: one pattern copied from the "Across participants" section of evidence/session06/session_notes.md, 20 words or fewer>>
- Observed: <<OBSERVATION 2: a second pattern from the same section, 20 words or fewer; delete this line if the notes list only one>>
- Raw evidence: [tasks.csv](../../evidence/session06/tasks.csv) · [session notes](../../evidence/session06/session_notes.md) · [README](../../evidence/session06/README.md)

<<SCREENSHOT: replace this whole line with ![Participant screen](../../evidence/session06/screenshots/FILENAME.png) using one consented screenshot's real file name, or delete this line if there are no screenshots>>

---

<!-- time: 40 -->
## Decision: <<DECISION: the decision word(s) exactly as written in section 5 of docs/decisions/2026-10-06_midpoint_decision.md on main>>

- Rule written September 30, before this week's sessions. Outcome: **{{AUTO_RULE_OUTCOME}}**. {{AUTO_RULE_REASON}}
- Why: <<REASON 1: first reason from section 5 of the decision memo, one line>>
- Why: <<REASON 2: second reason from section 5 of the decision memo, one line>>
- What would change our mind: <<TRIGGER: the condition from section 5 of the decision memo that would make the team pivot, one line>>

---

<!-- time: 20 -->
## What did not work, and what is next

- Did not work: the Session 04 pilot could not be scored (the clock included answer typing; the participant answered a different task). We rebuilt the protocol.
- Did not work: <<NEGATIVE: one real failure from this week, from evidence/session06/session_notes.md "Measurement notes" or the numbers above, one line>>
- Next, Session 07 (October 20): ship per-category thresholds; act on what participants struggled with; recruit more participants.

**Questions?**

---

<!-- time: 0 -->
## Appendix: the decision rule and cost to serve

{{AUTO_RULE_TABLE}}

- Cost to serve, measured {{AUTO_DEMO_CHECK_DATE}} on a team laptop: model load {{AUTO_COST_LOAD_SECONDS}}, {{AUTO_COST_MS_PER_SENTENCE}} per sentence, no network or API calls.
- Every number in this deck: [metrics.md](metrics.md), generated from committed files by `scripts/midpoint_facts.py`.
