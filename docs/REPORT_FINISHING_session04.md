# Finish the factual fields and generate the upload report

The supplied `reports/session04.md` contains **real technical results** and the exact course section order. It cannot truthfully claim that your team merged code, obtained reviews or ran outside-user sessions until those actions occur. The facts file makes the remaining edits explicit.

## Fill `submission_facts.json`

| Field | What you enter |
|---|---|
| `repo_url` | Already set to `https://github.com/Niveda-227/ClauseGuard` (no branch suffix) |
| `branch_protection_verified` | Set to true only after inspecting `main` protection requiring one approving review |
| `outside_user_evidence_reviewed` | Set to true only after reviewing actual anonymous records of outside users using the running product |
| `contributions_verified` | Set to true only after checking all five members' actual work and supporting links |
| `shipped_evidence_urls` | Actual linked issue, approved PR and merged commit URLs for work now on `main` |
| `user_observation` | Who in anonymous terms, date, actual interface, task, outcome and observed friction; no invented quotes |
| `change_from_user` | What you changed because of the session, or what you explicitly queued and why |
| `user_change_evidence_urls` | PR for the change, or issue for the honest next action |
| `current_blockers` | Actual remaining limitation, owner, needed help and next step; use a clear sentence if no new blocker |
| `members.NAME.github` | That person's real GitHub handle, without `@` (Niveda pre-filled as `Niveda-227`; confirm) |
| `members.NAME.completed_work` | Concrete engineering and research/evaluation work that person actually completed |
| `members.NAME.evidence_urls` | Real issue/PR/commit links backing that contribution, including their code work |

All URL lists must point to your repository. The script checks syntax and local files, **not GitHub's live state or the authenticity of your statements**. Do not mark flags true without checking.

## Generate and inspect

Run from the project root after the actual sessions and code merges:

```bash
python scripts/finalize_session04.py
python scripts/validate_submission.py --session 04 --ready
```

The finalizer reads genuine `evidence/session04/tasks.csv`, computes the product metric for the included model and `sep22_v1`, fills handles and contributions, and writes the user summary. It keeps an ignored local backup of the pre-finalization report. Review the resulting Markdown yourself. If validation stops, address the real missing work; do not remove checks to make an incomplete report look complete.

Then open a report PR linking the actual issue; have a teammate approve it and merge before 5 p.m. Eastern. GitHub proof links for earlier implementation PRs can already exist when the report PR is opened. The final report PR itself need not claim it was merged before it actually was.

If the deadline arrives with missing user evidence, submit the honest report with unknown values and the blocker explained. That may lose requirement-specific credit, but does not justify invented activity.
