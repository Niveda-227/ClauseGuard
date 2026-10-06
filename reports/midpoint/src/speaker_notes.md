# Speaker notes: mid-semester presentation (Niveda presents)

Target: 4:45 spoken, 15 seconds of buffer inside the 5:00 limit. Say the numbers exactly as written; every one comes from `reports/midpoint/metrics.md`. Speak to the audience, not the screen.

## Slide 1 · Title (10 s)

"We're ClauseGuard. We help people find the clauses in Terms of Service that matter, and we always show the original sentence. I'm Niveda, Users and Research; the full team is on the slide."

## Slide 2 · Problem and user (20 s)

Say the three lines on the slide in your own words, one sentence each. End with: "A flag is a pointer to read, not a legal judgment, and nothing leaves the user's computer."

## Slide 3 · Live demo (80 s)

Switch to the app window (it is already open; see `docs/DEMO_RUNSHEET_midpoint.md`).

1. Click **Load fictional example**, then **Analyze terms**. Say: "This is a fictional terms document we wrote. Eleven sentences, analyzed locally in well under a second." Point at the status bar: "This model ID, {{AUTO_MODEL_SHA12}}, is the exact model behind every number I'll show."
2. Choose **Category → Arbitration**. Click the result. Say: "The sentence is highlighted in the original text, with a plain-English explanation and the model's score. The user reads the real words, not our summary."
3. Choose **Category → All sentences**. Click **sentence 3** ("We may change these terms at any time without notice"). Say: "Here it fails. This sentence gets two tags. 'Unilateral change' is right; 'Unilateral termination' is wrong. That is our biggest problem, and it's what we tested with users this week."

Switch back to the slides. If the app does not respond within 5 seconds, say "Here is the same analysis as a web page" and open `analysis.html`. If that fails too, Hemanth plays the recorded backup.

## Slide 4 · Metric vs baseline (35 s)

"Our model metric is macro-F1 over eight clause categories, on {{AUTO_VAL_SENTENCES}} validation sentences from {{AUTO_VAL_COMPANIES}} companies the model never saw in training. The shipped model scores {{AUTO_HYBRID_MACRO_F1}}; a simple single-word baseline scores {{AUTO_BASELINE_MACRO_F1}}. We haven't touched the test set; that's saved for the end of term. Last week we tested per-category thresholds with a leave-one-company-out check: {{AUTO_LOCO_MACRO_F1}}. That's not in the product yet; it ships in Session 07."

## Slide 5 · Where it fails (25 s)

"Two failures. First, it flags too much: {{AUTO_MODEL_FLAGS_PER_100}} flags per 100 sentences, where human annotators marked {{AUTO_GOLD_FLAGS_PER_100}}, and {{AUTO_WRONG_FLAG_PCT}} of our flags name the wrong category. Second, {{AUTO_WEAKEST_CATEGORY}} is weak, F1 {{AUTO_WEAKEST_F1}}, and we only have {{AUTO_WEAKEST_SUPPORT}} validation examples of it."

## Slide 6 · What real users did (55 s)

"{{AUTO_PARTICIPANTS}} people outside our team used the running app. Each did one task with a plain text editor and one with ClauseGuard, in alternating order. I read the task aloud, they repeated it back, and the clock stopped the moment they gave their answer. With ClauseGuard: {{AUTO_CG_SUCCESSES}} of {{AUTO_CG_TRIALS}} correct, median {{AUTO_CG_MEDIAN_S}}. Without it: {{AUTO_MANUAL_SUCCESSES}} of {{AUTO_MANUAL_TRIALS}}, median {{AUTO_MANUAL_MEDIAN_S}}."

Then: <<SAY FOR OBSERVATIONS: write here, in full sentences, what you will say about the two observations on the slide, using only what is written in evidence/session06/session_notes.md>>

End with: "The raw records, tasks.csv and our notes written during the sessions, are in the repository, linked on the slide. The two tasks differ in difficulty, so this is not a controlled comparison."

## Slide 7 · Decision (40 s)

"Before this week's sessions, we wrote down a rule for this decision and committed it. The rule's outcome is: {{AUTO_RULE_OUTCOME}}. {{AUTO_RULE_REASON}}"

Then: <<SAY FOR DECISION: write here, in full sentences, the decision and the two reasons exactly as they appear in section 5 of docs/decisions/2026-10-06_midpoint_decision.md, plus what would change the team's mind>>

## Slide 8 · What did not work, next (20 s)

"What didn't work: our first user pilot couldn't be scored because of how we measured, so we rebuilt the protocol." Then read the second "Did not work" line. "Next, for Session 07: ship the tuned thresholds, fix what participants struggled with, and recruit more people. Thank you. Questions?"

## Questions (2 minutes)

Niveda repeats each question aloud (so everyone hears it), then hands it to the owner listed in `reports/midpoint/qa_prep.md`. Answers: 20 seconds each, a number and its source file. If nobody knows: "We haven't measured that; here is how we would."
