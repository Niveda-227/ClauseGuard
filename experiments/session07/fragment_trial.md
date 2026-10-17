# Heading and short-fragment filter: trial (Session 07)

Product model (per-category thresholds) on 2,275 validation sentences: 239 flags, 62 of them wrong tags. 0 sentences have fewer than 6 words. Not shipped; the app is unchanged.

Rule set before running: PASS = removes at least 5 wrong tags AND no annotator label on any hidden sentence.

| Candidate filter | Sentences hidden | Flags removed | Wrong tags removed | Correct tags removed | Annotator labels on hidden sentences | Passes |
|---|---:|---:|---:|---:|---:|---|
| fewer than 3 words | 0 | 0 | 0 | 0 | 0 | no |
| fewer than 4 words | 0 | 0 | 0 | 0 | 0 | no |
| fewer than 5 words | 0 | 0 | 0 | 0 | 0 | no |
| fewer than 6 words | 0 | 0 | 0 | 0 | 0 | no |
| letters but no lower case (ALL-CAPS heading) | 0 | 0 | 0 | 0 | 0 | no |
| 8 words or fewer and no . ! ? ; : at the end | 53 | 2 | 2 | 0 | 0 | no |

**Result:** no candidate passes the rule; do not ship a fragment filter.

Validation split only; counts are optimistic because the candidates are compared on the same split. Not shipped: a passing filter is a Session 08 candidate. No sentence text is stored.
