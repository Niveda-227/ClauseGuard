# ClauseGuard

Terms of Service agreements are long, dense, and nobody actually reads
them. The clauses that matter most, like arbitration waivers,
auto-renewal terms, and unilateral changes, end up buried in pages of
legal text that most people skip past. ClauseGuard reads the document
for you and flags the clauses worth paying attention to.

## Why we're building this
Every one of us has clicked "I agree" without reading a single line.
The clauses that actually cost people money or rights when something
goes wrong are rarely the ones anyone catches in time. We wanted a
tool that does the reading for you and tells you, in plain terms,
where the risk actually is.

## What it does
ClauseGuard takes a Terms of Service document and classifies each
sentence against a set of clause categories known to be unfair or
consumer-unfriendly. Instead of skimming the whole document or
trusting a generic summary, a user gets a direct list of the flagged
sentences, the category each one falls into, and the original text,
so nothing is paraphrased away from what the document actually says.

Categories we detect:
- Unilateral termination (the company can end your access without cause)
- Unilateral change (terms can be changed without meaningful notice)
- Content removal (your content can be taken down at their discretion)
- Contract by using (you're bound just by using the site, no explicit agreement)
- Choice of law (disputes are forced into a jurisdiction that favors them)
- Jurisdiction (you have to litigate somewhere inconvenient for you)
- Arbitration (you give up your right to sue in court)
- Limitation of liability (they're not responsible even when it's their fault)

## How it works
A multi-label text classifier trained on real ToS documents, using
TF-IDF features and logistic regression per category, so each sentence
can be flagged for more than one type of risk at once. It runs
entirely on-device, no document ever gets sent to an external API,
which matters for something as sensitive as a legal contract.

## Team

| Name | Role |
|---|---|
| Ameer Shaik | Product |
| Hemanth Reddy | Engineering |
| Jayakrishna Puttur | Data & Evaluation |
| Niveda Jawahar | Users & Research |
| Ankan Roy | Operations |

Everyone writes code alongside their role. Ankan also runs the board
and the weekly reports.

## Project structure
- `clauses/` the classifier: training and inference code
- `app.py` entry point for running ClauseGuard
- `tests/` automated tests for the classifier
- `data/` dataset files and loading scripts
- `docs/lean_canvas.md` our working hypotheses on user, problem, and value
- `reports/` weekly progress reports

## Setup
Instructions coming once the codebase is pushed.
