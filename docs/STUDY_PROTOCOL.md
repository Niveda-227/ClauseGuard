# Outside-user study protocol

**Version:** v1 proposal, subject to a pilot before locking. No user sessions have been conducted for this package.

1. Recruit people outside the five-member team. Explain that the task tests software usability and clause finding, not the legal safety of their agreements. Get informed agreement to the activity and any recording. A recording is optional; a contemporaneous anonymized task record also counts under the course guidelines.
2. Use permitted public/fictional documents and a reviewed task answer key. Avoid private agreements or personal information. The provided fictional text is a demonstration, not representative evaluation data. Team-generated labels are not independent legal judgments.
3. Assign anonymous participant IDs such as U001. Store any recruitment/contact records separately from the repo. Do not enter names or emails into the logging command.
4. Give a concrete task such as finding the clause that permits unilateral changes. Include tasks whose target category is absent. Predefine correct outcomes before observing users.
5. Compare original-text and ClauseGuard conditions on matched, different documents. Counterbalance condition order. Record language/experience factors only at a non-identifying level if relevant and consented.
6. Start a timer when the user receives the task. Record completion time for all tasks, correct/incorrect outcome, and model identity. The proposed north-star is correct completion within 180 seconds. Failed, timed-out and abandoned assigned tasks belong in the denominator; record them as incorrect and retain elapsed time. Do not report only successful tasks.
7. Record what confused the user at the time. Open an issue describing the product change it motivates. Commit anonymized raw evidence in the same reporting week.
8. Report participant count, task count, protocol, condition order and any changes. The same tester can participate again, but describe repeat exposure. No course-mandated participant count was specified; a few well-recorded sessions are a reasonable early target, not proof of general effectiveness.

## Logging an actual task

Run this only after a real session, replacing the example values with observed values:

```bash
python -m clauses.cli record-task --output evidence/session04/tasks.csv --participant U001 --task D01_change --condition clauseguard --correct yes --seconds 85 --protocol v1
python -m clauses.cli summarize-tasks --input evidence/session04/tasks.csv
```

The command records current UTC time and the actual selected model's SHA-256. It rejects duplicates for the same participant/task/condition/protocol. For a genuine later trial use a new task ID. For manual reading use `--condition manual`. The numbers in the command are examples, not evidence. The script cannot verify that a person or task existed; the team is accountable for accurate records.

## Raw evidence folder contents

Recommended: tasks.csv, dated observation notes using anonymous IDs, a consent-status note, and a permitted screenshot or recording if collected. Do not commit private consent signatures or recruitment contacts. Record the model hash and commit shown to users. Unit-test data and the fictional demonstration do not count as user validation.

## Analysis and limitations

Success percent = 100 × successful tasks / all assigned tasks. Report median time across all tasks and clarify timeouts, not just the faster successful cases. Summaries keep model/protocol/time-limit groups separate. Avoid claims of significance from small convenience samples. No flag is not evidence that a term is safe, and users' confidence is not the ground truth for classification.
