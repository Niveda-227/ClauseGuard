# The one-time test-split result (Session 12)

Release 1.0.0, model `dafbb5470f2fb2678cae273eac7c23046bbad0487c7be247174a99a08ad493bd`, shipped cut-offs. Test split: 1607 sentences from 10 companies, read once by `scripts/final_test.py` (see `experiments/test_exposure.jsonl`). Rule: [docs/decisions/final_test_rule.json](../../docs/decisions/final_test_rule.json).

| Measure | Test split | Honest validation | Optimistic validation |
|---|---:|---:|---:|
| Macro-F1 (8 categories) | 0.7626 | 0.6768 | 0.7244 |
| Micro-F1 | 0.7292 | | |
| Flags per 100 sentences | 11.64 | | |
| Correct tags / wrong tags / missed labels | 136 / 51 / 50 | | |

**The pre-set rule:** test macro-F1 0.7626; honest validation 0.6768; difference +0.0858 (margin 0.05). **Result: HIGHER than the honest validation estimate.**

## By category

| Category | Test support | Test precision | Test recall | Test F1 | Honest validation F1 |
|---|---:|---:|---:|---:|---:|
| Limitation of liability | 38 | 0.6750 | 0.7105 | 0.6923 | 0.6929 |
| Unilateral termination | 38 | 0.6522 | 0.7895 | 0.7143 | 0.6875 |
| Unilateral change | 38 | 0.7188 | 0.6053 | 0.6571 | 0.6545 |
| Content removal | 13 | 0.5789 | 0.8462 | 0.6875 | 0.6071 |
| Contract by using | 23 | 0.9375 | 0.6522 | 0.7692 | 0.7500 |
| Choice of law | 13 | 0.9231 | 0.9231 | 0.9231 | 0.7742 |
| Jurisdiction | 16 | 0.8571 | 0.7500 | 0.8000 | 0.9000 |
| Arbitration | 7 | 0.8571 | 0.8571 | 0.8571 | 0.3478 |

Read once with the frozen release and its shipped cut-offs; nothing was tuned on the test split. Counts and scores only.
