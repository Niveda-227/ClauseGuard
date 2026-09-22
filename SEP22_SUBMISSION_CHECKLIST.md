# Due today: September 22, 2026

**Deadline: 5:00 p.m. Eastern (EDT), equivalent to 21:00 UTC.** This is Session 04, the first weekly report. The course grades what is on the team repository's `main` at the cutoff.

## Required deliverables

| Requirement | What must exist by the deadline | Included / remaining |
|---|---|---|
| Correct weekly report | `reports/session04.md` on `main`, with the exact YAML fields and eight template sections | Technical sections populated; real team/GitHub/user facts remain |
| Shipped work | Working code merged to `main` or deployed, supported by issues and approving PR reviews | Runnable code included; team must review and merge |
| Real-user validation | Outside-team person uses running product; raw timestamped evidence committed this week | Timer, documents and protocol included; conduct the actual session |
| Metrics | Actual number, comparison and evaluation provenance; first prior value may be honestly unavailable | Three verified model results included; collect product north-star |
| Balanced contribution | Visible actual work from all five members, with code and supporting evidence | Five-person task/review plan included; perform and link actual work |
| Branch protection | `main` requires at least one approving review | Team must verify in GitHub; checked by instructor today |
| Existing team setup | Company/problem, hats, repository URL submitted; instructor `aaarrmiinnn` has access if private | Names/hats provided; repo is https://github.com/Niveda-227/ClauseGuard (owner Niveda-227); instructor access still to verify if private |
| Startup framing | One-page lean canvas kept in the repo | Included; team reviews hypotheses and updates from real findings |

No slides, final report, full-semester completion or paid deployment is due today. The course does not set a minimum user count or an F1 pass threshold. The two-person pilot below is our practical recommendation, not an instructor rule.

## Suggested execution timeline — all times Eastern

| Time / checkpoint | Owner | Concrete action / output |
|---|---|---|
| Start now; aim before noon | All five | Extract, install Python dependencies, read your task, run product; agree which generated work each person will review/adapt |
| By 1:00 p.m. | Niveda (repo owner) + Hemanth + Ankan | Verify repo access, issues, labels, assignees, Session 04 milestone and board; protect `main`; open implementation PR |
| By 2:00 p.m. | Jayakrishna + Hemanth | Reproduce tests/model results; inspect false positives and a false negative; verify laptop GUI or CLI workflow |
| By 3:00 p.m. | Niveda + Ameer | Run real outside-user tasks, capture CSV/JSON contemporaneously, note one friction point; make a justified small fix or file its next-action issue |
| By 4:00 p.m. | All five | Complete/review each assigned work item; fill actual contribution statements and proof links |
| By 4:30 p.m. | Ankan + Ameer | Fill `submission_facts.json`; finalize report; calculate actual north-star; verify paths and all links |
| By 4:45 p.m. | PR reviewer + author | Approve and merge report, code and evidence; leave time for corrections |
| Before 5:00 p.m. | Ankan + Hemanth | Open remote `main`; inspect `reports/session04.md`, evidence files, model files and branch protection; confirm repository URL submission/access |

If starting later, compress the working blocks while preserving actual evidence and review. Do not backdate missing work. Report a missed item honestly if it cannot be completed.

## What to commit

Commit source (`app.py`, `clauses/`, `scripts/`, `tests/`), `requirements.txt`, model files in `artifacts/`, documentation, the Session 04 report, `experiments/session04/`, and the genuine anonymous files created in `evidence/session04/`. Keep the earlier initial experiment provenance as supplied.

Do not commit `.venv`, cache files, downloaded data archives, personal user data, API keys, or unrelated private documents. The supplied `.gitignore` covers routine generated/private paths. Do not upload only the ZIP: the grader needs the actual root-level report path.

## GitHub workflow

1. Use the shared team repo: https://github.com/Niveda-227/ClauseGuard. Niveda (owner) adds the four teammates as collaborators. Submit its URL through the instructor's designated channel; the guideline does not specify a platform in this document.
2. Ensure `main` requires one approving review. If the repo is private, ensure the instructor can access it.
3. Create a labeled, assigned issue per real task and a Session 04 milestone. Board columns: Todo, In Progress, In Review, Done.
4. Work on a branch for the issue; put its actual number in the branch name. Commit completed work using the actual author's account.
5. Open a PR, link the issue (`Closes #<actual issue number>`), and request the assigned teammate reviewer. A review must precede merge.
6. Merge code and experiments, collect/commit the current user evidence, and merge the final report before the cutoff. Add real merge/PR links in the report.
7. Open the remote `main` report and click every relative evidence link. A file on a feature branch or a local commit alone is insufficient.

Do not manufacture backdated commits, empty contributions or review history. The package is a starting implementation; each reported contribution must reflect work the named member actually did.

## Last inspection

- [ ] Five real GitHub handles in YAML; five accurate contribution statements with evidence.
- [ ] Real issue + approved PR + commit links support shipped claims.
- [ ] Raw outside-user records are anonymized and included in this week's merge.
- [ ] Product success numerator/denominator match the CSV; previous is `null` for this first week.
- [ ] Model F1 values are described as validation development results, not final test performance or week-over-week improvement.
- [ ] The app uses the reported hybrid SHA-256; selected model files open locally.
- [ ] `python scripts/validate_submission.py --session 04 --ready` passes after actual facts are inserted.
- [ ] Remote `main` contains the report by 5:00 p.m. Eastern; protection and instructor access checked.

Sources: [course guidelines](https://github.com/aaarrmiinnn/UMD-DATA641-MSML641/blob/fall-2026/project/guidelines.md) and [report template](https://github.com/aaarrmiinnn/UMD-DATA641-MSML641/blob/fall-2026/reports/_TEMPLATE.md), fetched September 22. Local copies are in `course_reference/`.
