# Ablation: which configuration should the final release use? (Session 11)

Validation split only (2275 sentences, 10 companies); test split not read. Rule: [docs/decisions/final_model_rule.json](../../docs/decisions/final_model_rule.json), frozen before this script was first run, never changed after.

Sanity check: the retrained shipped configuration reproduces the product model's validation scores (within one millionth: yes; same flags: yes).

| Rank | Features | Class weighting | Cut-offs | Honest macro-F1 | Micro-F1 | Flags per 100 | Fresh docs macro-F1 (reported only) |
|---:|---|---|---|---:|---:|---:|---:|
| 1 | hybrid (shipped) | balanced | per_category | 0.6768 | 0.6880 | 11.03 | 0.4139 |
| 2 | word | balanced | per_category | 0.6563 | 0.6571 | 10.59 | 0.4359 |
| 3 | char | balanced | per_category | 0.6455 | 0.6545 | 13.10 | 0.4055 |
| 4 | hybrid | balanced | fixed_0.5 | 0.6333 | 0.6275 | 17.49 | 0.4653 |
| 5 | hybrid | none | per_category | 0.6277 | 0.6498 | 9.89 | 0.4041 |
| 6 | word | balanced | fixed_0.5 | 0.6156 | 0.6084 | 18.24 | 0.4730 |
| 7 | char | balanced | fixed_0.5 | 0.5684 | 0.5615 | 21.93 | 0.4257 |
| 8 | char | none | per_category | 0.5598 | 0.6051 | 11.43 | 0.4055 |
| 9 | word | none | per_category | 0.4927 | 0.5826 | 9.27 | 0.4158 |
| 10 | hybrid | none | fixed_0.5 | 0.3598 | 0.4343 | 3.43 | 0.1961 |
| 11 | char | none | fixed_0.5 | 0.2540 | 0.3366 | 2.37 | 0.1640 |
| 12 | word | none | fixed_0.5 | 0.1405 | 0.2151 | 1.32 | 0.0891 |

## Per category (honest F1)

| Configuration | Limitation of liability | Unilateral termination | Unilateral change | Content removal | Contract by using | Choice of law | Jurisdiction | Arbitration |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| hybrid / balanced / per_category | 0.693 | 0.688 | 0.654 | 0.607 | 0.750 | 0.774 | 0.900 | 0.348 |
| word / balanced / per_category | 0.677 | 0.646 | 0.528 | 0.576 | 0.800 | 0.774 | 0.778 | 0.471 |
| char / balanced / per_category | 0.667 | 0.653 | 0.600 | 0.571 | 0.718 | 0.765 | 0.842 | 0.348 |
| hybrid / balanced / fixed_0.5 | 0.629 | 0.658 | 0.506 | 0.540 | 0.720 | 0.812 | 0.878 | 0.323 |
| hybrid / none / per_category | 0.644 | 0.703 | 0.481 | 0.604 | 0.683 | 0.667 | 0.865 | 0.375 |
| word / balanced / fixed_0.5 | 0.637 | 0.637 | 0.458 | 0.513 | 0.679 | 0.788 | 0.842 | 0.370 |
| char / balanced / fixed_0.5 | 0.603 | 0.603 | 0.440 | 0.440 | 0.562 | 0.743 | 0.800 | 0.356 |
| char / none / per_category | 0.580 | 0.667 | 0.425 | 0.604 | 0.600 | 0.615 | 0.833 | 0.154 |
| word / none / per_category | 0.603 | 0.676 | 0.520 | 0.471 | 0.588 | 0.667 | 0.417 | 0.000 |
| hybrid / none / fixed_0.5 | 0.483 | 0.488 | 0.537 | 0.270 | 0.560 | 0.435 | 0.105 | 0.000 |
| char / none / fixed_0.5 | 0.400 | 0.436 | 0.400 | 0.222 | 0.105 | 0.364 | 0.105 | 0.000 |
| word / none / fixed_0.5 | 0.346 | 0.212 | 0.400 | 0.061 | 0.000 | 0.105 | 0.000 | 0.000 |

## The pre-set rule

- best hybrid / balanced / per_category 0.6768; shipped 0.6768; gain 0.0000 (a switch needs at least 0.02).
- **Result: KEEP the shipped model for the final release.**

Validation split only; honest = leave-one-company-out for per-category cut-offs. Choosing among 12 configurations on one split flatters the best one; the Session 12 test-split run is the unbiased number. Fresh-document macro-F1 is reported only: those labels were not made independently.
