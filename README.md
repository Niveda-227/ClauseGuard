# ClauseGuard

Terms of Service agreements are long, dense, and nobody actually reads
them. The clauses that matter most, like arbitration waivers,
auto-renewal terms, and unilateral changes, end up buried in pages of
legal text that most people skip past. ClauseGuard reads the document
for you and flags the clauses worth paying attention to.

Repository: https://github.com/Niveda-227/ClauseGuard

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
A multi-label sentence classifier: every sentence is scored
independently for all eight categories, so one sentence can be flagged
for more than one type of risk at once. The shipped model combines word
TF-IDF (1-2 grams) with character n-grams (3-5), fed into one-vs-rest
logistic regression with class balancing. It is trained on 5,532
sentences from 30 companies and evaluated on a held-out validation
split of 2,275 sentences from 10 different companies. It runs entirely
on-device, no document ever gets sent to an external API, which matters
for something as sensitive as a legal contract.

Validation results (0-1 scale, eight-category scores):

| Model | Macro-F1 | Micro-F1 |
|---|---:|---:|
| baseline (unigram, unweighted) | 0.2551 | 0.3300 |
| balanced (1-2 grams, class-weighted) | 0.6156 | 0.6084 |
| **hybrid (selected, + char n-grams)** | **0.6333** | **0.6275** |

The reserved test split is untouched, for a later frozen evaluation.

## Team

| Name | Role | GitHub |
|---|---|---|
| Ameer Shaik | Product | @sohail-umd |
| Hemanth Reddy | Engineering | @hreddy14 |
| Jayakrishna Puttur | Data & Evaluation | @Jayakrishna-Reddy |
| Niveda Jawahar | Users & Research | @Niveda-227 |
| Ankan Roy | Operations | @royak747 |

Everyone writes code alongside their role. Ankan also runs the board
and the weekly reports.

## Project structure
- `clauses/` the classifier: training, inference, export and study tooling
- `app.py` desktop app entry point
- `artifacts/` the trained models, with hashes
- `tests/` automated tests
- `data/` dataset provenance and license (the dataset itself is downloaded by `python -m clauses.cli data`, not committed)
- `examples/study/` fictional study documents and the public task bank; answer keys are never committed
- `private/` (git-ignored) observer-only material such as answer keys; never pushed
- `experiments/` validation metrics, per-category errors, error notes
- `evidence/` anonymized user-session records
- `docs/lean_canvas.md` our working hypotheses on user, problem, and value
- `reports/` weekly progress reports

## Documentation

- [How it works](docs/HOW_IT_WORKS.md): pipeline, metrics and likely questions
- [Study protocol v2](docs/STUDY_PROTOCOL_V2.md): how outside-user sessions are run from Session 05
- [Model card](docs/MODEL_CARD.md) and [data provenance](data/README.md)
- [Lean canvas](docs/lean_canvas.md)
- Weekly reports: [reports/](reports/)

## Setup

Requires Python 3.12.

```bash
git clone https://github.com/Niveda-227/ClauseGuard.git
cd ClauseGuard
python3.12 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

Analyze a document from the command line:

```bash
python -m clauses.cli analyze --input examples/fictional_terms.txt --html-out analysis.html
```

Or open the desktop app:

```bash
python app.py
```

The trained model is included, so no API key, training run or dataset
download is needed to use it. To reproduce the evaluation instead:

```bash
python -m clauses.cli data          # downloads the pinned dataset
python -m unittest discover -s tests -v
```

## Limitations
Eight clause categories only; it does not cover privacy or data-sharing
practices. English only. The labels come from a European consumer-law
view of "unfair", drawn from 50 platform agreements. The model misses
clauses and flags some wrongly, and arbitration in particular is weak
(F1 about 0.32 on few examples). **No flags does not mean the document
is safe.** ClauseGuard is not legal advice.
