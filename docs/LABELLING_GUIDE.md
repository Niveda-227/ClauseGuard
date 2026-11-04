# Labelling guide for the fresh Terms of Service (Session 10)

Two team members label every sentence of the three documents in `examples/fresh/` on their own, without seeing each other's labels. The labels are the "answers" the model is checked against in `scripts/fresh_eval.py`. The guide was written on 2026-11-04, before any label existed.

## How to label

- Use the tool: `python -m clauses.labelling --doc <doc_id> --annotator <A1 or A2>`. It shows one sentence at a time, exactly as the app splits the document, with the sentence before it for context.
- For each sentence, type the numbers of every category the sentence **itself** states (for example `3` or `1,5`), or press **Enter** for none. A sentence can have several categories.
- Judge each sentence on its own words. The sentence before it is only there to help you understand it.
- **Headings are never labelled** (for example "Limitation of Liability" or "Termination." on its own line): a heading states no clause.
- **When unsure, do not label.** Type `?` to mark the sentence as unsure (it is then saved with no category, and counted in the notes). Do not look up what the model says.
- **Never open the other annotator's file** (`private/labels/...` on their laptop, or `data/fresh_labels/` once it is on `main`) before you have finished and posted your fingerprint.
- Take breaks: about 380 sentences take 45 to 75 minutes. The tool saves after every sentence; `q` stops and the next run continues where you left off.

## The eight categories

Label a sentence with a category when it creates or states a term of that kind that favours the company over the user. These are the UNFAIR-ToS categories, in the app's order.

| # | Category | Label the sentence when it ... | Do not label when ... |
|---|---|---|---|
| 1 | Limitation of liability | excludes or limits what the company owes if something goes wrong (no liability for losses, a cap on damages, "as is" with no responsibility for harm) | it only describes the user's own responsibility for their account, or is a plain warranty disclaimer that says nothing about liability or damages |
| 2 | Unilateral termination | lets the company suspend, end or close the user's account or access, or end the service, at its own decision | the user is the one cancelling, or it only explains what happens to data after the user cancels |
| 3 | Unilateral change | lets the company change the terms, the service, features or prices on its own decision | it only promises notice without saying the company may change something, or it is the user changing their plan |
| 4 | Content removal | lets the company remove, delete, block or refuse the user's content at its own decision | it is about the user deleting their own content, or deletion after the user cancels |
| 5 | Contract by using | says that using or accessing the service means the user accepts the terms | it only asks the user to read or agree in another way (for example by signing) |
| 6 | Choice of law | names the law that governs the agreement or disputes (for example "governed by the laws of California") | a law is only mentioned in passing (for example "must comply with U.S. copyright law") |
| 7 | Jurisdiction | names the courts or the place where disputes must be brought | it names only the governing law, not the courts or place |
| 8 | Arbitration | requires or allows disputes to be settled by arbitration instead of a court, or describes how that arbitration works | the word appears without any arbitration requirement |

## Examples (invented, not from the documents)

| Sentence | Label |
|---|---|
| "We may close your account at any time for any reason." | 2 |
| "We may update these terms and the price of the service at any time." | 3 |
| "By using the app you agree to these terms." | 5 |
| "These terms are governed by the laws of Vermont, and disputes go to the courts of Burlington." | 6, 7 |
| "We are not liable for any indirect losses." | 1 |
| "You can delete your posts from the settings page." | none |
| "Termination." (a heading) | none |

## What happens next

After both annotators finish, `scripts/label_agreement.py` measures how often they agree (Cohen's kappa, an agreement measure that corrects for agreement by chance) and builds two answer sets: **strict** (a category counts only when both annotators gave it) and **lenient** (it counts when either did). The rules for judging the model on these labels are in `docs/decisions/2026-11-04_fresh_documents_rule.md`, written before any label existed.
