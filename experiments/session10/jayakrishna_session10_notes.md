# Session 10 evaluation notes (Jayakrishna, annotator A2)

Two jobs this week: label the three fresh Terms of Service as the second annotator (A2), then run the two measurements on the labels of both annotators. Every number below is filled from the result files by `scripts/fill_notes.py`; the words are mine.

## 1. My labels (A2)

- Sentences labelled: 376; with at least one category: 68; unsure: 0; about 11 minutes.
- Fingerprint, posted in the team chat on Thursday 5 November, 7:55pm, when Hemanth's first-round labels were already on `main`: `9530769cf1c9cde0fed19b9140e1653af9a939746df7d454d3e4cfc9755aadbc`
- I did not open `data/fresh_labels/A1/` or run ClauseGuard on these documents before posting it: confirmed.

## 2. Do the two annotators agree? (`experiments/session10/label_agreement.md`)

- Pooled Cohen's kappa: 0.87. Sentences where we gave different categories: 20 of 376.
- Strict answers (both of us): 70 labels. Lenient (either of us): 90 labels.
- Where we disagreed most, in words: Almost all of our 20 disagreements are one pattern: I added a second category where Hemanth gave one. In 19 of the 20, I had the extra label. The biggest group is “Contract by using” and “Unilateral change”. I tagged sentences like “Use of the software constitutes acceptance of this agreement” and “If you do not agree to abide by the terms, please do not become a user” as a change clause too, because the contract can be changed later. Hemanth tagged them only as contract-by-using. The second group is termination sentences about frozen accounts and deleted content, where I also added “Content removal” or “Unilateral termination” and he kept the one closest to the main point. I think this happened because I read each sentence together with the clause around it, and he read each sentence by itself. Where one of us labelled a sentence as a clause and the other didn’t, we nearly always agreed on the category.

## 3. The shipped model on the fresh documents (`experiments/session10/fresh_eval.md`)

- Strict macro-F1: 0.4139, against 0.6768 on validation (honest, Session 07). Lenient macro-F1 (reported only): 0.3606.
- Strict counts: 22 correct tags, 11 wrong tags, 48 missed labels; 8.78 flags per 100 sentences.
- The errors, in words: The model mostly misses clauses and rarely flags the wrong thing: 48 missed labels against 11 wrong tags. It misses plain, conversational wording. Examples are “If the bet does not work out, that’s on you, not us” and “After the trial period, you need to pay in advance”, and the Crowdsignal warranty and “at your sole risk” sentences that don’t use the usual liability wording. It also misses arbitration sentences about JAMS rules and class actions, and “Unilateral change” sentences that explain why the terms change. Most of its wrong tags come from section headings, like “Termination.”, “Limitation of Liability” and “Liability”, which it scores very high just because the heading names the topic. It also confuses “we reserve the right to modify or discontinue the Services” with a termination clause.

## 4. The three pre-set rules (strict, fixed on 2026-11-04 before any label existed)

- Domain shift: fresh macro-F1 0.4139 against 0.6768 on validation, a drop of 0.2629 (the limit is 0.15). Result: **DOMAIN SHIFT: treat it as the main risk in Session 11**
- Cue margin `0.10`: possible cues reach 8.3% of the missed labels (4 of 48), 2.93 per 100 sentences (needs at least 20% and at most 5 per 100). Result: **KEEP the 0.05 margin**
- Zero-flag-only marks: the marks reach 2.1% of the missed labels (1 of 48), 2.93 per 100 sentences (needs at least 40% and at most 20 per 100). Result: **KEEP showing all marks, off-by-default toggle stays**
- What this means for Session 11, in words: The model does much worse on documents it has never seen, and none of the cue or mark ideas we tested fixes that, so Session 11 should treat domain shift as the main risk. The best option is to work on the model itself (more varied training sentences, plainer wording, ignoring headings) instead of changing the margin or the marks.

## Limits

- Three documents (two from the same company) and two team annotators who are not lawyers. The answer set is small, so one sentence can move a percentage a lot; the counts are always next to the percentages.
- The rules and the search words were not changed after the labels existed. The validation and test splits were not used for anything new.

<!-- Numbers filled by scripts/fill_notes.py from the result files in experiments/session10/. -->
