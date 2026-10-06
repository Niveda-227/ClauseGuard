# Mid-semester presentation (Session 06, Tuesday October 6, 2026)

Five minutes plus two for questions. Presenter: **Niveda** (the final demo day presenter is Ameer, so the presenter rotates as the course requires).

| File | What it is | Made by |
|---|---|---|
| `slides.html` | The deck. Open in a browser: arrow keys to move, **F** full screen, **T** timer | `scripts/build_slides.py` |
| `slides.md` | The same deck as Markdown (renders on GitHub) | `scripts/build_slides.py` |
| `speaker_notes.md` | What the presenter says on each slide | `scripts/build_slides.py` |
| `qa_prep.md` | Likely questions, who answers, and the source of each answer | `scripts/build_slides.py` |
| `metrics.md`, `facts.json`, `figures/` | Every number and chart, computed from committed files | `scripts/midpoint_facts.py` |
| `src/` | The hand-written sources of the four generated files above. **Edit these, not the generated files** | Ankan, with the team |
| `rehearsal_log.md` | Real, timed rehearsals | Ankan |

## Where the numbers come from

- Model vs baseline: `experiments/session04/*/metrics.json` (validation split; the test split is not used before Session 12).
- Threshold experiment: `experiments/session05/threshold_cv.json` (not shipped).
- Users: `evidence/session05/` and `evidence/session06/` (protocol sep29_v2).
- Decision rule: `docs/decisions/midpoint_rule.json`, committed before the Session 06 sessions; the decision itself is in `docs/decisions/2026-10-06_midpoint_decision.md`.
- Cost to serve: `experiments/session06/demo_check.json`.

## Rebuild

```bash
python scripts/build_slides.py --final
```

It re-computes every number first and refuses to build while a placeholder is unfilled, a link is broken or the deck is over 5:00.

## The demo

The demo runs the real app (`python app.py`) on `examples/fictional_terms.txt`, following `docs/DEMO_RUNSHEET_midpoint.md`. Fallbacks, in order: the HTML version of the same analysis (`analysis.html`, made by `scripts/demo_check.py`), then Hemanth's recorded backup.
