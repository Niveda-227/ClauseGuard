# The shipped model on fresh real Terms of Service (Session 10)

Model `dafbb5470f2f`, product cut-offs. 3 documents (basecamp 156, cloudup 77, crowdsignal 143 sentences), 376 sentences. No company is in UNFAIR-ToS. Answers: two team annotators (see `label_agreement.md`).

## Overall

| | Strict (both annotators) | Lenient (either) |
|---|---:|---:|
| Macro-F1 (categories with an answer) | 0.4139 | 0.3606 |
| Micro-F1 | 0.4272 | 0.3577 |
| Answer labels | 70 | 90 |
| Flags | 33 | 33 |
| Correct tags | 22 | 22 |
| Wrong tags | 11 | 11 |
| Missed labels | 48 | 68 |
| Flags per 100 sentences | 8.78 | 8.78 |

Validation macro-F1 (honest, Session 07): 0.6768. Categories in the strict macro-F1: Limitation of liability, Unilateral termination, Unilateral change, Content removal, Contract by using, Choice of law, Jurisdiction, Arbitration.

## Per category (strict)

| Category | Answers | Flags | Correct | Wrong | Missed | F1 |
|---|---:|---:|---:|---:|---:|---:|
| Limitation of liability | 21 | 11 | 7 | 4 | 14 | 0.44 |
| Unilateral termination | 18 | 11 | 7 | 4 | 11 | 0.48 |
| Unilateral change | 9 | 4 | 2 | 2 | 7 | 0.31 |
| Content removal | 4 | 2 | 1 | 1 | 3 | 0.33 |
| Contract by using | 9 | 3 | 3 | 0 | 6 | 0.50 |
| Choice of law | 1 | 1 | 1 | 0 | 0 | 1.00 |
| Jurisdiction | 1 | 0 | 0 | 0 | 1 | 0.00 |
| Arbitration | 7 | 1 | 1 | 0 | 6 | 0.25 |

## Help for missed clauses (strict)

| What the user sees | How many | Per 100 sentences | Missed labels reached |
|---|---:|---:|---:|
| Possible cues, margin 0.05 | 6 | 1.60 | 2 of 48 (4.2%) |
| Possible cues, margin 0.10 | 11 | 2.93 | 4 of 48 (8.3%) |
| Worth-a-look marks, all | 64 | 17.02 | 18 of 48 (37.5%) |
| Worth-a-look marks, zero-flag categories only | 11 | 2.93 | 1 of 48 (2.1%) |

## The three pre-set rules (strict answers)

- **Domain shift:** fresh macro-F1 0.4139 against 0.6768, a drop of 0.2629 (the limit is 0.15). Result: **DOMAIN SHIFT: treat it as the main risk in Session 11**.
- **Cue margin 0.10:** reach 8.3% of missed labels (needs at least 20%), 2.93 per 100 sentences (at most 5). Result: **KEEP the 0.05 margin**.
- **Zero-flag-only marks:** reach 2.1% of missed labels (needs at least 40%), 2.93 per 100 sentences (at most 20). Result: **KEEP showing all marks, off-by-default toggle stays**.

## Every error (strict)

| Document | Sentence | Category | Kind | Score | Cut-off |
|---|---:|---|---|---:|---:|
| basecamp | 17 | Contract by using | missed label | 0.519 | 0.80 |
| basecamp | 19 | Limitation of liability | missed label | 0.723 | 0.75 |
| basecamp | 25 | Limitation of liability | wrong tag | 0.997 | 0.75 |
| basecamp | 35 | Unilateral termination | missed label | 0.037 | 0.70 |
| basecamp | 36 | Unilateral termination | missed label | 0.120 | 0.70 |
| basecamp | 37 | Unilateral termination | missed label | 0.158 | 0.70 |
| basecamp | 52 | Content removal | missed label | 0.256 | 0.80 |
| basecamp | 53 | Content removal | missed label | 0.287 | 0.80 |
| basecamp | 54 | Content removal | missed label | 0.390 | 0.80 |
| basecamp | 63 | Unilateral termination | missed label | 0.446 | 0.70 |
| basecamp | 67 | Unilateral termination | missed label | 0.506 | 0.70 |
| basecamp | 72 | Unilateral termination | wrong tag | 0.990 | 0.70 |
| basecamp | 72 | Content removal | wrong tag | 0.824 | 0.80 |
| basecamp | 75 | Unilateral change | missed label | 0.618 | 0.80 |
| basecamp | 83 | Unilateral termination | missed label | 0.464 | 0.70 |
| basecamp | 125 | Unilateral termination | wrong tag | 0.812 | 0.70 |
| basecamp | 144 | Unilateral termination | wrong tag | 0.836 | 0.70 |
| basecamp | 145 | Unilateral termination | missed label | 0.393 | 0.70 |
| basecamp | 148 | Limitation of liability | missed label | 0.651 | 0.75 |
| basecamp | 149 | Limitation of liability | wrong tag | 0.996 | 0.75 |
| basecamp | 153 | Limitation of liability | missed label | 0.034 | 0.75 |
| cloudup | 4 | Contract by using | missed label | 0.050 | 0.80 |
| cloudup | 5 | Contract by using | missed label | 0.179 | 0.80 |
| cloudup | 8 | Contract by using | missed label | 0.113 | 0.80 |
| cloudup | 32 | Unilateral change | wrong tag | 0.837 | 0.80 |
| cloudup | 33 | Unilateral change | missed label | 0.303 | 0.80 |
| cloudup | 35 | Unilateral change | missed label | 0.174 | 0.80 |
| cloudup | 36 | Unilateral change | missed label | 0.255 | 0.80 |
| cloudup | 37 | Unilateral change | missed label | 0.024 | 0.80 |
| cloudup | 37 | Contract by using | missed label | 0.632 | 0.80 |
| cloudup | 38 | Unilateral change | missed label | 0.068 | 0.80 |
| cloudup | 43 | Unilateral termination | missed label | 0.637 | 0.70 |
| cloudup | 49 | Unilateral termination | wrong tag | 0.714 | 0.70 |
| cloudup | 51 | Unilateral change | wrong tag | 0.989 | 0.80 |
| cloudup | 55 | Limitation of liability | wrong tag | 0.970 | 0.75 |
| cloudup | 57 | Limitation of liability | missed label | 0.426 | 0.75 |
| cloudup | 65 | Arbitration | missed label | 0.057 | 0.80 |
| cloudup | 66 | Arbitration | missed label | 0.758 | 0.80 |
| cloudup | 67 | Arbitration | missed label | 0.558 | 0.80 |
| cloudup | 68 | Arbitration | missed label | 0.033 | 0.80 |
| cloudup | 72 | Jurisdiction | missed label | 0.094 | 0.55 |
| cloudup | 74 | Arbitration | missed label | 0.194 | 0.80 |
| cloudup | 75 | Arbitration | missed label | 0.118 | 0.80 |
| crowdsignal | 3 | Contract by using | missed label | 0.235 | 0.80 |
| crowdsignal | 32 | Unilateral termination | missed label | 0.511 | 0.70 |
| crowdsignal | 77 | Limitation of liability | missed label | 0.022 | 0.75 |
| crowdsignal | 78 | Limitation of liability | missed label | 0.098 | 0.75 |
| crowdsignal | 79 | Limitation of liability | missed label | 0.029 | 0.75 |
| crowdsignal | 82 | Limitation of liability | missed label | 0.079 | 0.75 |
| crowdsignal | 83 | Limitation of liability | missed label | 0.203 | 0.75 |
| crowdsignal | 84 | Limitation of liability | missed label | 0.330 | 0.75 |
| crowdsignal | 88 | Limitation of liability | missed label | 0.042 | 0.75 |
| crowdsignal | 92 | Unilateral change | missed label | 0.134 | 0.80 |
| crowdsignal | 95 | Limitation of liability | wrong tag | 0.976 | 0.75 |
| crowdsignal | 101 | Limitation of liability | missed label | 0.072 | 0.75 |
| crowdsignal | 102 | Limitation of liability | missed label | 0.128 | 0.75 |
| crowdsignal | 105 | Limitation of liability | missed label | 0.021 | 0.75 |
| crowdsignal | 128 | Unilateral termination | missed label | 0.214 | 0.70 |
| crowdsignal | 132 | Unilateral termination | missed label | 0.420 | 0.70 |

Counts, sentence numbers (from 1) and scores only, no sentence text. The rules use the strict answer set; lenient is reported only. Three documents and two team annotators: a small check. The *_text and summary fields give the same values as text for the report.
