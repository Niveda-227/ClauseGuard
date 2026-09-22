# Weekly-report evidence-link checking

A correctly named report can still point to missing evidence files. This checker resolves inline local Markdown links relative to the report, rejects paths outside the repository and flags unresolved report fields.

## Run

```bash
python scripts/check_report_links.py --output experiments/session04/ankan_link_check.json
python -m unittest discover -s tests -p 'test_ankan_links.py' -v
```

## How it works

A local path check proves only that a referenced file or directory exists. It cannot establish that a user session was real, that a PR was approved, or that main contains the report at the deadline.

Your first PR can contain only the link checker and its test/usage guide. After the other PRs and real user sessions are complete, open a **separate report-finalization PR**:

```bash
python scripts/finalize_session04.py
python scripts/validate_submission.py --session 04 --ready
python scripts/check_report_links.py --ready --output experiments/session04/ankan_link_check.json
```

Fill `submission_facts.json` with real facts first. The finalizer and ready checks may correctly stop until they exist. Include the final report and summary; ask Ameer to review. Do not mark a future report merge as already completed. This checker handles the supplied report's inline links; it does not implement every Markdown syntax or validate remote URLs/anchors.

## Research question

Compare the eight course headings with the actual report, audit its proof links against the repo, and inspect branch protection manually. Identify any missing evidence and its owner.

This is AI-assisted implementation material. Team members should record their actual review, adaptation and verification in the PR rather than claim unperformed work.
