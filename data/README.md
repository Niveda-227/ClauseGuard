# Data access and provenance

Source: UNFAIR-ToS distributed with LexGLUE, original CLAUDETTE research.

- https://huggingface.co/datasets/coastalcph/lex_glue
- https://zenodo.org/records/5532997
- https://arxiv.org/abs/1805.01217
- https://aclanthology.org/2022.acl-long.297/

The dataset card lists CC BY 4.0 for the distribution. Preserve attribution and inspect original-source rights before redistributing additional documents. The ZIP excludes the source archive; `python -m clauses.cli data` fetches it and checks SHA-256:

`934470d74b62139dfbfad4a13b75a32e4a4d26a680ab12eedfb7659cdf669d53`

Read the pinned archive's `unfair_tos.jsonl` member. Verified splits: 5,532 train, 2,275 validation, 1,607 test. The original source has `company` and `data_type`, allowing document-aware checks. Label order is defined in `clauses/schema.py` and matches the dataset card. Preserve test separation. Initial evaluation used only validation; final-test predictions/metrics are not supplied.

No private user documents belong in this folder. `examples/fictional_terms.txt` was authored for this project and has no benchmark claims. Experiment exports use source row IDs and labels, not copied full text. Source code and model artifacts do not remove the need to cite the original data and record future third-party license requirements.
