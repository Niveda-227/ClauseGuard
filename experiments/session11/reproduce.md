# Rebuilding the product model from a clean clone (Session 11)

**Reproduced: yes.** The shipped configuration (word 1-2-grams + character 3-5-grams (TF-IDF); one logistic regression per category (liblinear, C 1.0, balanced class weights); seed 641) was trained on the train split only with the product code and given the product cut-offs.

| Check | Passed |
|---|---|
| Validation scores equal the product model's (within one millionth) | yes |
| Same flags on every validation sentence | yes |
| Demo document flagged exactly as rehearsed | yes |
| Training sentences match the model manifest | yes |
| Training companies match the model manifest | yes |
| Dataset archive matches the model manifest | yes |

## Fingerprints of this release

- Dataset archive SHA-256: `934470d74b62139dfbfad4a13b75a32e4a4d26a680ab12eedfb7659cdf669d53`
- Product model file (`artifacts/selected.joblib`) SHA-256: `dafbb5470f2fb2678cae273eac7c23046bbad0487c7be247174a99a08ad493bd`
- Training data: 5532 sentences from 30 companies; validation: 2275 sentences
- Cut-offs: Limitation of liability 0.75, Unilateral termination 0.70, Unilateral change 0.80, Content removal 0.80, Contract by using 0.80, Choice of law 0.65, Jurisdiction 0.55, Arbitration 0.80
- SHA-256 over the validation flags: `0e635d75ca4662bd4e5b0511f101117e78c3b0d14da76b16a22c03a9565cea3b`

The rebuilt model is compared by its outputs, not by its file bytes: a saved joblib file contains a creation time and so never has the same SHA-256 twice.
The test split was not read.
